"""Voicing techniques (6 functions).

Each modifies ``bar.voicing`` (a ``Shape`` or ``Bishape``) rather than
``bar.chord``.  The chord name is preserved; only the hand-shape changes.

    - inversion           — set chord.inversion label
    - density             — thin (2-finger) / full (4-finger) shape
    - stacking            — single Shape → Bishape (same shape LH, octave-up RH)
    - pedal               — add pedal tone (annotation-level MVP)
    - voice_leading       — pick candidate voicing minimising interval movement
    - open_closed_spread  — spread to ``open`` (widen 2→3→4) or ``closed``
                            (collapse 4→3→2)

All pure: use :func:`dataclasses.replace` and build new tuples.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional

from grammar.types import Bar, Bishape, Shape

from techniques.substitution import _as_roman


def _annotate(bar: Bar, name: str) -> Bar:
    return replace(bar, technique=name)


# ──────────────────────────────────────────────────────────────────────────
# 1. Inversion
# ──────────────────────────────────────────────────────────────────────────

def inversion(bar: Bar, *, which: str = '¹', ctx: Optional[dict] = None) -> Bar:
    """Set ``bar.chord.inversion`` to ``which`` (one of '¹', '²', '³')."""
    roman = _as_roman(bar.chord)
    if roman is None:
        return _annotate(bar, 'Inversion')
    new_chord = replace(roman, inversion=which)
    return replace(bar, chord=new_chord, technique='Inversion')


# ──────────────────────────────────────────────────────────────────────────
# 2. Density
# ──────────────────────────────────────────────────────────────────────────

def _shape_density(shape: Shape, level: str) -> Shape:
    """Return a thinned or thickened Shape.

    - ``'thin'`` keeps only the first interval (2-finger shape).
    - ``'full'`` extends to 4 intervals by repeating 3 (Δ7/9-colour stack).
    """
    if level == 'thin':
        if len(shape.intervals) <= 1:
            return shape
        return replace(shape, intervals=shape.intervals[:1])
    if level == 'full':
        if len(shape.intervals) >= 3:
            return shape
        needed = 3 - len(shape.intervals)
        return replace(shape, intervals=shape.intervals + (3,) * needed)
    return shape


def density(bar: Bar, *, level: str = 'thin', ctx: Optional[dict] = None) -> Bar:
    """Shrink or extend ``bar.voicing`` to ``level`` ('thin' | 'full')."""
    if bar.voicing is None:
        return _annotate(bar, 'Density')
    if isinstance(bar.voicing, Shape):
        new_voicing = _shape_density(bar.voicing, level)
    elif isinstance(bar.voicing, Bishape):
        new_voicing = Bishape(
            lh=_shape_density(bar.voicing.lh, level),
            rh=_shape_density(bar.voicing.rh, level),
        )
    else:
        return _annotate(bar, 'Density')
    return replace(bar, voicing=new_voicing, technique='Density')


# ──────────────────────────────────────────────────────────────────────────
# 3. Stacking (Shape → Bishape with RH one octave higher)
# ──────────────────────────────────────────────────────────────────────────

def stacking(bar: Bar, *, ctx: Optional[dict] = None) -> Bar:
    """If ``bar.voicing`` is a single Shape, promote to a Bishape (LH = same
    shape; RH = same intervals anchored a diatonic octave above).

    Because ``degree`` is a 1..7 scale-degree anchor (not a string number), we
    keep ``rh.degree`` equal to ``lh.degree``; the octave offset is a rendering
    concern.  If already a Bishape, no-op (annotation only).
    """
    if bar.voicing is None or isinstance(bar.voicing, Bishape):
        return _annotate(bar, 'Stacking')
    if not isinstance(bar.voicing, Shape):
        return _annotate(bar, 'Stacking')
    bish = Bishape(lh=bar.voicing, rh=bar.voicing)
    return replace(bar, voicing=bish, technique='Stacking')


# ──────────────────────────────────────────────────────────────────────────
# 4. Pedal
# ──────────────────────────────────────────────────────────────────────────

def pedal(bar: Bar, *, degree: Optional[int] = None,
          ctx: Optional[dict] = None) -> Bar:
    """Pedal-tone voicing.

    MVP: annotate with ``technique='Pedal'`` and stash the requested degree as
    the voicing anchor if a Shape is already present.  Pedal changes in the
    grammar (``PedalChange``) are about pedal-harp setup; they aren't a
    voicing-level bar transform, so we don't emit them here.
    """
    # MVP: refine with pedagogy
    if degree is not None and isinstance(bar.voicing, Shape):
        new_voicing = replace(bar.voicing, degree=degree)  # type: ignore[arg-type]
        return replace(bar, voicing=new_voicing, technique='Pedal')
    return _annotate(bar, 'Pedal')


# ──────────────────────────────────────────────────────────────────────────
# 5. Voice leading
# ──────────────────────────────────────────────────────────────────────────

def _shape_distance(a: Shape, b: Shape) -> int:
    """Sum of absolute interval differences; degree delta counted once.

    Minimisation proxy — not a semitone count, but gives a monotone ordering
    over voicings anchored to the same key.
    """
    dd = abs(a.degree - b.degree)
    ia = a.intervals
    ib = b.intervals
    # Pad shorter interval tuple so comparison is well-defined.
    n = max(len(ia), len(ib))
    ia += (0,) * (n - len(ia))
    ib += (0,) * (n - len(ib))
    return dd + sum(abs(x - y) for x, y in zip(ia, ib))


def voice_leading(bars: tuple[Bar, ...], *, i: int,
                  ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Pick the voicing for ``bars[i]`` that minimises total interval movement
    from ``bars[i-1].voicing``.

    ``ctx['candidates']`` is an iterable of candidate ``Shape``/``Bishape``
    values for bar ``i``.  If no candidates or no previous voicing, no-op
    (annotation only).
    """
    if i < 1 or i >= len(bars):
        return bars
    candidates = (ctx or {}).get('candidates')
    prev_voicing = bars[i - 1].voicing
    if not candidates or prev_voicing is None:
        new_bar = replace(bars[i], technique='Voice leading')
        return bars[:i] + (new_bar,) + bars[i + 1:]

    # Score candidates by distance from previous voicing.
    def score(cand):
        p = prev_voicing.lh if isinstance(prev_voicing, Bishape) else prev_voicing
        c = cand.lh if isinstance(cand, Bishape) else cand
        if not isinstance(p, Shape) or not isinstance(c, Shape):
            return 10 ** 9
        return _shape_distance(p, c)

    best = min(candidates, key=score)
    new_bar = replace(bars[i], voicing=best, technique='Voice leading')
    return bars[:i] + (new_bar,) + bars[i + 1:]


