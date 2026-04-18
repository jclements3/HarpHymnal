"""Tests for the 18 technique operators in techniques/*."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from grammar.types import Bar, Bishape, Roman, Shape

from techniques.substitution import (
    third_sub, quality_sub, modal_reframing,
    deceptive_sub, common_tone_pivot,
)
from techniques.approach import (
    step_approach, third_approach, dominant_approach,
    suspension_approach, double_approach,
)
from techniques.voicing import (
    inversion, density, stacking, pedal,
    voice_leading, open_closed_spread,
)
from techniques.placement import anticipation, delay


def _bar(chord: Roman, *, voicing=None) -> Bar:
    return Bar(melody=(), chord=chord, voicing=voicing)


I   = Roman('I')
ii  = Roman('ii')
iii = Roman('iii')
IV  = Roman('IV')
V   = Roman('V')
vi  = Roman('vi')
vii = Roman('vii○')


# ──────────────────────────────────────────────────────────────────────────
# Substitution
# ──────────────────────────────────────────────────────────────────────────

def test_third_sub_default_down():
    out = third_sub(_bar(I))
    assert isinstance(out, Bar)
    assert out.chord.numeral == 'vi'       # I → vi (down a 3rd)
    assert out.technique == 'Third sub'


def test_third_sub_up():
    out = third_sub(_bar(I), ctx={'direction': 'up'})
    assert out.chord.numeral == 'iii'


def test_quality_sub_V_to_V7():
    out = quality_sub(_bar(V))
    assert out.chord.numeral == 'V'
    assert out.chord.quality == '7'
    assert out.technique == 'Quality sub'


def test_quality_sub_V7_to_V():
    out = quality_sub(_bar(Roman('V', '7')))
    assert out.chord.quality is None


def test_modal_reframing_major_to_minor():
    out = modal_reframing(_bar(I), ctx={'target_mode': 'minor'})
    assert out.chord.numeral == 'III'
    assert out.technique == 'Modal reframing'


def test_deceptive_sub_V_to_vi():
    out = deceptive_sub(_bar(V), ctx={'resolves_to': 'I'})
    assert out.chord.numeral == 'vi'
    assert out.technique == 'Deceptive sub'


def test_deceptive_sub_noop_without_ctx():
    # Without resolves_to='I', annotate only — chord unchanged.
    out = deceptive_sub(_bar(V))
    assert out.chord.numeral == 'V'
    assert out.technique == 'Deceptive sub'


def test_common_tone_pivot_with_ctx():
    # I → (pivot) → IV; a neighbor sharing ≥2 tones with each.
    out = common_tone_pivot(_bar(I), ctx={'next_chord': IV})
    assert isinstance(out, Bar)
    assert out.technique == 'Common-tone pivot'
    # vi shares {C,E} with I and {C,A} with IV — wait, vi is {A,C,E};
    # I is {C,E,G}; IV is {F,A,C}.  vi ∩ I = {C,E} (2), vi ∩ IV = {A,C} (2). ✓
    assert out.chord.numeral in {'vi', 'iii'}  # either qualifies


def test_common_tone_pivot_noop_without_ctx():
    out = common_tone_pivot(_bar(I))
    assert out.chord.numeral == 'I'
    assert out.technique == 'Common-tone pivot'


# ──────────────────────────────────────────────────────────────────────────
# Approach
# ──────────────────────────────────────────────────────────────────────────

def test_step_approach_below():
    bars = (_bar(I), _bar(V))
    out = step_approach(bars, i=0)
    assert isinstance(out, tuple)
    assert len(out) == 2
    # Default below V is IV.
    assert out[0].chord.numeral == 'IV'
    assert out[0].technique == 'Step approach'


def test_third_approach_below():
    bars = (_bar(I), _bar(V))
    out = third_approach(bars, i=0)
    # Down a 3rd from V is iii.
    assert out[0].chord.numeral == 'iii'
    assert out[0].technique == 'Third approach'


def test_dominant_approach_makes_V():
    bars = (_bar(I), _bar(I))
    out = dominant_approach(bars, i=0)
    assert out[0].chord.numeral == 'V'
    assert out[0].technique == 'Dominant approach'


def test_dominant_approach_seventh():
    bars = (_bar(I), _bar(I))
    out = dominant_approach(bars, i=0, ctx={'seventh': True})
    assert out[0].chord.numeral == 'V'
    assert out[0].chord.quality == '7'


def test_suspension_approach_adds_s4():
    bars = (_bar(V), _bar(I))
    out = suspension_approach(bars, i=0)
    assert out[0].chord.quality == 's4'
    assert out[0].technique == 'Suspension approach'


def test_double_approach_marks_two_bars():
    bars = (_bar(I), _bar(IV), _bar(I))
    out = double_approach(bars, i=1)
    assert out[0].technique == 'Double approach'
    assert out[1].technique == 'Double approach'


# ──────────────────────────────────────────────────────────────────────────
# Voicing
# ──────────────────────────────────────────────────────────────────────────

def test_inversion_sets_label():
    out = inversion(_bar(I), which='¹')
    assert out.chord.inversion == '¹'
    assert out.technique == 'Inversion'


def test_density_thin_drops_intervals():
    bar = _bar(I, voicing=Shape(degree=1, intervals=(3, 3)))
    out = density(bar, level='thin')
    assert out.voicing == Shape(degree=1, intervals=(3,))
    assert out.technique == 'Density'


def test_density_full_extends_intervals():
    bar = _bar(I, voicing=Shape(degree=1, intervals=(3, 3)))
    out = density(bar, level='full')
    assert len(out.voicing.intervals) == 3
    assert out.technique == 'Density'


def test_stacking_shape_to_bishape():
    bar = _bar(I, voicing=Shape(degree=1, intervals=(3, 3)))
    out = stacking(bar)
    assert isinstance(out.voicing, Bishape)
    assert out.technique == 'Stacking'


def test_pedal_annotates():
    bar = _bar(I, voicing=Shape(degree=1, intervals=(3, 3)))
    out = pedal(bar, degree=5)
    assert out.technique == 'Pedal'
    # degree=5 threads through since a Shape is present.
    assert out.voicing.degree == 5


def test_voice_leading_picks_closest():
    prev_voicing = Shape(degree=1, intervals=(3, 3))
    cand_a = Shape(degree=2, intervals=(3, 3))       # distance 1
    cand_b = Shape(degree=5, intervals=(4, 4))       # distance 4+2
    bars = (
        _bar(I, voicing=prev_voicing),
        _bar(ii),
    )
    out = voice_leading(bars, i=1, ctx={'candidates': [cand_a, cand_b]})
    assert out[1].voicing == cand_a
    assert out[1].technique == 'Voice leading'


def test_open_closed_spread_open_widens():
    bar = _bar(I, voicing=Shape(degree=1, intervals=(2, 3)))
    out = open_closed_spread(bar, spread='open')
    assert out.voicing.intervals == (3, 4)
    assert out.technique == 'Open/closed spread'


def test_open_closed_spread_closed_narrows():
    bar = _bar(I, voicing=Shape(degree=1, intervals=(4, 3)))
    out = open_closed_spread(bar, spread='closed')
    assert out.voicing.intervals == (3, 2)


# ──────────────────────────────────────────────────────────────────────────
# Placement
# ──────────────────────────────────────────────────────────────────────────

def test_anticipation_annotates():
    bars = (_bar(I), _bar(V), _bar(I))
    out = anticipation(bars, i=1)
    assert out[1].technique == 'Anticipation'
    assert len(out) == 3


def test_delay_annotates():
    bars = (_bar(I), _bar(V), _bar(I))
    out = delay(bars, i=1)
    assert out[1].technique == 'Delay'
