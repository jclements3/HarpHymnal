#!/usr/bin/env python3
"""Build the (interval-pattern × degree) chord-match table.

Rows: interval-only shape patterns (dyads, triads, tetrads).
Columns: the seven degrees, ^1 .. ^7.
Cell: a music21 chord name for the resulting pitch set, computed against
      a Tonic C / all-naturals pedal state.

Outputs an HTML <table> snippet to stdout. The build_html.py post-build
inlines it into index.html.
"""
from __future__ import annotations

import re
import sys
from music21 import chord, pitch

# Diatonic scale in C major (Tonic C, all naturals).
SCALE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# Scale degree (1..7) -> bold-rendered Roman numeral (diatonic case in C major).
_DEG_ROMAN = {1: 'I', 2: 'ii', 3: 'iii', 4: 'IV', 5: 'V', 6: 'vi', 7: 'vii°'}

# Curated interval patterns.  Each row carries the pattern code (digits as
# they appear in shape syntax) plus a one-word description.  Order roughly
# moves from sparse to dense voicings.
PATTERNS: list[tuple[str, str]] = [
    # Dyads (1 interval)
    ('3',   'Dyad: 3rd'),
    ('4',   'Dyad: 4th'),
    ('5',   'Dyad: 5th'),
    ('8',   'Dyad: octave'),
    # Triads (2 intervals)
    ('33',  'Triad: stacked 3rds'),
    ('34',  'Triad: 3rd + 4th'),
    ('35',  'Triad: 3rd + 5th'),
    ('43',  'Triad: 4th + 3rd'),
    ('44',  'Triad: stacked 4ths (quartal)'),
    ('45',  'Triad: 4th + 5th'),
    ('53',  'Triad: 5th + 3rd'),
    # Universal-winner tetrads (3 intervals)
    ('333', 'Tetrad: stacked 3rds (Δ7)'),
    ('335', 'Tetrad: universal winner'),
    ('336', 'Tetrad: universal winner'),
    ('344', 'Tetrad: universal winner'),
    ('345', 'Tetrad: universal winner'),
    ('346', 'Tetrad: universal winner'),
    ('355', 'Tetrad: universal winner'),
    ('356', 'Tetrad: universal winner'),
    ('435', 'Tetrad: universal winner'),
    ('436', 'Tetrad: universal winner'),
    ('446', 'Tetrad: universal winner'),
    ('456', 'Tetrad: universal winner'),
    # Mode-flavored / quartal
    ('444', 'Tetrad: quartal stack (Lydian)'),
]


def shape_pitches(degree: int, intervals: str, base_octave: int = 4) -> list[pitch.Pitch]:
    """Compute the pitch list for shape `^<degree> <intervals>` in C-major.

    Each interval digit `v` is `v-1` scale steps (digit 3 = 3rd = 2 steps).
    The diatonic scale wraps every 7 letters, octave incrementing by 1.
    """
    idx = degree - 1  # scale-step index from C
    out = []
    letter = SCALE[idx % 7]
    octv = base_octave + idx // 7
    out.append(pitch.Pitch(f'{letter}{octv}'))
    for ch in intervals:
        steps = int(ch, 16) - 1
        idx += steps
        letter = SCALE[idx % 7]
        octv = base_octave + idx // 7
        out.append(pitch.Pitch(f'{letter}{octv}'))
    return out


_LETTER_INDEX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}

# (interval-number, semitones) → quality shorthand. Interval-number comes
# from letter-step distance + 1 (so the digit `5` always names a 5th,
# never a 4th, even when the actual semitone count is 6).
_INTERVAL_QUALITY = {
    (2, 1): 'm2',  (2, 2): 'M2',
    (3, 3): 'm3',  (3, 4): 'M3',
    (4, 5): 'P4',  (4, 6): 'A4',
    (5, 6): 'd5',  (5, 7): 'P5',  (5, 8): 'A5',
    (6, 8): 'm6',  (6, 9): 'M6',
    (7, 10): 'm7', (7, 11): 'M7',
    (8, 12): '8va',
    (9, 13): 'm9', (9, 14): 'M9',
}


