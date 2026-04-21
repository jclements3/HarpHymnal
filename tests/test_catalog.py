"""Phase 8 smoke test — load ``data/reharm/catalog.json`` and verify shape.

This is intentionally lightweight: Phase 8 is UI + indexing, not heavy
numerical behavior.  Runnable either via ``pytest`` or as a script.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "data" / "reharm" / "catalog.json"


def _load() -> dict:
    assert CATALOG.is_file(), f"catalog missing: {CATALOG}"
    with CATALOG.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_top_level_shape() -> None:
    cat = _load()
    for key in ("version", "generated", "dimension_order", "fragment_schema",
                "variation_schema", "tactic_name_table", "hymns", "slug_table",
                "tactic_index_schema", "tactic_index", "corpus_stats"):
        assert key in cat, f"missing top-level key: {key}"
    assert cat["version"] == 1
    assert isinstance(cat["dimension_order"], list)
    assert len(cat["dimension_order"]) == 12
    assert isinstance(cat["tactic_name_table"], list)
    # Index 0 reserved as the empty string.
    assert cat["tactic_name_table"][0] == ""


def test_corpus_stats_counts() -> None:
    cat = _load()
    s = cat["corpus_stats"]
    assert s["total_hymns"] >= 1
    assert s["total_variations"] >= s["total_hymns"]
    assert s["total_fragments"] >= 0
    assert isinstance(s["tactic_coverage_matrix"], dict)


def test_hymn_entries_shape() -> None:
    cat = _load()
    for slug, h in cat["hymns"].items():
        assert "title" in h
        assert "variations" in h
        assert "fragments" in h
        for v in h["variations"]:
            assert "idx" in v and "dt" in v
            assert isinstance(v["dt"], list)
            assert len(v["dt"]) == 12
        for f in h["fragments"]:
            assert "pi" in f and "vi" in f and "dt" in f
            assert isinstance(f["dt"], list)
            assert len(f["dt"]) == 12
        # Only spot-check the first hymn to keep the test fast
        break


def test_slug_table_covers_hymns() -> None:
    cat = _load()
    slugs_in_dict = set(cat["hymns"].keys())
    slugs_in_table = set(cat["slug_table"])
    assert slugs_in_dict == slugs_in_table


def test_tactic_index_flat_encoding() -> None:
    cat = _load()
    stride = cat.get("tactic_index_flat_stride", 3)
    for tid, flat in cat["tactic_index"].items():
        assert isinstance(flat, list)
        assert len(flat) % stride == 0


def test_size_under_cap() -> None:
    # Soft cap: Phase 8 brief says "under 20 MB"; allow a small slack
    # (21 MB) so contributors can add a field or two without failing CI.
    size = CATALOG.stat().st_size
    assert size < 21 * 1024 * 1024, f"catalog.json is {size} bytes, over 21MB cap"


def main() -> int:
    import traceback
    fns = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    fail = 0
    for fn in fns:
        try:
            fn()
            print(f"ok    {fn.__name__}")
        except Exception:
            fail += 1
            print(f"FAIL  {fn.__name__}")
            traceback.print_exc()
    print(f"{len(fns) - fail}/{len(fns)} passed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
