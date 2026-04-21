"""Tests for ``trefoil.reharm.legality`` (Phase 5).

Runnable either with pytest or as a plain script::

    python3 -m pytest tests/test_legality.py
    python3 tests/test_legality.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trefoil.reharm.legality import (  # noqa: E402
    CROSS_BAR_REACH_WARN,
    EXPOSE_LOW_BASS_THRESHOLD,
    LegalityReport,
    check_corpus,
    check_variation,
    score_variation,
)

AMAZING_GRACE_DIR = ROOT / "data" / "reharm" / "variations" / "amazing_grace"


def _load_variation(name: str) -> dict:
    return json.loads((AMAZING_GRACE_DIR / name).read_text())


def _load_all_amazing_grace() -> list[dict]:
    return [
        json.loads(p.read_text())
        for p in sorted(AMAZING_GRACE_DIR.glob("*.json"))
    ]


# --------------------------------------------------------------- #
# Hard-legality: all 40 Amazing Grace variations pass             #
# --------------------------------------------------------------- #

def test_all_amazing_grace_variations_pass_hard_legality():
    variations = _load_all_amazing_grace()
    assert len(variations) == 40, f"expected 40 Amazing Grace variations, got {len(variations)}"
    failures: list[tuple[int, list[str]]] = []
    for i, v in enumerate(variations, start=1):
        rpt = check_variation(v)
        if not rpt.passed:
            failures.append((i, rpt.errors))
    assert not failures, (
        "variations failed hard legality:\n"
        + "\n".join(f"  v{i:02d}: {errs}" for i, errs in failures)
    )


# --------------------------------------------------------------- #
# Warning surface: at least one variation shows SATB-zone or      #
# reach warnings                                                  #
# --------------------------------------------------------------- #

def test_at_least_one_variation_has_warnings():
    """The selector is coverage-targeted, not bias-optimised — we expect
    at least one variation to trip some soft warning across the 40."""
    variations = _load_all_amazing_grace()
    any_warning = False
    for v in variations:
        rpt = check_variation(v)
        if rpt.warnings:
            any_warning = True
            break
    assert any_warning, (
        "expected at least one Amazing Grace variation with a warning "
        "(reach / lever / satb-zone); got zero"
    )


# --------------------------------------------------------------- #
# score_variation: expose_extremes reward                         #
# --------------------------------------------------------------- #

def _bar(
    bar_num: int,
    lh: list[list[int]],
    rh: list[list[int]],
    density: str = "density.one_attack",
    register: str = "register.wide",
    texture: str = "texture.staggered",
    lever: str = "lever.no_flip",
    phrase_role: str = "phrase_role.opening",
) -> dict:
    """Build a minimal bar record for hand-crafted variations."""
    lh_idx = [(p[1] - 1) * 7 + (p[0] - 1) + 1 for p in lh] if lh else []
    rh_idx = [(p[1] - 1) * 7 + (p[0] - 1) + 1 for p in rh] if rh else []
    # bass = lowest LH, top = highest RH (fall back to LH when RH is empty)
    bass = min(zip(lh_idx, lh), default=(None, None))[1] if lh_idx else None
    top_source = rh if rh else lh
    top_idx_source = rh_idx if rh_idx else lh_idx
    top = max(zip(top_idx_source, top_source), default=(None, None))[1] if top_idx_source else None
    return {
        "bar": bar_num,
        "tactic_manifest": {
            "substitution": "substitution.as_written",
            "shape": "shape.full_4",
            "register": register,
            "density": density,
            "texture": texture,
            "lh_activity": "lh_activity.sustain",
            "rh_activity": "rh_activity.melody_alone",
            "connect_from": "connect_from.released",
            "connect_to": "connect_to.land_down",
            "lever": lever,
            "range": "range.stay",
            "phrase_role": phrase_role,
        },
        "shape_id": "handcrafted",
        "lh": lh,
        "rh": rh,
        "bass": bass,
        "top": top,
        "gap": 0,
        "chord_used": {"numeral": "I", "quality": None, "translated": "I"},
    }


def test_expose_extremes_rewards_low_bass_and_high_top():
    """Hand-crafted variation: every bar has bass at string ≤ 14 and
    RH top clearly above highest LH voice ⇒ expose_extremes close to 1.
    """
    # LH pair at (C, oct 2) = string 8 and (E, oct 2) = string 10.
    # RH pair at (G, oct 5) = string 33 and (C, oct 6) = string 36.
    low_bass_high_top = [
        _bar(i, lh=[[1, 2], [3, 2]], rh=[[5, 5], [1, 6]])
        for i in range(1, 5)
    ]
    low = {"bars": low_bass_high_top}

    # Contrast: bass up at string ~22 and RH sits on top of LH (no gap).
    mid_bass_crowded = [
        _bar(i, lh=[[1, 4], [3, 4]], rh=[[5, 4], [1, 5]])
        for i in range(1, 5)
    ]
    mid = {"bars": mid_bass_crowded}

    s_low = score_variation(low)
    s_mid = score_variation(mid)
    assert s_low["expose_extremes_score"] > s_mid["expose_extremes_score"], (
        f"low-bass/high-top variation should score higher on expose_extremes; "
        f"got low={s_low['expose_extremes_score']:.2f} "
        f"mid={s_mid['expose_extremes_score']:.2f}"
    )
    # And the low-bass variation should post a strong absolute reward.
    assert s_low["expose_extremes_score"] >= 0.75


# --------------------------------------------------------------- #
# Cross-bar reach warning fires on 20-string bass jump            #
# --------------------------------------------------------------- #

def test_cross_bar_reach_fires_on_large_bass_jump():
    # Bar 1: bass at string 1 (C1).  Bar 2: bass at string 22 (C4).
    # Jump = 21 strings, clearly > CROSS_BAR_REACH_WARN.
    bar1 = _bar(1, lh=[[1, 1], [3, 1]], rh=[[5, 5], [1, 6]])
    bar2 = _bar(2, lh=[[1, 4], [3, 4]], rh=[[5, 5], [1, 6]])
    var = {"bars": [bar1, bar2]}

    rpt = check_variation(var)
    assert any("cross-bar bass reach" in w for w in rpt.warnings), (
        f"expected cross-bar bass reach warning; got warnings={rpt.warnings}"
    )
    # Sanity: the jump magnitude in the message should exceed the threshold.
    assert rpt.passed, (
        f"hand-crafted two-bar variation should still pass hard legality; "
        f"errors={rpt.errors}"
    )


# --------------------------------------------------------------- #
# check_corpus aggregator                                         #
# --------------------------------------------------------------- #

def test_check_corpus_amazing_grace():
    summary = check_corpus(AMAZING_GRACE_DIR)
    assert summary["n_variations"] == 40
    assert summary["failed"] == 0, (
        f"expected all 40 to pass hard legality; "
        f"{summary['failed']} failed; errors[:3]={summary['errors'][:3]}"
    )
    assert summary["passed"] == 40


# --------------------------------------------------------------- #
# Script entry point                                              #
# --------------------------------------------------------------- #

if __name__ == "__main__":
    fns = [
        test_all_amazing_grace_variations_pass_hard_legality,
        test_at_least_one_variation_has_warnings,
        test_expose_extremes_rewards_low_bass_and_high_top,
        test_cross_bar_reach_fires_on_large_bass_jump,
        test_check_corpus_amazing_grace,
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
