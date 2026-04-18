"""LilyPond renderer — piano scores for the 4-finger harpist.

Ported from ``legacy/tools/build_piano_score.py`` to consume the grammar-native
``Song`` objects produced by :mod:`parsers.abc`.  No imports from ``legacy.*``;
the patterns (figure decoding, pitch math, LilyPond emission, style dispatch)
are copied and adapted.

Pipeline (per hymn):

    data/hymns/<slug>.json           (parsers.abc.Song, grammar-conformant)
        +
    trefoil.pool.load_pool()         (118-fraction pool)
        │
        ▼   mapper.harp_mapper.pick_with_substitution (per bar)
    per-bar chord assignment (Bishape + LH/RH figures + RN labels)
        │
        ▼   render_piano_score(song, pool)
    LilyPond source string
        │
        ▼   compile_ly(...)
    data/scores/<slug>.{ly,pdf,svg,midi}

Style rules (Phase 1 only — no ornaments):

- ``grand_chord`` on bar 1 and the final bar — full-bar block chord with
  pedal grace.
- ``cadence_arp`` on phrase-ending bars (not last) — beat-1 block chord +
  middle eighths + final-beat quarter = current chord root.
- ``strum_pickup`` everywhere else — beat-1 block chord + middle eighths +
  final-beat quarter = upper diatonic neighbor of next chord root.

Pedal grace uses ``base_octave=1`` and clamps up to ``HARP_LOW_MIDI=31`` (G1)
— pedal always lands in Bb1–F2, below the bass staff.

Public API:
    render_piano_score(song, pool) -> str
    compile_ly(ly_path, formats=('pdf','svg','midi')) -> dict[str, Path]
    build_score(hymn_json_path, out_dir, pool, compile=True, formats=(...)) -> dict
    build_all_scores(hymns_dir, out_dir, pool, compile=True, jobs=None) -> dict
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable, Optional

from grammar.emit import emit_roman
from grammar.types import Bar, Note, Rest, Roman, Song
from mapper.harp_mapper import pick_with_substitution
from parsers.abc import hymn_slug
from trefoil.pool import Pool


# ═════════════════════════════════════════════════════════════════════════════
#   Pitch / figure math (copied from legacy, not imported)
# ═════════════════════════════════════════════════════════════════════════════

HARP_LOW_MIDI = 31  # ~G1 — pedal clamp floor

STRING_ALPHABET: dict[str, int] = {str(n): n for n in range(1, 10)}
STRING_ALPHABET.update({'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15})

MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
MINOR_STEPS = [0, 2, 3, 5, 7, 8, 10]
PITCH_CLASS = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

_ROMAN_DEG = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7,
}


def rn_to_root_degree(rn: Optional[str]) -> Optional[int]:
    """``'V7' → 5``, ``'bVII' → 7``, ``'vii°' → 7``.  Returns 1..7 or None."""
    if not rn:
        return None
    m = re.match(r'^[b#\u266d\u266f]?([ivIV]+)', rn)
    if not m:
        return None
    return _ROMAN_DEG.get(m.group(1))


def figure_to_strings(fig: str) -> list[int]:
    """Harp figure → string positions, e.g. ``'1333' → [1, 3, 5, 7]``."""
    start = STRING_ALPHABET[fig[0]]
    positions = [start]
    for ch in fig[1:]:
        positions.append(positions[-1] + int(ch) - 1)
    return positions


def parse_key_root(key_root_str: str) -> int:
    """``'Bb'/'B-' → 10``, ``'F#' → 6``, ``'G' → 7``."""
    s = key_root_str.strip() if key_root_str else ''
    if not s:
        return 0
    base = PITCH_CLASS[s[0].upper()]
    for ch in s[1:]:
        if ch == '#':
            base = (base + 1) % 12
        elif ch in ('-', 'b'):
            base = (base - 1) % 12
    return base


def string_to_midi(string_num: int, key_root: str, mode: str = 'major',
                   base_octave: int = 4) -> int:
    """Harp string N in key K → MIDI pitch."""
    steps = MAJOR_STEPS if mode == 'major' else MINOR_STEPS
    tonic_pc = parse_key_root(key_root)
    zero_based = string_num - 1
    octave_offset = zero_based // 7
    degree_idx = zero_based % 7
    semitones_above_tonic = steps[degree_idx] + 12 * octave_offset
    return 12 * (base_octave + 1) + tonic_pc + semitones_above_tonic


def diatonic_neighbor(midi: int, key_root: str, mode: str, direction: int) -> int:
    """MIDI of the diatonic note one scale-step ``+1`` or ``-1`` from ``midi``."""
    tonic_pc = parse_key_root(key_root)
    steps = MAJOR_STEPS if mode == 'major' else MINOR_STEPS
    pc_above = (midi - tonic_pc) % 12
    if pc_above not in steps:
        return midi + direction * 2
    idx = steps.index(pc_above)
    new_idx = idx + direction
    octave_shift = 0
    if new_idx < 0:
        new_idx += 7
        octave_shift = -1
    elif new_idx >= 7:
        new_idx -= 7
        octave_shift = 1
    orig_octaves = (midi - tonic_pc) // 12
    return tonic_pc + 12 * (orig_octaves + octave_shift) + steps[new_idx]


# ═════════════════════════════════════════════════════════════════════════════
#   LilyPond pitch + duration
# ═════════════════════════════════════════════════════════════════════════════

LY_LETTER_ORDER = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
LY_LETTER_NATURAL_PC = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}


def music21_key_to_ly(key_root_str: str, mode: str) -> str:
    """``'Bb' → 'bes \\major'``, ``'F#' → 'fis \\minor'``."""
    if not key_root_str:
        return 'c \\major'
    letter = key_root_str[0].lower()
    accid = ''
    for ch in key_root_str[1:]:
        if ch == '#':
            accid = 'is'
        elif ch in ('-', 'b'):
            accid = 'es'
    mode_str = '\\major' if mode == 'major' else '\\minor'
    return f'{letter}{accid} {mode_str}'


def key_pc_to_ly_spelling(key_root_str: str, mode: str) -> dict[int, str]:
    """Per-pc LilyPond spelling (courtesy-accidental-aware) for the key's scale."""
    if not key_root_str:
        return {}
    tonic_letter = key_root_str[0].lower()
    if tonic_letter not in LY_LETTER_ORDER:
        return {}
    tonic_pc = parse_key_root(key_root_str)
    steps = MAJOR_STEPS if mode == 'major' else MINOR_STEPS
    start = LY_LETTER_ORDER.index(tonic_letter)
    result: dict[int, str] = {}
    for i in range(7):
        letter = LY_LETTER_ORDER[(start + i) % 7]
        natural_pc = LY_LETTER_NATURAL_PC[letter]
        target_pc = (tonic_pc + steps[i]) % 12
        diff = (target_pc - natural_pc) % 12
        if diff == 0:
            spelling = letter
        elif diff == 1:
            spelling = letter + 'is'
        elif diff == 2:
            spelling = letter + 'isis'
        elif diff == 11:
            spelling = letter + 'es'
        elif diff == 10:
            spelling = letter + 'eses'
        else:
            spelling = letter
        result[target_pc] = spelling
    return result


