#!/usr/bin/env python3
"""Build side-by-side SATB-vs-Jazz comparison pages (279 total).

Column order (beat-1 row shows legacy + chord; subsequent beats blank):
    bar.beat  <pedal>  <35-col SATB strip>  legacy-RN  <jazz-pedal>  chord  <47-col jazz strip>

Pedal column = 4-cell braille pedal diagram.
  - SATB side: shown at bar 1 beat 1 with the initial key-signature pedal
    setting.  Shown again at any beat where a SATB accidental forces a
    pedal move.  Blank otherwise.
  - Jazz side: modal treatment (Ionian for major hymns; Aeolian for minor
    unless overridden to Dorian in data/reharm/mode_overrides.json).
    Levers are set once at piece start and never flipped mid-piece
    (REHARM_TACTICS Decision 5), so the jazz pedal diagram appears only
    on bar 1 beat 1 and is blank elsewhere.

Jazz strip rendering: for each bar, the chosen best-variation's
``bars[i].lh + bars[i].rh`` notes are placed at ``(oct-1)*7 + (deg-1)``
on a 47-column strip.  Rendered only on each bar's beat-1 row; subsequent
beats in the bar leave the strip blank.

Hymns and jazz voicings are rendered in their native keys — no transposition.

Sources:
  legacy/hymnal_export/<Title>.json       → beats[] with per-beat S/A/T/B
  data/hymns/<slug>.json                  → bars[].chord (per-bar RN)
  data/jazz/<slug>.json                   → bars[].spec (per-bar jazz chord)
  data/reharm/variations/<slug>/v*.json   → candidate reharm variations
  data/reharm/mode_overrides.json         → per-hymn dorian overrides

Output: jazz/compare/<slug>.html
"""
from __future__ import annotations
import html
import json
import re
import sys
from pathlib import Path

# Allow running both as `python3 trefoil/build_compare_pages.py` and as
# `python3 -m trefoil.build_compare_pages`.
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from music21 import pitch

from trefoil.pedal import (
    PEDAL_CELLS, initial_pedal_state, pedals_to_braille,
    pitch_letter_alter, plan_bar_pedal_events,
)
from trefoil.reharm.legality import score_variation

ROOT = Path(__file__).resolve().parent.parent
HYMNS = ROOT / "data" / "hymns"
JAZZ = ROOT / "data" / "jazz"
LEGACY = ROOT / "legacy" / "hymnal_export"
VARIATIONS = ROOT / "data" / "reharm" / "variations"
MODE_OVERRIDES = ROOT / "data" / "reharm" / "mode_overrides.json"
OUT = ROOT / "jazz" / "compare"

LETTERS = ["C", "D", "E", "F", "G", "A", "B"]
LETTER_IDX = {l: i for i, l in enumerate(LETTERS)}

SATB_OCT_LOW, SATB_OCT_HIGH = 2, 6
SATB_COLS = (SATB_OCT_HIGH - SATB_OCT_LOW + 1) * 7   # 35

JAZZ_COLS = 47    # C1..G7

CHORD_WIDTH = 7   # matches legacy col width for alignment
LEGACY_WIDTH = 7


# ───────────────────── Grid rendering ─────────────────────

def satb_col(letter: str, octv: int) -> int | None:
    if octv < SATB_OCT_LOW or octv > SATB_OCT_HIGH:
        return None
    if letter not in LETTER_IDX:
        return None
    return (octv - SATB_OCT_LOW) * 7 + LETTER_IDX[letter]


def build_satb_strip(beat: dict) -> str:
    grid = ["."] * SATB_COLS
    for voice in ("S", "A", "T", "B"):
        p_str = beat.get(voice)
        if not p_str:
            continue
        try:
            p = pitch.Pitch(p_str)
        except Exception:
            continue
        col = satb_col(p.step, p.octave)
        if col is not None:
            grid[col] = p.step
    return "".join(grid)


# ───────────────────── Label helpers ─────────────────────

ROMAN_UC = {"I": "Ⅰ", "II": "Ⅱ", "III": "Ⅲ", "IV": "Ⅳ",
            "V": "Ⅴ", "VI": "Ⅵ", "VII": "Ⅶ"}
ROMAN_LC = {"i": "ⅰ", "ii": "ⅱ", "iii": "ⅲ", "iv": "ⅳ",
            "v": "ⅴ", "vi": "ⅵ", "vii": "ⅶ"}


