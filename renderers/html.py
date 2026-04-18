"""HTML renderer — builds the tablet-friendly Harp Trefoil viewer.

This module is **pure file plumbing**. It does not generate scores or drills
(those come from Steps 6/7). It reads whatever JSON fixtures already live in
``data/hymns/`` and ``data/drills/**`` and produces:

1. ``data/index.json`` — combined manifest consumed by ``viewer/app.js``.
2. ``<target>/*`` — a byte-copy of every file in ``viewer/`` (index.html,
   app.css, app.js, sw.js, etc.), ready to ship to a static host or drop
   onto a tablet.

Public API:
    build_index(data_root: Path) -> dict
    write_viewer(data_root: Path, viewer_root: Path, target: Path | None = None) -> Path

Both functions are idempotent and safe to call on an empty ``data/``.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


# ───────────────────────────── slugging ─────────────────────────────

def _slugify(text: str) -> str:
    """Lowercase, collapse non-alnum runs to single ``_``, strip edges.

    Kept in sync with ``tools/build_review_html.py::hymn_slug`` from legacy
    (same algorithm; not imported).
    """
    out, prev_us = [], False
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
            prev_us = False
        elif not prev_us:
            out.append("_")
            prev_us = True
    slug = "".join(out).strip("_")
    return slug or "untitled"


# ───────────────────────────── hymns ────────────────────────────────

def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def _hymn_entry(path: Path) -> dict[str, Any]:
    """Extract the fields the viewer's nav needs from one hymn JSON.

    Step 3 has not yet produced the real hymn JSON schema, so we're
    defensive: accept any of the plausible key shapes (``key`` as a dict
    ``{root, mode}``, or flat ``key_root``/``mode``; ``meter`` as a dict
    ``{beats, unit}`` or a string like ``"4/4"``).
    """
    raw = _read_json(path)
    slug = str(raw.get("slug") or path.stem)
    title = str(raw.get("title") or path.stem.replace("_", " ").title())

    # key → "Bb minor" / "C major" / ""
    key_obj = raw.get("key")
    if isinstance(key_obj, dict):
        root = key_obj.get("root") or ""
        mode = key_obj.get("mode") or ""
        key_str = f"{root} {mode}".strip()
    elif isinstance(key_obj, str):
        key_str = key_obj
    else:
        root = raw.get("key_root") or ""
        mode = raw.get("mode") or raw.get("modal_name") or ""
        key_str = f"{root} {mode}".strip()

    # meter → "4/4"
    meter_obj = raw.get("meter")
    if isinstance(meter_obj, dict):
        beats = meter_obj.get("beats")
        unit = meter_obj.get("unit")
        meter_str = f"{beats}/{unit}" if beats and unit else ""
    elif isinstance(meter_obj, str):
        meter_str = meter_obj
    else:
        meter_str = ""

    return {
        "slug": slug,
        "title": title,
        "key": key_str,
        "meter": meter_str,
    }


def _collect_hymns(data_root: Path) -> list[dict[str, Any]]:
    hymns_dir = data_root / "hymns"
    if not hymns_dir.is_dir():
        return []
    entries = [_hymn_entry(p) for p in sorted(hymns_dir.glob("*.json"))]
    entries.sort(key=lambda e: e["title"].lower())
    return entries


# ───────────────────────────── drills ───────────────────────────────

# Used to pretty-print the technique label from a directory slug.  The
# grammar enumerates the 18 technique names (SDD §3.6); we slugify each
# one with ``_slugify`` and reverse-look-up here.
_TECHNIQUE_LABELS = {
    # Substitution
    "third_sub": "Third sub",
    "quality_sub": "Quality sub",
    "modal_reframing": "Modal reframing",
    "deceptive_sub": "Deceptive sub",
    "common_tone_pivot": "Common-tone pivot",
    # Approach
    "step_approach": "Step approach",
    "third_approach": "Third approach",
    "dominant_approach": "Dominant approach",
    "suspension_approach": "Suspension approach",
    "double_approach": "Double approach",
    # Voicing
    "inversion": "Inversion",
    "density": "Density",
    "stacking": "Stacking",
    "pedal": "Pedal",
    "voice_leading": "Voice leading",
    "open_closed_spread": "Open/closed spread",
    # Placement
    "anticipation": "Anticipation",
    "delay": "Delay",
}

# Path slug → pretty label.  ``2nds CW`` → ``2nds_cw`` etc.
_PATH_LABELS = {
    "2nds_cw":  "2nds CW",
    "2nds_ccw": "2nds CCW",
    "3rds_cw":  "3rds CW",
    "3rds_ccw": "3rds CCW",
    "4ths_cw":  "4ths CW",
    "4ths_ccw": "4ths CCW",
}


def _drill_entry(path: Path, data_root: Path) -> dict[str, Any]:
    raw = _read_json(path)
    rel = path.relative_to(data_root / "drills")
    # directory structure: data/drills/<technique_slug>/<path_slug>.json
    parts = rel.parts
    technique_slug = parts[0] if len(parts) >= 2 else ""
    path_slug = path.stem

    technique = raw.get("technique") or _TECHNIQUE_LABELS.get(technique_slug, technique_slug)
    path_label = raw.get("path") or _PATH_LABELS.get(path_slug, path_slug)
    steps = raw.get("steps") or []
    slug = f"{technique_slug}/{path_slug}" if technique_slug else path_slug

    return {
        "technique": str(technique),
        "path": str(path_label),
        "slug": slug,
        "steps_count": len(steps) if isinstance(steps, list) else 0,
    }


def _collect_drills(data_root: Path) -> list[dict[str, Any]]:
    drills_dir = data_root / "drills"
    if not drills_dir.is_dir():
        return []
    entries = [_drill_entry(p, data_root) for p in sorted(drills_dir.rglob("*.json"))]
    # Sort by technique, then a stable path order.
    path_order = {v: i for i, v in enumerate(_PATH_LABELS.values())}
    entries.sort(
        key=lambda e: (e["technique"].lower(), path_order.get(e["path"], 99), e["path"].lower())
    )
    return entries


# ───────────────────────────── public API ───────────────────────────

def build_index(data_root: Path) -> dict[str, Any]:
    """Scan ``data/hymns/*.json`` and ``data/drills/**/*.json`` → manifest.

    Returns::

        {
          "hymns":  [{"slug", "title", "key", "meter"}, ...],
          "drills": [{"technique", "path", "slug", "steps_count"}, ...],
        }

    Safe to call on a non-existent or empty ``data_root``.
    """
    return {
        "hymns": _collect_hymns(data_root),
        "drills": _collect_drills(data_root),
    }


def write_viewer(
    data_root: Path,
    viewer_root: Path,
    target: Path | None = None,
) -> Path:
    """Build ``data/index.json`` and copy ``viewer/*`` into ``target``.

    If ``target`` is ``None``, the viewer files are left in place and only
    ``data/index.json`` is (re-)written.  Otherwise ``target`` receives a
    byte-copy of every file under ``viewer_root`` plus a ``data/``
    subdirectory mirroring ``data_root``.

    Returns the written ``index.json`` path.
    """
    data_root = Path(data_root)
    viewer_root = Path(viewer_root)

    data_root.mkdir(parents=True, exist_ok=True)
    manifest = build_index(data_root)
    index_path = data_root / "index.json"
    with index_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    if target is not None:
        target = Path(target)
        target.mkdir(parents=True, exist_ok=True)
        _copy_viewer_tree(viewer_root, target)
        # Mirror data/ under the target too, so the tablet bundle is
        # self-contained.
        target_data = target / "data"
        if target_data.resolve() != data_root.resolve():
            if target_data.exists():
                shutil.rmtree(target_data)
            shutil.copytree(data_root, target_data)

    return index_path


def _copy_viewer_tree(src: Path, dst: Path) -> None:
    """Copy every regular file under ``src`` into ``dst`` (preserving layout).

    Skips ``__pycache__``, ``__init__.py`` (Python bookkeeping only), and
    anything inside ``.`` dotfolders.
    """
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        # skip Python bookkeeping & dotdirs
        if any(part == "__pycache__" or part.startswith(".") for part in rel.parts):
            continue
        if rel.name == "__init__.py":
            continue
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


__all__ = ["build_index", "write_viewer"]
