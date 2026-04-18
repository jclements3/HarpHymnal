"""Substitution techniques (5 functions, single-bar).

Each function replaces ``bar.chord`` with a related diatonic chord, preserving
``bar.melody`` exactly.  All functions are pure: they return a new ``Bar`` built
with :func:`dataclasses.replace` and never mutate the input.

Techniques:
    - third_sub          — swap with diatonic chord a 3rd away
    - quality_sub        — keep root, change quality to other diatonic option
    - modal_reframing    — reinterpret numeral in a different mode's tonic
    - deceptive_sub      — V(7) → vi when ctx['resolves_to'] == 'I'
    - common_tone_pivot  — pick a diatonic neighbor sharing ≥2 pitches with
                           both current chord and ctx['next_chord']

Diatonicism: every result stays inside the 7-note scale of the current key.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional

from grammar.types import Bar, Chord, Roman


# Ionian-labelled diatonic ladder (the 118 vocabulary is Ionian-labelled; minor
# keys are reframed to relative major upstream by the mapper).
_MAJOR_DEGREES: tuple[str, ...] = ('I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii○')
_MINOR_DEGREES: tuple[str, ...] = ('i', 'ii○', 'III', 'iv', 'v', 'VI', 'VII')

# Relative-mode pivots: degree index in Ionian → degree index in Aeolian that
# shares the same diatonic triad.  E.g. major I ≡ minor III (C-major I = C E G,
# C-minor III = C E♭ G — different pitches, but the *same degree class* when
# the tonic centre shifts).  The modal_reframing technique uses this table.
_MAJOR_TO_MINOR_NUMERAL = {
    'I':   'III',
    'ii':  'iv',
    'iii': 'v',
    'IV':  'VI',
    'V':   'VII',
    'vi':  'i',
    'vii○': 'ii○',
}
_MINOR_TO_MAJOR_NUMERAL = {v: k for k, v in _MAJOR_TO_MINOR_NUMERAL.items()}


def _degree_index(numeral: str) -> Optional[int]:
    """Return 0..6 position of a numeral within its diatonic ladder, else None."""
    if numeral in _MAJOR_DEGREES:
        return _MAJOR_DEGREES.index(numeral)
    if numeral in _MINOR_DEGREES:
        return _MINOR_DEGREES.index(numeral)
    return None


def _ladder_for(numeral: str) -> Optional[tuple[str, ...]]:
    if numeral in _MAJOR_DEGREES:
        return _MAJOR_DEGREES
    if numeral in _MINOR_DEGREES:
        return _MINOR_DEGREES
    return None


def _annotate(bar: Bar, name: str) -> Bar:
    return replace(bar, technique=name)


def _as_roman(chord: Chord) -> Optional[Roman]:
    """Return the chord as a Roman, or None if it's a Bichord (not supported here)."""
    return chord if isinstance(chord, Roman) else None


# ──────────────────────────────────────────────────────────────────────────
# 1. Third substitution
# ──────────────────────────────────────────────────────────────────────────

def third_sub(bar: Bar, *, ctx: Optional[dict] = None) -> Bar:
    """Swap ``bar.chord`` with the diatonic chord a third away.

    Down-a-3rd is the default (I → vi, IV → ii, V → iii).  ``ctx={'direction':
    'up'}`` flips to up-a-3rd (I → iii, etc.).  No-op for bichords.  The result
    is annotated ``technique='Third sub'``.
    """
    roman = _as_roman(bar.chord)
    if roman is None:
        return _annotate(bar, 'Third sub')

    ladder = _ladder_for(roman.numeral)
    idx = _degree_index(roman.numeral)
    if ladder is None or idx is None:
        return _annotate(bar, 'Third sub')

    direction = (ctx or {}).get('direction', 'down')
    step = -2 if direction == 'down' else +2
    new_numeral = ladder[(idx + step) % 7]
    new_chord = replace(roman, numeral=new_numeral, quality=None, inversion=None)
    return replace(bar, chord=new_chord, technique='Third sub')


# ──────────────────────────────────────────────────────────────────────────
# 2. Quality substitution
# ──────────────────────────────────────────────────────────────────────────

# Diatonic quality pairs: at the same root, which other quality is idiomatic
# within the 118-chord strictly-diatonic vocabulary.
_QUALITY_FLIP_MAJOR = {
    'I':   (None, 'Δ7'),        # I ↔ IΔ7
    'ii':  (None, '7'),         # ii ↔ ii7
    'iii': (None, '7'),         # iii ↔ iii7
    'IV':  (None, 'Δ7'),        # IV ↔ IVΔ7
    'V':   (None, '7'),         # V ↔ V7
    'vi':  (None, '7'),         # vi ↔ vi7
    'vii○': (None, 'ø7'),       # vii○ ↔ viiø7 (half-dim is diatonic)
}