def roman_unicode_numeral(num: str) -> str:
    """Convert the roman-letter part of a numeral to Unicode roman while
    preserving any leading accidental (`b`, `#`, `♭`, `♯`) and any trailing
    quality suffix (e.g., `°`, `○`, `ø`, etc.) attached to the numeral."""
    if not num:
        return ""
    m = re.match(r"^([b#♭♯]*)([IVXivx]+)(.*)$", num)
    if not m:
        return num
    pref, rn, suf = m.groups()
    return pref + (ROMAN_UC.get(rn) or ROMAN_LC.get(rn) or rn) + suf


def legacy_label_for_bar(bar_chord: dict | None) -> str:
    if not bar_chord:
        return ""
    num = bar_chord.get("numeral") or ""
    qual = bar_chord.get("quality") or ""
    return roman_unicode_numeral(num) + qual


def pretty_fraction_label(bar: dict | None) -> str:
    if not bar:
        return ""
    spec = bar.get("spec") or {}
    num = spec.get("numeral") or ""
    if not num:
        return ""
    qual = spec.get("quality", "") or ""
    return roman_unicode_numeral(num) + qual


# ───────────────────── Slug mapping ─────────────────────

SLUG_PAT = re.compile(r"_+")


def build_legacy_map() -> dict[str, Path]:
    m = {}
    for p in LEGACY.glob("*.json"):
        slug = SLUG_PAT.sub("_", p.stem.lower()).strip("_")
        m[slug] = p
    return m


# ───────────────────── Jazz variation picking ─────────────────────

# Cache score_variation results so each variation is scored at most once
# across the whole run.
_BEST_VARIATION_CACHE: dict[str, dict | None] = {}


def pick_best_variation(slug: str) -> dict | None:
    """Return the highest-total-score variation JSON for this hymn, or None.

    Ties on ``total_score`` are broken by lowest ``variation_index`` (the
    ``v##`` number in the filename).  Cached in memory.
    """
    if slug in _BEST_VARIATION_CACHE:
        return _BEST_VARIATION_CACHE[slug]

    vdir = VARIATIONS / slug
    if not vdir.is_dir():
        _BEST_VARIATION_CACHE[slug] = None
        return None

    files = sorted(vdir.glob("v*.json"))
    best: dict | None = None
    best_score: float = -1e18
    best_idx: int = 10**9
    best_filename: str = ""

    for f in files:
        try:
            var = json.loads(f.read_text())
        except Exception:
            continue
        try:
            s = score_variation(var)
            total = float(s.get("total_score", 0.0))
        except Exception:
            continue
        idx = int(var.get("variation_index") or 10**9)
        if (total > best_score) or (total == best_score and idx < best_idx):
            best = var
            best_score = total
            best_idx = idx
            best_filename = f.stem
            # Stash the resolved score so the compare-page footer can show it
            # without rescoring later.
            best["_resolved_total_score"] = total
            best["_resolved_variation_index"] = idx
            best["_resolved_variation_stem"] = best_filename

    _BEST_VARIATION_CACHE[slug] = best
    return best


def jazz_mode_for(slug: str, src_mode: str, overrides: dict) -> str:
    """Return ``"ionian"``, ``"aeolian"``, or ``"dorian"`` for the jazz side."""
    if src_mode.lower() != "minor":
        return "ionian"
    resolved = (overrides.get("overrides") or {}).get(slug)
    if resolved in ("aeolian", "dorian"):
        return resolved
    return "aeolian"


def jazz_initial_pedal(key_root: str, mode: str) -> dict[str, int]:
    """Initial pedal state for the jazz side, honoring Ionian/Aeolian/Dorian.

    music21's Key supports ``"major"``/``"minor"`` plus the Greek modal
    names, so we map our internal labels directly.
    """
    mode_key = {
        "ionian":  "major",
        "aeolian": "minor",
        "dorian":  "dorian",
    }.get(mode, "major")
    return initial_pedal_state(key_root, mode_key)


# ───────────────────── Jazz strip rendering ─────────────────────

JAZZ_STRIP_BLANK = " " * JAZZ_COLS


