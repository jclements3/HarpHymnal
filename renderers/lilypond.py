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
from mapper.harp_mapper import pick_with_substitution, pick_with_techniques
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


def _is_dominant_rn(rn: Optional[str]) -> bool:
    """``True`` if ``rn`` is built on the V degree (``'V'``, ``'V7'``, ``'V¹'``, …).

    Used by the approach-pickup gate: we never pile ``V`` on top of ``V``.
    """
    if not rn:
        return False
    m = re.match(r'^[b#\u266d\u266f]?([ivIV]+)', rn)
    if not m:
        return False
    return m.group(1) == 'V'


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


_SORTED_DURS_DESC = sorted(_DUR_MAP.keys(), reverse=True)


def ql_to_lilypond_durations(ql: float) -> list[str]:
    """Decompose a quarter-length into one or more standard LilyPond durations
    meant to be tied together.  A 9/8 bar (``ql=4.5``) has no single-token
    representation, so it splits as ``['1', '8']`` (whole tied to eighth).
    Standard durations (1.0, 3.0, 4.0, ...) return a single-element list.
    """
    out: list[str] = []
    remaining = round(ql * 32) / 32
    while remaining > 1e-6:
        picked = None
        for s in _SORTED_DURS_DESC:
            if s <= remaining + 1e-6:
                picked = s
                break
        if picked is None:
            out.append('4')
            remaining = 0.0
            break
        out.append(_DUR_MAP[picked])
        remaining -= picked
    return out or ['4']


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
        rest_pieces = [f'r{d}' for d in ql_to_lilypond_durations(full_bar_ql)]
        return ' '.join(rest_pieces)

    out: list[str] = []
    dyn_applied = False
    label_applied = False
    for e in events:
        pieces: list[str] = []
        if e.get('grace_midis'):
            grace_chord = midis_to_lilypond_chord(e['grace_midis'], pc_spelling)
            pieces.append('\\acciaccatura { ' + grace_chord + '8 }')
        is_rest = not e.get('midis')
        chord = 'r' if is_rest else midis_to_lilypond_chord(e['midis'], pc_spelling)
        durs = ql_to_lilypond_durations(e['duration_ql'])
        for i, d in enumerate(durs):
            seg = chord + d
            if i == 0:
                if label and not label_applied:
                    seg += '^\\markup { ' + label + ' }'
                    label_applied = True
                if dynamic and not dyn_applied:
                    seg += '\\' + dynamic
                    dyn_applied = True
                if arpeggiate and len(e.get('midis', [])) > 1:
                    seg += '\\arpeggio'
            if not is_rest and i < len(durs) - 1:
                seg += '~'
            pieces.append(seg)
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
        # Hard gap rule (grammar/constants.py MIN_GAP=0): RH bottom must sit
        # strictly above LH top, else the hands collide on the same harp string.
        # Playability trumps the "RH below melody" style preference — if the
        # octave drop above put RH into LH territory, walk it back up.
        if rh_midis and lh_events and lh_events[0].get('midis'):
            lh_top = max(lh_events[0]['midis'])
            while rh_midis and min(rh_midis) <= lh_top:
                rh_midis = [m + 12 for m in rh_midis]
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
    """Beat-1 block chord + middle eighth arpeggio + final-beat quarter tail.

    The tail is a single pitch (``tail_midi``).  Approach-pickup uses the
    plural variant :func:`_chord_then_chord_motion` to emit a block chord tail.
    """
    return _chord_then_chord_motion(base_lh_events, bar_duration, [tail_midi])


def _chord_then_chord_motion(base_lh_events: list[dict], bar_duration: float,
                              tail_midis: list[int]) -> list[dict]:
    """Beat-1 block chord + middle eighth arpeggio + final-beat chord tail.

    Identical to :func:`_chord_then_motion` except the final-beat tail is a
    chord (``tail_midis`` may be one or more MIDI pitches).  Used by the
    approach-pickup layout to stamp V-of-key as a block chord on the last beat.
    """
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
                'midis': list(tail_midis),
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


# ─────────────────────────────────────────────────────────────────────────────
#   Approach decoration (Task #11 — techniques/approach.py::dominant_approach)
# ─────────────────────────────────────────────────────────────────────────────

