"""Tests for mapper/harp_mapper.py — the grammar-native 118-fraction picker."""
from __future__ import annotations

import pytest

from grammar.types import Bishape, Roman, Shape
from mapper.harp_mapper import (
    Pick,
    cycle_of_transition,
    infer_contour,
    pick_fraction,
    pick_transition,
    pick_with_substitution,
    translate_minor_to_major,
    translate_minor_V_with_strategy,
)
from trefoil.pool import Pool, load_pool


@pytest.fixture(scope='module')
def pool() -> Pool:
    return load_pool()


# ──────────────────────────────────────────────────────────────────────────
# pick_fraction
# ──────────────────────────────────────────────────────────────────────────

def test_pick_fraction_v7_returns_picks(pool: Pool):
    picks = pick_fraction(pool, 'V7', 'D', 'G4')
    assert picks, 'expected at least one pick for V7 / D / G4'
    assert all(isinstance(p, Pick) for p in picks)
    assert all(isinstance(p.bishape, Bishape) for p in picks)


def test_pick_fraction_v7_first_pick_is_v_degree(pool: Pool):
    picks = pick_fraction(pool, 'V7', 'D', 'G4')
    top = picks[0]
    # LH chord must be on degree 5. Either a clean ``V``/``V7`` Roman or a
    # concatenated pool form like ``V7iii`` whose numeral starts at V.
    assert top.lh_chord.numeral.startswith('V')
    # If the top entry is a clean ``V7``, quality is '7'; if it's the entry
    # labelled e.g. ``V7iii``, the full roman string still contains '7'.
    full_lh = (top.lh_chord.numeral or '') + (top.lh_chord.quality or '')
    assert '7' in full_lh or top.lh_chord.quality == '7' or top.lh_chord.quality is None \
        , 'expected V or V7 LH (quality absent is acceptable if V triad)'


def test_pick_fraction_respects_top_n(pool: Pool):
    picks = pick_fraction(pool, 'V7', 'D', 'G4', top_n=5)
    assert len(picks) <= 5


def test_pick_fraction_unknown_rn_returns_empty(pool: Pool):
    assert pick_fraction(pool, 'ZZZ', 'D') == []


def test_pick_fraction_minor_translates(pool: Pool):
    # 'i' in E minor is relative major's 'vi' in G major. We should still find
    # some entry (the pool has vi voicings).
    picks = pick_fraction(pool, 'i', 'E', mode='minor')
    assert picks, 'expected at least one pick for i in E minor'


def test_pick_fraction_carries_ipool_and_source(pool: Pool):
    picks = pick_fraction(pool, 'I', 'C')
    assert picks
    for p in picks:
        assert p.ipool in {e.ipool for e in pool.entries}
        assert p.source in ('paths', 'reserve')


# ──────────────────────────────────────────────────────────────────────────
# pick_transition
# ──────────────────────────────────────────────────────────────────────────

def test_pick_transition_v_to_i_is_fourths_cycle(pool: Pool):
    picks = pick_transition(pool, 'V', 'I', 'C')
    assert picks, 'V → I is a 4ths cycle edge — expected at least one pick'
    # All transition picks come from the trefoil paths with cycle == '4ths'.
    for p in picks:
        assert p.source == 'paths'
        assert p.meta.get('cycle') == '4ths'


def test_pick_transition_non_cycle_falls_back_to_rn_to(pool: Pool):
    # I → I is not a cycle edge; pick_transition should fall back to pick_fraction(rn_to='I').
    picks = pick_transition(pool, 'I', 'I', 'C')
    assert picks
    # Fallback path returns Picks matching I on the LH (or RH for rh-root match).
    numerals = {p.lh_chord.numeral for p in picks} | {p.rh_chord.numeral for p in picks}
    assert any(n.startswith('I') for n in numerals)


def test_pick_transition_contour_boosts_matching_direction(pool: Pool):
    # V → I is a CW 4ths edge; 'ascending' contour aligns with CW and adds +6.
    neutral = pick_transition(pool, 'V', 'I', 'C', contour=None)
    asc = pick_transition(pool, 'V', 'I', 'C', contour='ascending')
    assert neutral and asc
    # All edges in this test pair are CW (direction is set by scale-degree delta).
    assert all(p.meta.get('direction') == 'CW' for p in neutral)
    assert all(p.meta.get('direction') == 'CW' for p in asc)
    # Ascending contour should push top score up by 6.
    assert asc[0].score >= neutral[0].score