_CHROMATIC_DEFAULTS = {
    0: 'c', 1: 'cis', 2: 'd', 3: 'ees', 4: 'e', 5: 'f',
    6: 'fis', 7: 'g', 8: 'aes', 9: 'a', 10: 'bes', 11: 'b',
}


def midi_to_lilypond(midi: int, pc_spelling: Optional[dict[int, str]] = None) -> str:
    """MIDI → LilyPond absolute pitch notation."""
    pc = midi % 12
    spelling = (pc_spelling or {}).get(pc) or _CHROMATIC_DEFAULTS[pc]
    letter = spelling[0]
    natural_pc = LY_LETTER_NATURAL_PC[letter]
    if 'isis' in spelling:
        accid_offset = 2
    elif 'eses' in spelling:
        accid_offset = -2
    elif 'is' in spelling:
        accid_offset = 1
    elif 'es' in spelling:
        accid_offset = -1
    else:
        accid_offset = 0
    spelled_at_nat_oct = natural_pc + 48 + accid_offset
    octave_diff = (midi - spelled_at_nat_oct) // 12
    if octave_diff > 0:
        return spelling + "'" * octave_diff
    if octave_diff < 0:
        return spelling + ',' * (-octave_diff)
    return spelling


# Quarter-length → LilyPond duration string.
_DUR_MAP = {
    0.0625: '32',  0.09375: '32.',
    0.125: '32',   0.1875: '32.',
    0.25: '16',    0.375: '16.',
    0.5: '8',      0.75: '8.',
    1.0: '4',      1.5: '4.',
    2.0: '2',      3.0: '2.',
    4.0: '1',      6.0: '1.',
    8.0: '\\breve',
}


def ql_to_lilypond_duration(ql: float) -> str:
    """Quarter-length → LilyPond duration string."""
    key = round(ql * 32) / 32
    if key in _DUR_MAP:
        return _DUR_MAP[key]
    for v, s in _DUR_MAP.items():
        if abs(ql - v) < 1e-3:
            return s
    return '4'


def midis_to_lilypond_chord(midis: list[int],
                            pc_spelling: Optional[dict[int, str]] = None) -> str:
    """``[60, 64, 67] → "<c' e' g'>"``.  Single-pitch → bare name."""
    if not midis:
        return 'r'
    if len(midis) == 1:
        return midi_to_lilypond(midis[0], pc_spelling)
    return '<' + ' '.join(midi_to_lilypond(m, pc_spelling) for m in midis) + '>'


# ═════════════════════════════════════════════════════════════════════════════
#   Chord-fraction labels (top-of-bar markup)
# ═════════════════════════════════════════════════════════════════════════════