def _approach_pickup_fig(key_root: str, mode: str, pool: 'Pool',
                         next_rn: Optional[str] = None) -> Optional[str]:
    """Resolve the LH figure for a diatonic V-of-the-key pickup.

    Wires :func:`mapper.harp_mapper.pick_fraction` against the global ``V`` —
    the pool is strictly diatonic, so every "V of target" collapses to plain
    ``V`` when the secondary dominant isn't in the scale.  ``next_rn`` is
    accepted for future elaboration (e.g. pulling melody context) but is not
    yet consulted.  Returns the ``lh_figure`` string (e.g. ``'533'``) or None
    if the pool has no scoring match — effectively never for a diatonic pool.
    """
    from mapper.harp_mapper import pick_fraction
    picks = pick_fraction(pool, 'V', key_root, mode=mode, top_n=1)
    if not picks:
        return None
    entry = pool.get(picks[0].ipool)
    return entry.lh_figure


def _approach_pickup_midis(key_root: str, mode: str, pool: 'Pool',
                            *, ref_midi: int,
                            next_rn: Optional[str] = None) -> list[int]:
    """MIDI pitches for a V-of-key block chord sitting just below ``ref_midi``.

    ``ref_midi`` is the anchor (typically the bar's bass note) the pickup
    should live near — we octave-shift the resolved figure so its bass is not
    more than a fifth below the anchor and the top note is not above it.
    Returns ``[]`` if the figure could not be resolved.
    """
    fig = _approach_pickup_fig(key_root, mode, pool, next_rn=next_rn)
    if not fig:
        return []
    strings = figure_to_strings(fig)
    midis = [string_to_midi(s, key_root, mode, base_octave=2) for s in strings]
    # Keep the pickup chord close to the bar's anchor bass note — walk octaves
    # until the lowest tone sits within a fifth below the anchor.
    if midis:
        while max(midis) < ref_midi - 7:
            midis = [m + 12 for m in midis]
        while min(midis) > ref_midi + 5:
            midis = [m - 12 for m in midis]
        # Clamp to the harp's low register just like the pedal grace does.
        while min(midis) < HARP_LOW_MIDI:
            midis = [m + 12 for m in midis]
    return midis


def layout_bar_approach_pickup(assignment: dict, melody_events: list[dict],
                                key_root: str, mode: str,
                                meter_num: int, meter_den: int,
                                next_assignment: Optional[dict] = None,
                                pool: Optional['Pool'] = None) -> dict:
    """Strum + eighth arpeggio + V-of-key block chord on the last beat.

    This is the Phase-1 realization of ``techniques/approach.py``'s
    ``dominant_approach``: the final beat of a phrase-interior pre-cadence
    bar is replaced with a V-of-the-key block chord, setting up the cadence
    bar that follows.  If ``pool`` is not supplied the layout degrades
    gracefully to ``layout_bar_strum_pickup`` (single upper-neighbor pickup),
    so this function is still safe to call without a pool in hand.
    """
    base = layout_bar_grand(assignment, melody_events, key_root, mode,
                            meter_num, meter_den)
    bar_duration = meter_num * (4.0 / meter_den)
    if bar_duration < 2.0 + 1e-6 or not base['lh_events']:
        return base
    if pool is None:
        return layout_bar_strum_pickup(assignment, melody_events, key_root,
                                       mode, meter_num, meter_den,
                                       next_assignment=next_assignment)

    ref = base['lh_events'][0]['midis'][0]
    next_rn = (next_assignment or {}).get('rn')
    tail_midis = _approach_pickup_midis(key_root, mode, pool,
                                        ref_midi=ref, next_rn=next_rn)
    if not tail_midis:
        return layout_bar_strum_pickup(assignment, melody_events, key_root,
                                       mode, meter_num, meter_den,
                                       next_assignment=next_assignment)

    base['lh_events'] = _chord_then_chord_motion(base['lh_events'],
                                                  bar_duration, tail_midis)
    return base


def _should_use_approach_pickup(ibar: int, assignment: Optional[dict],
                                 next_assignment: Optional[dict],
                                 phrase_end_bars: set[int],
                                 is_last_bar: bool) -> bool:
    """Gate the Dominant-approach pickup for bar ``ibar`` (1-based).

    Fires on a phrase-interior bar ``n`` when:

    - ``n`` is not bar 1 and is not itself the last bar;
    - ``n+1`` is a phrase-ending bar (so ``n`` is the pre-cadence bar);
    - ``n`` is not itself a phrase-ending bar (interior only);
    - the current chord is not already a dominant (avoid V→V→I redundancy);
    - the mapper did not pick a substitution (never pile techniques).
    """
    if assignment is None or next_assignment is None:
        return False
    if ibar == 1 or is_last_bar:
        return False
    if ibar in phrase_end_bars:
        return False
    if (ibar + 1) not in phrase_end_bars:
        return False
    if _is_dominant_rn(assignment.get('rn')):
        return False
    if assignment.get('harmonic_substitution'):
        return False
    return True


