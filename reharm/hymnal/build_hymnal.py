#!/usr/bin/env python3
"""Bulk-build Reharm Hymnal at multiple levels side-by-side.

Renders every hymn x level through the abcjsharp FORK (jazz/fork_render.js) so the
Reharm Hymnal matches the rest of the harp apps: harp grand-staff stems (V:1 up /
V:2 down) and middle-C centered between the staves -- NOT abcm2ps. Writes:

  - tablet_app/assets/reharm/hymns/L<level>/<slug>.svg
  - tablet_app/assets/reharm/reharm_hymns.js             (window.REHARM_HYMNS)

Run:
    python build_hymnal.py                  # builds L1..L7
    python build_hymnal.py --levels 1,2,3   # custom level set

Catalog entries: {slug, num, title, key, meter, bars, svgs: {"1": ..., ...}, pages}
so the tablet UI picks svgs[currentLevel] at render time.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/home/james.clements/projects/HarpHymnal")
from reharm_hymnal import REHARM_LEVELS, build_abc          # noqa: E402
from jazz.fork_batch import fork_render, strip_abcm2ps       # noqa: E402

HYMNS_DIR = Path("/home/james.clements/projects/HarpHymnal/data/hymns")
ASSETS = Path("/home/james.clements/projects/HarpHymnal/tablet_app/"
              "app/src/main/assets/reharm")
INDEX_JS = ASSETS / "reharm_hymns.js"
STAFFWIDTH = 1000          # justify each source line to this -> note kerning


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=str, default="1,2,3,4,5,6,7")
    ap.add_argument("--hymn-dir", type=Path, default=HYMNS_DIR)
    args = ap.parse_args()

    levels = [int(x) for x in args.levels.split(",") if x.strip()]
    for lvl in levels:
        if lvl not in REHARM_LEVELS:
            sys.exit(f"unknown level: {lvl}")

    # numbering: sort by title, number from 1
    pre = []
    for jp in sorted(args.hymn_dir.glob("*.json")):
        try:
            h = json.loads(jp.read_text(encoding="utf-8"))
            pre.append((h.get("title", jp.stem), jp))
        except Exception:
            pre.append((jp.stem, jp))
    pre.sort(key=lambda t: t[0].lower())
    numbered = [(f"{i:03d}", jp) for i, (_, jp) in enumerate(pre, 1)]

    print(f"Building {len(numbered)} hymns at levels {levels} through the fork...")
    items, results, fails = [], [], []
    for num, jp in numbered:
        slug = jp.stem
        try:
            raw = jp.read_text(encoding="utf-8")
            hymn = json.loads(raw)
        except Exception as e:
            print(f"  SKIP {slug}: {e}"); fails.append(slug); continue
        if not hymn.get("bars") or not hymn.get("key"):
            print(f"  SKIP {slug}: no bars/key"); fails.append(slug); continue

        svgs_map, hymn_items, ok_all = {}, [], True
        for lvl in levels:
            try:
                reharmed = REHARM_LEVELS[lvl](json.loads(raw))   # fresh copy per level
                abc = strip_abcm2ps(build_abc(reharmed, x_num=1, num_prefix=num))
            except Exception as e:
                print(f"  FAIL {slug} L{lvl}: {str(e)[:120]}"); ok_all = False; break
            hymn_items.append({"abc": abc, "out": f"hymns/L{lvl}/{slug}.svg",
                               "staffwidth": STAFFWIDTH})
            svgs_map[str(lvl)] = f"reharm/hymns/L{lvl}/{slug}.svg"
        if not ok_all:
            fails.append(slug); continue
        items.extend(hymn_items)
        results.append({
            "slug": slug, "num": num, "title": hymn["title"],
            "key": f"{hymn['key']['root']} {hymn['key']['mode']}",
            "meter": f"{hymn['meter']['beats']}/{hymn['meter']['unit']}",
            "bars": len(hymn["bars"]), "svgs": svgs_map, "pages": 1,
        })

    print(f"Rendering {len(items)} SVGs through the fork...")
    ok, rfails = fork_render(str(ASSETS), items)
    print(f"Done. hymns OK={len(results)} skipped={len(fails)} | "
          f"svgs OK={ok} render-fails={len(rfails)}")
    for f in rfails[:10]:
        print("  RENDER FAIL", f[:100])

    results.sort(key=lambda r: r["num"])
    INDEX_JS.write_text("window.REHARM_HYMNS = "
                        + json.dumps(results, indent=2, ensure_ascii=False) + ";\n",
                        encoding="utf-8")
    print(f"Wrote index: {INDEX_JS} ({len(results)} entries, levels={levels})")


if __name__ == "__main__":
    main()
