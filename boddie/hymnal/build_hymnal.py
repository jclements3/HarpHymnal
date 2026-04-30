#!/usr/bin/env python3
"""Bulk-build the Boddie Hymnal.

Mirrors ../reharm/hymnal/build_hymnal.py but produces a SINGLE output per
hymn -- no L1/L2/L3 ladder. Boddie has one render style.

Writes:
  - /tmp/boddie_hymnal_stage/<slug>.abc      (intermediate ABC)
  - /tmp/boddie_hymnal_stage/<slug>NNN.svg   (compiled by abcm2ps -g)
  - tablet_app/.../boddie/hymns/<slug>.svg   (viewBox-patched, page 1)
  - tablet_app/.../boddie/boddie_hymns.js    (window.BODDIE_HYMNS)

Run from anywhere:

    python3 boddie/hymnal/build_hymnal.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from boddie_hymnal import render_boddie  # noqa

REPO = Path(__file__).resolve().parents[2]
HYMNS_DIR = REPO / "data" / "hymns"
DEST = REPO / "tablet_app" / "app" / "src" / "main" / "assets" / "boddie" / "hymns"
INDEX_JS = REPO / "tablet_app" / "app" / "src" / "main" / "assets" / "boddie" / "boddie_hymns.js"
STAGE = Path("/tmp/boddie_hymnal_stage")


def add_viewbox(svg_text: str) -> str:
    m = re.search(r'<svg[^>]*width="([\d.]+)px"\s+height="([\d.]+)px"', svg_text)
    if not m:
        return svg_text
    if 'viewBox=' in svg_text:
        return svg_text
    w, h = m.group(1), m.group(2)
    return svg_text.replace(
        m.group(0),
        m.group(0) + f' viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet"',
        1,
    )


def build_one(jpath: Path, num_prefix: str) -> dict | None:
    slug = jpath.stem
    try:
        hymn = json.loads(jpath.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  SKIP {slug}: JSON load: {e}")
        return None
    if not hymn.get("bars") or not hymn.get("key"):
        print(f"  SKIP {slug}: no bars/key")
        return None

    try:
        abc = render_boddie(hymn, x_num=1, num_prefix=num_prefix)
    except Exception as e:
        print(f"  FAIL {slug}: render: {e}")
        return None

    abc_path = STAGE / f"{slug}.abc"
    abc_path.write_text(abc, encoding="utf-8")

    out_prefix = STAGE / slug
    try:
        subprocess.run(
            ["abcm2ps", str(abc_path), "-g", "-O", str(out_prefix)],
            check=True, capture_output=True, timeout=30,
        )
    except subprocess.CalledProcessError as e:
        print(f"  FAIL {slug}: abcm2ps: {e.stderr.decode()[:200]}")
        return None
    except subprocess.TimeoutExpired:
        print(f"  FAIL {slug}: abcm2ps timeout")
        return None

    svgs = sorted(STAGE.glob(f"{slug}[0-9][0-9][0-9].svg"))
    if not svgs:
        print(f"  FAIL {slug}: no SVG produced")
        return None

    svg_text = svgs[0].read_text(encoding="utf-8")
    svg_text = add_viewbox(svg_text)
    (DEST / f"{slug}.svg").write_text(svg_text, encoding="utf-8")

    return {
        "slug": slug,
        "num": num_prefix,
        "title": hymn["title"],
        "key": f"{hymn['key']['root']} {hymn['key']['mode']}",
        "meter": f"{hymn['meter']['beats']}/{hymn['meter']['unit']}",
        "bars": len(hymn["bars"]),
        "svg": f"boddie/hymns/{slug}.svg",
        "pages": len(svgs),
    }


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)

    jsons = sorted(HYMNS_DIR.glob("*.json"))
    pre = []
    for jp in jsons:
        try:
            h = json.loads(jp.read_text(encoding="utf-8"))
            pre.append((h.get("title", jp.stem), jp))
        except Exception:
            pre.append((jp.stem, jp))
    pre.sort(key=lambda t: t[0].lower())
    numbered = [(f"{i:03d}", jp) for i, (_, jp) in enumerate(pre, 1)]

    print(f"Processing {len(numbered)} hymns (Boddie style, single output)...")
    results = []
    fails = []
    for i, (num, jp) in enumerate(numbered, 1):
        rec = build_one(jp, num)
        if rec is None:
            fails.append(jp.stem)
            continue
        results.append(rec)
        if i % 25 == 0:
            print(f"  {i}/{len(numbered)}  OK={len(results)} FAIL={len(fails)}")

    print(f"Done. OK={len(results)} FAIL={len(fails)}")
    if fails:
        print(f"Failures: {fails[:10]}{'...' if len(fails) > 10 else ''}")

    results.sort(key=lambda r: r["num"])
    js = ("window.BODDIE_HYMNS = "
          + json.dumps(results, indent=2, ensure_ascii=False) + ";\n")
    INDEX_JS.write_text(js, encoding="utf-8")
    print(f"Wrote index: {INDEX_JS} ({len(results)} entries)")


if __name__ == "__main__":
    main()
