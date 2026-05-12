"""Deborah Henson-Conant Somerset 2020 Left-Hand Patterns for harp.

Source: somerset/somerset01..17.png — 17 LH accompaniment patterns each based
on the chord progression (the root of each chord is the "1" of the pattern).

This module renders a full LH ABC voice body for a hymn using a chosen pattern
applied bar-by-bar according to the hymn's roman-numeral chord progression.

Public API:
    AVAILABLE: list[str] — pattern names suitable for a UI dropdown.
    render_lh_voice(pattern, bar_chords, key_root, key_mode, meter_beats, key_sig)
        → str — ABC voice body (joined with bar lines and newlines).
"""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Callable, Optional

from music21 import key as m21key

from .consolidator import midi_to_abc


# ─── Roman-numeral parsing (subset; covers the diatonic heads used by the analyzer) ───
_RN_DEGREE: dict[str, int] = {
    "I": 1, "ii": 2, "iii": 3, "IV": 4, "V": 5, "vi": 6, "vii": 7,
    "i": 1, "II": 2, "III": 3, "iv": 4, "v": 5, "VI": 6, "VII": 7,
}


def _rn_head(rn: str) -> Optional[str]:
    """Return the bare roman-numeral letters from a figure ("V7" → "V")."""
    if not rn:
        return None
    m = re.match(r"^[#b]?([ivIV]+)", rn)
    return m.group(1) if m else None


def _is_diminished(rn: str) -> bool:
    return rn and any(s in rn for s in ('°', 'o', 'ø'))


# ─── Duration helper ─────────────────────────────────────────────────────────
def _dur(d: float) -> str:
    """ABC duration token under L:1/4 (1.0 = quarter)."""
    if d == int(d):
        n = int(d)
        return "" if n == 1 else str(n)
    if d == 0.5: return "/2"
    if d == 1.5: return "3/2"
    if d == 0.25: return "/4"
    if d == 0.75: return "3/4"
    f = Fraction(d).limit_denominator(16)
    return f"{f.numerator}/{f.denominator}"


# Hard ceiling for LH pitches: B3 (one semitone below middle C). Anything
# higher is octave-displaced down so the LH stays in the bass clef.
LH_TOP_MIDI = 59  # B3


def _clamp_lh(midi: int) -> int:
    while midi > LH_TOP_MIDI:
        midi -= 12
    return midi


def _chord_tok(midis: list[int], key_sig: dict[str, int]) -> str:
    # Sort + dedup after clamping so close-position triads come out correctly.
    seen: set[int] = set()
    midis = sorted(_clamp_lh(m) for m in midis)
    midis = [m for m in midis if not (m in seen or seen.add(m))]
    if len(midis) == 1:
        return midi_to_abc(midis[0], key_sig)
    return '[' + ''.join(midi_to_abc(m, key_sig) for m in midis) + ']'


# ─── Pattern factories — each returns [(duration_in_quarters, [pitch_offsets_from_root]), ...] ───
# `t` = third (3 minor, 4 major). `f` = fifth (6 dim, 7 perfect).

def _p_octaves(t, f):
    return [(4.0, [-12, 0])]

def _p_1_5_8_arp(t, f):
    return [(1.0, [0]), (1.0, [f]), (2.0, [12])]

def _p_1_5_10_chord(t, f):
    return [(4.0, [0, f, 12 + t])]

def _p_1_5_10_arp_44(t, f):
    return [(1.0, [0]), (1.0, [f]), (2.0, [12 + t])]

def _p_1_5_10_arp_34(t, f):
    return [(1.0, [0]), (1.0, [f]), (1.0, [12 + t])]

def _p_alberti(t, f):
    # 4/4: eight eighth notes, 1-5-3-5 repeating
    return [(0.5, [0]), (0.5, [f]), (0.5, [t]), (0.5, [f])] * 2

def _p_calypso(t, f):
    return [(1.5, [0]), (0.5, [12]), (1.0, [f]), (1.0, [12])]

def _p_simple_latin_1855(t, f):
    return [(1.5, [0]), (0.5, [12]), (1.0, [f]), (1.0, [f])]

def _p_simple_latin_15105(t, f):
    return [(1.5, [0]), (0.5, [f]), (1.0, [12 + t]), (1.0, [f])]

def _p_simple_latin_11055(t, f):
    return [(1.5, [0]), (0.5, [12 + t]), (1.0, [f]), (1.0, [f])]

def _p_pretty_waltz(t, f):
    # 3/4 with added 9th (14 st = octave + 2nd)
    return [(0.5, [0]), (0.5, [f]), (0.5, [14]),
            (0.5, [12]), (0.5, [14]), (0.5, [12])]

