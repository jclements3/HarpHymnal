"""Typed schema + loader + validator for the reharm tactic pool.

Replaces the inline dict-of-dicts validation that used to live in
``trefoil/build_reharm_tactics.py`` with @dataclass records, richer
compatibility modelling (``requires``, ``derived_from``, ``note``), and a
handful of helpers for selector code:

    >>> spec = TacticsSpec.load(Path("data/reharm/tactics.json"))
    >>> warnings = validate(spec)      # -> list[str]
    >>> compatibility(spec, {"shape.no_lh", "lh_activity.sustain"})
    False
    >>> legal_completions(spec, {"shape.full_4"}, "register")
    [<Tactic register.same>, ...]

The module is stdlib-only (``dataclasses``, ``json``). No pip deps.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# --------------------------------------------------------------------------- #
# Dataclasses                                                                 #
# --------------------------------------------------------------------------- #

@dataclass
class Bias:
    id: str
    name: str
    rule: str
    penalty_target: str = ""


@dataclass
class Dimension:
    id: str
    name: str


@dataclass
class Tactic:
    id: str
    dimension: str
    name: str
    tags: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    derived_from: str | None = None
    note: str = ""


@dataclass
class TacticsSpec:
    version: int
    biases: list[Bias]
    dimensions: list[Dimension]
    tactics: list[Tactic]

    # ------------------------------------------------------------------ #
    # Loader                                                             #
    # ------------------------------------------------------------------ #

    @classmethod
    def load(cls, path: str | Path) -> "TacticsSpec":
        raw = json.loads(Path(path).read_text())
        return cls.from_dict(raw)

    @classmethod
    def from_dict(cls, raw: dict) -> "TacticsSpec":
        biases = [
            Bias(
                id=b["id"],
                name=b.get("name", b["id"]),
                rule=b.get("rule", ""),
                penalty_target=b.get("penalty_target", ""),
            )
            for b in raw.get("biases", [])
        ]
        dimensions = [
            Dimension(id=d["id"], name=d.get("name", d["id"]))
            for d in raw.get("dimensions", [])
        ]
        tactics = [
            Tactic(
                id=t["id"],
                dimension=t["dimension"],
                name=t.get("name", t["id"]),
                tags=list(t.get("tags", []) or []),
                conflicts=list(t.get("conflicts", []) or []),
                requires=list(t.get("requires", []) or []),
                derived_from=t.get("derived_from"),
                note=t.get("note", "") or "",
            )
            for t in raw.get("tactics", [])
        ]
        return cls(
            version=int(raw.get("version", 1)),
            biases=biases,
            dimensions=dimensions,
            tactics=tactics,
        )

    # ------------------------------------------------------------------ #
    # Indexing helpers                                                   #
    # ------------------------------------------------------------------ #

    def tactic_index(self) -> dict[str, Tactic]:
        return {t.id: t for t in self.tactics}

    def tactics_by_dimension(self, dim: str) -> list[Tactic]:
        return [t for t in self.tactics if t.dimension == dim]


# --------------------------------------------------------------------------- #
# Validation                                                                  #
# --------------------------------------------------------------------------- #

def validate(spec: TacticsSpec) -> list[str]:
    """Human-readable warnings for the structured tactic pool.

    Covers:
      * duplicate tactic ids
      * tactics referring to unknown dimensions
      * conflicts / requires referencing unknown ids
      * conflict-edge symmetry (A→B implies B→A)
      * require cycles
      * derived_from pointing at a non-existent tactic
    """
    warnings: list[str] = []

    dim_ids = {d.id for d in spec.dimensions}

    # Duplicate ids.
    seen: set[str] = set()
    for t in spec.tactics:
        if t.id in seen:
            warnings.append(f"duplicate tactic id: {t.id}")
        seen.add(t.id)

    index = spec.tactic_index()
    known_ids = set(index.keys())

    # Unknown dimension; unknown conflict/requires ids; derived_from target.
    for t in spec.tactics:
        if t.dimension not in dim_ids:
            warnings.append(f"{t.id}: unknown dimension {t.dimension!r}")
        for c in t.conflicts:
            if c not in known_ids:
                warnings.append(f"{t.id}: conflict references unknown id {c!r}")
        for r in t.requires:
            if r not in known_ids:
                warnings.append(f"{t.id}: requires references unknown id {r!r}")
        if t.derived_from is not None and t.derived_from not in known_ids:
            warnings.append(
                f"{t.id}: derived_from references unknown id {t.derived_from!r}"
            )

    # Conflict symmetry: if A lists B, B should list A.
    for t in spec.tactics:
        for c in t.conflicts:
            if c not in known_ids:
                continue  # already warned above
            other = index[c]
            if t.id not in other.conflicts:
                warnings.append(
                    f"conflict asymmetry: {t.id} lists {c} but {c} does not list {t.id}"
                )

    # requires cycle detection via DFS.
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {tid: WHITE for tid in known_ids}

    def _visit(node: str, stack: list[str]) -> None:
        color[node] = GRAY
        stack.append(node)
        for nxt in index[node].requires:
            if nxt not in known_ids:
                continue  # already warned
            if color[nxt] == GRAY:
                # Found a cycle; report the cyclic path slice.
                try:
                    start = stack.index(nxt)
                    cycle_path = stack[start:] + [nxt]
                except ValueError:
                    cycle_path = [node, nxt]
                warnings.append(
                    "requires cycle: " + " -> ".join(cycle_path)
                )
            elif color[nxt] == WHITE:
                _visit(nxt, stack)
        stack.pop()
        color[node] = BLACK

    for tid in known_ids:
        if color[tid] == WHITE:
            _visit(tid, [])

    # Deduplicate cycle warnings (DFS may report the same cycle from
    # different entry points).
    seen_w: set[str] = set()
    deduped: list[str] = []
    for w in warnings:
        if w not in seen_w:
            seen_w.add(w)
            deduped.append(w)
    return deduped


# --------------------------------------------------------------------------- #
# Compatibility                                                               #
# --------------------------------------------------------------------------- #

def compatibility(spec: TacticsSpec, chosen: Iterable[str]) -> bool:
    """Return True iff the chosen tactic ids are pairwise-compatible.

    A set is compatible when:
      * every id exists in the spec
      * no pair appears in each other's ``conflicts`` list
      * every tactic's ``requires`` ids are also in ``chosen``
    """
    chosen_set = set(chosen)
    index = spec.tactic_index()

    # Every id must exist.
    for tid in chosen_set:
        if tid not in index:
            return False

    # Pairwise conflicts.
    for tid in chosen_set:
        t = index[tid]
        for c in t.conflicts:
            if c in chosen_set:
                return False

    # requires edges must be satisfied.
    for tid in chosen_set:
        for r in index[tid].requires:
            if r not in chosen_set:
                return False

    return True


def legal_completions(
    spec: TacticsSpec, chosen: Iterable[str], dimension: str
) -> list[Tactic]:
    """Tactics in ``dimension`` that could be added to ``chosen`` legally.

    A candidate ``cand`` is legal iff ``compatibility(spec, chosen | {cand})``
    holds. Tactics already present in ``chosen`` are skipped.
    """
    chosen_set = set(chosen)
    out: list[Tactic] = []
    for t in spec.tactics_by_dimension(dimension):
        if t.id in chosen_set:
            continue
        if compatibility(spec, chosen_set | {t.id}):
            out.append(t)
    return out


__all__ = [
    "Bias",
    "Dimension",
    "Tactic",
    "TacticsSpec",
    "validate",
    "compatibility",
    "legal_completions",
]
