"""Tests for ``trefoil.reharm.schema``.

Runnable either with pytest or as a plain script:

    python3 -m pytest tests/test_reharm_schema.py
    python3 tests/test_reharm_schema.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trefoil.reharm.schema import (  # noqa: E402
    TacticsSpec,
    compatibility,
    legal_completions,
    validate,
)

TACTICS_JSON = ROOT / "data" / "reharm" / "tactics.json"


# --------------------------------------------------------------------------- #
# Loader + current-pool cleanliness                                           #
# --------------------------------------------------------------------------- #

def test_real_pool_loads_with_zero_warnings():
    spec = TacticsSpec.load(TACTICS_JSON)
    assert spec.tactics, "expected non-empty tactics list"
    assert spec.dimensions, "expected non-empty dimensions list"
    warnings = validate(spec)
    assert warnings == [], f"expected 0 warnings, got: {warnings}"


# --------------------------------------------------------------------------- #
# validate() — negative cases                                                 #
# --------------------------------------------------------------------------- #

def _minimal_spec_dict() -> dict:
    return {
        "version": 1,
        "biases": [],
        "dimensions": [
            {"id": "shape", "name": "Shape"},
            {"id": "register", "name": "Register"},
        ],
        "tactics": [
            {"id": "shape.a", "dimension": "shape", "name": "Shape A"},
            {"id": "shape.b", "dimension": "shape", "name": "Shape B"},
            {"id": "register.x", "dimension": "register", "name": "Reg X"},
        ],
    }


def test_duplicate_id_detected():
    raw = _minimal_spec_dict()
    raw["tactics"].append({"id": "shape.a", "dimension": "shape", "name": "dupe"})
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert any("duplicate tactic id" in w and "shape.a" in w for w in warns), warns


def test_unknown_dimension_detected():
    raw = _minimal_spec_dict()
    raw["tactics"].append(
        {"id": "ghost.z", "dimension": "ghost", "name": "Ghost"}
    )
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert any("unknown dimension" in w and "ghost.z" in w for w in warns), warns


def test_unknown_conflict_id_detected():
    raw = _minimal_spec_dict()
    raw["tactics"][0]["conflicts"] = ["shape.does_not_exist"]
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert any(
        "conflict references unknown id" in w and "shape.does_not_exist" in w
        for w in warns
    ), warns


def test_conflict_symmetry_violation_detected():
    raw = _minimal_spec_dict()
    # A conflicts with B but B does not list A back.
    raw["tactics"][0]["conflicts"] = ["shape.b"]
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert any("conflict asymmetry" in w for w in warns), warns


def test_conflict_symmetry_ok_when_bidirectional():
    raw = _minimal_spec_dict()
    raw["tactics"][0]["conflicts"] = ["shape.b"]
    raw["tactics"][1]["conflicts"] = ["shape.a"]
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert not any("conflict asymmetry" in w for w in warns), warns


def test_requires_unknown_detected():
    raw = _minimal_spec_dict()
    raw["tactics"][0]["requires"] = ["shape.missing"]
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert any(
        "requires references unknown id" in w and "shape.missing" in w
        for w in warns
    ), warns


def test_requires_cycle_detected():
    raw = _minimal_spec_dict()
    raw["tactics"][0]["requires"] = ["shape.b"]
    raw["tactics"][1]["requires"] = ["shape.a"]
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert any("requires cycle" in w for w in warns), warns


def test_derived_from_unknown_detected():
    raw = _minimal_spec_dict()
    raw["tactics"][0]["derived_from"] = "shape.phantom"
    spec = TacticsSpec.from_dict(raw)
    warns = validate(spec)
    assert any(
        "derived_from references unknown id" in w and "shape.phantom" in w
        for w in warns
    ), warns


# --------------------------------------------------------------------------- #
# compatibility() / legal_completions()                                       #
# --------------------------------------------------------------------------- #

def test_compatibility_rejects_known_conflict_pair():
    spec = TacticsSpec.load(TACTICS_JSON)
    assert not compatibility(spec, {"shape.no_lh", "lh_activity.sustain"})


def test_compatibility_accepts_handcrafted_legal_tuple():
    spec = TacticsSpec.load(TACTICS_JSON)
    legal = {
        "shape.full_4",
        "register.same",
        "lh_activity.sustain",
        "rh_activity.melody_alone",
        "density.per_beat",
        "texture.block",
        "connect_from.step",
        "connect_to.land_down",
        "substitution.as_written",
        "lever.no_flip",
        "range.stay",
        "phrase_role.middle",
    }
    assert compatibility(spec, legal), (
        "expected handcrafted tuple to be compatible"
    )


def test_compatibility_rejects_requires_unmet():
    spec = TacticsSpec.load(TACTICS_JSON)
    # texture.single_line requires shape.no_lh + rh_activity.melody_alone.
    assert not compatibility(spec, {"texture.single_line"})
    assert compatibility(
        spec,
        {"texture.single_line", "shape.no_lh", "rh_activity.melody_alone"},
    )


def test_legal_completions_nonempty_for_partial():
    spec = TacticsSpec.load(TACTICS_JSON)
    partial = {"shape.full_4", "register.same"}
    completions = legal_completions(spec, partial, "lh_activity")
    assert completions, "expected some lh_activity tactics to be legal completions"
    # Every returned id must keep the set compatible.
    for t in completions:
        assert compatibility(spec, partial | {t.id})


def test_legal_completions_excludes_conflicting_picks():
    spec = TacticsSpec.load(TACTICS_JSON)
    partial = {"shape.no_lh"}
    completions = legal_completions(spec, partial, "lh_activity")
    completion_ids = {t.id for t in completions}
    # shape.no_lh conflicts with every active lh_activity; only the
    # derived label lh_activity.none survives as a compatible pick.
    assert "lh_activity.sustain" not in completion_ids
    assert "lh_activity.arp_up" not in completion_ids
    assert "lh_activity.partial_silence" not in completion_ids
    assert "lh_activity.none" in completion_ids


# --------------------------------------------------------------------------- #
# Script-mode runner                                                          #
# --------------------------------------------------------------------------- #

def _run_all() -> int:
    tests = [
        ("real pool loads cleanly", test_real_pool_loads_with_zero_warnings),
        ("duplicate id detected", test_duplicate_id_detected),
        ("unknown dimension detected", test_unknown_dimension_detected),
        ("unknown conflict id detected", test_unknown_conflict_id_detected),
        ("conflict asymmetry detected", test_conflict_symmetry_violation_detected),
        ("conflict symmetry ok when bidirectional", test_conflict_symmetry_ok_when_bidirectional),
        ("requires unknown id detected", test_requires_unknown_detected),
        ("requires cycle detected", test_requires_cycle_detected),
        ("derived_from unknown detected", test_derived_from_unknown_detected),
        ("compatibility rejects known conflict pair", test_compatibility_rejects_known_conflict_pair),
        ("compatibility accepts handcrafted legal tuple", test_compatibility_accepts_handcrafted_legal_tuple),
        ("compatibility rejects requires unmet", test_compatibility_rejects_requires_unmet),
        ("legal_completions nonempty", test_legal_completions_nonempty_for_partial),
        ("legal_completions excludes conflicting", test_legal_completions_excludes_conflicting_picks),
    ]
    passed = 0
    failed: list[tuple[str, BaseException]] = []
    for name, fn in tests:
        try:
            fn()
        except BaseException as e:  # noqa: BLE001
            failed.append((name, e))
            print(f"FAIL  {name}: {e}")
        else:
            passed += 1
            print(f"ok    {name}")
    print(f"\n{passed}/{len(tests)} passed")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_run_all())
