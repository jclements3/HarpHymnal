"""Approach techniques (5 functions, multi-bar).

Each function inserts or modifies a bar that *approaches* the next chord.
Signature: ``fn(bars, *, i, ctx=None) → tuple[Bar, ...]`` — ``i`` is the index
of the bar to transform; ``bars[i+1]`` is the landing bar.  No I/O, no
mutation — new tuples and new ``Bar`` objects only.

All approach chords stay **strictly diatonic** in the current key.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional

from grammar.types import Bar, Roman

from techniques.substitution import _MAJOR_DEGREES, _degree_index, _as_roman


def _set_chord(bar: Bar, numeral: str, *, quality: Optional[str] = None,
               technique: Optional[str] = None) -> Bar:
    roman = _as_roman(bar.chord)
    if roman is None:
        # For a bichord we only annotate (MVP): technique labels still flow.
        return replace(bar, technique=technique)
    new_chord = replace(roman, numeral=numeral, quality=quality, inversion=None)
    return replace(bar, chord=new_chord, technique=technique)


def _target_numeral(bars: tuple[Bar, ...], i: int) -> Optional[str]:
    if i + 1 >= len(bars):
        return None
    nxt = _as_roman(bars[i + 1].chord)
    return nxt.numeral if nxt is not None else None


def _replace_at(bars: tuple[Bar, ...], i: int, new_bar: Bar) -> tuple[Bar, ...]:
    return bars[:i] + (new_bar,) + bars[i + 1:]


# ──────────────────────────────────────────────────────────────────────────
# 1. Step approach (diatonic 2nd below-or-above target root)
# ──────────────────────────────────────────────────────────────────────────

def step_approach(bars: tuple[Bar, ...], *, i: int,
                  ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Make ``bars[i]`` a diatonic step away from ``bars[i+1]``'s chord root.

    Default direction is *below* (down a 2nd).  ``ctx={'direction': 'above'}``
    flips to a 2nd above.  Annotates ``technique='Step approach'``.
    """
    target = _target_numeral(bars, i)
    if target is None or _degree_index(target) is None:
        return bars

    direction = (ctx or {}).get('direction', 'below')
    step = -1 if direction == 'below' else +1
    new_numeral = _MAJOR_DEGREES[(_degree_index(target) + step) % 7]
    new_bar = _set_chord(bars[i], new_numeral, technique='Step approach')
    return _replace_at(bars, i, new_bar)


# ──────────────────────────────────────────────────────────────────────────
# 2. Third approach (diatonic 3rd below-or-above target root)
# ──────────────────────────────────────────────────────────────────────────

def third_approach(bars: tuple[Bar, ...], *, i: int,
                   ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Make ``bars[i]`` a diatonic 3rd from ``bars[i+1]``'s chord root.

    Default direction is *below*.  ``ctx={'direction': 'above'}`` flips up.
    """
    target = _target_numeral(bars, i)
    if target is None or _degree_index(target) is None:
        return bars

    direction = (ctx or {}).get('direction', 'below')
    step = -2 if direction == 'below' else +2
    new_numeral = _MAJOR_DEGREES[(_degree_index(target) + step) % 7]
    new_bar = _set_chord(bars[i], new_numeral, technique='Third approach')
    return _replace_at(bars, i, new_bar)


# ──────────────────────────────────────────────────────────────────────────
# 3. Dominant approach (diatonic V of the *global* key — not secondary)
# ──────────────────────────────────────────────────────────────────────────

def dominant_approach(bars: tuple[Bar, ...], *, i: int,
                      ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Make ``bars[i]`` the global key's V (or V7 if ``ctx['seventh']``).

    Strictly diatonic — this is the V of the key, never a secondary dominant.
    """
    if i >= len(bars):
        return bars
    quality = '7' if (ctx or {}).get('seventh') else None
    new_bar = _set_chord(bars[i], 'V', quality=quality,
                         technique='Dominant approach')
    return _replace_at(bars, i, new_bar)


# ──────────────────────────────────────────────────────────────────────────
# 4. Suspension approach (replace quality with s4)
# ──────────────────────────────────────────────────────────────────────────

def suspension_approach(bars: tuple[Bar, ...], *, i: int,
                        ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Replace ``bars[i]``'s chord quality with ``s4`` (sus4)."""
    if i >= len(bars):
        return bars
    roman = _as_roman(bars[i].chord)
    if roman is None:
        new_bar = replace(bars[i], technique='Suspension approach')
        return _replace_at(bars, i, new_bar)
    new_chord = replace(roman, quality='s4')
    new_bar = replace(bars[i], chord=new_chord, technique='Suspension approach')
    return _replace_at(bars, i, new_bar)


# ──────────────────────────────────────────────────────────────────────────
# 5. Double approach (step on bars[i-1], dominant on bars[i])
# ──────────────────────────────────────────────────────────────────────────

def double_approach(bars: tuple[Bar, ...], *, i: int,
                    ctx: Optional[dict] = None) -> tuple[Bar, ...]:
    """Combine ``step_approach`` on ``bars[i-1]`` and ``dominant_approach`` on
    ``bars[i]`` for a 2-bar approach into ``bars[i+1]``.

    No-op at the left edge (``i < 1``) or right edge (``i+1 >= len(bars)``).
    """
    if i < 1 or i + 1 >= len(bars):
        return bars
    # First apply step_approach to the bar *before* i, targeting bars[i].
    intermediate = step_approach(bars, i=i - 1, ctx=ctx)
    # Then dominant_approach on bar i itself.
    result = dominant_approach(intermediate, i=i, ctx=ctx)
    # Mark both bars with the composite technique name.
    new_prev = replace(result[i - 1], technique='Double approach')
    new_cur = replace(result[i], technique='Double approach')
    result = result[:i - 1] + (new_prev, new_cur) + result[i + 1:]
    return result