def render_rn_markup(rn_str: str, color: str) -> str:
    """``'V7' → bold V, plain 7``.  Trailing inversion superscript.

    Accepts both legacy-concatenated forms (``V7iii`` where ``iii`` = third
    inversion) and grammar-canonical forms (``V7³``).  Either way the base
    renders bold, quality tail renders plain, inversion renders superscripted.
    """
    if not rn_str:
        return f'\\with-color {color} ""'

    # Grammar form first: trailing ¹²³ superscripts.
    inv_num = ''
    m_super = re.match(r'^(.+?)([¹²³])$', rn_str)
    if m_super:
        rn_str = m_super.group(1)
        inv_num = {'¹': '1', '²': '2', '³': '3'}[m_super.group(2)]

    m = re.match(r'^([b#]?[ivIV]+[°○ø]?)(.*)$', rn_str)
    base, tail = (m.group(1), m.group(2)) if m else (rn_str, '')
    if not inv_num:
        for suffix, digit in (('iii', '3'), ('ii', '2'), ('i', '1')):
            if tail.endswith(suffix):
                inv_num = digit
                tail = tail[:-len(suffix)]
                break
    pieces = [f'\\bold "{base}"']
    if tail:
        pieces.append(f'"{tail}"')
    if inv_num:
        pieces.append(f'\\raise #0.6 \\smaller "{inv_num}"')
    return f'\\with-color {color} \\concat {{ ' + ' '.join(pieces) + ' }'


def chord_label_markup(assignment: Optional[dict]) -> Optional[str]:
    """Assemble LilyPond \\markup body for a bar's RH/LH chord fraction."""
    if not assignment:
        return None
    lh_rom = (assignment.get('lh_rom') or assignment.get('rn') or '').strip()
    rh_rom = (assignment.get('rh_rom') or assignment.get('rn') or '').strip()
    rh_color = '#(rgb-color 0.122 0.306 0.475)'  # HymnReharmTemplate.tex blue
    lh_color = '#(rgb-color 0.482 0.169 0.169)'  # HymnReharmTemplate.tex red
    parts = [
        render_rn_markup(rh_rom, rh_color),
        render_rn_markup(lh_rom, lh_color),
    ]
    return "\\override #'(baseline-skip . 1.8) \\center-column { " + ' '.join(parts) + ' }'


# ═════════════════════════════════════════════════════════════════════════════
#   Bar-event emission
# ═════════════════════════════════════════════════════════════════════════════

def events_to_lilypond_bar(events: list[dict], full_bar_ql: float,
                            pc_spelling: Optional[dict[int, str]] = None,
                            arpeggiate: bool = False,
                            dynamic: Optional[str] = None,
                            label: Optional[str] = None) -> str:
    """One voice's events in a bar → LilyPond notation.

    ``label`` attaches ``^\\markup { ... }`` to the first note.  ``dynamic``
    attaches a dynamic marking (``\\mf``, ``\\p``, ...) to the first note.
    ``arpeggiate`` emits ``\\arpeggio`` on any multi-note chord.
    """
    events = sorted(events, key=lambda e: e['offset_ql'])
    if not events:
        return f'r{ql_to_lilypond_duration(full_bar_ql)}'

    out: list[str] = []
    dyn_applied = False
    label_applied = False
    for e in events:
        pieces: list[str] = []
        if e.get('grace_midis'):
            grace_chord = midis_to_lilypond_chord(e['grace_midis'], pc_spelling)
            pieces.append('\\acciaccatura { ' + grace_chord + '8 }')
        chord = midis_to_lilypond_chord(e['midis'], pc_spelling)
        dur = ql_to_lilypond_duration(e['duration_ql'])
        note = chord + dur
        if label and not label_applied:
            note += '^\\markup { ' + label + ' }'
            label_applied = True
        if dynamic and not dyn_applied:
            note += '\\' + dynamic
            dyn_applied = True
        if arpeggiate and len(e.get('midis', [])) > 1:
            note += '\\arpeggio'
        pieces.append(note)
        out.append(' '.join(pieces))
    return ' '.join(out)


# ═════════════════════════════════════════════════════════════════════════════
#   Per-bar style layouts (Phase 1)
# ═════════════════════════════════════════════════════════════════════════════

def _grammar_pitch_to_midi(pitch) -> int:
    """Grammar ``Pitch`` dataclass or dict → MIDI number."""
    if isinstance(pitch, dict):
        letter = pitch['letter']
        accid = pitch.get('accidental') or ''
        octave = int(pitch['octave'])
    else:
        letter = pitch.letter
        accid = pitch.accidental or ''
        octave = int(pitch.octave)
    pc = PITCH_CLASS[letter]
    if accid == '♯':
        pc = (pc + 1) % 12
    elif accid == '♭':
        pc = (pc - 1) % 12
    return 12 * (octave + 1) + pc


