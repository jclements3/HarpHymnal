"""Drill-page generation.

See :mod:`drills.build` for the procedural ``(technique, path) → Drill`` API
and :mod:`drills.types` for the typed domain objects (``Brace``,
``DrillStep``, ``Drill``).
"""
from drills.types import Brace, Drill, DrillStep
from drills.build import (
    PATHS,
    PATH_NAMES,
    TECHNIQUES,
    build_all,
    build_drill,
    display_names,
    drill_to_dict,
    path_slug,
    technique_slug,
    write_all,
    write_drill,
)

__all__ = [
    'Brace', 'Drill', 'DrillStep',
    'PATHS', 'PATH_NAMES', 'TECHNIQUES',
    'build_all', 'build_drill', 'display_names', 'drill_to_dict',
    'path_slug', 'technique_slug', 'write_all', 'write_drill',
]