def _jazz_string_index(note) -> int | None:
    """Map a [deg, oct] pair (1..7 deg, 1..7 oct) to a 0-indexed 47-col slot.

    Uses the shape-library formula ``(oct-1)*7 + (deg-1)`` (zero-indexed).
    Returns None when the note is malformed or out of range.
    """
    if not note or len(note) < 2:
        return None
    try:
        deg = int(note[0])
        octv = int(note[1])
    except (TypeError, ValueError):
        return None
    if deg < 1 or deg > 7:
        return None
    col = (octv - 1) * 7 + (deg - 1)
    if col < 0 or col >= JAZZ_COLS:
        return None
    return col


# Degree → letter using C-based diatonic mapping (matches pretty-fraction /
# shape-library convention: 1=C, 2=D, 3=E, 4=F, 5=G, 6=A, 7=B).
_JAZZ_DEG_LETTER = {1: "C", 2: "D", 3: "E", 4: "F", 5: "G", 6: "A", 7: "B"}


def build_jazz_strip(bar_entry: dict | None) -> str:
    """Render one bar's LH+RH shape onto a 47-cell strip.

    ``bar_entry`` is a single element of ``variation["bars"]``.  Returns
    a 47-char string with letters at each populated string slot and
    spaces elsewhere.  Returns a full-blank strip when the entry has no
    voicing (e.g. the selector could not find a shape for this chord).
    """
    if not bar_entry:
        return JAZZ_STRIP_BLANK
    grid = [" "] * JAZZ_COLS
    for hand in ("lh", "rh"):
        for note in bar_entry.get(hand) or []:
            col = _jazz_string_index(note)
            if col is None:
                continue
            deg = int(note[0])
            grid[col] = _JAZZ_DEG_LETTER.get(deg, "?")
    return "".join(grid)


# ───────────────────── Page assembly ─────────────────────

PAGE_TPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Compare — {title}</title>
<style>
:root {{ --bg:#f7f3ea; --ink:#2a2a2a; --muted:#888; --line:#d8d0c0; --panel:#ffffff;
        --lhcol:#7B2B2B; --rhcol:#1F4E79; --banner:#7B2B2B; --pedalcol:#5A4A2B; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background:var(--bg); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
#topbar {{ padding:14px 24px; background:var(--banner); color:#fff;
  display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; }}
#topbar a {{ color:#fff; text-decoration:none; font-size:15px; }}
#topbar h1 {{ font-size:20px; }}
#topbar .meta {{ font-size:14px; opacity:.85; font-family:"Courier New",monospace; }}
#topbar .meta strong {{ font-weight:bold; }}
main {{ padding:20px 16px 60px; }}
.block {{ font-family:"DejaVu Sans Mono","Consolas","Menlo","Cascadia Mono","Courier New",monospace; font-size:10.5pt;
  background:var(--panel); border:1px solid var(--line); border-radius:6px;
  padding:10px 14px; overflow-x:auto; white-space:pre; line-height:1.35; }}
.block .hdr {{ color:var(--muted); font-weight:bold; }}
/* fixed-width columns so braille (which may not render at exactly 1ch) */
/* cannot push the SATB column out of alignment */
.block .bar-num {{ display:inline-block; width:6ch; color:var(--muted); font-weight:bold; }}
.block .pedal   {{ display:inline-block; width:5ch; color:var(--pedalcol); font-weight:bold; }}
.block .satb    {{ display:inline-block; width:35ch; color:var(--lhcol); }}
.block .legacy  {{ display:inline-block; width:7ch; }}
.block .chord   {{ display:inline-block; width:7ch; color:var(--muted); }}
.block .jazz    {{ display:inline-block; width:47ch; color:var(--rhcol); }}
.block .sep     {{ display:inline-block; width:2ch; }}
.footer {{ font-family:"DejaVu Sans Mono","Consolas","Menlo","Courier New",monospace;
  font-size:10pt; color:var(--muted); padding:8px 14px 0 14px; }}
</style></head><body>
<div id="topbar">
  <a href="../comparison.html">← Comparison</a>
  <h1>{title}</h1>
  <span class="meta"><strong>key</strong> {src_key} &nbsp;·&nbsp; <strong>time</strong> {meter} &nbsp;·&nbsp; jazz pool in C</span>