def _bar_melody_events(bar_melody: list, bar_duration: float) -> list[dict]:
    """Turn a grammar-bar's melody list into LilyPond-ready event dicts.

    Melody events in the grammar carry duration (in quarter-lengths) and
    ornaments, but no offset — they are consecutive in time.  We rebuild the
    offsets by cumulative duration.
    """
    events: list[dict] = []
    offset = 0.0
    for item in bar_melody:
        is_rest = (
            isinstance(item, Rest) or
            (isinstance(item, dict) and item.get('kind') == 'rest')
        )
        if is_rest:
            dur = float(item['duration']) if isinstance(item, dict) else float(item.duration)
            events.append({'offset_ql': offset, 'duration_ql': dur, 'midis': []})
            offset += dur
            continue
        # Note
        if isinstance(item, dict):
            dur = float(item['duration'])
            midi = _grammar_pitch_to_midi(item['pitch'])
        else:
            dur = float(item.duration)
            midi = _grammar_pitch_to_midi(item.pitch)
        events.append({'offset_ql': offset, 'duration_ql': dur, 'midis': [midi]})
        offset += dur
    return events


def layout_bar_grand(assignment: dict, melody_events: list[dict],
                     key_root: str, mode: str, meter_num: int, meter_den: int,
                     next_assignment: Optional[dict] = None) -> dict:
    """Full-bar block chord with pedal grace (bar 1 / last bar)."""
    lh_fig = assignment.get('lh_fig', '')
    rh_fig = assignment.get('rh_fig', '')
    rn = assignment.get('rn', '')
    bar_duration = meter_num * (4.0 / meter_den)

    grace_midis: list[int] = []
    root_degree = rn_to_root_degree(rn)
    if root_degree:
        pedal_midi = string_to_midi(root_degree, key_root, mode, base_octave=1)
        while pedal_midi < HARP_LOW_MIDI:
            pedal_midi += 12
        grace_midis = [pedal_midi]

    lh_events: list[dict] = []
    if lh_fig:
        lh_strings = figure_to_strings(lh_fig)
        lh_midis = [string_to_midi(s, key_root, mode, base_octave=2) for s in lh_strings]
        lh_events.append({
            'offset_ql': 0.0,
            'duration_ql': bar_duration,
            'midis': lh_midis,
            'grace_midis': grace_midis,
        })
    elif grace_midis:
        lh_events.append({
            'offset_ql': 0.0,
            'duration_ql': bar_duration,
            'midis': grace_midis,
        })

    rh_events: list[dict] = []
    if rh_fig:
        rh_strings = figure_to_strings(rh_fig)
        rh_midis = [string_to_midi(s, key_root, mode, base_octave=3) for s in rh_strings]
        melody_midis = {m for ev in melody_events for m in ev['midis']}
        if melody_events:
            all_mel = [m for ev in melody_events for m in ev['midis']]
            if all_mel:
                melody_top = max(all_mel)
                while rh_midis and max(rh_midis) > melody_top:
                    rh_midis = [m - 12 for m in rh_midis]
        rh_midis = [m for m in rh_midis if m not in melody_midis]
        if rh_midis:
            rh_events.append({
                'offset_ql': 0.0,
                'duration_ql': bar_duration,
                'midis': rh_midis,
            })

    return {'lh_events': lh_events, 'rh_events': rh_events,
            'melody_events': melody_events}


def _chord_then_motion(base_lh_events: list[dict], bar_duration: float,
                        tail_midi: int) -> list[dict]:
    """Beat-1 block chord + middle eighth arpeggio + final-beat quarter tail."""
    new_lh: list[dict] = []
    for ev in base_lh_events:
        midis = ev['midis']
        grace = ev.get('grace_midis')
        if len(midis) <= 1:
            new_lh.append(ev)
            continue

        new_lh.append({
            'offset_ql': 0.0,
            'duration_ql': 1.0,
            'midis': midis,
            'grace_midis': grace,
        })

        mid_start = 1.0
        mid_end = bar_duration - 1.0
        num_eighths = max(0, int(round((mid_end - mid_start) / 0.5)))
        arp_pool = midis[1:] if len(midis) > 1 else midis
        for i in range(num_eighths):
            new_lh.append({
                'offset_ql': mid_start + i * 0.5,
                'duration_ql': 0.5,
                'midis': [arp_pool[i % len(arp_pool)]],
            })

        if mid_end < bar_duration - 1e-6:
            new_lh.append({
                'offset_ql': mid_end,
                'duration_ql': 1.0,
                'midis': [tail_midi],
            })
    return new_lh