_STYLE_LAYOUTS = {
    'grand_chord': layout_bar_grand,
    'strum_pickup': layout_bar_strum_pickup,
    'cadence_arp': layout_bar_cadence_arp,
    'approach_pickup': layout_bar_approach_pickup,
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


def assign_bars(song: Song, pool: Pool, *,
                use_techniques: bool = True) -> list[Optional[dict]]:
    """Walk ``song.bars`` and compute a per-bar assignment dict via the mapper.

    Each assignment dict carries the legacy-compatible keys the layout
    functions expect: ``rn``, ``lh_fig``, ``rh_fig``, ``lh_rom``, ``rh_rom``,
    ``ipool``, plus the substitution bookkeeping (``harmonic_substitution``,
    ``requested_rn``, ``technique``).  Returns a list the same length as
    ``song.bars``.

    When ``use_techniques`` is True (default), the technique-aware picker is
    used so Third sub / Deceptive sub / Common-tone pivot can replace the
    input RN where musically warranted. Set to False to match the legacy
    pre-technique output for diffing.
    """
    key_root = song.key.root
    mode = song.key.mode
    bars = song.bars
    n = len(bars)

    # Phrase endings (for cadence tag surfacing + deceptive-sub gating).
    phrase_final_bars: set[int] = set()
    last_bar_num = n
    for ph in song.phrases:
        if ph.ibars:
            phrase_final_bars.add(ph.ibars[-1])

    assignments: list[Optional[dict]] = []
    prev_pick = None
    for i, bar in enumerate(bars):
        ibar = i + 1
        rn_str = _rn_string(bar.chord)
        melody = _first_melody_pitch_str(bar)
        prev_rn = _rn_string(bars[i - 1].chord) if i > 0 else None
        next_rn = _rn_string(bars[i + 1].chord) if i + 1 < n else None
        is_final = (ibar == last_bar_num) and (ibar in phrase_final_bars)
        is_phrase_end = ibar in phrase_final_bars
        v_dur = None
        try:
            v_dur = sum(
                float(item.duration) for item in bar.melody
            ) or None
        except Exception:
            pass

        if use_techniques:
            picks = pick_with_techniques(
                pool, rn_str, key_root,
                next_rn=next_rn,
                prev_rn=prev_rn,
                melody=melody,
                mode=mode,
                is_final_cadence=is_final,
                v_duration_beats=v_dur,
                is_phrase_end=is_phrase_end,
                prev_pick=prev_pick,
            )
        else:
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
            prev_pick = None
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
            'technique': getattr(pick, 'technique', None),
        })
        prev_pick = pick
    return assignments


# ═════════════════════════════════════════════════════════════════════════════
#   Voicing hints (Task #12 — techniques/voicing.py as renderer-level tweaks)
# ═════════════════════════════════════════════════════════════════════════════
#
# The mapper has already picked a pool Bishape (LH fig + RH fig) per bar.  The
# voicing module in ``techniques/voicing.py`` defines 6 pure-function operators
# that return a modified Bar with a new ``voicing`` Bishape — but here in the
# renderer we apply them as lightweight *hints* that reshape the concrete
# figures without changing the RN label.  Scope for Phase 1:
#
#   - ``inversion=1``    on the 2nd occurrence of a repeated phrase-final RN
#                        (e.g. bar 8 of a 16-bar hymn whose bar 4 has the same
#                        chord) — rotates the LH figure so the 3rd is in the
#                        bass, giving the player contrast on the reprise.
#   - ``density=extend`` on phrase-final bars with ``bar_duration >= 3`` beats
#                        AND sparse melody (<= 2 events) — appends a 3-interval
#                        to the RH figure, producing a 7th/9th colour tone.
#   - ``pedal=1``        on the first bar of phrases >= 6 bars long — injects a
#                        low tonic as a grace / stacked bass under the normal
#                        LH, creating a grounding anchor.
#
# Voice-leading / stacking / open-closed spread are deferred.