def _p_slap_bass(t, f):
    # Simplified (no slap accent in MIDI): low root + 5 alternating
    return [(0.5, [0]), (0.5, [f]), (0.5, [0]), (0.5, [f])] * 2

def _p_samba(t, f):
    return [(0.5, [0]), (0.5, [12]), (0.5, [-5]), (0.5, [0])] * 2

def _p_mexican(t, f):
    return [(1.5, [-12]), (0.5, [0]),
            (1.0, [0, t, f]), (1.0, [0, t, f])]

def _p_stride(t, f):
    return [(1.0, [-12]), (1.0, [0, t, f]),
            (1.0, [-5]),  (1.0, [0, t, f])]

def _p_broken_stride(t, f):
    return [(1.5, [-12]), (0.5, [0]),
            (1.0, [0, t, f]), (1.0, [-5])]

def _p_waltz(t, f):
    # 3/4 oom-pah-pah
    return [(1.0, [-12]), (2.0, [0, t, f])]


PATTERNS: dict[str, dict[int, Callable]] = {
    "Octaves":                {4: _p_octaves},
    "1-5-8 Arpeggiated":      {4: _p_1_5_8_arp},
    "1-5-10 Chord":           {4: _p_1_5_10_chord},
    "1-5-10 Arpeggiated":     {4: _p_1_5_10_arp_44, 3: _p_1_5_10_arp_34},
    "Alberti Bass":           {4: _p_alberti},
    "Calypso":                {4: _p_calypso},
    "Simple Latin 1-8-5-5":   {4: _p_simple_latin_1855},
    "Simple Latin 1-5-10-5":  {4: _p_simple_latin_15105},
    "Simple Latin 1-10-5-5":  {4: _p_simple_latin_11055},
    "Pretty Waltz (+9th)":    {3: _p_pretty_waltz},
    "Slap Bass":              {4: _p_slap_bass},
    "Samba":                  {4: _p_samba},
    "Mexican (Latin)":        {4: _p_mexican},
    "Stride Bass":            {4: _p_stride},
    "Latin Broken Stride":    {4: _p_broken_stride},
    "Waltz":                  {3: _p_waltz},
}

AVAILABLE = list(PATTERNS.keys())


# ─── Root MIDI selection ────────────────────────────────────────────────────
def _root_midi(K: m21key.Key, degree: int) -> int:
    """Compute chord root MIDI in the C3-B3 octave (LH bass register)."""
    pc = K.pitches[degree - 1].pitchClass
    midi = 48 + pc
    while midi > 59:
        midi -= 12
    while midi < 48:
        midi += 12
    return midi


# ─── Public API ──────────────────────────────────────────────────────────────
def render_one_bar(
    pattern: str,
    rn_str: str,
    K: m21key.Key,
    meter_beats: int,
    key_sig: dict[str, int],
) -> str:
    p_map = PATTERNS.get(pattern)
    if p_map is None:
        return f"z{_dur(float(meter_beats))}"

    head = _rn_head(rn_str)
    degree = _RN_DEGREE.get(head) if head else None
    if degree is None:
        return f"z{_dur(float(meter_beats))}"

    is_min = head and head[0].islower()
    is_dim = _is_diminished(rn_str)
    third_st = 3 if (is_min or is_dim) else 4
    fifth_st = 6 if is_dim else 7

    events_fn = p_map.get(meter_beats) or next(iter(p_map.values()))
    events = events_fn(third_st, fifth_st)

    root_midi = _root_midi(K, degree)
    tokens = []
    for dur, offsets in events:
        midis = [root_midi + off for off in offsets]
        tokens.append(_chord_tok(midis, key_sig) + _dur(dur))
    return ' '.join(tokens)


def render_lh_voice(
    pattern: str,
    bar_chords: dict[int, str],
    key_root: str,
    key_mode: str,
    meter_beats: int,
    key_sig: dict[str, int],
) -> str:
    if pattern not in PATTERNS:
        return ""
    if not bar_chords:
        return ""

    K = m21key.Key(key_root + ('m' if key_mode == 'minor' else ''))
    bar_count = max(bar_chords.keys())

    bar_tokens = [
        render_one_bar(pattern, bar_chords.get(bar, ""), K, meter_beats, key_sig)
        for bar in range(1, bar_count + 1)
    ]

    lines: list[str] = []
    buf: list[str] = []
    for i, tok in enumerate(bar_tokens):
        buf.append(tok)
        is_last = (i == len(bar_tokens) - 1)
        buf.append('|]' if is_last else '|')
        if is_last or (i + 1) % 4 == 0:
            lines.append(' '.join(buf))
            buf = []
    return '\n'.join(lines)
