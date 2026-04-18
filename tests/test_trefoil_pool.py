"""Tests for trefoil/pool.py — load, index, degree-prefixed ipool numbering."""
from __future__ import annotations

from collections import Counter

import pytest

from grammar.types import Bishape, Roman, Shape
from trefoil.pool import Pool, PoolEntry, load_pool


@pytest.fixture(scope='module')
def pool() -> Pool:
    return load_pool()


def test_size_is_118(pool: Pool):
    assert len(pool) == 118


def test_ipool_numbering_is_degree_prefixed(pool: Pool):
    """Every ipool is '{degree}{rank:02d}' with degree ∈ 1..7."""
    for e in pool.entries:
        assert len(e.ipool) == 3
        assert e.ipool.isdigit()
        assert e.ipool[0] in '1234567'
        # rank >= 01
        assert int(e.ipool[1:]) >= 1


def test_ipool_counts_per_degree(pool: Pool):
    """Degree buckets match the expected distribution (21/19/13/21/21/11/12)."""
    counts = Counter(e.ipool[0] for e in pool.entries)
    assert counts == {
        '1': 21, '2': 19, '3': 13, '4': 21, '5': 21, '6': 11, '7': 12,
    }


def test_ipool_ranks_are_contiguous(pool: Pool):
    """Within each degree, ranks run 01..N with no gaps."""
    per_degree: dict[str, list[int]] = {d: [] for d in '1234567'}
    for e in pool.entries:
        per_degree[e.ipool[0]].append(int(e.ipool[1:]))
    for d, ranks in per_degree.items():
        assert ranks == list(range(1, len(ranks) + 1)), \
            f"degree {d} has non-contiguous ranks {ranks}"


def test_get_by_ipool(pool: Pool):
    e = pool.get('101')
    assert e.ipool == '101'
    assert e.lh_chord.numeral.startswith('I')  # I-rooted
    e2 = pool.get('701')
    assert e2.ipool == '701'


def test_get_zero_pads(pool: Pool):
    # '1' -> '001' is rejected; '101' is the first I-rooted entry.
    with pytest.raises(KeyError):
        pool.get('1')
    assert pool.get('101').ipool == '101'


def test_get_rejects_unknown(pool: Pool):
    with pytest.raises(KeyError):
        pool.get('999')
    with pytest.raises(KeyError):
        pool.get('801')   # no degree 8


def test_entries_are_bishapes(pool: Pool):
    for e in pool.entries:
        assert isinstance(e, PoolEntry)
        assert isinstance(e.bishape, Bishape)
        assert isinstance(e.bishape.lh, Shape)
        assert isinstance(e.bishape.rh, Shape)
        assert isinstance(e.lh_chord, Roman)
        assert isinstance(e.rh_chord, Roman)


def test_all_voicings_of_tonic(pool: Pool):
    matches = pool.all_voicings_of('I')
    assert len(matches) >= 3
    for e in matches:
        assert 'I' in (e.lh_chord.numeral, e.rh_chord.numeral)


def test_all_voicings_of_accepts_roman_dataclass(pool: Pool):
    target = Roman(numeral='vi', quality=None, inversion=None)
    matches = pool.all_voicings_of(target)
    assert len(matches) >= 1


def test_ipool_of_round_trips(pool: Pool):
    sample = pool.get('101')
    assert pool.ipool_of(sample.bishape) == '101'
    sample = pool.get('410')
    assert pool.ipool_of(sample.bishape) == '410'


def test_ipool_of_unknown_returns_none(pool: Pool):
    unknown = Bishape(lh=Shape(degree=1, intervals=(2, 2)),   # type: ignore[arg-type]
                      rh=Shape(degree=9, intervals=(2, 2)))   # type: ignore[arg-type]
    assert pool.ipool_of(unknown) is None


def test_first_entries_per_degree_are_paths(pool: Pool):
    """The rank-01 entry in each degree bucket comes from the trefoil paths
    (TeX ordering lists the path voicings first within each degree)."""
    for d in '1234567':
        first = pool.get(f'{d}01')
        assert first.source == 'paths', \
            f"degree {d} rank 01 should be a path entry, got {first.source}"


def test_pool_equals_paths_plus_reserve(pool: Pool):
    """pool = paths ∪ reserve: every entry is exactly one of the two, totalling 118."""
    path_count    = sum(1 for e in pool.entries if e.source == 'paths')
    reserve_count = sum(1 for e in pool.entries if e.source == 'reserve')
    assert path_count == 42
    assert reserve_count == 76
    assert path_count + reserve_count == len(pool) == 118


def test_meta_carries_cycle_fields_for_path_entries(pool: Pool):
    jazz = pool.get('101')   # I-rooted rank-01 is a path entry
    assert jazz.source == 'paths'
    assert 'cycle' in jazz.meta
    assert 'cw_label' in jazz.meta
    assert 'ccw_label' in jazz.meta


def test_meta_carries_mood_for_reserve_entries(pool: Pool):
    reserve = next(e for e in pool.entries if e.source == 'reserve')
    assert 'mood' in reserve.meta


def test_figure_strings_round_trip(pool: Pool):
    from grammar.parse import parse_figure
    for e in pool.entries:
        lh_anchor, lh_ivals = parse_figure(e.lh_figure)
        assert e.bishape.lh.degree == lh_anchor
        assert tuple(e.bishape.lh.intervals) == lh_ivals