# ──────────────────────────────────────────────────────────────────────────
# 6. Open/closed spread
# ──────────────────────────────────────────────────────────────────────────

def _spread_intervals(intervals: tuple[int, ...], direction: str) -> tuple[int, ...]:
    """Widen (open) or narrow (closed) each interval within [2..4]."""
    if direction == 'open':
        return tuple(min(4, i + 1) if i < 4 else i for i in intervals)
    if direction == 'closed':
        return tuple(max(2, i - 1) if i > 2 else i for i in intervals)
    return intervals


def open_closed_spread(bar: Bar, *, spread: str = 'open',
                       ctx: Optional[dict] = None) -> Bar:
    """Re-space ``bar.voicing``: ``'open'`` widens 2→3→4; ``'closed'`` collapses."""
    if bar.voicing is None:
        return _annotate(bar, 'Open/closed spread')
    if isinstance(bar.voicing, Shape):
        new_voicing = replace(
            bar.voicing,
            intervals=_spread_intervals(bar.voicing.intervals, spread),
        )
    elif isinstance(bar.voicing, Bishape):
        new_voicing = Bishape(
            lh=replace(bar.voicing.lh,
                       intervals=_spread_intervals(bar.voicing.lh.intervals, spread)),
            rh=replace(bar.voicing.rh,
                       intervals=_spread_intervals(bar.voicing.rh.intervals, spread)),
        )
    else:
        return _annotate(bar, 'Open/closed spread')
    return replace(bar, voicing=new_voicing, technique='Open/closed spread')
