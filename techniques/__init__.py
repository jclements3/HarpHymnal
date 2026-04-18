"""Reharm technique operators — 18 pure functions over grammar objects.

Four families (see SDD §3.6 and GRAMMAR.md):
    substitution (5) — third_sub, quality_sub, modal_reframing,
                       deceptive_sub, common_tone_pivot
    approach (5)     — step_approach, third_approach, dominant_approach,
                       suspension_approach, double_approach
    voicing (6)      — inversion, density, stacking, pedal, voice_leading,
                       open_closed_spread
    placement (2)    — anticipation, delay

Every function is pure (no I/O, no mutation, no globals) and stays strictly
diatonic in the current key.
"""
from techniques.substitution import (
    third_sub,
    quality_sub,
    modal_reframing,
    deceptive_sub,
    common_tone_pivot,
)
from techniques.approach import (
    step_approach,
    third_approach,
    dominant_approach,
    suspension_approach,
    double_approach,
)
from techniques.voicing import (
    inversion,
    density,
    stacking,
    pedal,
    voice_leading,
    open_closed_spread,
)
from techniques.placement import (
    anticipation,
    delay,
)

__all__ = [
    # substitution
    'third_sub', 'quality_sub', 'modal_reframing',
    'deceptive_sub', 'common_tone_pivot',
    # approach
    'step_approach', 'third_approach', 'dominant_approach',
    'suspension_approach', 'double_approach',
    # voicing
    'inversion', 'density', 'stacking', 'pedal',
    'voice_leading', 'open_closed_spread',
    # placement
    'anticipation', 'delay',
]
