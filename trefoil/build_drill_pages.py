#!/usr/bin/env python3
"""Generate one HTML page per drill (108 total) + a slim drills.html index.

Source: data/jazz_drills/<family>/<cycle>.json
Output:
  jazz/drills/<family>_<cycle>.html   — one per drill
  jazz/drills.html                    — index linking to them
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRILLS_JSON = ROOT / "data" / "jazz_drills"
OUT_DIR = ROOT / "jazz" / "drills"
INDEX = ROOT / "jazz" / "drills.html"

COL_TO_LETTER = {1: "C", 2: "D", 3: "E", 4: "F", 5: "G", 6: "A", 7: "B"}

SUPERFAMILIES = {
    "Approach": {
        "color": "#4080A0",
        "families": [
            "dominant_approach", "double_approach", "step_approach",
            "suspension_approach", "third_approach",
        ],
    },
    "Placement": {
        "color": "#7B4A9E",
        "families": ["anticipation", "delay"],
    },
    "Substitution": {
        "color": "#C0605A",
        "families": [
            "common_tone_pivot", "deceptive_sub", "modal_reframing",
            "quality_sub", "third_sub",
        ],
    },
    "Voicing": {
        "color": "#50A050",
        "families": [
            "density", "inversion", "open_closed_spread",
            "pedal", "stacking", "voice_leading",
        ],
    },
}

FAMILY_TO_SUPER = {
    fam: super_name
    for super_name, info in SUPERFAMILIES.items()
    for fam in info["families"]
}


def render_grid(lh: list[list[int]], rh: list[list[int]]) -> str:
    """Render a 47-string grid for one step, LH+RH combined."""
    grid = ["."] * 47
    for col, octv in lh + rh:
        idx = (octv - 1) * 7 + (col - 1)
        if 0 <= idx < 47:
            grid[idx] = COL_TO_LETTER[col]
    return "".join(grid)


def header_row() -> str:
    """Octave markers above the 47-string grid."""
    row = [" "] * 47
    for octv in range(1, 8):
        pos = (octv - 1) * 7
        if pos < 47:
            row[pos] = str(octv)
    return "".join(row)


def pretty_family(fam: str) -> str:
    words = fam.replace("_", " ")
    return words[0].upper() + words[1:]


def pretty_cycle(stem: str) -> str:
    return stem.replace("_", " ").upper().replace("CW", "CW").replace("CCW", "CCW")


def cycle_label(path: str) -> str:
    return path


def drill_slug(family: str, cycle_stem: str) -> str:
    return f"{family}_{cycle_stem}"


DRILL_PAGE_TPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title} — HarpHymnal Jazz</title>
<style>
  :root {{ --bg:#f7f3ea; --ink:#2a2a2a; --muted:#888; --line:#d8d0c0; --panel:#ffffff; --accent:{color}; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ background: var(--bg); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height:1.5; }}
  #topbar {{ padding: 16px 24px; background: var(--accent); color: #fff;
    display: flex; align-items: center; gap: 16px; }}
  #topbar a {{ color: #fff; text-decoration: none; font-size: 15px; }}
  #topbar h1 {{ font-size: 20px; flex: 1; }}
  #topbar .sub {{ font-size: 13px; opacity: .85; }}
  main {{ padding: 20px 24px 60px; max-width: 900px; margin: 0 auto; }}
  .meta {{ color: var(--muted); margin-bottom: 18px; font-size: 14px; }}
  .meta strong {{ color: var(--ink); }}
  .walk {{ font-family: "Courier New", monospace; font-size: 14px;
    background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
    padding: 16px 18px; }}
  pre.hdr {{ color: var(--muted); padding-left: 90px; margin: 0 0 4px 0;
    letter-spacing: 0; }}
  .step {{ display: flex; align-items: baseline; gap: 12px; margin-bottom: 4px; }}
  .chord-name {{ min-width: 78px; font-weight: bold; color: var(--accent);
    font-family: "Courier New", monospace; font-size: 14px; }}
  pre.notes {{ flex: 1; letter-spacing: 0; margin: 0; }}
  .comment {{ font-size: 12px; color: var(--muted); font-style: italic;
    padding-left: 90px; margin-bottom: 8px; }}
</style></head><body>
<div id="topbar">
  <a href="../drills.html">← Drills</a>
  <h1>{title}</h1>
  <span class="sub">{super_name}</span>
</div>
<main>
  <div class="meta"><strong>{technique}</strong> · cycle path: <strong>{path}</strong> · {nsteps} steps</div>
  <div class="walk">
<pre class="hdr">{hdr}</pre>
{steps_html}
  </div>
</main>
</body></html>
"""


