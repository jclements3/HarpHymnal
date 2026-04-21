"""Tests for ``trefoil.reharm.selector``.

Runnable either with pytest or as a plain script::

    python3 -m pytest tests/test_selector.py
    python3 tests/test_selector.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trefoil.reharm.schema import TacticsSpec, compatibility  # noqa: E402
from trefoil.reharm.selector import (  # noqa: E402
    MODE_TO_IONIAN,
    generate_variations,
    infer_phrase_role,
    pick_mode,
    select_variation,
    translate_roman,
)

TACTICS_JSON = ROOT / "data" / "reharm" / "tactics.json"
SHAPE_LIBRARY_JSON = ROOT / "data" / "reharm" / "shape_library.json"
OVERRIDES_JSON = ROOT / "data" / "reharm" / "mode_overrides.json"
HYMNS_DIR = ROOT / "data" / "hymns"


def _load_spec():
    return TacticsSpec.load(TACTICS_JSON)


def _load_library():
    return json.loads(SHAPE_LIBRARY_JSON.read_text())


def _load_overrides():
    return json.loads(OVERRIDES_JSON.read_text())


def _load_hymn(slug: str):
    return json.loads((HYMNS_DIR / f"{slug}.json").read_text())


# --------------------------------------------------------------------------- #
# Determinism                                                                 #
# --------------------------------------------------------------------------- #

def test_deterministic_same_seed_same_output():
    hymn = _load_hymn("amazing_grace")
    spec = _load_spec()
    lib = _load_library()
    ov = {}
    a = select_variation(hymn, 12345, spec, lib, ov)
    b = select_variation(hymn, 12345, spec, lib, ov)
    assert len(a["bars"]) == len(b["bars"])
    for ba, bb in zip(a["bars"], b["bars"]):
        assert ba["tactic_manifest"] == bb["tactic_manifest"]
        assert ba["shape_id"] == bb["shape_id"]


# --------------------------------------------------------------------------- #
# Legality                                                                    #
# --------------------------------------------------------------------------- #

def test_every_bar_tactic_tuple_is_compatible():
    hymn = _load_hymn("amazing_grace")
    spec = _load_spec()
    lib = _load_library()
    v = select_variation(hymn, 42, spec, lib, {})
    for b in v["bars"]:
        chosen = set(b["tactic_manifest"].values())
        assert compatibility(spec, chosen), (
            f"bar {b['bar']} tactic tuple not compatible: {chosen}"
        )


# --------------------------------------------------------------------------- #
# Shape match                                                                 #
# --------------------------------------------------------------------------- #

def test_every_chosen_shape_matches_translated_chord():
    hymn = _load_hymn("amazing_grace")
    spec = _load_spec()
    lib = _load_library()
    v = select_variation(hymn, 7, spec, lib, {})
    shape_by_id = {s["id"]: s for s in lib["shapes"]}
    for b in v["bars"]:
        if not b["shape_id"]:
            continue
        sh = shape_by_id.get(b["shape_id"])
        assert sh is not None, f"bar {b['bar']} references unknown shape_id"
        translated = b["chord_used"]["translated"]
        lib_numeral = sh["chord"]["numeral"]
        assert lib_numeral == translated, (
            f"bar {b['bar']}: shape numeral {lib_numeral} != translated "
            f"numeral {translated}"
        )


# --------------------------------------------------------------------------- #
# Coverage                                                                    #
# --------------------------------------------------------------------------- #

def test_coverage_across_40_variations_amazing_grace():
    spec = _load_spec()
    variations = generate_variations("amazing_grace", n_variations=40)
    coverage: dict[str, int] = {}
    for v in variations:
        for b in v["bars"]:
            for tid in b["tactic_manifest"].values():
                coverage[tid] = coverage.get(tid, 0) + 1
    # Every tactic in the spec (excluding derived_from labels) should be
    # covered at least once — with 40 variations × 16 bars × 12 dims = 7680
    # picks, and 79-4 = 75 non-derived tactics, plenty of headroom.
    non_derived = [t for t in spec.tactics if t.derived_from is None]
    uncovered = [t.id for t in non_derived if t.id not in coverage]
    # Shape tactics with no library support are expected not to be picked.
    # We explicitly allow them here.
    allowed_uncovered = {
        # Shape tactics with no library support yet (Phase 3 gap).
        "shape.no_lh", "shape.shell_37", "shape.quartal", "shape.sus",
        "shape.add9", "shape.add11", "shape.add13",
        # texture.single_line requires shape.no_lh, which is not pickable.
        "texture.single_line",
        # Modal treatment (Decision 5) forces lever.no_flip — other lever
        # tactics are selectable in principle but not in the modal baseline.
        "lever.flip_and_back", "lever.flip_hold",
        "lever.use_flipped", "lever.prepare_next",
        # phrase_role.release requires motion-based cadence detection to
        # fire cleanly; the 4-phrase Amazing Grace doesn't currently produce
        # it.  Exercised on other hymns.
        "phrase_role.release",
    }
    unexpected = [tid for tid in uncovered if tid not in allowed_uncovered]
    assert not unexpected, f"uncovered tactics: {unexpected}"


# --------------------------------------------------------------------------- #
# Minor-hymn translation                                                      #
# --------------------------------------------------------------------------- #

def test_minor_hymn_aeolian_translation():
    hymn = _load_hymn("god_rest_ye_merry_gentlemen")
    spec = _load_spec()
    lib = _load_library()
    v = select_variation(hymn, 99, spec, lib, {})
    assert v["mode"] == "aeolian"
    # 'i' chord should translate to Ionian-rel 'vi'
    found_i = False
    for b in v["bars"]:
        if b["chord_used"]["numeral"] == "i":
            assert b["chord_used"]["translated"] == "vi", (
                f"bar {b['bar']}: Aeolian 'i' should map to 'vi'"
            )
            found_i = True
    assert found_i, "expected at least one i chord in god_rest_ye_merry_gentlemen"


def test_translate_roman_tables():
    assert translate_roman("i", "aeolian") == "vi"
    assert translate_roman("III", "aeolian") == "I"
    assert translate_roman("iv", "aeolian") == "ii"
    assert translate_roman("V", "aeolian") == "iii"  # harmonic-min V → modal v
    assert translate_roman("i", "dorian") == "ii"
    assert translate_roman("I", "ionian") == "I"


def test_pick_mode_major_and_minor():
    assert pick_mode({"key": {"mode": "major"}}, {}) == "ionian"
    assert pick_mode({"key": {"mode": "minor"}}, {}) == "aeolian"
    assert pick_mode(
        {"key": {"mode": "minor"}}, {"_resolved": "dorian"}
    ) == "dorian"


# --------------------------------------------------------------------------- #
# Phrase role                                                                 #
# --------------------------------------------------------------------------- #

def test_phrase_role_positional_baseline():
    # First bar of phrase → opening.
    assert infer_phrase_role(0, 4) == "phrase_role.opening"
    # Last bar of phrase → cadence (no motion).
    assert infer_phrase_role(3, 4) == "phrase_role.cadence"
    # Second-to-last bar of phrase (len >= 3) → cadence_approach.
    assert infer_phrase_role(2, 4) == "phrase_role.cadence_approach"
    # Middle bar.
    assert infer_phrase_role(1, 4) == "phrase_role.middle"


def test_phrase_role_motion_override():
    # V → I mid-phrase: motion wins, becomes cadence even though positional
    # would say "middle".
    assert infer_phrase_role(1, 4, chord_motion=("V", "I")) == "phrase_role.cadence"
    # V → V mid-phrase: no motion pair match, positional wins.
    assert infer_phrase_role(1, 4, chord_motion=("V", "V")) == "phrase_role.middle"


def test_amazing_grace_first_bar_is_opening():
    """Positional baseline: first bar of each phrase gets opening."""
    hymn = _load_hymn("amazing_grace")
    spec = _load_spec()
    lib = _load_library()
    v = select_variation(hymn, 1, spec, lib, {})
    # Bar 1 is first bar of phrase 1 → opening.
    assert v["bars"][0]["tactic_manifest"]["phrase_role"] == "phrase_role.opening"


# --------------------------------------------------------------------------- #
# MODE_TO_IONIAN table sanity                                                 #
# --------------------------------------------------------------------------- #

def test_mode_to_ionian_shape_contains_required_keys():
    for mode in ("ionian", "aeolian", "dorian"):
        assert mode in MODE_TO_IONIAN, f"missing mode table {mode}"
    # Aeolian table must cover the core seven per REHARM_TACTICS table.
    ae = MODE_TO_IONIAN["aeolian"]
    for k in ("i", "III", "iv", "v"):
        assert k in ae, f"aeolian table missing {k}"


# --------------------------------------------------------------------------- #
# Script entry-point                                                          #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    fns = [
        test_deterministic_same_seed_same_output,
        test_every_bar_tactic_tuple_is_compatible,
        test_every_chosen_shape_matches_translated_chord,
        test_coverage_across_40_variations_amazing_grace,
        test_minor_hymn_aeolian_translation,
        test_translate_roman_tables,
        test_pick_mode_major_and_minor,
        test_phrase_role_positional_baseline,
        test_phrase_role_motion_override,
        test_amazing_grace_first_bar_is_opening,
        test_mode_to_ionian_shape_contains_required_keys,
    ]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
            failed += 1
        except Exception as e:  # pragma: no cover
            print(f"  ERR   {fn.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
