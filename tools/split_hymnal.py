#!/usr/bin/env python3
"""Split source/OpenHymnal.abc into one file per tune.

Each tune is detected by an `X:` reference-number line and runs until
just before the next `X:` (or EOF). The Open Hymnal preamble (if any)
is duplicated above each tune so the resulting file is a complete,
parseable ABC by itself.

Outputs:
  abccomposer/examples/hymns/<slug>.abc   one per tune
  abccomposer/examples/hymns/index.json   manifest [{title, path, slug}]

Run from the repo root:  python3 tools/split_hymnal.py
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "OpenHymnal.abc"
OUT_DIR = ROOT / "abccomposer" / "examples" / "hymns"
TABLET_DIR = ROOT / "tablet_app" / "app" / "src" / "main" / "assets" \
                  / "abccomposer" / "examples" / "hymns"


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")[:80]
    return s or "untitled"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC}")
    text = SRC.read_text(encoding="utf-8")

    # Split on `X:N` lines that begin a tune. First chunk is preamble.
    parts = re.split(r"(?=^X:\s*\d+)", text, flags=re.MULTILINE)
    preamble = ""
    if parts and not parts[0].lstrip().startswith("X:"):
        preamble = parts.pop(0).rstrip() + "\n\n"

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    seen: dict[str, int] = {}
    index: list[dict] = []

    for tune in parts:
        # First T: line is the title; secondary T: lines are alternate titles.
        m = re.search(r"^T:\s*(.+?)$", tune, re.MULTILINE)
        title = (m.group(1).strip() if m else "Untitled")
        slug = slugify(title)
        seen[slug] = seen.get(slug, 0) + 1
        if seen[slug] > 1:
            slug = f"{slug}-{seen[slug]}"

        out_path = OUT_DIR / f"{slug}.abc"
        out_path.write_text(preamble + tune.rstrip() + "\n", encoding="utf-8")
        index.append({"title": title, "path": f"hymns/{slug}.abc", "slug": slug})

    # Sort manifest alphabetically by title for the picker.
    index.sort(key=lambda r: r["title"].lower())
    (OUT_DIR / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Mirror to tablet bundle so Gradle picks them up.
    if TABLET_DIR.exists():
        shutil.rmtree(TABLET_DIR)
    shutil.copytree(OUT_DIR, TABLET_DIR)

    print(f"wrote {len(index)} hymn files to {OUT_DIR.relative_to(ROOT)}")
    print(f"mirrored to {TABLET_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
