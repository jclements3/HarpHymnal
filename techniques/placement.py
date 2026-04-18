"""Placement techniques (2 functions, multi-bar).

These adjust *when* a chord change lands relative to its notated bar.  The
underlying ``Bar`` structure has no sub-beat chord-timing slot, so v1 is
annotation-only: mark the bar with ``technique='Anticipation'`` or
``'Delay'`` and leave structural re-timing to renderers that care.

Pure functions: no mutation.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional

from grammar.types import Bar


def _replace_at(bars: tuple[Bar, ...], i: int, new_bar: Bar) -> tuple[Bar, ...]:
    return bars[:i] + (new_bar,) + bars[i + 1:]


def anticipation(bars: tuple[Bar, ...], *, i: int, beats: float = 0.5,
                 ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Shift the chord change of ``bars[i]`` earlier by ``beats``.

    MVP: annotate ``bars[i].technique = 'Anticipation'``.  Structural
    re-timing (sub-beat chord grid) is a renderer concern.
    """
    # MVP: refine with pedagogy
    if not (0 <= i < len(bars)):
        return bars
    new_bar = replace(bars[i], technique='Anticipation')
    return _replace_at(bars, i, new_bar)


def delay(bars: tuple[Bar, ...], *, i: int, beats: float = 0.5,
          ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Shift the chord change of ``bars[i]`` later by ``beats``.

    MVP: annotate ``bars[i].technique = 'Delay'``.
    """
    # MVP: refine with pedagogy
    if not (0 <= i < len(bars)):
        return bars
    new_bar = replace(bars[i], technique='Delay')
    return _replace_at(bars, i, new_bar)
