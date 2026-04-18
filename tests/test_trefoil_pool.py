"""Tests for trefoil/pool.py — load, index, canonical 001..118 numbering."""
from __future__ import annotations

import pytest

from grammar.types import Bishape, Roman, Shape
from trefoil.pool import Pool, PoolEntry, load_pool


@pytest.fixture(scope='module')
def pool() -> Pool:
    return load_pool()


def test_size_is_118(pool: Pool):
    assert len(pool) == 118


def test_ipool_numbering_is_canonical(pool: Pool):
    # jazz (042) then stacked (076) in document order.
    ipools = [e.ipool for e in pool]
    assert ipools[0] == '001'
    assert ipools[41] == '042'
    assert ipools[42] == '043'
    assert ipools[-1] == '118'
    assert all(e.source == 'jazz_progressions' for e in pool.entries[:42])
    assert all(e.source == 'stacked_chords' for e in pool.entries[42:])


def test_get_by_ipool(pool: Pool):
    e = pool.get('001')
    assert e.ipool == '001'
    assert e.source == 'jazz_progressions'
    e2 = pool.get('118')
    assert e2.source == 'stacked_chords'


def test_get_zero_pads(pool: Pool):
    # Lenient: '1' and '01' both normalize to '001'.
    assert pool.get('1').ipool == '001'
    assert pool.get('42').ipool == '042'


def test_get_rejects_unknown(pool: Pool):
    with pytest.raises(KeyError):
        pool.get('999')


def test_entries_are_bishapes(pool: Pool):
    for e in pool.entries:
        assert isinstance(e, PoolEntry)
        assert isinstance(e.bishape, Bishape)
        assert isinstance(e.bishape.lh, Shape)
        assert isinstance(e.bishape.rh, Shape)
        assert isinstance(e.lh_chord, Roman)
        assert isinstance(e.rh_chord, Roman)


def test_all_voicings_of_tonic(pool: Pool):
    # I appears as LH in many jazz entries and as either hand in stacked.
    matches = pool.all_voicings_of('I')
    assert len(matches) >= 3
    for e in matches:
        assert 'I' in (e.lh_chord.numeral, e.rh_chord.numeral)


def test_all_voicings_of_accepts_roman_dataclass(pool: Pool):
    target = Roman(numeral='vi', quality=None, inversion=None)
    matches = pool.all_voicings_of(target)
    assert len(matches) >= 1


def test_ipool_of_round_trips(pool: Pool):
    # Pick one entry and reverse-lookup.
    sample = pool.get('001')
    assert pool.ipool_of(sample.bishape) == '001'
    sample = pool.get('050')
    assert pool.ipool_of(sample.bishape) == '050'


def test_ipool_of_unknown_returns_none(pool: Pool):
    unknown = Bishape(lh=Shape(degree=1, intervals=(2, 2)),   # type: ignore[arg-type]
                      rh=Shape(degree=9, intervals=(2, 2)))   # type: ignore[arg-type]
    assert pool.ipool_of(unknown) is None


def test_meta_carries_jazz_fields(pool: Pool):
    jazz = pool.get('001')
    assert 'cycle' in jazz.meta
    assert 'cw_label' in jazz.meta
    assert 'ccw_label' in jazz.meta


def test_meta_carries_stacked_mood(pool: Pool):
    stacked = pool.get('043')
    assert 'mood' in stacked.meta


def test_figure_strings_round_trip(pool: Pool):
    # Every entry's figure strings match what parse_figure produced.
    from grammar.parse import parse_figure
    for e in pool.entries:
        lh_anchor, lh_ivals = parse_figure(e.lh_figure)
        assert e.bishape.lh.degree == lh_anchor
        assert tuple(e.bishape.lh.intervals) == lh_ivals
