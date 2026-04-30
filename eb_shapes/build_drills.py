#!/usr/bin/env python3
"""Eb 33-string shape sweeps -- one drill per interval-pattern row of the
chord matrix in shapes/build_chord_table.py.

Each drill sweeps the *shape* (not every cell) from the lowest playable
position on a 33-string Eb-tuned lever harp to the highest. Default
range: C2 to G6 (33 diatonic strings inclusive). All seven scale degrees
in Eb major are walked at each octave, then the next octave up, etc.,
sorted by lowest pitch ascending so the sweep reads from bottom of the
harp to top.

Output:
  - tablet_app/.../eb_shapes/sweeps/<NN>_<pattern>.svg
  - tablet_app/.../eb_shapes/eb_shape_drills.js  (window.EB_SHAPE_DRILLS)

Run from anywhere:

    python3 eb_shapes/build_drills.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shapes"))
from build_chord_table import PATTERNS  # noqa

REPO = Path(__file__).resolve().parents[1]
DEST_SVG = REPO / "tablet_app" / "app" / "src" / "main" / "assets" / "eb_shapes" / "sweeps"
INDEX_JS = REPO / "tablet_app" / "app" / "src" / "main" / "assets" / "eb_shapes" / "eb_shape_drills.js"
STAGE = Path("/tmp/eb_shapes_stage")

# 33-string Eb lever harp default: C2 to G6.
LETTERS = ["C", "D", "E", "F", "G", "A", "B"]
LOW_LETTER = "C"
LOW_OCTAVE = 2
HIGH_LETTER = "G"
HIGH_OCTAVE = 6

# Eb major's tonic letter is E (with K:Eb auto-flatting it). Degree 1
# starts at letter index 2 in the C-relative LETTERS array.
EB_TONIC_LETTER_IDX = 2


def position(letter: str, octv: int) -> int:
    """Diatonic position counted in scale steps from C0."""
    return LETTERS.index(letter) + 7 * octv


LOW_POS = position(LOW_LETTER, LOW_OCTAVE)
HIGH_POS = position(HIGH_LETTER, HIGH_OCTAVE)


def shape_pitches_eb(degree: int, intervals: str, base_octave: int):
    """Return [(letter, octave), ...] in Eb major. Letters use the
    C-major naming so ABC's K:Eb signature applies the appropriate
    flats automatically."""
    idx = (degree - 1) + EB_TONIC_LETTER_IDX
    out = [(LETTERS[idx % 7], base_octave + idx // 7)]
    for ch in intervals:
        steps = int(ch, 16) - 1
        idx += steps
        out.append((LETTERS[idx % 7], base_octave + idx // 7))
    return out


def in_range(pitches) -> bool:
    return all(LOW_POS <= position(l, o) <= HIGH_POS for (l, o) in pitches)


def sweep_for(pattern: str):
    """All (degree, base_oct, pitches) where the shape fits in C2..G6,
    sorted by lowest pitch ascending."""
    seen = set()
    rows = []
    for base_oct in range(LOW_OCTAVE - 2, HIGH_OCTAVE + 2):
        for degree in range(1, 8):
            ps = shape_pitches_eb(degree, pattern, base_oct)
            if not in_range(ps):
                continue
            sig = tuple(ps)
            if sig in seen:
                continue
            seen.add(sig)
            rows.append((position(*ps[0]), degree, base_oct, ps))
    rows.sort()
    return [(d, b, ps) for (_p, d, b, ps) in rows]


def pitch_to_abc(letter: str, octv: int) -> str:
    if octv >= 5:
        return letter.lower() + "'" * (octv - 5)
    return letter.upper() + "," * (4 - octv)


def chord_token(pitches) -> str:
    return "[" + "".join(pitch_to_abc(*p) for p in pitches) + "]"


# Treble/bass split point: anything whose bottom note is at or above G3
# goes on the treble staff; anything below goes on the bass staff. That
# keeps low-bass sweeps off the treble ledger lines.
SPLIT_POS = position("G", 3)


def split_voices(rows):
    v1_cells, v2_cells = [], []
    for degree, base_oct, pitches in rows:
        bottom = position(*pitches[0])
        cell = f"!arpeggio!{chord_token(pitches)}4"
        if bottom >= SPLIT_POS:
            v1_cells.append(cell)
            v2_cells.append("z4")
        else:
            v1_cells.append("z4")
            v2_cells.append(cell)
    return v1_cells, v2_cells


def pack_bars(v1_cells, v2_cells, beats_per_bar: int = 4):
    """Pack 4 quarter-note cells per 4/4 bar; return parallel bar lists."""
    bars1, bars2 = [], []
    for i in range(0, len(v1_cells), beats_per_bar):
        chunk1 = v1_cells[i:i + beats_per_bar]
        chunk2 = v2_cells[i:i + beats_per_bar]
        while len(chunk1) < beats_per_bar:
            chunk1.append("z4")
            chunk2.append("z4")
        bars1.append(" ".join(chunk1))
        bars2.append(" ".join(chunk2))
    return bars1, bars2


LINE_BUDGET_BARS = 3  # bars per system (rolled chords are wide)


def render_drill_abc(idx: int, pattern: str, note: str):
    rows = sweep_for(pattern)
    if not rows:
        return None, None, 0
    v1_cells, v2_cells = split_voices(rows)
    bars1, bars2 = pack_bars(v1_cells, v2_cells)

    abc_lines = []
    abc_lines.append(f"X:{idx}")
    abc_lines.append(f"T:Shape {pattern} sweep -- {note}")
    abc_lines.append("T:Eb 33-string harp - low to high")
    abc_lines.append("M:4/4")
    abc_lines.append("L:1/16")
    abc_lines.append('Q:1/4=72')
    abc_lines.append("K:Eb")
    abc_lines.append("%%scale 0.72")
    abc_lines.append("%%pagewidth 22cm")
    abc_lines.append("%%leftmargin 1cm")
    abc_lines.append("%%rightmargin 1cm")
    abc_lines.append("%%annotationfont Times-Italic 12")
    abc_lines.append("%%setfont-1 Times-Bold 14")
    abc_lines.append("%%score {V1 V2}")
    abc_lines.append("V:V1 clef=treble")
    abc_lines.append("V:V2 clef=bass")

    # Pack bars into systems of LINE_BUDGET_BARS bars each.
    v1_systems, v2_systems = [], []
    for i in range(0, len(bars1), LINE_BUDGET_BARS):
        v1_systems.append(" | ".join(bars1[i:i + LINE_BUDGET_BARS]) + " |")
        v2_systems.append(" | ".join(bars2[i:i + LINE_BUDGET_BARS]) + " |")
    abc_lines.append("[V:V1]")
    abc_lines.extend(v1_systems)
    abc_lines.append("[V:V2]")
    abc_lines.extend(v2_systems)

    return "\n".join(abc_lines) + "\n", f"{pattern}: {note}", len(rows)


def add_viewbox(svg_text: str) -> str:
    m = re.search(r'<svg[^>]*width="([\d.]+)px"\s+height="([\d.]+)px"', svg_text)
    if not m or 'viewBox=' in svg_text:
        return svg_text
    w, h = m.group(1), m.group(2)
    return svg_text.replace(
        m.group(0),
        m.group(0) + f' viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet"',
        1,
    )


def build_one(idx: int, pattern: str, note: str):
    abc, title, count = render_drill_abc(idx, pattern, note)
    if not abc:
        return None
    safe_pat = pattern
    slug = f"{idx:02d}_{safe_pat}"
    abc_path = STAGE / f"{slug}.abc"
    abc_path.write_text(abc, encoding="utf-8")
    out_prefix = STAGE / slug
    try:
        subprocess.run(
            ["abcm2ps", str(abc_path), "-g", "-O", str(out_prefix)],
            check=True, capture_output=True, timeout=20,
        )
    except subprocess.CalledProcessError as e:
        print(f"  FAIL {slug}: abcm2ps: {e.stderr.decode()[:200]}")
        return None
    svgs = sorted(STAGE.glob(f"{slug}[0-9][0-9][0-9].svg"))
    if not svgs:
        print(f"  FAIL {slug}: no svg")
        return None
    # If the drill produced multiple pages, concatenate by writing a
    # single multi-page record. For now we reference page 1 only and
    # log the page count for the user.
    svg_text = svgs[0].read_text(encoding="utf-8")
    svg_text = add_viewbox(svg_text)
    (DEST_SVG / f"{slug}.svg").write_text(svg_text, encoding="utf-8")
    extra_pages = []
    for k, extra in enumerate(svgs[1:], start=2):
        extra_text = add_viewbox(extra.read_text(encoding="utf-8"))
        extra_path = DEST_SVG / f"{slug}-p{k}.svg"
        extra_path.write_text(extra_text, encoding="utf-8")
        extra_pages.append(f"eb_shapes/sweeps/{slug}-p{k}.svg")
    return {
        "idx": idx,
        "slug": slug,
        "title": title,
        "pattern": pattern,
        "note": note,
        "iterations": count,
        "svg": f"eb_shapes/sweeps/{slug}.svg",
        "extra_pages": extra_pages,
        "pages": 1 + len(extra_pages),
    }


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    DEST_SVG.mkdir(parents=True, exist_ok=True)
    for old in DEST_SVG.glob("*.svg"):
        old.unlink()

    drills = []
    for idx, (pat, note) in enumerate(PATTERNS, start=1):
        rec = build_one(idx, pat, note)
        if rec is None:
            print(f"  SKIP pattern {pat}: no in-range positions")
            continue
        print(f"  {idx:02d} {pat:<5} {rec['iterations']:>3} positions, "
              f"{rec['pages']} page(s)")
        drills.append(rec)

    print(f"Built {len(drills)} drills total")
    js = ("window.EB_SHAPE_DRILLS = "
          + json.dumps(drills, indent=2, ensure_ascii=False) + ";\n")
    INDEX_JS.write_text(js, encoding="utf-8")
    print(f"Wrote index: {INDEX_JS}")


if __name__ == "__main__":
    main()