def _rotate_figure_inv1(fig: str) -> str:
    """Rotate a figure one step left: root moves out, 3rd becomes new bass.
    ``'133' -> '333'``, ``'1332' -> '3323'``, ``'124' -> '242'``.  Returns
    the input unchanged on short or unparsable figures.
    """
    if not fig or len(fig) < 2:
        return fig
    try:
        start = STRING_ALPHABET[fig[0]]
        positions = [start]
        for ch in fig[1:]:
            positions.append(positions[-1] + int(ch) - 1)
    except (KeyError, ValueError):
        return fig
    # Original intervals-between-adjacent: keep list stable.
    intervals = [positions[i + 1] - positions[i] + 1
                 for i in range(len(positions) - 1)]
    new_top = positions[-1] + intervals[0] - 1
    new_positions = positions[1:] + [new_top]
    _INV = {v: k for k, v in STRING_ALPHABET.items()}
    head = _INV.get(new_positions[0])
    if head is None:  # overflow past string F (=15)
        return fig
    tail_chars: list[str] = []
    for a, b in zip(new_positions, new_positions[1:]):
        d = b - a + 1
        if d < 1 or d > 9:
            return fig
        tail_chars.append(str(d))
    return head + ''.join(tail_chars)


def _extend_figure_9th(fig: str) -> str:
    """Append a 3-interval to stack an extra diatonic third on top.
    ``'933' -> '9333'``.  If appending would overflow string F, re-anchor
    one octave lower so the extension still fits.
    """
    if not fig:
        return fig
    try:
        start = STRING_ALPHABET[fig[0]]
        positions = [start]
        for ch in fig[1:]:
            positions.append(positions[-1] + int(ch) - 1)
    except (KeyError, ValueError):
        return fig
    new_top = positions[-1] + 2  # +3-1 = +2 (stack-a-third)
    if new_top <= 15:
        return fig + '3'
    # Overflow — drop the whole voicing an octave (7 strings) and retry.
    shifted = [p - 7 for p in positions]
    if shifted[0] < 1 or shifted[-1] + 2 > 15:
        return fig  # still can't fit; give up
    _INV = {v: k for k, v in STRING_ALPHABET.items()}
    head = _INV.get(shifted[0])
    if head is None:
        return fig
    rest = [str(b - a + 1) for a, b in zip(shifted, shifted[1:])]
    return head + ''.join(rest) + '3'


def _voicing_plan(song: Song,
                  assignments: list[Optional[dict]]) -> dict[int, str]:
    """Build the ibar -> voicing-hint-name map per the Task #12 policy.

    Returns a dict keyed by 1-based ibar; values are hint strings such as
    ``'inversion=1'``, ``'density=extend'``, ``'pedal=1'``.  At most one hint
    per bar — priority pedal > inversion > density so the grounding anchor
    isn't overwritten by a colour tweak.
    """
    plan: dict[int, str] = {}
    n = len(assignments)
    if n == 0:
        return plan

    # --- pedal=1: first bar of phrases with >= 6 bars --------------------
    for ph in song.phrases:
        ibars = list(ph.ibars or ())
        if len(ibars) >= 6 and ibars:
            ib = ibars[0]
            if 1 <= ib <= n and assignments[ib - 1] is not None:
                plan[ib] = 'pedal=1'

    # --- inversion=1 on the SECOND occurrence only of a repeated phrase-final
    # RN (per Task #12 policy: "bar 8 of a 16-bar hymn with same chord as bar 4
    # — inversion on 2nd occurrence only").  Third and later occurrences are
    # left alone so the figure contrast is a one-shot surprise, not a pattern.
    phrase_final_bars: list[int] = []
    for ph in song.phrases:
        ibars = list(ph.ibars or ())
        if ibars:
            phrase_final_bars.append(ibars[-1])
    rn_counts: dict[str, int] = {}
    for ib in phrase_final_bars:
        if not (1 <= ib <= n):
            continue
        a = assignments[ib - 1]
        if a is None:
            continue
        rn = (a.get('rn') or '').strip()
        if not rn:
            continue
        rn_counts[rn] = rn_counts.get(rn, 0) + 1
        if rn_counts[rn] == 2 and ib not in plan:
            plan[ib] = 'inversion=1'

    # --- density=extend on sustained phrase-final bars -------------------
    meter = song.meter
    bar_duration = float(meter.beats) * (4.0 / float(meter.unit))
    if bar_duration >= 3.0:
        for ph in song.phrases:
            ibars = list(ph.ibars or ())
            if not ibars:
                continue
            ib = ibars[-1]
            if not (1 <= ib <= n):
                continue
            if ib in plan:
                continue
            a = assignments[ib - 1]
            if a is None:
                continue
            bar = song.bars[ib - 1]
            n_events = len(bar.melody)
            if n_events <= 2:
                plan[ib] = 'density=extend'

    return plan


