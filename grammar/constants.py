"""System-wide constants for the HarpHymnal pool and grammar.

Single source of truth for magic numbers that appear across the codebase.
Values reflect the *current* curated pool and the physical constraints of
a 34-string lever harp with a 4-fingers-per-hand playing technique.

If the pool vocabulary is ever expanded or re-curated, adjust these values
and run `tests/test_constants.py` (it re-derives them from the pool and
catches drift).
"""
from __future__ import annotations


# ──────────────────────────── Pool sizes ─────────────────────────────

POOL_SIZE    = 118     # total fractions in the curated vocabulary
PATHS_SIZE   = 42      # fractions that walk the six trefoil cycles
RESERVE_SIZE = 76      # coloristic fractions held for substitution (POOL_SIZE - PATHS_SIZE)

assert PATHS_SIZE + RESERVE_SIZE == POOL_SIZE, \
    "paths + reserve must equal the pool size"


# ──────────────────────── Harp string geometry ───────────────────────

HARP_STRINGS = 15      # usable figure-alphabet range: positions 1..F (hex) = 1..15
                       # covers two diatonic octaves above the low tonic.

PATTERN_COUNT = 14     # distinct hand patterns in the HarpChordSystem
                       # (24, 33, 34, 42, 43, 44, 233, 323, 332, 333, 334, 433, 434, 444)

DIATONIC_DEGREES = 7   # scale degrees per octave (I..vii°)


# ───────────────────────────── Gap bounds ────────────────────────────

# "gap" = number of strings between the top of LH and the bottom of RH.
# Formally: gap = min(positions(rh)) - max(positions(lh)) - 1
#   gap == 0  → LH top and RH bottom are on adjacent strings (tightest legal coupling).
#   gap  < 0  → same-string overlap. UNPLAYABLE on harp; the LH and RH can share
#               a pitch class an octave apart but never pluck the same string at
#               the same time.  Any bishape with gap < 0 is rejected.
#   gap == N  → LH and RH are N strings apart.
#
# Values derived empirically from the curated pool; update if curation changes.

MIN_GAP = 0            # hard lower bound: gap must be >= 0 (no same-string collision)
MAX_GAP = 6            # hard upper bound: largest gap in the curated pool
                       # (both gap-6 entries are wide 4ths-cycle voicings:
                       #  iii/vii° and ii/vi, each spanning a full octave).

PREFERRED_MAX_GAP = 3  # soft bound: gap < 4 is preferred for harmonic cohesion.
                       # 105 of 118 pool fractions (89%) satisfy gap <= PREFERRED_MAX_GAP.


def is_playable_gap(gap: int) -> bool:
    """Reject same-string overlap."""
    return gap >= MIN_GAP


def is_preferred_gap(gap: int) -> bool:
    """Within the preferred harmonic-cohesion band."""
    return MIN_GAP <= gap <= PREFERRED_MAX_GAP