def _dyad_quality(p1: pitch.Pitch, p2: pitch.Pitch) -> str:
    """Compute interval shorthand respecting spelling — B-F as digit `4` is
    A4, but as digit `5` is d5, even though both span 6 semitones."""
    li_diff = _LETTER_INDEX[p2.name] - _LETTER_INDEX[p1.name]
    oct_diff = p2.octave - p1.octave
    steps = li_diff + oct_diff * 7
    semis = (_PC_FROM_NAME[p2.name] - _PC_FROM_NAME[p1.name]) + oct_diff * 12
    return _INTERVAL_QUALITY.get((steps + 1, semis), f'{steps + 1}({semis}st)')

# Pitch-class number → diatonic letter (Tonic C, all naturals — no
# accidentals appear in any cell).
_PC_NAME = {0: 'C', 2: 'D', 4: 'E', 5: 'F', 7: 'G', 9: 'A', 11: 'B'}
_PC_FROM_NAME = {v: k for k, v in _PC_NAME.items()}

# Templates: (sorted intervals from root in semitones) → jazz suffix.
# When this is found as the bass-relative signature, the chord name is
# `<bass><suffix>`; when found as some other pitch's signature, the name
# is `<that pitch><suffix>/<bass>` (slash-chord notation).
_TEMPLATES: dict[tuple[int, ...], str] = {
    # Triads
    (0, 4, 7):     '',
    (0, 3, 7):     'm',
    (0, 3, 6):     '°',
    (0, 4, 8):     '+',
    (0, 5, 7):     'sus4',
    (0, 2, 7):     'sus2',
    # Triads with omitted 5th — common jazz no-5 voicings
    (0, 4, 11):    'maj7(no5)',
    (0, 4, 10):    '7(no5)',
    (0, 3, 10):    'm7(no5)',
    (0, 3, 11):    'mMaj7(no5)',
    # No-3 triads — root + 5th + 7th-class
    (0, 7, 11):    'maj7(no3)',
    (0, 7, 10):    '7(no3)',
    (0, 6, 10):    'ø7(no3)',
    # Tetrads — root + extensions, 5 present
    (0, 4, 7, 11): 'maj7',
    (0, 4, 7, 10): '7',
    (0, 3, 7, 10): 'm7',
    (0, 3, 6, 10): 'ø7',
    (0, 3, 6, 9):  '°7',
    (0, 4, 7, 9):  '6',
    (0, 3, 7, 9):  'm6',
    # Tetrads — added-tone voicings, 5 present
    (0, 2, 4, 7):  'add9',
    (0, 2, 3, 7):  'm(add9)',
    (0, 1, 3, 7):  'm(♭9)',
    (0, 1, 3, 6):  '°(♭9)',
    (0, 2, 4, 9):  '6/9',
    (0, 2, 3, 9):  'm6/9',
    # Tetrads — suspended
    (0, 5, 7, 10): '7sus4',
    (0, 5, 7, 11): 'maj7sus4',
    (0, 5, 6, 10): 'ø7sus4',
    # Maj7 family with sharp-11 / Lydian flavor
    (0, 6, 7, 11): 'maj7(♯11)',
    (0, 4, 6, 11): 'maj7(♯11)(no5)',
    # add-11 voicings — kept primarily so the slash logic can find clean
    # names like "Cadd11/E" or "Gmaj7add11/D" via slash on these sets.
    (0, 4, 5, 7):  'add11',
    (0, 3, 5, 7):  'm(add11)',
    (0, 4, 5, 11): 'maj7add11',
    (0, 4, 5, 10): '7add11',
    (0, 3, 5, 10): 'm7add11',
    # Quartal triads (4+4 from root) — root + 4 + (7-flavor)
    (0, 5, 10):    '7sus4(no5)',
    (0, 5, 11):    'maj7sus4(no5)',
    (0, 6, 11):    'maj7(♯11)(no3,5)',
    # Major triad + #11 (Lydian, no 7) — needed for slash on (344/^6, 344/^7)
    (0, 4, 6, 7):  'maj(add♯11)',
    # 6(no5) — needed for slash detection
    (0, 4, 9):     '6(no5)',
    (0, 3, 9):     'm6(no5)',
}