def build_drill_page(drill: dict, family: str, cycle_stem: str) -> str:
    super_name = FAMILY_TO_SUPER.get(family, "")
    color = SUPERFAMILIES[super_name]["color"] if super_name else "#8B5A2B"
    technique = drill["technique"]
    path = drill["path"]
    title = f"{technique} — {path}"
    steps = drill["steps"]

    step_rows = []
    for s in steps:
        name = html.escape(s["chord_name"])
        grid = render_grid(s.get("lh", []), s.get("rh", []))
        comment = s.get("comment", "")
        step_rows.append(
            f'    <div class="step">\n'
            f'      <div class="chord-name">{name}</div>\n'
            f'      <pre class="notes">{grid}</pre>\n'
            f'    </div>'
        )
        if comment:
            step_rows.append(f'    <div class="comment">{html.escape(comment)}</div>')

    return DRILL_PAGE_TPL.format(
        title=html.escape(title),
        super_name=html.escape(super_name),
        color=color,
        technique=html.escape(technique),
        path=html.escape(path),
        nsteps=len(steps),
        hdr=header_row(),
        steps_html="\n".join(step_rows),
    )


INDEX_TPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Drills — HarpHymnal Jazz</title>
<style>
  :root {{ --bg:#f7f3ea; --ink:#2a2a2a; --muted:#888; --line:#d8d0c0; --panel:#ffffff; --jazz:#8B5A2B; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ background: var(--bg); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height:1.5; }}
  #topbar {{ padding: 16px 24px; background: var(--jazz); color: #fff;
    display: flex; align-items: center; gap: 16px; }}
  #topbar a {{ color: #fff; text-decoration: none; font-size: 15px; }}
  #topbar h1 {{ font-size: 22px; flex: 1; }}
  .fam-nav {{ padding: 10px 24px; background: var(--panel); border-bottom: 1px solid var(--line);
    position: sticky; top: 0; font-size: 15px; z-index: 10; }}
  .fam-nav a {{ color: var(--jazz); text-decoration: none; font-weight: bold;
    padding: 3px 10px; border-radius: 4px; display: inline-block; }}
  .fam-nav a:hover {{ background: var(--line); }}
  main {{ padding: 20px 24px 60px; max-width: 1000px; margin: 0 auto; }}
  main > h2 {{ color: var(--jazz); margin-bottom: 8px; }}
  main > p.intro {{ color: var(--muted); margin-bottom: 20px; }}

  details.superfam {{ margin-bottom: 14px; border: 2px solid; border-radius: 8px;
    background: var(--panel); overflow: hidden; }}
  details.superfam > summary {{ padding: 12px 18px; font-size: 18px; font-weight: bold;
    color: #fff; cursor: pointer; list-style: none;
    display: flex; justify-content: space-between; align-items: baseline; }}
  details.superfam > summary::-webkit-details-marker {{ display: none; }}
  details.superfam > summary::after {{ content: '▸'; transition: transform 0.15s; font-size: 14px; }}
  details.superfam[open] > summary::after {{ transform: rotate(90deg); }}
  .sf-count {{ font-size: 13px; font-weight: normal; opacity: .85; }}
  .sf-body {{ padding: 14px 18px; }}

  .subfam {{ margin-bottom: 14px; }}
  .subfam-title {{ font-size: 15px; font-weight: bold; color: var(--ink); margin-bottom: 6px; }}
  .drill-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .drill-list a {{ text-decoration: none; color: var(--ink);
    padding: 6px 12px; border: 1px solid var(--line); border-radius: 4px;
    background: #fafaf6; font-family: "Courier New", monospace; font-size: 13px; }}
  .drill-list a:hover {{ background: var(--line); }}
</style></head><body>
<div id="topbar">
  <a href="index.html">← Home</a>
  <h1>Drills</h1>
  <span style="font-size:13px; opacity:.85">chord pool walks · new jazz pool</span>
</div>
<div class="fam-nav">{nav_html}</div>
<main>
<h2>Jazz Drills</h2>
<p class="intro">{total} cycle-walk drills across {n_super} technique families. Click a drill to open its step-by-step walk.</p>
{superfams_html}
</main>
<script>
  document.querySelectorAll('.fam-nav a').forEach(a => {{
    a.addEventListener('click', e => {{
      const target = document.querySelector(a.getAttribute('href'));
      if (target) target.open = true;
    }});
  }});
</script>
</body></html>
"""


def build_index(drill_records: list[tuple[str, str, dict]]) -> str:
    """drill_records: list of (family, cycle_stem, drill_json)"""
    by_super: dict[str, dict[str, list[tuple[str, str, dict]]]] = {}
    for family, cycle_stem, drill in drill_records:
        super_name = FAMILY_TO_SUPER.get(family)
        if not super_name:
            continue
        by_super.setdefault(super_name, {}).setdefault(family, []).append(
            (family, cycle_stem, drill)
        )

    nav_parts = []
    sf_blocks = []
    for super_name, info in SUPERFAMILIES.items():
        if super_name not in by_super:
            continue
        anchor = f"sf-{super_name.lower()}"
        nav_parts.append(f'<a href="#{anchor}">{super_name}</a>')
        color = info["color"]
        sub_blocks = []
        count = 0
        for family in info["families"]:
            if family not in by_super[super_name]:
                continue
            drills = by_super[super_name][family]
            count += len(drills)
            fam_pretty = pretty_family(family)
            links = []
            for fam, cycle_stem, drill in drills:
                slug = drill_slug(fam, cycle_stem)
                path = drill["path"]
                links.append(
                    f'<a href="drills/{slug}.html">{html.escape(path)}</a>'
                )
            sub_blocks.append(
                f'<div class="subfam">\n'
                f'  <div class="subfam-title">{html.escape(fam_pretty)}</div>\n'
                f'  <div class="drill-list">{"".join(links)}</div>\n'
                f'</div>'
            )
        sf_blocks.append(
            f'<details class="superfam" id="{anchor}" style="border-color:{color}">\n'
            f'  <summary style="background:{color}">{super_name} '
            f'<span class="sf-count">({count} drills)</span></summary>\n'
            f'  <div class="sf-body">\n' + "\n".join(sub_blocks) + "\n  </div>\n"
            f'</details>'
        )

    return INDEX_TPL.format(
        nav_html=" · ".join(nav_parts),
        total=len(drill_records),
        n_super=len([s for s in SUPERFAMILIES if s in by_super]),
        superfams_html="\n".join(sf_blocks),
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    drill_records = []
    for fam_dir in sorted(DRILLS_JSON.iterdir()):
        if not fam_dir.is_dir():
            continue
        for jf in sorted(fam_dir.glob("*.json")):
            cycle_stem = jf.stem
            drill = json.loads(jf.read_text())
            drill_records.append((fam_dir.name, cycle_stem, drill))

    for family, cycle_stem, drill in drill_records:
        slug = drill_slug(family, cycle_stem)
        html_out = build_drill_page(drill, family, cycle_stem)
        (OUT_DIR / f"{slug}.html").write_text(html_out)

    INDEX.write_text(build_index(drill_records))
    print(f"wrote {len(drill_records)} drill pages to {OUT_DIR}")
    print(f"wrote index {INDEX}")


if __name__ == "__main__":
    main()