</div>
<main><div class="block"><span class="hdr">{hdr}</span>
{rows}</div>
<div class="footer">{footer}</div></main></body></html>
"""


PEDAL_WIDTH = 5   # 4 braille cells + 1 pad so "pedal" header fits exactly


def build_header() -> str:
    satb_hdr = [" "] * SATB_COLS
    for i, octv in enumerate(range(SATB_OCT_LOW, SATB_OCT_HIGH + 1)):
        pos = i * 7
        if pos < SATB_COLS:
            satb_hdr[pos] = str(octv)
    jazz_hdr = [" "] * JAZZ_COLS
    for octv in range(1, 8):
        pos = (octv - 1) * 7
        if pos < JAZZ_COLS:
            jazz_hdr[pos] = str(octv)
    return (
        f"{'#':<6}"
        f"{'pedal':<{PEDAL_WIDTH}}  "
        f"{''.join(satb_hdr)}  "
        f"{'legacy':<{LEGACY_WIDTH}}  "
        f"{'pedal':<{PEDAL_WIDTH}}  "
        f"{'chord':<{CHORD_WIDTH}}  "
        f"{''.join(jazz_hdr)}"
    )


def build_rows(by_bar: dict[int, list[dict]], hymn_bars: list[dict],
               jazz_bars: dict[int, dict], pedal_state: dict[str, int],
               variation_bars_by_bar: dict[int, dict] | None = None,
               jazz_pedal_state: dict[str, int] | None = None) -> str:
    rows = []
    first_row = True
    variation_bars_by_bar = variation_bars_by_bar or {}
    bar_nums = sorted(by_bar.keys())
    # Jazz-side pedal braille: rendered at bar 1 beat 1 only (no mid-piece
    # flips per REHARM_TACTICS Decision 5).  None means no variation is
    # available, so we leave the whole column blank.
    jazz_pedal_braille = (
        pedals_to_braille(jazz_pedal_state) if jazz_pedal_state else None
    )

    for bar_num in bar_nums:
        beats_in_bar = by_bar[bar_num]
        hymn_idx = bar_num - 1
        chord_spec = hymn_bars[hymn_idx].get("chord") if 0 <= hymn_idx < len(hymn_bars) else None
        legacy_lbl = legacy_label_for_bar(chord_spec)
        jazz_bar = jazz_bars.get(bar_num)
        chord_lbl = pretty_fraction_label(jazz_bar)
        variation_bar = variation_bars_by_bar.get(bar_num)
        jazz_strip = build_jazz_strip(variation_bar)

        # Plan bar-level pedal events (consolidates first change of each
        # pedal to the bar's first beat when safe).
        bar_events = plan_bar_pedal_events(beats_in_bar, pedal_state)

        for i, beat in enumerate(beats_in_bar):
            beat_num = beat.get("beat", i + 1)
            bar_beat = f"{bar_num}.{beat_num}"
            satb = build_satb_strip(beat)

            changes_here = bar_events.get(beat_num, {})
            if changes_here:
                pedal_state = {**pedal_state, **changes_here}
            render_pedal = first_row or bool(changes_here)
            pedal_str = pedals_to_braille(pedal_state) if render_pedal else " " * PEDAL_CELLS

            show_bar_cols = (i == 0)
            legacy_cell = legacy_lbl if show_bar_cols else ""
            chord_cell = chord_lbl if show_bar_cols else ""
            # Jazz pedal: only on bar 1 beat 1, per Decision 5.
            if first_row and jazz_pedal_braille is not None:
                jazz_pedal_str = jazz_pedal_braille
            else:
                jazz_pedal_str = " " * PEDAL_CELLS
            # Jazz strip: only on each bar's beat-1 row.
            jazz_cell = jazz_strip if show_bar_cols else " " * JAZZ_COLS

            first_row = False

            row = (
                f'<span class="bar-num">{bar_beat}</span>'
                f'<span class="pedal">{pedal_str}</span>'
                f'<span class="sep"> </span>'
                f'<span class="satb">{html.escape(satb)}</span>'
                f'<span class="sep"> </span>'
                f'<span class="legacy">{html.escape(legacy_cell)}</span>'
                f'<span class="sep"> </span>'
                f'<span class="pedal">{jazz_pedal_str}</span>'
                f'<span class="sep"> </span>'
                f'<span class="chord">{html.escape(chord_cell)}</span>'
                f'<span class="sep"> </span>'
                f'<span class="jazz">{jazz_cell}</span>'
            )
            rows.append(row)
    return "\n".join(rows)


def hymn_number(abc_src: str) -> str | None:
    m = re.search(r"^X:\s*(\d+)", abc_src, re.MULTILINE)
    return m.group(1) if m else None


def build_page(new_slug: str, legacy_path: Path,
               mode_overrides: dict | None = None) -> str:
    hymn = json.loads((HYMNS / f"{new_slug}.json").read_text())
    jazz = json.loads((JAZZ / f"{new_slug}.json").read_text()) \
        if (JAZZ / f"{new_slug}.json").exists() else {"bars": []}
    legacy = json.loads(legacy_path.read_text())

    title = hymn.get("title") or new_slug.replace("_", " ").title()
    num = hymn_number(hymn.get("_abc_source", ""))
    if num:
        title = f"{int(num):03d} {title}"
    meter = hymn.get("meter") or {}
    meter_str = f"{meter.get('beats', '?')}/{meter.get('unit', '?')}"
    src_key_root = legacy["music"]["key_root"]
    src_mode = legacy["music"]["mode"]
    src_key = f"{src_key_root} {src_mode}"

    beats = legacy.get("beats", [])
    by_bar: dict[int, list[dict]] = {}
    for b in beats:
        by_bar.setdefault(b["bar"], []).append(b)
    for bar_beats in by_bar.values():
        bar_beats.sort(key=lambda x: x.get("beat", 0))

    jazz_bars: dict[int, dict] = {jb.get("bar", i + 1): jb
                                   for i, jb in enumerate(jazz.get("bars", []))}
    hymn_bars = hymn.get("bars", [])

    pedal_state = initial_pedal_state(src_key_root, src_mode)

    # Jazz side: pick the best variation by total_score, derive its bar map,
    # and compute the single-flip initial pedal from the hymn's jazz mode.
    overrides = mode_overrides or {}
    best = pick_best_variation(new_slug)
    if best is not None:
        variation_bars = best.get("bars") or []
        variation_bars_by_bar = {
            vb.get("bar", i + 1): vb
            for i, vb in enumerate(variation_bars)
        }
        jazz_mode = jazz_mode_for(new_slug, src_mode, overrides)
        jazz_pedal_state = jazz_initial_pedal(src_key_root, jazz_mode)
        jazz_var_stem = best.get("_resolved_variation_stem") or "?"
        jazz_total = best.get("_resolved_total_score", 0.0)
        footer_text = (
            f"jazz variation: {jazz_var_stem} "
            f"(total_score {jazz_total:.2f}) · mode: {jazz_mode}"
        )
    else:
        variation_bars_by_bar = {}
        jazz_pedal_state = None
        footer_text = "jazz variation: (none available)"

    rows = build_rows(
        by_bar, hymn_bars, jazz_bars, pedal_state,
        variation_bars_by_bar=variation_bars_by_bar,
        jazz_pedal_state=jazz_pedal_state,
    )

    return PAGE_TPL.format(
        title=html.escape(title),
        src_key=html.escape(src_key),
        meter=html.escape(meter_str),
        hdr=html.escape(build_header()),
        rows=rows,
        footer=html.escape(footer_text),
    )


def main():
    import time
    OUT.mkdir(parents=True, exist_ok=True)
    legacy_map = build_legacy_map()
    hymns = sorted(HYMNS.glob("*.json"))

    # Load mode overrides once.
    try:
        mode_overrides = json.loads(MODE_OVERRIDES.read_text())
    except Exception:
        mode_overrides = {}

    t0 = time.time()
    ok = 0
    populated = 0
    fail = []
    for h in hymns:
        slug = h.stem
        legacy_path = legacy_map.get(slug)
        if not legacy_path:
            fail.append((slug, "no legacy match"))
            continue
        try:
            page = build_page(slug, legacy_path, mode_overrides=mode_overrides)
            (OUT / f"{slug}.html").write_text(page)
            ok += 1
            if _BEST_VARIATION_CACHE.get(slug) is not None:
                populated += 1
        except Exception as e:
            fail.append((slug, f"{type(e).__name__}: {e}"))
    elapsed = time.time() - t0
    print(f"ok: {ok}  jazz-populated: {populated}  failed: {len(fail)}  "
          f"elapsed: {elapsed:.1f}s")
    for slug, err in fail[:10]:
        print(f"  {slug}: {err}")


if __name__ == "__main__":
    main()
