"""Typed domain objects for drills.

A :class:`Drill` is one *technique* practised along one *path* around the
trefoil.  Each :class:`DrillStep` has a :class:`Brace` — the chord
nonterminal at this slot together with the set of ipools that realise it —
plus a one-line pedagogy comment rendered alongside.

Per SDD §3.5 and GRAMMAR.md::

    brace = ipool, { ipool } | chord
    step  = brace, { brace }
    drill = technique, path, step, { step }

We keep the data model purely structural (no rendering).  The render layer
decides how to draw braces (``{006|015|029}``) and glue steps into HTML.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Brace:
    """One slot on a drill path.

    Attributes:
        ipools: Canonical 001..118 indices of every pool entry that realises
            the chord nonterminal at this slot.  At least one per diatonic
            chord in a well-formed drill.
        chord_nonterminal: Roman-numeral label for the slot — used by the
            rendering layer to title the brace (``I``, ``ii``, …, ``vii○``).
    """
    ipools: tuple[str, ...]
    chord_nonterminal: str


@dataclass(frozen=True)
class DrillStep:
    """A single row of a drill page: one brace plus a pedagogy comment."""
    brace: Brace
    comment: str


@dataclass(frozen=True)
class Drill:
    """One technique × one path × eight closed-loop steps."""
    technique: str
    path: str
    steps: tuple[DrillStep, ...]