def layout_bar_strum_pickup(assignment: dict, melody_events: list[dict],
                            key_root: str, mode: str,
                            meter_num: int, meter_den: int,
                            next_assignment: Optional[dict] = None) -> dict:
    """Strum + eighth arpeggio + upper-neighbor pickup to the next chord root."""
    base = layout_bar_grand(assignment, melody_events, key_root, mode,
                            meter_num, meter_den)
    if next_assignment is None:
        return base
    next_root = rn_to_root_degree(next_assignment.get('rn', ''))
    if not next_root:
        return base

    bar_duration = meter_num * (4.0 / meter_den)
    if bar_duration < 2.0 + 1e-6:
        return base

    ref = base['lh_events'][0]['midis'][0] if base['lh_events'] else HARP_LOW_MIDI + 12
    target = string_to_midi(next_root, key_root, mode, base_octave=2)
    while target < ref - 7:
        target += 12
    pickup_midi = diatonic_neighbor(target, key_root, mode, +1)

    base['lh_events'] = _chord_then_motion(base['lh_events'], bar_duration,
                                           pickup_midi)
    return base


def layout_bar_cadence_arp(assignment: dict, melody_events: list[dict],
                            key_root: str, mode: str,
                            meter_num: int, meter_den: int,
                            next_assignment: Optional[dict] = None) -> dict:
    """Strum + eighth arpeggio + landing on the current chord root (bottom of LH)."""
    base = layout_bar_grand(assignment, melody_events, key_root, mode,
                            meter_num, meter_den)
    bar_duration = meter_num * (4.0 / meter_den)
    if bar_duration < 2.0 + 1e-6:
        return base
    if not base['lh_events']:
        return base
    landing = base['lh_events'][0]['midis'][0]
    base['lh_events'] = _chord_then_motion(base['lh_events'], bar_duration,
                                           landing)
    return base


_STYLE_LAYOUTS = {
    'grand_chord': layout_bar_grand,
    'strum_pickup': layout_bar_strum_pickup,
    'cadence_arp': layout_bar_cadence_arp,
}


def pick_style(bar_num: int, phrase_end_bars: set[int], is_last_bar: bool) -> str:
    """Return the style name for bar ``bar_num`` (1-based).

    - bar 1 / last bar                     → ``grand_chord``
    - phrase-ending bar (not last)         → ``cadence_arp``
    - everything else                      → ``strum_pickup``
    """
    if is_last_bar or bar_num == 1:
        return 'grand_chord'
    if bar_num in phrase_end_bars:
        return 'cadence_arp'
    return 'strum_pickup'


# ═════════════════════════════════════════════════════════════════════════════
#   Chord assignment computation (mapper.harp_mapper on the fly)
# ═════════════════════════════════════════════════════════════════════════════

def _first_melody_pitch_str(bar: Bar) -> Optional[str]:
    """Return the first melody note's music21-style string (``'G4'``) or None."""
    for item in bar.melody:
        if isinstance(item, Note):
            letter = item.pitch.letter
            accid = item.pitch.accidental
            oct_ = item.pitch.octave
            tail = ''
            if accid == '♯':
                tail = '#'
            elif accid == '♭':
                tail = '-'
            return f'{letter}{tail}{oct_}'
    return None


def _rn_string(r: Roman) -> str:
    """Grammar ``Roman`` → canonical string form.  ``vii○`` stays as ``vii○``.

    Note: the pool uses ``vii°`` (U+00B0) while grammar uses ``vii○`` (U+25CB).
    The mapper accepts both glyphs, so we pass through whatever emit_roman
    produces without further normalization.
    """
    return emit_roman(r)


def assign_bars(song: Song, pool: Pool) -> list[Optional[dict]]:
    """Walk ``song.bars`` and compute a per-bar assignment dict via the mapper.

    Each assignment dict carries the legacy-compatible keys the layout
    functions expect: ``rn``, ``lh_fig``, ``rh_fig``, ``lh_rom``, ``rh_rom``,
    ``ipool``, plus the substitution bookkeeping (``harmonic_substitution``,
    ``requested_rn``).  Returns a list the same length as ``song.bars``.
    """
    key_root = song.key.root
    mode = song.key.mode
    bars = song.bars
    n = len(bars)

    # Phrase endings (for cadence tag surfacing).
    phrase_final_bars: set[int] = set()
    last_bar_num = n
    for ph in song.phrases:
        if ph.ibars:
            phrase_final_bars.add(ph.ibars[-1])

    assignments: list[Optional[dict]] = []
    for i, bar in enumerate(bars):
        ibar = i + 1
        rn_str = _rn_string(bar.chord)
        melody = _first_melody_pitch_str(bar)
        prev_rn = _rn_string(bars[i - 1].chord) if i > 0 else None
        next_rn = _rn_string(bars[i + 1].chord) if i + 1 < n else None
        is_final = (ibar == last_bar_num) and (ibar in phrase_final_bars)
        v_dur = None
        try:
            v_dur = sum(
                float(item.duration) for item in bar.melody
            ) or None
        except Exception:
            pass

        picks = pick_with_substitution(
            pool, rn_str, key_root,
            next_rn=next_rn,
            prev_rn=prev_rn,
            melody=melody,
            mode=mode,
            is_final_cadence=is_final,
            v_duration_beats=v_dur,
            top_n=1,
        )
        if not picks:
            assignments.append(None)
            continue
        pick = picks[0]
        entry = pool.get(pick.ipool)
        assignments.append({
            'rn': rn_str,
            'lh_rom': _rn_string(pick.lh_chord),
            'rh_rom': _rn_string(pick.rh_chord),
            'lh_fig': entry.lh_figure,
            'rh_fig': entry.rh_figure,
            'ipool': pick.ipool,
            'harmonic_substitution': pick.harmonic_substitution,
            'requested_rn': pick.requested_rn,
        })
    return assignments


