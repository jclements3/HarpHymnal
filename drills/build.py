"""Procedurally build drill pages.

Drill space is the Cartesian product of 18 techniques × 6 paths = 108 drills.
Each drill walks one closed-loop path (8 steps, returning to ``I``) and
annotates each step with a one-line pedagogy comment shaped by the technique.

Public surface::

    build_drill(technique: str, path: str, pool: Pool) -> Drill
    build_all(pool: Pool) -> list[Drill]
    write_drill(drill: Drill, out_root: Path) -> Path
    write_all(drills, out_root) -> list[Path]

Naming / slug conventions:
    technique display name  → ``Third sub``        → slug ``third_sub``
    technique display name  → ``Open/closed spread``→ slug ``open_closed_spread``
    path display name       → ``4ths CW``           → slug ``4ths_cw``

The brace at each step is the set of pool entries whose LH chord matches the
step's chord nonterminal exactly (bare — no quality, no inversion).  Using an
LH-exact filter keeps braces small and focused (≥ 3 for every diatonic chord
in the 118 pool).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Optional

from grammar.types import Bar, Roman

from techniques import (
    anticipation,
    common_tone_pivot,
    deceptive_sub,
    delay,
    density,
    dominant_approach,
    double_approach,
    inversion,
    modal_reframing,
    open_closed_spread,
    pedal,
    quality_sub,
    stacking,
    step_approach,
    suspension_approach,
    third_approach,
    third_sub,
    voice_leading,
)

from drills.types import Brace, Drill, DrillStep


# ═════════════════════════════════════════════════════════════════════════
# Techniques — canonical (export-name, display-name) pairs in __init__ order
# ═════════════════════════════════════════════════════════════════════════
#
# The export name is the Python identifier re-exported from
# ``techniques/__init__.py`` (``techniques.__all__``) — the drill tests assert
# this list matches ``__init__`` exactly to catch typos.  The display name is
# what ends up in the Drill JSON's ``technique`` field; this matches the
# in-module ``technique='…'`` annotations set by each operator.

TECHNIQUES: tuple[tuple[str, str], ...] = (
    # substitution (5)
    ('third_sub',           'Third sub'),
    ('quality_sub',         'Quality sub'),
    ('modal_reframing',     'Modal reframing'),
    ('deceptive_sub',       'Deceptive sub'),
    ('common_tone_pivot',   'Common-tone pivot'),
    # approach (5)
    ('step_approach',       'Step approach'),
    ('third_approach',      'Third approach'),
    ('dominant_approach',   'Dominant approach'),
    ('suspension_approach', 'Suspension approach'),
    ('double_approach',     'Double approach'),
    # voicing (6)
    ('inversion',           'Inversion'),
    ('density',             'Density'),
    ('stacking',            'Stacking'),
    ('pedal',               'Pedal'),
    ('voice_leading',       'Voice leading'),
    ('open_closed_spread',  'Open/closed spread'),
    # placement (2)
    ('anticipation',        'Anticipation'),
    ('delay',               'Delay'),
)

_DISPLAY_TO_EXPORT: dict[str, str] = {disp: exp for exp, disp in TECHNIQUES}
_DISPLAY_NAMES: tuple[str, ...] = tuple(disp for _, disp in TECHNIQUES)


def display_names() -> tuple[str, ...]:
    """All 18 display-name strings in canonical order."""
    return _DISPLAY_NAMES


# ═════════════════════════════════════════════════════════════════════════
# Paths — each an 8-step closed loop starting and ending at I
# ═════════════════════════════════════════════════════════════════════════
#
# Labels use the ``vii○`` (white-circle) glyph from GRAMMAR.md.  When we
# query the pool (which stores the same chord as ``vii°`` — degree sign)
# we translate via :func:`_pool_numeral`.

PATHS: dict[str, tuple[str, ...]] = {
    '2nds CW':  ('I', 'ii',  'iii',  'IV',   'V',    'vi',  'vii○', 'I'),
    '2nds CCW': ('I', 'vii○', 'vi',  'V',    'IV',   'iii', 'ii',   'I'),
    '3rds CW':  ('I', 'iii', 'V',    'vii○', 'ii',   'IV',  'vi',   'I'),
    '3rds CCW': ('I', 'vi',  'IV',   'ii',   'vii○', 'V',   'iii',  'I'),
    '4ths CW':  ('I', 'IV',  'vii○', 'iii',  'vi',   'ii',  'V',    'I'),
    '4ths CCW': ('I', 'V',   'ii',   'vi',   'iii',  'vii○', 'IV',  'I'),
}

PATH_NAMES: tuple[str, ...] = tuple(PATHS.keys())


# ═════════════════════════════════════════════════════════════════════════
# Brace expansion
# ═════════════════════════════════════════════════════════════════════════

def _pool_numeral(nonterminal: str) -> str:
    """Translate grammar-spec chord label to the pool's internal spelling.

    The pool JSON uses ``vii°`` (degree sign, U+00B0); the grammar uses
    ``vii○`` (white circle, U+25CB).  Every other diatonic chord is spelt
    identically in both.
    """
    return 'vii°' if nonterminal == 'vii○' else nonterminal


def _brace_for(pool, nonterminal: str) -> Brace:
    """All pool entries whose LH chord matches ``nonterminal`` exactly.

    "Exactly" means bare numeral (no quality, no inversion) — keeps the
    brace small and focused.  Guaranteed ≥ 1 ipool for every diatonic
    chord in the 118 pool (verified by ``tests/test_drills_build.py``).
    """
    pool_label = _pool_numeral(nonterminal)
    target = Roman(numeral=pool_label, quality=None, inversion=None)
    matches = pool.all_voicings_of(target)
    ipools = tuple(
        e.ipool for e in matches
        if e.lh_chord.numeral == pool_label
        and (e.lh_chord.quality or '') == ''
        and (e.lh_chord.inversion or '') == ''
    )
    return Brace(ipools=ipools, chord_nonterminal=nonterminal)


# ═════════════════════════════════════════════════════════════════════════
# Comment composition — one short pedagogy line per step
# ═════════════════════════════════════════════════════════════════════════

# Which family each display name belongs to (substitution / approach /
# voicing / placement).  Drives comment shaping.
_FAMILY: dict[str, str] = {
    'Third sub':           'substitution',
    'Quality sub':         'substitution',
    'Modal reframing':     'substitution',
    'Deceptive sub':       'substitution',
    'Common-tone pivot':   'substitution',
    'Step approach':       'approach',
    'Third approach':      'approach',
    'Dominant approach':   'approach',
    'Suspension approach': 'approach',
    'Double approach':     'approach',
    'Inversion':           'voicing',
    'Density':             'voicing',
    'Stacking':            'voicing',
    'Pedal':               'voicing',
    'Voice leading':       'voicing',
    'Open/closed spread':  'voicing',
    'Anticipation':        'placement',
    'Delay':               'placement',
}

# Substitution operators that transform a single ``Bar``.
_SUB_FUNCS: dict[str, Callable[..., Bar]] = {
    'Third sub':         third_sub,
    'Quality sub':       quality_sub,
    'Modal reframing':   modal_reframing,
    'Deceptive sub':     deceptive_sub,
    'Common-tone pivot': common_tone_pivot,
}

# Display strings that describe a voicing transformation.
_VOICING_COMMENT: dict[str, str] = {
    'Inversion':          'play {chord} in first inversion (3rd on the bottom)',
    'Density':            'thin {chord} to a 2-finger shape, then full to 4-finger',
    'Stacking':           'stack {chord}: LH shape, RH same shape one octave up',
    'Pedal':              'hold tonic pedal under {chord}',
    'Voice leading':      'pick the {chord} voicing that moves least from the previous',
    'Open/closed spread': 'spread {chord} open (widen intervals 2 to 3 to 4)',
}

_PLACEMENT_COMMENT: dict[str, str] = {
    'Anticipation': 'land {chord} a half-beat early',
    'Delay':        'land {chord} a half-beat late',
}


def _sub_comment(display: str, current: str, next_: Optional[str]) -> str:
    """Compose a comment for a substitution technique at this step.

    Runs the operator on a bare ``Bar(chord=Roman(current))`` and compares
    the result's numeral with the input.
    """
    func = _SUB_FUNCS[display]
    bar = Bar(melody=(), chord=Roman(numeral=current))
    # Provide context for the two context-dependent substitutions.
    ctx: Optional[dict] = None
    if display == 'Deceptive sub':
        ctx = {'resolves_to': 'I'}
    elif display == 'Common-tone pivot' and next_ is not None:
        ctx = {'next_chord': Roman(numeral=_pool_numeral_back(next_))}
    out = func(bar, ctx=ctx) if ctx is not None else func(bar)
    out_roman = out.chord if isinstance(out.chord, Roman) else None
    new_numeral = out_roman.numeral if out_roman else current

    if new_numeral == current and (out_roman and (out_roman.quality or '')
                                   == '' and (out_roman.inversion or '') == ''):
        # Operator was a no-op at this slot — still comment on what the
        # technique WOULD do here, to keep the drill readable.
        return f'{display.lower()}: hold {current} (no diatonic sub available)'
    if out_roman and out_roman.quality:
        return f'replace {current} with {new_numeral}{out_roman.quality}'
    return f'replace {current} with {new_numeral}'


def _pool_numeral_back(label: str) -> str:
    """Reverse translation — kept available for future renderers; no-op today."""
    return label  # grammar uses ``vii○`` throughout; don't back-translate.


def _approach_comment(display: str, current: str, next_: Optional[str]) -> str:
    """Approach techniques comment on how to approach the NEXT chord."""
    target = next_ if next_ is not None else current
    if display == 'Step approach':
        return f'approach {target} by step from below ({current} is already diatonic)'
    if display == 'Third approach':
        return f'approach {target} from a diatonic 3rd below'
    if display == 'Dominant approach':
        return f'approach {target} with the global V (play V here)'
    if display == 'Suspension approach':
        return f'approach {target} through a suspension on {current} (s4)'
    if display == 'Double approach':
        return f'approach {target} with step + dominant over two bars'
    return display


def _voicing_comment(display: str, current: str) -> str:
    template = _VOICING_COMMENT[display]
    return template.format(chord=current)


def _placement_comment(display: str, current: str) -> str:
    template = _PLACEMENT_COMMENT[display]
    return template.format(chord=current)


def _step_comment(display: str, current: str, next_: Optional[str]) -> str:
    family = _FAMILY[display]
    if family == 'substitution':
        return _sub_comment(display, current, next_)
    if family == 'approach':
        return _approach_comment(display, current, next_)
    if family == 'voicing':
        return _voicing_comment(display, current)
    if family == 'placement':
        return _placement_comment(display, current)
    return display


# ═════════════════════════════════════════════════════════════════════════
# Drill construction
# ═════════════════════════════════════════════════════════════════════════

def build_drill(technique: str, path: str, pool) -> Drill:
    """Build one drill: ``technique`` practised along ``path``.

    ``technique`` is the display name (e.g. ``'Third sub'``); ``path`` is
    one of :data:`PATH_NAMES` (e.g. ``'4ths CW'``).  Raises on unknown
    names — tests catch typos.
    """
    if technique not in _FAMILY:
        raise ValueError(f"unknown technique {technique!r}; "
                         f"expected one of {_DISPLAY_NAMES}")
    if path not in PATHS:
        raise ValueError(f"unknown path {path!r}; expected one of {PATH_NAMES}")

    chords = PATHS[path]
    steps: list[DrillStep] = []
    for k, chord in enumerate(chords):
        next_chord: Optional[str] = chords[k + 1] if k + 1 < len(chords) else None
        brace = _brace_for(pool, chord)
        comment = _step_comment(technique, chord, next_chord)
        steps.append(DrillStep(brace=brace, comment=comment))

    return Drill(technique=technique, path=path, steps=tuple(steps))


def build_all(pool) -> list[Drill]:
    """Build every drill in the 18 × 6 = 108 Cartesian product.

    Enumeration order: technique display-name order × path display-name order.
    """
    drills: list[Drill] = []
    for _, display in TECHNIQUES:
        for path in PATH_NAMES:
            drills.append(build_drill(display, path, pool))
    return drills


# ═════════════════════════════════════════════════════════════════════════
# Slug conventions
# ═════════════════════════════════════════════════════════════════════════

def technique_slug(display: str) -> str:
    """``'Third sub'`` → ``'third_sub'``; ``'Open/closed spread'`` →
    ``'open_closed_spread'``; ``'Common-tone pivot'`` → ``'common_tone_pivot'``.
    """
    if display in _DISPLAY_TO_EXPORT:
        return _DISPLAY_TO_EXPORT[display]
    # Fallback for unknown names — conservative lowercase + non-alnum→underscore.
    slug = re.sub(r'[^a-z0-9]+', '_', display.lower()).strip('_')
    return slug


def path_slug(path: str) -> str:
    """``'4ths CW'`` → ``'4ths_cw'``."""
    return path.lower().replace(' ', '_')


# ═════════════════════════════════════════════════════════════════════════
# JSON emission
# ═════════════════════════════════════════════════════════════════════════

def drill_to_dict(drill: Drill) -> dict:
    """Convert a ``Drill`` to a JSON-ready dict (no rendering glue)."""
    return {
        'technique': drill.technique,
        'path':      drill.path,
        'steps': [
            {
                'brace': {
                    'ipools':            list(step.brace.ipools),
                    'chord_nonterminal': step.brace.chord_nonterminal,
                },
                'comment': step.comment,
            }
            for step in drill.steps
        ],
    }


def write_drill(drill: Drill, out_root: Path) -> Path:
    """Write one drill to ``<out_root>/<technique_slug>/<path_slug>.json``.

    Returns the absolute path written.
    """
    out_root = Path(out_root)
    out_dir = out_root / technique_slug(drill.technique)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{path_slug(drill.path)}.json'
    out_path.write_text(
        json.dumps(drill_to_dict(drill), indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    return out_path


def write_all(drills: list[Drill], out_root: Path) -> list[Path]:
    """Write every drill under ``out_root``; return the list of paths written."""
    return [write_drill(d, out_root) for d in drills]
