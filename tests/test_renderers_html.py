"""Tests for renderers/html.py — index builder + viewer staging."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from renderers.html import build_index, write_viewer


# ───────────────────────── build_index ──────────────────────────

def test_build_index_on_empty_data(tmp_path: Path):
    """Empty data root → empty hymns & drills lists (no exceptions)."""
    result = build_index(tmp_path)
    assert result == {"hymns": [], "drills": []}


def test_build_index_on_missing_subdirs(tmp_path: Path):
    """A data root that doesn't even contain hymns/ or drills/ is fine."""
    # tmp_path exists but is empty — no hymns/, no drills/
    assert not (tmp_path / "hymns").exists()
    result = build_index(tmp_path)
    assert result == {"hymns": [], "drills": []}


def test_build_index_collects_stub_records(tmp_path: Path):
    """One stub hymn + one stub drill → correct shape."""
    hymns = tmp_path / "hymns"
    drills = tmp_path / "drills" / "third_sub"
    hymns.mkdir(parents=True)
    drills.mkdir(parents=True)

    (hymns / "silent_night.json").write_text(json.dumps({
        "slug": "silent_night",
        "title": "Silent Night",
        "key": {"root": "Bb", "mode": "major"},
        "meter": {"beats": 6, "unit": 8},
    }), encoding="utf-8")

    (drills / "4ths_cw.json").write_text(json.dumps({
        "technique": "Third sub",
        "path": "4ths CW",
        "steps": [
            {"abc": "[CEG] [EGB]", "comment": "tonic → iii"},
            {"abc": "[EGB] [Ace]", "comment": "iii → vi"},
        ],
    }), encoding="utf-8")

    result = build_index(tmp_path)

    assert len(result["hymns"]) == 1
    hymn = result["hymns"][0]
    assert hymn["slug"] == "silent_night"
    assert hymn["title"] == "Silent Night"
    assert "Bb" in hymn["key"] and "major" in hymn["key"]
    assert hymn["meter"] == "6/8"
    # No extra fields leak from the on-disk record.
    assert set(hymn.keys()) == {"slug", "title", "key", "meter"}

    assert len(result["drills"]) == 1
    drill = result["drills"][0]
    assert drill["technique"] == "Third sub"
    assert drill["path"] == "4ths CW"
    assert drill["slug"] == "third_sub/4ths_cw"
    assert drill["steps_count"] == 2
    assert set(drill.keys()) == {"technique", "path", "slug", "steps_count"}


def test_build_index_tolerates_broken_json(tmp_path: Path):
    """A malformed JSON file shouldn't crash the indexer."""
    hymns = tmp_path / "hymns"
    hymns.mkdir()
    (hymns / "broken.json").write_text("{ not valid json", encoding="utf-8")
    result = build_index(tmp_path)
    # Still get a record (slug from the filename, empty key/meter).
    assert len(result["hymns"]) == 1
    assert result["hymns"][0]["slug"] == "broken"


def test_build_index_alpha_sort(tmp_path: Path):
    """Hymns sort by title, case-insensitive."""
    hymns = tmp_path / "hymns"
    hymns.mkdir()
    for slug, title in [
        ("joy", "Joy to the World"),
        ("amazing", "Amazing Grace"),
        ("silent", "Silent Night"),
    ]:
        (hymns / f"{slug}.json").write_text(json.dumps({
            "slug": slug, "title": title,
        }), encoding="utf-8")

    titles = [h["title"] for h in build_index(tmp_path)["hymns"]]
    assert titles == ["Amazing Grace", "Joy to the World", "Silent Night"]


# ───────────────────────── write_viewer ─────────────────────────

def _stub_viewer(root: Path) -> None:
    """Build a minimal viewer-source tree for copy-tree tests."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "index.html").write_text("<!doctype html><title>t</title>", encoding="utf-8")
    (root / "app.css").write_text("body{}", encoding="utf-8")
    (root / "app.js").write_text("// no-op", encoding="utf-8")
    (root / "sw.js").write_text("// sw", encoding="utf-8")
    # bookkeeping files we expect to be skipped
    (root / "__init__.py").write_text("", encoding="utf-8")
    pyc = root / "__pycache__"; pyc.mkdir(exist_ok=True)
    (pyc / "x.pyc").write_bytes(b"\x00")


def test_write_viewer_writes_index_in_place(tmp_path: Path):
    data = tmp_path / "data"
    viewer = tmp_path / "viewer"
    data.mkdir(); _stub_viewer(viewer)

    idx = write_viewer(data, viewer)  # no bundle target
    assert idx == data / "index.json"
    assert idx.exists()
    payload = json.loads(idx.read_text(encoding="utf-8"))
    assert payload == {"hymns": [], "drills": []}


def test_write_viewer_copies_viewer_tree(tmp_path: Path):
    """With an explicit bundle target, every viewer file is copied."""
    data = tmp_path / "data"
    viewer = tmp_path / "viewer"
    bundle = tmp_path / "out"
    data.mkdir(); _stub_viewer(viewer)

    write_viewer(data, viewer, target=bundle)

    for name in ("index.html", "app.css", "app.js", "sw.js"):
        assert (bundle / name).is_file(), f"missing {name} in bundle"
    # __init__.py and __pycache__ should be skipped
    assert not (bundle / "__init__.py").exists()
    assert not (bundle / "__pycache__").exists()
    # data/ is mirrored under the bundle so the tablet package is self-contained
    assert (bundle / "data" / "index.json").is_file()


def test_write_viewer_idempotent(tmp_path: Path):
    """Running twice in a row must not raise."""
    data = tmp_path / "data"
    viewer = tmp_path / "viewer"
    bundle = tmp_path / "out"
    data.mkdir(); _stub_viewer(viewer)

    write_viewer(data, viewer, target=bundle)
    write_viewer(data, viewer, target=bundle)  # again, no error
    assert (bundle / "index.html").exists()


def test_write_viewer_copies_real_viewer_tree(tmp_path: Path):
    """Sanity-check against the repo's actual viewer/ directory.

    This confirms the shipped files can be staged into a bundle without
    error.  (The test lives in-tree so it stays in sync if anyone adds new
    viewer assets.)
    """
    repo    = Path(__file__).resolve().parent.parent
    viewer  = repo / "viewer"
    data    = tmp_path / "data"; data.mkdir()
    bundle  = tmp_path / "bundle"

    write_viewer(data, viewer, target=bundle)
    # Key files must be present.
    for name in ("index.html", "app.css", "app.js", "sw.js"):
        assert (bundle / name).is_file(), f"{name} missing from staged bundle"