def quality_sub(bar: Bar, *, ctx: Optional[dict] = None) -> Bar:
    """Keep the root, flip to the other diatonic quality if one exists.

    Examples: ``V → V7``, ``V7 → V``, ``I → IΔ7``, ``IVΔ7 → IV``.
    No-op (but still annotated) when the chord has no diatonic alternate.
    """
    roman = _as_roman(bar.chord)
    if roman is None:
        return _annotate(bar, 'Quality sub')

    pair = _QUALITY_FLIP_MAJOR.get(roman.numeral)
    if pair is None:
        return _annotate(bar, 'Quality sub')

    a, b = pair
    # Pick the "other" member of the pair.
    new_quality = b if roman.quality == a else a
    if new_quality == roman.quality:
        return _annotate(bar, 'Quality sub')

    new_chord = replace(roman, quality=new_quality)
    return replace(bar, chord=new_chord, technique='Quality sub')


# ──────────────────────────────────────────────────────────────────────────
# 3. Modal reframing
# ──────────────────────────────────────────────────────────────────────────

def modal_reframing(bar: Bar, *, ctx: Optional[dict] = None) -> Bar:
    """Reinterpret the chord in a different mode's tonic centre.

    ``ctx={'target_mode': 'minor'}`` rewrites a major-key numeral to its
    relative-minor numeral (e.g. I → III because the I of C major is the III
    of A minor).  ``target_mode='major'`` does the reverse.
    """
    roman = _as_roman(bar.chord)
    if roman is None:
        return _annotate(bar, 'Modal reframing')

    target = (ctx or {}).get('target_mode', 'minor')
    if target == 'minor':
        new_numeral = _MAJOR_TO_MINOR_NUMERAL.get(roman.numeral)
    elif target == 'major':
        new_numeral = _MINOR_TO_MAJOR_NUMERAL.get(roman.numeral)
    else:
        new_numeral = None

    if new_numeral is None:
        return _annotate(bar, 'Modal reframing')

    new_chord = replace(roman, numeral=new_numeral)
    return replace(bar, chord=new_chord, technique='Modal reframing')


# ──────────────────────────────────────────────────────────────────────────
# 4. Deceptive substitution
# ──────────────────────────────────────────────────────────────────────────

def deceptive_sub(bar: Bar, *, ctx: Optional[dict] = None) -> Bar:
    """V (or V7) → vi when ``ctx={'resolves_to': 'I'}``.

    Creates a deceptive cadence by replacing the dominant with the relative
    minor that would follow it.  No-op for non-dominant chords or when the
    resolution target is missing / not ``I``.
    """
    roman = _as_roman(bar.chord)
    if roman is None:
        return _annotate(bar, 'Deceptive sub')

    resolves_to = (ctx or {}).get('resolves_to')
    if resolves_to != 'I':
        return _annotate(bar, 'Deceptive sub')
    if roman.numeral != 'V':
        return _annotate(bar, 'Deceptive sub')

    new_chord = replace(roman, numeral='vi', quality=None, inversion=None)
    return replace(bar, chord=new_chord, technique='Deceptive sub')


# ──────────────────────────────────────────────────────────────────────────
# 5. Common-tone pivot
# ──────────────────────────────────────────────────────────────────────────

# Diatonic triad pitch-classes in C-major (used for common-tone counting).
# Degree 0..6 → set of (0..6) scale-degree pitch classes.
_TRIAD_PCS = {
    0: frozenset({0, 2, 4}),   # I   = 1 3 5
    1: frozenset({1, 3, 5}),   # ii  = 2 4 6
    2: frozenset({2, 4, 6}),   # iii = 3 5 7
    3: frozenset({3, 5, 0}),   # IV  = 4 6 1
    4: frozenset({4, 6, 1}),   # V   = 5 7 2
    5: frozenset({5, 0, 2}),   # vi  = 6 1 3
    6: frozenset({6, 1, 3}),   # vii°= 7 2 4
}


def _common_tones(a: str, b: str) -> int:
    ia, ib = _degree_index(a), _degree_index(b)
    if ia is None or ib is None:
        return 0
    # Map into major-ladder indices for pitch-class comparison.
    pa = _TRIAD_PCS[ia % 7]
    pb = _TRIAD_PCS[ib % 7]
    return len(pa & pb)


def common_tone_pivot(bar: Bar, *, ctx: Optional[dict] = None) -> Bar:
    """Replace chord with a diatonic neighbor sharing ≥2 pitches with BOTH
    the current chord and ``ctx['next_chord']``.

    ``ctx['next_chord']`` must be a :class:`Roman` for the function to act.
    If no suitable neighbor exists, returns the bar unchanged (annotation only).
    """
    roman = _as_roman(bar.chord)
    if roman is None or ctx is None or 'next_chord' not in ctx:
        return _annotate(bar, 'Common-tone pivot')

    nxt = ctx['next_chord']
    if not isinstance(nxt, Roman):
        return _annotate(bar, 'Common-tone pivot')

    ladder = _ladder_for(roman.numeral) or _MAJOR_DEGREES
    current = roman.numeral
    target = nxt.numeral

    best: Optional[str] = None
    best_score = -1
    for cand in ladder:
        if cand == current or cand == target:
            continue
        score = _common_tones(cand, current) + _common_tones(cand, target)
        # Require ≥ 2 common tones with each side individually.
        if _common_tones(cand, current) < 2 or _common_tones(cand, target) < 2:
            continue
        if score > best_score:
            best = cand
            best_score = score

    if best is None:
        return _annotate(bar, 'Common-tone pivot')

    new_chord = replace(roman, numeral=best, quality=None, inversion=None)
    return replace(bar, chord=new_chord, technique='Common-tone pivot')
