#!/usr/bin/env python3
"""Boddie Drills -- one card per chord-bearing cell of the Chords.html matrix.

Drives from `shapes/build_chord_table.py`'s (interval-pattern x scale-degree)
matrix. Skips the 4 dyad rows (intervals, not chords), the `45` triad row
(degenerates to a 4th-dyad name), and any cells whose name is purely
dissonant (b9 stack on B/F/B-rooted shapes). All remaining cells become
2-bar Boddie ABC drill cards: bar 1 = bass + ascending arpeggio, bar 2 =
wide rolled chord with fermata.

Output:
  - tablet_app/.../boddie/drills/<NN>_<row>_<deg>.svg
  - tablet_app/.../boddie/boddie_drills.js  (window.BODDIE_DRILLS)

Run from anywhere:

    python3 boddie/drills/build_drills.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Matrix definitions -- imported from shapes/build_chord_table.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shapes"))
from build_chord_table import PATTERNS, shape_pitches, short_chord_name  # noqa

REPO = Path(__file__).resolve().parents[2]
DEST_SVG = REPO / "tablet_app" / "app" / "src" / "main" / "assets" / "boddie" / "drills"
INDEX_JS = REPO / "tablet_app" / "app" / "src" / "main" / "assets" / "boddie" / "boddie_drills.js"
STAGE = Path("/tmp/boddie_drills_stage")

# Rows we exclude from the deck (dyads + the degenerate 45 row).
SKIP_PATTERNS = {"3", "4", "5", "8", "45"}


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


def is_chord_bearing(name: str) -> bool:
    """Reject cells whose chord name is dissonant or non-chord. Specifically:

    - any name containing `(♭9)` -- the diminished/minor-flat-9 voicings
      that Brook would not use as figuration material
    - bare interval names (still possible if a row like `45` slipped
      through; defensive)
    """
    if "(♭9)" in name or "(b9)" in name:
        return False
    if " quartal" in name and "/" in name:
        return False  # quartal slash-chords are too vague for a drill card
    if name.startswith("-") or name.endswith("-"):
        return False
    return True


# -----------------------------------------------------------------------------
# Pitch -> ABC

LETTER_BY_NAME = "CDEFGAB"


def pitch_name_to_abc(name: str, octv: int) -> str:
    """Render a music21 Pitch.name + octave to ABC (no accidentals
    needed -- chord matrix is built in pure-natural C major).
    """
    letter = name[0]
    if octv >= 5:
        return letter.lower() + "'" * (octv - 5)
    return letter.upper() + "," * (4 - octv)


# -----------------------------------------------------------------------------
# Boddie figuration of one cell

def figure_cell(degree: int, intervals: str):
    """Return (bar1_abc, bar2_abc) for one chord-matrix cell rendered in
    Boddie LH arpeggio style. All in C major.
    """
    pitches = shape_pitches(degree, intervals, base_octave=4)
    # Bass register (octave 2) -- bottom note of the chord transposed down.
    # Drone (octave 1) -- root letter at octave 1.
    bass_letter = pitches[0].name
    drone = pitch_name_to_abc(bass_letter, 1)
    bass = pitch_name_to_abc(bass_letter, 2)

    # Arpeggio register (octave 3 climbing into 4) -- restate each chord
    # tone an octave above its lowest position.
    arp = []
    for p in pitches:
        oct_for_arp = max(3, p.octave - 1)  # if base_octave=4 -> 3
        arp.append(pitch_name_to_abc(p.name, oct_for_arp))

    # Build 8 eighth-note cells (4/4 = 16 sixteenths = 8 eighths).
    # Cell 1: drone+bass octave pluck. Cells 2-8: rising arpeggio looping.
    bar1_cells = [f"[{drone}{bass}]"] + [arp[i % len(arp)] for i in range(7)]
    bar1 = " ".join(f"{c}2" for c in bar1_cells)

    # Bar 2: wide-spread rolled chord -- all pitches at octave 2 + bass
    # drone added below.
    spread = [drone] + [pitch_name_to_abc(p.name, 2) for p in pitches]
    bar2 = "!fermata!!arpeggio![" + "".join(spread) + "]16"
    return bar1, bar2


def render_drill_abc(idx: int, pat: str, note: str, degree: int, name: str) -> tuple[str, str]:
    bar1, bar2 = figure_cell(degree, pat)
    title = f"{name}  ({pat} · ˆ8̂{degree})"
    abc = []
    abc.append(f"X:{idx}")
    abc.append(f"T:{name}")
    abc.append(f"T:{pat}  -  degree {degree}  -  {note}")
    abc.append("M:4/4")
    abc.append("L:1/16")
    abc.append('Q:1/4=72 "Slowly, with great expression"')
    abc.append("K:C")
    abc.append("%%scale 0.95")
    abc.append("%%annotationfont Times-Italic 14")
    abc.append("%%setfont-1 Times-Bold 16")
    abc.append("%%setfont-2 Times-Italic 12")
    abc.append("%%score {V1 V2}")
    abc.append("V:V1 clef=treble")
    abc.append("V:V2 clef=bass")
    # Treble: chord-as-rolled-block + fermata in bar 2 (mirrors Brook's
    # treble verticals on cadence bars).
    pitches = shape_pitches(degree, pat, base_octave=4)
    treble_chord = "!arpeggio![" + "".join(pitch_name_to_abc(p.name, p.octave)
                                          for p in pitches) + "]"
    abc.append(f'[V:V1] "^{name}" {treble_chord}16 | !fermata!{treble_chord}16 |')
    abc.append(f"[V:V2] {bar1} | {bar2} |")
    return "\n".join(abc) + "\n", title


def build_one(idx: int, pat: str, note: str, degree: int) -> dict | None:
    pitches = shape_pitches(degree, pat, base_octave=4)
    name = short_chord_name(pitches)
    if not is_chord_bearing(name):
        return None
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "chord"
    slug = f"{idx:03d}_{pat}_d{degree}_{safe_name}"
    abc, title = render_drill_abc(idx, pat, note, degree, name)
    abc_path = STAGE / f"{slug}.abc"
    abc_path.write_text(abc, encoding="utf-8")
    out_prefix = STAGE / slug
    try:
        subprocess.run(
            ["abcm2ps", str(abc_path), "-g", "-O", str(out_prefix)],
            check=True, capture_output=True, timeout=15,
        )
    except subprocess.CalledProcessError as e:
        print(f"  FAIL {slug}: abcm2ps: {e.stderr.decode()[:200]}")
        return None
    svgs = sorted(STAGE.glob(f"{slug}[0-9][0-9][0-9].svg"))
    if not svgs:
        print(f"  FAIL {slug}: no svg")
        return None
    svg_text = svgs[0].read_text(encoding="utf-8")
    svg_text = add_viewbox(svg_text)
    (DEST_SVG / f"{slug}.svg").write_text(svg_text, encoding="utf-8")
    return {
        "idx": idx,
        "slug": slug,
        "title": name,
        "pattern": pat,
        "degree": degree,
        "row_note": note,
        "svg": f"boddie/drills/{slug}.svg",
    }


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    DEST_SVG.mkdir(parents=True, exist_ok=True)
    # Wipe stale drill SVGs from the previous (28-card) build so leftover
    # files don't sit alongside the new deck.
    for old in DEST_SVG.glob("*.svg"):
        old.unlink()

    drills = []
    skipped = 0
    idx = 0
    for pat, note in PATTERNS:
        if pat in SKIP_PATTERNS:
            skipped += 7
            continue
        for degree in range(1, 8):
            idx += 1
            rec = build_one(idx, pat, note, degree)
            if rec is None:
                skipped += 1
                continue
            drills.append(rec)
    print(f"Built {len(drills)} drill cards (skipped {skipped} cells)")
    js = "window.BODDIE_DRILLS = " + json.dumps(drills, indent=2,
                                                ensure_ascii=False) + ";\n"
    INDEX_JS.write_text(js, encoding="utf-8")
    print(f"Wrote index: {INDEX_JS}")


if __name__ == "__main__":
    main()
