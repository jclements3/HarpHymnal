#!/usr/bin/env python3
"""Phrase-level Chopin-treatment piano renderer.

Three surface textures share the same voice-leading chain:
  L1  build_phrase_abc / render_phrase_piano_svg       — held ATB pad
  L2  build_phrase_abc_l2 / render_phrase_piano_svg_l2 — oom-pah-pah LH
  L3  build_phrase_abc_l3 / render_phrase_piano_svg_l3 — passing-tone soprano

`build_hymn_view.py` calls all three on each phrase and emits all three
SVGs side-by-side, then JS swaps them via the chopin-lvl-btn selector.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from voice_lead import (
    Voice, Voicing, chord_letters, initial_voicing_with_melody,
    solve_next_voicing,
)

REPO = Path(__file__).resolve().parents[1]
SHAPES = REPO / 'shapes'


# Key-signature accidental tables (sharps/flats added in standard order).
_SHARP_ORDER = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
_FLAT_ORDER  = ['B', 'E', 'A', 'D', 'G', 'C', 'F']
_MAJOR_FIFTHS = {
    'C':  0, 'G':  1, 'D':  2, 'A':  3, 'E':  4, 'B':  5, 'F#': 6, 'C#': 7,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6, 'Cb': -7,
}
_MINOR_FIFTHS = {
    'A':  0, 'E':  1, 'B':  2, 'F#': 3, 'C#': 4, 'G#': 5, 'D#': 6, 'A#': 7,
    'D': -1, 'G': -2, 'C': -3, 'F': -4, 'Bb': -5, 'Eb': -6, 'Ab': -7,
}


def _key_accidentals(key_root: str, mode: str) -> dict:
    """Letters → '#' or 'b' for what the key signature already alters."""
    table = _MINOR_FIFTHS if mode == 'minor' else _MAJOR_FIFTHS
    n = table.get(key_root, 0)
    out = {}
    if n > 0:
        for letter in _SHARP_ORDER[:n]:
            out[letter] = '#'
    elif n < 0:
        for letter in _FLAT_ORDER[:-n]:
            out[letter] = 'b'
    return out


def _abc_pitch(letter: str, accidental: str, octave: int,
               bar_state: dict | None = None) -> str:
    """Emit one ABC pitch token.

    When `bar_state` is supplied, only emit an accidental marker if the
    note's accidental differs from what's currently in force for that
    letter (initially the key signature, then whatever was last emitted
    in this bar). This matches abcm2ps's bar-persistence rule and avoids
    re-marking accidentals already implied by the key signature."""
    if bar_state is None:
        marker = {'#': '^', 'b': '_', '': ''}.get(accidental, '')
    else:
        cur = bar_state.get(letter, '')
        if accidental == cur:
            marker = ''
        else:
            marker = {'#': '^', 'b': '_', '': '='}[accidental]
            bar_state[letter] = accidental
    if octave >= 5:
        return marker + letter.lower() + ("'" * (octave - 5))
    return marker + letter.upper() + ("," * (4 - octave))


def _norm_acc(a) -> str:
    if a in (None, ''): return ''
    if a in ('#', '♯'): return '#'
    if a in ('b', '♭'): return 'b'
    return ''


def _melody_pitches(bar: dict) -> list[Voice]:
    out = []
    for ev in bar.get('melody') or []:
        if ev.get('kind') != 'note':
            continue
        p = ev['pitch']
        out.append(Voice(p['letter'], _norm_acc(p.get('accidental')), p['octave']))
    return out


def _melody_to_abc(bar: dict, sixteenths_per_beat: int,
                   bar_state: dict | None = None) -> str:
    """Render the bar's melody as an ABC token sequence under L:1/16.

    Durations in the JSON are in quarter-note lengths; convert each to an
    integer count of sixteenth-notes and emit `<pitch><count>`. Rests inside
    the melody are emitted as `z<count>`. Threads `bar_state` so accidentals
    are not re-marked when the key signature already covers them.
    """
    parts = []
    for ev in bar.get('melody') or []:
        dur_q = ev.get('duration') or 0
        n = max(1, round(dur_q * sixteenths_per_beat))
        if ev.get('kind') == 'rest':
            parts.append(f'z{n}')
            continue
        if ev.get('kind') != 'note':
            continue
        p = ev['pitch']
        parts.append(_abc_pitch(p['letter'], _norm_acc(p.get('accidental')),
                                p['octave'], bar_state) + str(n))
    return ' '.join(parts)


def _bar_chord_pcs(bar: dict, key_root: str) -> list[str]:
    ch = bar.get('chord') or {}
    num = ch.get('numeral') or 'I'
    qual = ch.get('quality') or ''
    return chord_letters(num, qual, key_root)


def _chord_token(voices: list[Voice], count: int,
                 bar_state: dict | None = None) -> str:
    pitches = [_abc_pitch(v.letter, v.accidental, v.octave, bar_state) for v in
               sorted(voices, key=lambda x: x.midi())]
    return '[' + ''.join(pitches) + ']' + str(count)


def _bar_units(beats: int, unit: int) -> int:
    """Sixteenth-note count for one full bar at the given meter."""
    return int(beats * 4 * (4 / unit))


def build_phrase_abc(phrase_bars: list[dict], voicings: list[Voicing],
                     key_root: str, mode: str, beats: int, unit: int,
                     title: str = '') -> str:
    """ABC for a single phrase: melody at original rhythm + voice-led ATB pad.

    `phrase_bars` and `voicings` are 1:1 — each bar's voicing supplies the
    A/T/B pitches for that bar. Empty/melody-less bars get rests."""
    bar_units = _bar_units(beats, unit)
    abc_key = key_root + ('m' if mode == 'minor' else '')
    key_acc = _key_accidentals(key_root, mode)

    soprano_lines, alto_lines, tenor_lines, bass_lines = [], [], [], []
    for bar, v in zip(phrase_bars, voicings):
        soprano_lines.append(_melody_to_abc(bar, 4, dict(key_acc)) or f'z{bar_units}')
        if v is None:
            alto_lines.append(f'z{bar_units}')
            tenor_lines.append(f'z{bar_units}')
            bass_lines.append(f'z{bar_units}')
        else:
            alto_lines.append(_chord_token([v.a], bar_units, dict(key_acc)))
            tenor_lines.append(_chord_token([v.t], bar_units, dict(key_acc)))
            bass_lines.append(_chord_token([v.b], bar_units, dict(key_acc)))

    return (
        'X: 1\n'
        f'T: {title}\n'
        f'M: {beats}/{unit}\n'
        'L: 1/16\n'
        f'K: {abc_key}\n'
        '%%staves [(S A) (T B)]\n'
        '%%scale 0.7\n'
        '%%staffsep 22\n'
        '%%musicspace 4\n'
        '%%maxshrink 1.0\n'
        'V: S clef=treble\n'
        'V: A clef=treble\n'
        'V: T clef=bass\n'
        'V: B clef=bass\n'
        '[V: S] ' + (' | '.join(soprano_lines) + ' |') + '\n'
        '[V: A] ' + (' | '.join(alto_lines) + ' |') + '\n'
        '[V: T] ' + (' | '.join(tenor_lines) + ' |') + '\n'
        '[V: B] ' + (' | '.join(bass_lines) + ' |') + '\n'
    )


def render_phrase_piano_svg(phrase_bars: list[dict], voicings: list[Voicing],
                            key_root: str, mode: str, beats: int, unit: int) -> str:
    """Render one phrase as an inline-SVG piano arrangement."""
    if not phrase_bars or not voicings:
        return ''
    abc = build_phrase_abc(phrase_bars, voicings, key_root, mode, beats, unit)
    return render_svg(abc)


def _l2_beat_layout(beats: int, unit: int) -> tuple[int, int]:
    """Return `(beat_units, num_beats)` in sixteenth-notes for L2.

    Simple meters (x/4) treat each quarter as one beat (4 sixteenths).
    Compound meters (x/8 with `beats` divisible by 3) treat each
    dotted-quarter as one beat (6 sixteenths). Anything else falls
    back to the simple rule with `beat_units = bar_units / beats`.
    """
    bar_units = _bar_units(beats, unit)
    if unit == 4:
        return 4, beats
    if unit == 8 and beats % 3 == 0:
        return 6, beats // 3
    if unit == 2:
        return 8, beats
    # Generic fallback: split the bar evenly into `beats` beats.
    if beats > 0 and bar_units % beats == 0:
        return bar_units // beats, beats
    return bar_units, 1


def _l2_bar_bass_abc(v: Voicing, beat_units: int, num_beats: int,
                     bar_state: dict | None = None) -> str:
    """Render one bar of the L2 oom-pah-pah pattern for the bass staff.

    Beat 1: a single bass quarter-note (the voicing's B).
    Beats 2..N: an [T A] chord stack (tenor + alto) of the bar's voicing.
    Each "beat" here is `beat_units` sixteenth-notes long.
    """
    parts = [_abc_pitch(v.b.letter, v.b.accidental, v.b.octave, bar_state) +
             str(beat_units)]
    for _ in range(num_beats - 1):
        parts.append(_chord_token([v.t, v.a], beat_units, bar_state))
    return ' '.join(parts)


def build_phrase_abc_l2(phrase_bars: list[dict], voicings: list[Voicing],
                        key_root: str, mode: str, beats: int, unit: int,
                        title: str = '') -> str:
    """ABC for a single phrase using the L2 ("arpeggiated pad") layout.

    Treble: melody at original rhythm. Bass: oom-pah-pah — bass quarter
    on beat 1 then [T A] chord stacks on every subsequent beat. Same
    voicing chain as L1; only the surface rhythm of the bass differs.
    """
    bar_units = _bar_units(beats, unit)
    beat_units, num_beats = _l2_beat_layout(beats, unit)
    abc_key = key_root + ('m' if mode == 'minor' else '')
    key_acc = _key_accidentals(key_root, mode)

    soprano_lines, bass_lines = [], []
    for bar, v in zip(phrase_bars, voicings):
        soprano_lines.append(_melody_to_abc(bar, 4, dict(key_acc)) or f'z{bar_units}')
        if v is None:
            bass_lines.append(f'z{bar_units}')
        else:
            bass_lines.append(_l2_bar_bass_abc(v, beat_units, num_beats, dict(key_acc)))

    return (
        'X: 1\n'
        f'T: {title}\n'
        f'M: {beats}/{unit}\n'
        'L: 1/16\n'
        f'K: {abc_key}\n'
        '%%staves [S BL]\n'
        '%%scale 0.7\n'
        '%%staffsep 22\n'
        '%%musicspace 4\n'
        '%%maxshrink 1.0\n'
        'V: S clef=treble\n'
        'V: BL clef=bass\n'
        '[V: S] ' + (' | '.join(soprano_lines) + ' |') + '\n'
        '[V: BL] ' + (' | '.join(bass_lines) + ' |') + '\n'
    )


def render_phrase_piano_svg_l2(phrase_bars: list[dict], voicings: list[Voicing],
                               key_root: str, mode: str, beats: int, unit: int) -> str:
    """Render one phrase as an inline-SVG L2 piano arrangement."""
    if not phrase_bars or not voicings:
        return ''
    abc = build_phrase_abc_l2(phrase_bars, voicings, key_root, mode, beats, unit)
    return render_svg(abc)


# ---------------------------------------------------------------------------
# Level 3 — ornamented (decorated soprano over held pad)
# ---------------------------------------------------------------------------

_L3_LETTERS = list('CDEFGAB')


def _l3_step_index(letter: str, octave: int) -> int:
    """Absolute diatonic-step index (letters only — no accidentals).
    Two pitches A and B differ by `_l3_step_index(B) - _l3_step_index(A)`
    diatonic steps, regardless of accidentals."""
    return octave * 7 + _L3_LETTERS.index(letter)


def _l3_step_from_index(idx: int) -> tuple[str, int]:
    """Inverse of `_l3_step_index`."""
    return _L3_LETTERS[idx % 7], idx // 7


def _melody_to_abc_l3(bar: dict, sixteenths_per_beat: int,
                      bar_state: dict | None = None) -> str:
    """Decorated melody for one bar.

    Between two adjacent melody notes within the bar whose absolute diatonic
    step distance is >= 2 (a third or wider), splice a single passing tone
    on the way: halve n1's duration and emit a passing-tone of the natural
    letter one diatonic step from n1 toward n2 for the second half.

    Skips: unisons, seconds (already stepwise), rests on either side, and
    any pair where halving n1 would yield a sub-sixteenth duration (n1's
    sixteenth count must be >= 2 and even — i.e. >=2 and divisible by 2).
    """
    events = bar.get('melody') or []
    # Build a flat list of (kind, pitch_or_None, dur_q) for easier traversal.
    seq = []
    for ev in events:
        if ev.get('kind') == 'note':
            p = ev['pitch']
            seq.append(('note', p, ev.get('duration') or 0))
        elif ev.get('kind') == 'rest':
            seq.append(('rest', None, ev.get('duration') or 0))
        # else: skip unknown kinds
    parts = []
    for i, (kind, p, dur_q) in enumerate(seq):
        n = max(1, round(dur_q * sixteenths_per_beat))
        if kind == 'rest':
            parts.append(f'z{n}')
            continue
        # Look ahead for a note neighbour in the SAME bar.
        nxt = None
        if i + 1 < len(seq):
            nk, np_, _ = seq[i + 1]
            if nk == 'note':
                nxt = np_
        # Default: emit n1 at its full duration with no decoration.
        emit_decorated = False
        passing_tone = None
        if nxt is not None:
            l1, o1 = p['letter'], p['octave']
            l2, o2 = nxt['letter'], nxt['octave']
            i1 = _l3_step_index(l1, o1)
            i2 = _l3_step_index(l2, o2)
            step_dist = i2 - i1
            abs_dist = abs(step_dist)
            # >=2 means third-or-wider; require halving to land on >=1 sixteenth
            if abs_dist >= 2 and n >= 2 and (n % 2) == 0:
                direction = 1 if step_dist > 0 else -1
                pt_idx = i1 + direction
                pt_letter, pt_octave = _l3_step_from_index(pt_idx)
                passing_tone = (pt_letter, pt_octave)
                emit_decorated = True
        if emit_decorated:
            half = n // 2
            parts.append(_abc_pitch(p['letter'], _norm_acc(p.get('accidental')),
                                    p['octave'], bar_state) + str(half))
            # Passing tone: natural letter (drop accidental — diatonic by letter).
            parts.append(_abc_pitch(passing_tone[0], '', passing_tone[1],
                                    bar_state) + str(half))
        else:
            parts.append(_abc_pitch(p['letter'], _norm_acc(p.get('accidental')),
                                    p['octave'], bar_state) + str(n))
    return ' '.join(parts)


def build_phrase_abc_l3(phrase_bars: list[dict], voicings: list[Voicing],
                        key_root: str, mode: str, beats: int, unit: int,
                        title: str = '') -> str:
    """ABC for a single phrase, Level 3 — decorated soprano over held pad.

    LH (T+B) and RH alto are identical to L1; only the soprano line is
    decorated with one diatonic passing tone per qualifying gap (third or
    wider, both notes within the same bar, halving stays >= 1 sixteenth).
    """
    bar_units = _bar_units(beats, unit)
    abc_key = key_root + ('m' if mode == 'minor' else '')
    key_acc = _key_accidentals(key_root, mode)

    soprano_lines, alto_lines, tenor_lines, bass_lines = [], [], [], []
    for bar, v in zip(phrase_bars, voicings):
        soprano_lines.append(_melody_to_abc_l3(bar, 4, dict(key_acc)) or f'z{bar_units}')
        if v is None:
            alto_lines.append(f'z{bar_units}')
            tenor_lines.append(f'z{bar_units}')
            bass_lines.append(f'z{bar_units}')
        else:
            alto_lines.append(_chord_token([v.a], bar_units, dict(key_acc)))
            tenor_lines.append(_chord_token([v.t], bar_units, dict(key_acc)))
            bass_lines.append(_chord_token([v.b], bar_units, dict(key_acc)))

    return (
        'X: 1\n'
        f'T: {title}\n'
        f'M: {beats}/{unit}\n'
        'L: 1/16\n'
        f'K: {abc_key}\n'
        '%%staves [(S A) (T B)]\n'
        '%%scale 0.7\n'
        '%%staffsep 22\n'
        '%%musicspace 4\n'
        '%%maxshrink 1.0\n'
        'V: S clef=treble\n'
        'V: A clef=treble\n'
        'V: T clef=bass\n'
        'V: B clef=bass\n'
        '[V: S] ' + (' | '.join(soprano_lines) + ' |') + '\n'
        '[V: A] ' + (' | '.join(alto_lines) + ' |') + '\n'
        '[V: T] ' + (' | '.join(tenor_lines) + ' |') + '\n'
        '[V: B] ' + (' | '.join(bass_lines) + ' |') + '\n'
    )


def render_phrase_piano_svg_l3(phrase_bars: list[dict], voicings: list[Voicing],
                               key_root: str, mode: str, beats: int, unit: int) -> str:
    """Render one phrase as an L3 (ornamented) inline-SVG piano arrangement."""
    if not phrase_bars or not voicings:
        return ''
    abc = build_phrase_abc_l3(phrase_bars, voicings, key_root, mode, beats, unit)
    return render_svg(abc)


def render_svg(abc: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        in_path = td_path / 'tune.abc'
        in_path.write_text(abc)
        out_prefix = td_path / 'tune'
        result = subprocess.run(
            ['abcm2ps', '-g', '-O', str(out_prefix), str(in_path)],
            capture_output=True,
        )
        svgs = sorted(td_path.glob('tune*.svg'))
        if not svgs:
            return f'<pre>abcm2ps failed:\n{result.stderr.decode()}\n\nABC:\n{abc}</pre>'
        parts = []
        for s in svgs:
            t = s.read_text()
            t = re.sub(r'^<\?xml[^>]*\?>\s*', '', t)
            t = re.sub(r'<!DOCTYPE[^>]*>\s*', '', t)
            parts.append(t)
        return '\n'.join(parts)


