"""Guard that constants in grammar.constants still match the curated pool."""
from __future__ import annotations

from grammar.constants import (
    HARP_STRINGS,
    MAX_GAP,
    MIN_GAP,
    PATHS_SIZE,
    PATTERN_COUNT,
    POOL_SIZE,
    PREFERRED_MAX_GAP,
    RESERVE_SIZE,
    is_playable_gap,
    is_preferred_gap,
)
from trefoil.pool import load_pool


def _positions(fig: str) -> list[int]:
    """Absolute string positions produced by a figure."""
    vals = [int(c) if c.isdigit() else ord(c) - ord('A') + 10 for c in fig]
    cur = vals[0]
    out = [cur]
    for iv in vals[1:]:
        cur += iv - 1
        out.append(cur)
    return out


def _gap(lh_fig: str, rh_fig: str) -> int:
    return min(_positions(rh_fig)) - max(_positions(lh_fig)) - 1


def test_pool_size():
    pool = load_pool()
    assert len(pool) == POOL_SIZE


def test_paths_reserve_counts():
    pool = load_pool()
    paths    = sum(1 for e in pool.entries if e.source == 'paths')
    reserve  = sum(1 for e in pool.entries if e.source == 'reserve')
    assert paths == PATHS_SIZE
    assert reserve == RESERVE_SIZE
    assert paths + reserve == POOL_SIZE


def test_every_fraction_has_playable_gap():
    pool = load_pool()
    for e in pool.entries:
        g = _gap(e.lh_figure, e.rh_figure)
        assert g >= MIN_GAP, \
            f'ipool {e.ipool}: gap={g} violates MIN_GAP={MIN_GAP}'


def test_max_gap_matches_pool():
    pool = load_pool()
    observed = max(_gap(e.lh_figure, e.rh_figure) for e in pool.entries)
    assert observed == MAX_GAP, \
        f'pool max gap is now {observed}; update MAX_GAP in grammar/constants.py'


def test_preferred_threshold_covers_majority():
    pool = load_pool()
    preferred = sum(1 for e in pool.entries
                    if is_preferred_gap(_gap(e.lh_figure, e.rh_figure)))
    # currently 105/118 at gap<=3 — if this drops below 80% the pool has drifted.
    assert preferred / len(pool) >= 0.80


def test_hard_bounds_monotonic():
    assert MIN_GAP <= PREFERRED_MAX_GAP < MAX_GAP
    assert PREFERRED_MAX_GAP < HARP_STRINGS
    assert PATTERN_COUNT == 14


def test_is_playable_gap():
    assert not is_playable_gap(-1)
    assert is_playable_gap(0)
    assert is_playable_gap(MAX_GAP)


def test_is_preferred_gap():
    assert is_preferred_gap(0)
    assert is_preferred_gap(PREFERRED_MAX_GAP)
    assert not is_preferred_gap(PREFERRED_MAX_GAP + 1)
    assert not is_preferred_gap(-1)