def _intervals_from(root_pc: int, pcs: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted({(pc - root_pc) % 12 for pc in pcs}))


def _try_chord_name(bass_pc: int, pcs: tuple[int, ...]) -> str | None:
    """Search templates for the cleanest chord name covering this pitch set.

    Considers both bass-as-root and every slash interpretation, then picks
    the candidate whose chord suffix is shortest (so a "F6/A" slash beats
    a clumsy bass-rooted "Am(addb6)add11" even though both are valid).
    Bass-as-root is preferred only on ties.
    """
    bass_name = _PC_NAME[bass_pc]
    candidates: list[tuple[int, int, str]] = []  # (suffix_len, tier, label)

    sig = _intervals_from(bass_pc, pcs)
    if sig in _TEMPLATES:
        suffix = _TEMPLATES[sig]
        candidates.append((len(suffix), 0, f'{bass_name}{suffix}'))

    for root_pc in pcs:
        if root_pc == bass_pc:
            continue
        sig = _intervals_from(root_pc, pcs)
        if sig in _TEMPLATES:
            suffix = _TEMPLATES[sig]
            root_name = _PC_NAME[root_pc]
            candidates.append((len(suffix), 1, f'{root_name}{suffix}/{bass_name}'))

    if candidates:
        candidates.sort()
        return candidates[0][2]
    return None


def short_chord_name(pitches: list[pitch.Pitch]) -> str:
    """Return a compact jazz-style chord name for the shape's pitch set.

    Triads / tetrads use root-position templates; non-bass roots produce
    slash-chord names (`Fmaj7/C`, `B°/D`). Dyads name the interval. Sets
    that match no template fall back to the pitch list.
    """
    pcs_list = sorted({_PC_FROM_NAME[p.name] for p in pitches})
    pcs = tuple(pcs_list)
    bass_pc = _PC_FROM_NAME[pitches[0].name]
    bass_name = pitches[0].name

    # Single pitch class repeated (octave doubling, unison shape).
    if len(pcs) == 1:
        return f'{bass_name} 8va'

    # Dyad — interval shorthand based on letter-step spelling, not just
    # semitones (so B-F differs between the 4th-dyad and 5th-dyad rows).
    if len(pcs) == 2:
        return f'{bass_name} {_dyad_quality(pitches[0], pitches[1])}'

    name = _try_chord_name(bass_pc, pcs)
    if name:
        return name

    # Quartal-pattern detection — every adjacent step is a P4 or A4.
    diffs = [(pcs_list[i + 1] - pcs_list[i]) for i in range(len(pcs_list) - 1)]
    if diffs and all(d in (5, 6) for d in diffs):
        return f'{bass_name} quartal'

    return '-'.join(p.name for p in pitches)


def cell(degree: int, intervals: str) -> str:
    pitches = shape_pitches(degree, intervals)
    return short_chord_name(pitches)


def emit_table() -> str:
    rows = []
    rows.append('<table class="chord-match">')
    rows.append('<thead><tr><th rowspan="2">Intervals</th>'
                '<th colspan="7">Degree</th><th rowspan="2">Notes</th></tr>')
    rows.append('<tr>')
    for d in range(1, 8):
        rows.append(f'<th><b class="deg">{_DEG_ROMAN[d]}</b></th>')
    rows.append('</tr></thead>')
    rows.append('<tbody>')
    for pat, note in PATTERNS:
        rows.append('<tr>')
        rows.append(f'<th><code>{pat}</code></th>')
        for d in range(1, 8):
            rows.append(f'<td><code>{cell(d, pat)}</code></td>')
        rows.append(f'<td>{note}</td>')
        rows.append('</tr>')
    rows.append('</tbody></table>')
    return '\n'.join(rows)


if __name__ == '__main__':
    sys.stdout.write(emit_table())
    sys.stdout.write('\n')