def _apply_voicing_hint(assignment: dict, hint: str) -> dict:
    """Return a shallow-copied assignment dict with figures re-shaped per hint.

    Attaches the hint name as ``assignment['voicing']`` so downstream consumers
    (and the label-markup pass) can see which bars were tweaked.  Pedal is
    NOT expressed as a figure change — it is handled at layout time by
    injecting a low tonic into the LH event stream; we merely tag it here.
    """
    out = dict(assignment)
    out['voicing'] = hint
    if hint == 'inversion=1':
        lh = out.get('lh_fig') or ''
        if lh:
            out['lh_fig'] = _rotate_figure_inv1(lh)
    elif hint == 'density=extend':
        rh = out.get('rh_fig') or ''
        if rh:
            out['rh_fig'] = _extend_figure_9th(rh)
    # 'pedal=1' has no figure-level change; layout pass injects a bass tonic.
    return out


def _inject_pedal_tone(bar_data: dict, key_root: str, mode: str) -> None:
    """Add a low-tonic pedal under the bar's LH events (in-place).

    If the bar already carries ``grace_midis`` (bar 1 / last bar), prepend the
    pedal to those; otherwise add it as ``grace_midis`` on the first LH event
    so it sounds as a grace leading into the beat-1 block.  Also stack a
    sustained low tonic as an additional midi in the first LH chord so it
    rings through the bar.
    """
    lh_events = bar_data.get('lh_events') or []
    if not lh_events:
        return
    pedal_midi = string_to_midi(1, key_root, mode, base_octave=1)
    while pedal_midi < HARP_LOW_MIDI:
        pedal_midi += 12
    first = lh_events[0]
    existing = list(first.get('midis') or [])
    if pedal_midi not in existing:
        first['midis'] = [pedal_midi] + existing
    grace = list(first.get('grace_midis') or [])
    if pedal_midi not in grace:
        first['grace_midis'] = [pedal_midi] + grace


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
    { \once \omit Staff.TimeSignature \voiceTwo __RHFILL__ }
  >>
}

lower = {
  \clef bass
  \global
  \once \omit Staff.TimeSignature
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

    # Voicing hints (Task #12): ibar -> hint name.  Applied to the per-bar
    # assignment dict so layout sees the reshaped figures; 'pedal=1' is
    # handled after layout via _inject_pedal_tone since it touches the LH
    # event stream, not the figure string.
    voicing_hints = _voicing_plan(song, assignments)
    for ib, hint in voicing_hints.items():
        a = assignments[ib - 1]
        if a is None:
            continue
        assignments[ib - 1] = _apply_voicing_hint(a, hint)

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
        # Approach decoration: upgrade strum_pickup → approach_pickup when the
        # bar is the phrase-interior pre-cadence (bar n with n+1 phrase-end,
        # original chord not already V, no mapper substitution in play).
        if style == 'strum_pickup' and _should_use_approach_pickup(
            ibar, assignment, next_assignment, phrase_end_bars,
            is_last_bar=is_last,
        ):
            style = 'approach_pickup'
            # Surface the technique on the assignment for downstream logging.
            assignment['technique'] = 'Dominant approach'
        layout_fn = _STYLE_LAYOUTS.get(style, layout_bar_grand)
        if style == 'approach_pickup':
            bar_data = layout_fn(assignment, melody_events, key_root, mode,
                                 meter_num, meter_den,
                                 next_assignment=next_assignment,
                                 pool=pool)
        else:
            bar_data = layout_fn(assignment, melody_events, key_root, mode,
                                 meter_num, meter_den,
                                 next_assignment=next_assignment)
        if voicing_hints.get(ibar) == 'pedal=1':
            _inject_pedal_tone(bar_data, key_root, mode)
        bar_data['label_markup'] = chord_label_markup(assignment)
        bar_data['style'] = style
        bar_data['voicing'] = assignment.get('voicing')
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
    'layout_bar_approach_pickup',
]
