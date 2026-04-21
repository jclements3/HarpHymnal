"""Canonical parser for the encoded roman-numeral strings in
`HarpTrefoil.json` / `HarpChordSystem.json`.

Those files flatten inversion superscripts (`¹ ² ³`) to the ASCII strings
`i ii iii`.  So `ii7iii` is *ii7 in third inversion*, not a mediant chord;
`V7ii` is V7 in second inversion; `IVΔii` is IV-major7 in second inversion.

That introduces a short-prefix ambiguity on strings like `Iii`, `Ii`,
`Vii` — they could be read as the longer roman (`III`, `II`, `VII`) in
root position, OR as the shorter roman (`I`, `I`, `V`) followed by an
inversion marker.  The *figure*'s first digit tells you the actual
sounded bass string, which unambiguously disambiguates: pick the parse
whose `(root + inv_offset) mod 7` equals the figure's first digit.

About nine entries in the 118-entry pool hit this ambiguity, but any
naive parser gets all of them wrong.  Use this module instead of rolling
your own.

Usage:
    >>> parse_roman_with_inversion("ii7iii", figure_bass_digit=1)
    {'accidental': '', 'root_roman': 'ii', 'root_degree': 2,
     'quality': '7', 'inversion': 'iii', 'inv_offset': 6, 'bass_degree': 1}
    >>> parse_roman_with_inversion("Iii", figure_bass_digit=5)
    {'accidental': '', 'root_roman': 'I', 'root_degree': 1,
     'quality': '',  'inversion': 'ii',  'inv_offset': 4, 'bass_degree': 5}
    >>> parse_roman_with_inversion("III", figure_bass_digit=3)
    {'accidental': '', 'root_roman': 'III', 'root_degree': 3,
     'quality': '',  'inversion': None, 'inv_offset': 0, 'bass_degree': 3}
"""
from __future__ import annotations

import re
from typing import Optional


_ROMAN_MAP = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
}
# Inversion → scale-degree offset of the bass relative to the root.
# 1st inv (i)   → 3rd in bass = +2 diatonic steps
# 2nd inv (ii)  → 5th in bass = +4
# 3rd inv (iii) → 7th in bass = +6 (only defined on 7-chords)
_INV_OFFSET = {"i": 2, "ii": 4, "iii": 6}

_ACC_RE = re.compile(r"^([b#♭♯]*)")


def _figure_digit(c: str) -> Optional[int]:
    """Convert a single figure character to a scale-degree integer 1-14.
    The figure alphabet is hex-ish (1-9, A-E) and can run up into the
    second octave (e.g. `A43` starts on string A = 10 = ii an octave up)."""
    if c.isdigit():
        return int(c)
    c = c.upper()
    if c in "ABCDEF":
        return 10 + (ord(c) - ord("A"))
    return None


def figure_bass_digit(fig: str) -> Optional[int]:
    """Return the sounded bass string as a diatonic degree 1..7, regardless
    of the absolute octave (mod-7).  `A43` has A=10 → degree 3 (ii moved up)."""
    if not fig:
        return None
    raw = _figure_digit(fig[0])
    if raw is None:
        return None
    return ((raw - 1) % 7) + 1


def parse_roman_with_inversion(
    roman_str: str, figure_bass_digit_value: Optional[int] = None
) -> Optional[dict]:
    """Decompose a roman string into {accidental, root_roman, root_degree,
    quality, inversion, inv_offset, bass_degree}.

    When there's a short-prefix ambiguity (e.g. `Iii` = III-root vs I-with-
    2nd-inversion), `figure_bass_digit_value` picks the interpretation whose
    predicted bass matches the figure.  Without the figure hint we fall back
    to the shorter-roman reading (which is correct in every ambiguous pool
    entry observed to date).
    """
    if not roman_str:
        return None
    acc = _ACC_RE.match(roman_str).group(1)
    rest = roman_str[len(acc):]
    if not rest:
        return None

    # Candidate interpretations: try every roman prefix length, see which
    # produces a plausible bass.
    candidates = []
    # Scan prefixes of increasing length.
    for prefix_len in range(1, len(rest) + 1):
        prefix = rest[:prefix_len]
        if prefix not in _ROMAN_MAP:
            continue
        root = _ROMAN_MAP[prefix]
        tail = rest[prefix_len:]
        # Inversion suffix, if present, is a trailing `i`/`ii`/`iii`.
        inv = None
        inv_m = re.search(r"(i{1,3})$", tail)
        if inv_m:
            inv = inv_m.group(1)
            quality = tail[:-len(inv)]
        else:
            quality = tail
        offset = _INV_OFFSET.get(inv, 0)
        bass_d = ((root - 1 + offset) % 7) + 1
        candidates.append({
            "accidental": acc,
            "root_roman": prefix,
            "root_degree": root,
            "quality": quality,
            "inversion": inv,
            "inv_offset": offset,
            "bass_degree": bass_d,
        })

    if not candidates:
        return None

    # If we have the figure bass digit, pick the interpretation whose
    # predicted bass matches.  Otherwise fall back to shortest-prefix.
    if figure_bass_digit_value is not None:
        for c in candidates:
            if c["bass_degree"] == figure_bass_digit_value:
                return c
        # No interpretation matches — return the shortest and let the
        # caller decide how to flag the mismatch.
    return candidates[0]


__all__ = [
    "parse_roman_with_inversion",
    "figure_bass_digit",
]