def test_pick_transition_ccw_edge_v_to_ii(pool: Pool):
    # ii → V is a CW 4ths edge, so V → ii is CCW.
    picks = pick_transition(pool, 'V', 'ii', 'C')
    assert picks
    assert all(p.meta.get('direction') == 'CCW' for p in picks)


# ──────────────────────────────────────────────────────────────────────────
# pick_with_substitution
# ──────────────────────────────────────────────────────────────────────────

def test_pick_with_substitution_bVII_backdoor(pool: Pool):
    # Minor V preceded by iv → bVII_backdoor strategy.
    picks = pick_with_substitution(pool, 'V', 'E', mode='minor', prev_rn='iv')
    assert picks
    for p in picks:
        assert p.harmonic_substitution == 'bVII_backdoor'
        assert p.requested_rn == 'V'


def test_pick_with_substitution_modal_v_default(pool: Pool):
    # Minor V with no preceding iv, no fermata-cadence, default to modal_v.
    picks = pick_with_substitution(pool, 'V', 'E', mode='minor')
    assert picks
    for p in picks:
        assert p.harmonic_substitution == 'modal_v'
        assert p.requested_rn == 'V'


def test_pick_with_substitution_III_deceptive_on_final_fermata(pool: Pool):
    picks = pick_with_substitution(pool, 'V', 'E', mode='minor',
                                   is_final_cadence=True, ending_marker='fermata')
    assert picks
    for p in picks:
        assert p.harmonic_substitution == 'III_deceptive'
        assert p.requested_rn == 'V'


def test_pick_with_substitution_major_key_no_substitution(pool: Pool):
    picks = pick_with_substitution(pool, 'V', 'C', mode='major', next_rn='I')
    assert picks
    for p in picks:
        assert p.harmonic_substitution is None
        assert p.requested_rn == 'V'


# ──────────────────────────────────────────────────────────────────────────
# cycle_of_transition
# ──────────────────────────────────────────────────────────────────────────

def test_cycle_of_transition_fifths_cw():
    # V → I is a CW 4ths edge (cycle of fifths order: I IV vii iii vi ii V I).
    assert cycle_of_transition(5, 1) == ('4ths', 'CW')


def test_cycle_of_transition_stepwise_cw():
    assert cycle_of_transition(1, 2) == ('2nds', 'CW')


def test_cycle_of_transition_thirds_cw():
    assert cycle_of_transition(1, 3) == ('3rds', 'CW')


def test_cycle_of_transition_non_cycle_returns_none():
    # 1 → 1 is not a cycle edge.
    assert cycle_of_transition(1, 1) == (None, None)


def test_cycle_of_transition_none_inputs():
    assert cycle_of_transition(None, 1) == (None, None)
    assert cycle_of_transition(1, None) == (None, None)


# ──────────────────────────────────────────────────────────────────────────
# infer_contour
# ──────────────────────────────────────────────────────────────────────────

def test_infer_contour_ascending_from_next():
    assert infer_contour(None, 'C4', 'E4') == 'ascending'


def test_infer_contour_descending_from_next():
    assert infer_contour(None, 'G4', 'C4') == 'descending'


def test_infer_contour_fallback_to_prev():
    assert infer_contour('C4', 'E4', None) == 'ascending'
    assert infer_contour('G4', 'C4', None) == 'descending'


def test_infer_contour_static_when_no_direction():
    assert infer_contour(None, 'C4', None) == 'static'
    assert infer_contour(None, None, None) == 'static'


# ──────────────────────────────────────────────────────────────────────────
# translation helpers
# ──────────────────────────────────────────────────────────────────────────

def test_translate_minor_to_major_i_to_vi():
    assert translate_minor_to_major('i') == 'vi'


def test_translate_minor_to_major_iv_to_ii():
    assert translate_minor_to_major('iv') == 'ii'


def test_translate_minor_V_with_strategy_table():
    assert translate_minor_V_with_strategy('modal_v') == 'iii7'
    assert translate_minor_V_with_strategy('bVII_backdoor') == 'V'
    assert translate_minor_V_with_strategy('III_deceptive') == 'I'
    assert translate_minor_V_with_strategy('pedal_i') == 'vi'
