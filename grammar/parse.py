"""Parsers: string → grammar objects.

Single source of truth for string forms of grammar productions.
Every script imports from here — no more scattered regex.
"""
from __future__ import annotations

import re
from typing import Optional

from grammar.types import Roman, Shape


_INVERSION_MAP = {'¹': '¹', '²': '²', '³': '³',
                  '1': '¹', '2': '²', '3': '³'}
_QUALITIES = (
    'Δ7', 'Δ', 'ø7', '○7', '7', '6', '9',
    's2', 's4', 'q7', 'q', '+8',
)


# Longest-first so 'vii○' matches before 'vii' and 'ii○' before 'ii'.
_NUMERALS = (
    'vii○', 'vii',
    'iii', 'ii○', 'ii',
    'iv', 'vi', 'v', 'i',
    'III', 'VII', 'VI', 'IV', 'II', 'V', 'I',
)


def parse_roman(s: str) -> Roman:
    """Parse a roman-numeral chord symbol into its three slots.

    Canonical order: numeral [quality] [inversion].  Examples:
      I, ii, V7, IΔ7, iiø7, vii○7, iii¹, IV+8².
    """
    s = s.strip()
    if not s:
        raise ValueError("empty roman numeral")

    # 1. Longest-match the numeral prefix so 'vii○' beats 'vii'.
    numeral: Optional[str] = None
    for cand in _NUMERALS:
        if s.startswith(cand):
            numeral = cand
            s = s[len(cand):]
            break
    if numeral is None:
        raise ValueError(f"unrecognized numeral in {s!r}")

    # 2. Strip trailing inversion (¹²³ or ascii 1|2|3).
    inv: Optional[str] = None
    for sup, canonical in _INVERSION_MAP.items():
        if s.endswith(sup):
            inv = canonical
            s = s[: -len(sup)]
            break

    # 3. What remains (middle) is the optional quality.  Validate.
    qual: Optional[str] = s if s else None
    if qual is not None and qual not in _QUALITIES:
        raise ValueError(f"unknown quality {qual!r} in roman")

    return Roman(numeral=numeral, quality=qual, inversion=inv)


_FIGURE_RE = re.compile(r'^([1-9A-F])([2-4]+)$')


def parse_figure(fig: str) -> tuple[int, tuple[int, ...]]:
    """Parse the wire-format figure like 'F33' or '5323' into (anchor, intervals).

    Returns (anchor_position, interval_tuple).  Anchor is 1..15 (hex-ish);
    intervals are each 2, 3, or 4.
    """
    m = _FIGURE_RE.match(fig.strip())
    if not m:
        raise ValueError(f"malformed figure: {fig!r}")
    anchor_ch, int_chars = m.group(1), m.group(2)
    anchor = int(anchor_ch, 16)    # '1'..'9' parse as decimal, 'A'..'F' as hex
    intervals = tuple(int(c) for c in int_chars)
    return anchor, intervals


def parse_shape(fig: str, degree: int) -> Shape:
    """Parse a wire-format figure + known scale-degree anchor → Shape.

    The figure's first character names a string position on the harp; the
    `degree` argument names which scale-degree that position corresponds to
    in the current key.  Usually the caller computes degree from the
    anchor + key context.
    """
    _, intervals = parse_figure(fig)
    return Shape(degree=degree, intervals=intervals)  # type: ignore[arg-type]