# ═════════════════════════════════════════════════════════════════════════════
#   LilyPond assembly
# ═════════════════════════════════════════════════════════════════════════════

_LY_TEMPLATE = r"""\version "2.22.1"

\header {
  title = "__TITLE__"
  subtitle = "__SUBTITLE__"
  tagline = ##f
}

global = {
  \key __KEYSIG__
  \time __METER__
}

upper = {
  \global
  <<
    { \voiceOne __MELODY__ }
    { \voiceTwo __RHFILL__ }
  >>
}

lower = {
  \clef bass
  \global
  __LH__
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=__BPM__ }
}
"""


def _escape_ly_string(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', r'\"')


def render_piano_score(song: Song, pool: Pool) -> str:
    """Build and return the LilyPond source for the piano score.  Pure function."""
    key_root = song.key.root
    mode = song.key.mode
    meter_num = int(song.meter.beats)
    meter_den = int(song.meter.unit)
    bpm = int(song.tempo.value or 90)
    title = song.title or 'Untitled'

    assignments = assign_bars(song, pool)

    # Phrase-end bars (cadence_arp) — last bar excluded (→ grand_chord instead).
    phrase_end_bars: set[int] = set()
    n = len(song.bars)
    for ph in song.phrases:
        if ph.ibars:
            phrase_end_bars.add(ph.ibars[-1])

    bar_duration = meter_num * (4.0 / meter_den)

    layouts: list[dict] = []
    for i, bar in enumerate(song.bars):
        ibar = i + 1
        is_last = (ibar == n)
        melody_events = _bar_melody_events(list(bar.melody), bar_duration)
        assignment = assignments[i]
        next_assignment = assignments[i + 1] if i + 1 < n else None

        if assignment is None:
            layouts.append({
                'lh_events': [],
                'rh_events': [],
                'melody_events': melody_events,
                'label_markup': None,
            })
            continue

        style = pick_style(ibar, phrase_end_bars, is_last_bar=is_last)
        layout_fn = _STYLE_LAYOUTS.get(style, layout_bar_grand)
        bar_data = layout_fn(assignment, melody_events, key_root, mode,
                             meter_num, meter_den,
                             next_assignment=next_assignment)
        bar_data['label_markup'] = chord_label_markup(assignment)
        bar_data['style'] = style
        layouts.append(bar_data)

    # Emit.
    keysig = music21_key_to_ly(key_root, mode)
    pc_spelling = key_pc_to_ly_spelling(key_root, mode)

    def voice_line(events_key: str, arpeggiate: bool, dynamic: Optional[str],
                   with_labels: bool = False) -> str:
        parts: list[str] = []
        for i, bar_d in enumerate(layouts):
            dyn = dynamic if i == 0 else None
            label = bar_d.get('label_markup') if with_labels else None
            parts.append(events_to_lilypond_bar(
                bar_d.get(events_key, []), bar_duration,
                pc_spelling, arpeggiate=arpeggiate, dynamic=dyn, label=label))
        return ' | '.join(parts) + ' |'

    melody_line = voice_line('melody_events', arpeggiate=False, dynamic='mf',
                             with_labels=True)
    rh_line = voice_line('rh_events', arpeggiate=True, dynamic='p')
    lh_line = voice_line('lh_events', arpeggiate=True, dynamic='p')

    subtitle = f'\u2669 = {bpm}'

    ly = _LY_TEMPLATE
    ly = ly.replace('__TITLE__', _escape_ly_string(title))
    ly = ly.replace('__SUBTITLE__', _escape_ly_string(subtitle))
    ly = ly.replace('__KEYSIG__', keysig)
    ly = ly.replace('__METER__', f'{meter_num}/{meter_den}')
    ly = ly.replace('__BPM__', str(bpm))
    ly = ly.replace('__MELODY__', melody_line)
    ly = ly.replace('__RHFILL__', rh_line)
    ly = ly.replace('__LH__', lh_line)
    return ly


# ═════════════════════════════════════════════════════════════════════════════
#   LilyPond invocation
# ═════════════════════════════════════════════════════════════════════════════

def compile_ly(ly_path: Path, *,
               formats: Iterable[str] = ('pdf', 'svg', 'midi')) -> dict[str, Path]:
    """Shell out to ``lilypond``; return the produced artifact paths.

    LilyPond writes output files next to the ``.ly`` source using its basename.
    If both ``pdf`` and ``svg`` are requested we must invoke LilyPond twice
    (the ``-dbackend=svg`` flag replaces PDF output).

    Missing artifacts (LilyPond silently skipped them, or the compile failed)
    are simply absent from the returned dict.
    """
    ly_path = Path(ly_path)
    ly_dir = ly_path.parent if ly_path.parent != Path('') else Path('.')
    ly_base = ly_path.stem
    formats = tuple(formats)

    if not shutil.which('lilypond'):
        raise RuntimeError('lilypond executable not found in PATH')

    want_pdf = 'pdf' in formats or 'midi' in formats
    want_svg = 'svg' in formats

    # Pass 1: default backend (PDF + MIDI).
    if want_pdf:
        cmd = [
            'lilypond', '-dno-point-and-click', '-o', ly_base, ly_path.name,
        ]
        _run_ly(cmd, cwd=ly_dir)

    # Pass 2: SVG backend.  Separate call — the backend flag swaps PDF out.
    if want_svg:
        cmd = [
            'lilypond', '-dno-point-and-click', '-dbackend=svg',
            '-o', ly_base, ly_path.name,
        ]
        _run_ly(cmd, cwd=ly_dir)

    out: dict[str, Path] = {'ly': ly_path}
    for ext in ('pdf', 'svg', 'midi'):
        if ext not in formats:
            continue
        candidates = [ly_dir / f'{ly_base}.{ext}']
        # LilyPond may also produce multi-page SVGs as <base>-page1.svg etc.
        if ext == 'svg':
            candidates += sorted(ly_dir.glob(f'{ly_base}-page*.svg'))
        # MIDI sometimes lands at <base>.mid (older LilyPond).
        if ext == 'midi':
            candidates.append(ly_dir / f'{ly_base}.mid')
        for cand in candidates:
            if cand.exists():
                out[ext] = cand
                break
    return out


def _run_ly(cmd: list[str], cwd: Path) -> None:
    """Run a LilyPond command and raise on failure with a short diagnostic."""
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        tail = '\n'.join((result.stderr or result.stdout).splitlines()[-6:])
        raise RuntimeError(
            f'lilypond {cmd[-1]!r} failed (rc={result.returncode}):\n{tail}'
        )


# ═════════════════════════════════════════════════════════════════════════════
#   Hymn-JSON → Song loader
# ═════════════════════════════════════════════════════════════════════════════

def _song_from_hymn_json(data: dict) -> Song:
    """Rebuild a ``Song`` from a ``data/hymns/<slug>.json`` record.

    Produces the minimum ``Song`` fields the renderer needs: title, key, meter,
    tempo, bars (with melody events + chord Roman), phrases.  Verses, pedals,
    form, and ornaments are preserved as-is but not used by Phase 1.
    """
    from grammar.types import Key, Meter, Note as GNote, Pitch, Rest as GRest, Tempo

    title = data.get('title', 'Untitled')
    k = data.get('key', {})
    key = Key(root=k.get('root', 'C'), mode=k.get('mode', 'major'))  # type: ignore[arg-type]
    m = data.get('meter', {})
    meter = Meter(beats=int(m.get('beats', 4)),
                  unit=int(m.get('unit', 4)))  # type: ignore[arg-type]
    t = data.get('tempo', {})
    tempo = Tempo(value=int(t.get('value', 90)),
                  unit=int(t.get('unit', 4)))  # type: ignore[arg-type]

    bars: list[Bar] = []
    for b in data.get('bars', []):
        mel: list = []
        for ev in b.get('melody', []):
            if ev.get('kind') == 'rest':
                mel.append(GRest(duration=float(ev['duration'])))
            else:
                p = ev['pitch']
                pitch = Pitch(letter=p['letter'], accidental=p.get('accidental'),
                              octave=int(p['octave']))  # type: ignore[arg-type]
                mel.append(GNote(pitch=pitch, duration=float(ev['duration'])))
        chord_d = b.get('chord', {'numeral': 'I', 'quality': None, 'inversion': None})
        chord = Roman(numeral=chord_d.get('numeral', 'I'),
                      quality=chord_d.get('quality'),
                      inversion=chord_d.get('inversion'))
        bars.append(Bar(
            melody=tuple(mel),
            chord=chord,
            voicing=None,
            technique=b.get('technique'),
        ))

    from grammar.types import Phrase
    phrases = tuple(
        Phrase(ibars=tuple(p.get('ibars', [])), path=p.get('path'))
        for p in data.get('phrases', [])
    )

    return Song(
        title=title,
        key=key,
        meter=meter,
        tempo=tempo,
        bars=tuple(bars),
        phrases=phrases,
        verses=(),
    )


def load_song(hymn_json_path: Path) -> Song:
    """Load a ``data/hymns/<slug>.json`` record as a ``Song``."""
    with Path(hymn_json_path).open('r', encoding='utf-8') as f:
        data = json.load(f)
    return _song_from_hymn_json(data)


# ═════════════════════════════════════════════════════════════════════════════
#   High-level build_score / build_all_scores
# ═════════════════════════════════════════════════════════════════════════════

def build_score(hymn_json_path: Path, out_dir: Path, pool: Pool,
                 *, compile: bool = True,
                 formats: Iterable[str] = ('pdf', 'svg', 'midi')) -> dict[str, Any]:
    """End-to-end build for one hymn.  Returns a dict of artifact paths.

    With ``compile=False`` only the ``.ly`` is written (handy for tests on
    machines without LilyPond).
    """
    hymn_json_path = Path(hymn_json_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    song = load_song(hymn_json_path)
    slug = hymn_slug(song.title) or hymn_json_path.stem
    ly_src = render_piano_score(song, pool)
    ly_path = out_dir / f'{slug}.ly'
    ly_path.write_text(ly_src, encoding='utf-8')

    artifacts: dict[str, Any] = {'ly': ly_path, 'slug': slug, 'title': song.title}
    if compile:
        produced = compile_ly(ly_path, formats=formats)
        artifacts.update(produced)
    return artifacts


def build_all_scores(hymns_dir: Path, out_dir: Path, pool: Pool,
                     *, compile: bool = True,
                     formats: Iterable[str] = ('pdf', 'svg', 'midi'),
                     jobs: Optional[int] = None) -> dict[str, Any]:
    """Batch-build every hymn in ``hymns_dir``.  Returns a report dict.

    The report contains a ``results`` list (one entry per hymn) and tally
    counts ``ok`` and ``fail``.  Successful entries have ``artifacts`` keyed
    by format; failed entries have ``error`` with the exception string.

    Parallelism: LilyPond is CPU-bound and each invocation is fully
    independent, so we dispatch to a ``ProcessPoolExecutor``.  Pass
    ``jobs=1`` for in-process sequential (useful in tests).
    """
    hymns_dir = Path(hymns_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    hymn_paths = sorted(hymns_dir.glob('*.json'))
    if not hymn_paths:
        return {'results': [], 'ok': 0, 'fail': 0}

    if jobs is None:
        jobs = max(1, (os.cpu_count() or 1))

    results: list[dict[str, Any]] = []

    if jobs == 1 or not compile:
        for hp in hymn_paths:
            results.append(_safe_build_one(hp, out_dir, pool, compile, formats))
    else:
        # ProcessPool — reload the pool in each worker from its canonical path
        # to avoid pickling grammar dataclasses across processes.
        pool_path = _guess_pool_path_from_pool(pool)
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            futures = {
                ex.submit(_worker_build_one, str(hp), str(out_dir),
                          pool_path, compile, tuple(formats)): hp
                for hp in hymn_paths
            }
            for fut in as_completed(futures):
                results.append(fut.result())

    results.sort(key=lambda r: r.get('slug') or r.get('source_path', ''))
    ok = sum(1 for r in results if not r.get('error'))
    fail = len(results) - ok
    return {'results': results, 'ok': ok, 'fail': fail}


def _safe_build_one(hymn_json_path: Path, out_dir: Path, pool: Pool,
                     compile: bool, formats: Iterable[str]) -> dict[str, Any]:
    try:
        art = build_score(hymn_json_path, out_dir, pool,
                          compile=compile, formats=formats)
        return {
            'slug': art['slug'],
            'title': art['title'],
            'source_path': str(hymn_json_path),
            'artifacts': {k: str(v) for k, v in art.items()
                           if isinstance(v, Path)},
        }
    except Exception as e:
        return {
            'slug': Path(hymn_json_path).stem,
            'title': None,
            'source_path': str(hymn_json_path),
            'error': f'{type(e).__name__}: {e}',
        }


def _worker_build_one(hymn_json_path: str, out_dir: str, pool_path: Optional[str],
                       compile: bool, formats: tuple[str, ...]) -> dict[str, Any]:
    """Sub-process entry: re-import, re-load the pool, and delegate."""
    from trefoil.pool import load_pool
    pool = load_pool(pool_path) if pool_path else load_pool()
    return _safe_build_one(Path(hymn_json_path), Path(out_dir), pool,
                           compile, formats)


def _guess_pool_path_from_pool(pool: Pool) -> Optional[str]:
    """Best-effort: if the pool was loaded from the default, return that
    path so sub-processes can reload it cheaply; else None (workers will
    fall back to ``load_pool()`` with its own default)."""
    from trefoil.pool import DEFAULT_POOL_PATH
    return str(DEFAULT_POOL_PATH) if DEFAULT_POOL_PATH.exists() else None


__all__ = [
    'HARP_LOW_MIDI',
    'render_piano_score',
    'compile_ly',
    'build_score',
    'build_all_scores',
    'load_song',
    'assign_bars',
    'pick_style',
    'chord_label_markup',
    'events_to_lilypond_bar',
    'midi_to_lilypond',
    'string_to_midi',
    'rn_to_root_degree',
    'diatonic_neighbor',
    # Layout functions exposed for tests / inspection.
    'layout_bar_grand',
    'layout_bar_strum_pickup',
    'layout_bar_cadence_arp',
]
