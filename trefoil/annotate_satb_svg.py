#!/usr/bin/env python3
"""Annotate SATB ABC sources with music21-derived roman-numeral labels AND
braille pedal diagrams, then re-run abc2svg to produce annotated SVG pages.

Per bar, two ABC annotations may attach to the first note of the top voice:
  1. Pedal braille diagram (4 Unicode cells) — whenever the bar's entering
     pedal state differs from the previous bar (i.e., pulled/consolidated
     changes planned by `trefoil.pedal.plan_bar_pedal_events`). Also always
     shown on the first bar of the piece.
  2. Roman numeral + quality from the new chord grammar (no inversion).

Sources:
  data/hymns/<slug>.json            → bars[].chord (per-bar RN)
  legacy/hymnal_export/<Title>.json → beats[] with per-beat S/A/T/B (drives
                                      the pedal planner)

Output: data/abc_svg/<slug>.html  (overwrites existing)
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trefoil.pedal import (
    initial_pedal_state, pedals_to_braille, plan_bar_pedal_events,
)

ROOT = Path(__file__).resolve().parent.parent
HYMNS = ROOT / "data" / "hymns"
LEGACY = ROOT / "legacy" / "hymnal_export"
OUT = ROOT / "data" / "abc_svg"
ABC2SVG = ROOT / "node_modules" / "abc2svg" / "abc2svg"

ROMAN_UC = {"I": "Ⅰ", "II": "Ⅱ", "III": "Ⅲ", "IV": "Ⅳ",
            "V": "Ⅴ", "VI": "Ⅵ", "VII": "Ⅶ"}
ROMAN_LC = {"i": "ⅰ", "ii": "ⅱ", "iii": "ⅲ", "iv": "ⅳ",
            "v": "ⅴ", "vi": "ⅵ", "vii": "ⅶ"}


def roman_unicode(numeral: str) -> str:
    """Convert roman letters to Unicode, preserving prefix accidentals and
    any trailing quality marker (e.g., `°`, `○`, `ø`)."""
    if not numeral:
        return ""
    m = re.match(r"^([b#♭♯]*)([IVXivx]+)(.*)$", numeral)
    if not m:
        return numeral
    prefix, rn, suffix = m.groups()
    uni = ROMAN_UC.get(rn) or ROMAN_LC.get(rn) or rn
    return prefix + uni + suffix


def legacy_label(chord: dict | None) -> str:
    if not chord:
        return ""
    num = chord.get("numeral") or ""
    qual = chord.get("quality") or ""
    return roman_unicode(num) + qual


NOTE_RE = re.compile(r"[A-Ga-gz]")


def inject_labels(bar_body: str, labels: list[str]) -> str:
    """Insert one or more `"^label"` annotations at the start of the bar,
    past leading whitespace and inline `[Q:...]` / `[K:...]` directives.

    Each non-empty label becomes its own `"^..."` annotation. abc2svg stacks
    them vertically above the staff in source order (earlier label = closer
    to the staff / lower stack position).
    """
    non_empty = [l for l in labels if l]
    if not non_empty:
        return bar_body
    annotation = "".join(f'"^{l}"' for l in non_empty)
    i = 0
    n = len(bar_body)
    while i < n:
        c = bar_body[i]
        if c in " \t":
            i += 1
            continue
        if c == "[" and i + 2 < n and bar_body[i + 1].isupper() \
                and bar_body[i + 2] == ":":
            j = bar_body.find("]", i + 1)
            if j == -1:
                break
            i = j + 1
            continue
        return bar_body[:i] + annotation + bar_body[i:]
    return bar_body


TOP_VOICES = ("S1V1", "S1")  # prefer S1V1 (4-voice); fall back to S1 (2-staff)


def pick_top_voice(abc_src: str) -> str:
    for v in TOP_VOICES:
        if re.search(rf"\[V:\s*{v}\b", abc_src):
            return v
    return TOP_VOICES[0]


def top_voice_line_iter(lines: list[str], voice: str):
    """Yield (line_index, line_text) for every [V: <voice>] line."""
    token = re.compile(rf"\[V:\s*{voice}\b")
    for i, ln in enumerate(lines):
        if token.search(ln):
            yield i, ln


def count_bar_segments(line: str) -> int:
    """Count non-empty, non-trailing bar segments in one S1V1 line.

    A bar segment is a `|`-delimited chunk that contains at least one note char.
    """
    # Drop [V: ...] header and any [Q: ...] directives for counting
    body = re.sub(r"\[V:[^\]]*\]", "", line)
    segs = body.split("|")
    count = 0
    for s in segs:
        stripped = s.strip()
        if not stripped or stripped == "]":
            continue
        if NOTE_RE.search(re.sub(r"\[[A-Z]:[^\]]*\]", "", stripped)):
            count += 1
    return count


def annotate_line(line: str, bar_labels: list[list[str]], start_idx: int,
                  skip_pickup: bool) -> tuple[str, int]:
    """Inject labels into one top-voice line. `bar_labels[i]` is a list of
    annotation strings for bar i+1 (earlier = closer to the staff). Returns
    (new_line, next_label_idx)."""
    header_match = re.match(r"^(\s*\[V:[^\]]*\])(.*)$", line, re.DOTALL)
    if not header_match:
        return line, start_idx
    header = header_match.group(1)
    body = header_match.group(2)

    segs = body.split("|")
    out_segs = []
    idx = start_idx
    for seg_i, seg in enumerate(segs):
        stripped = seg.strip()
        is_real_bar = bool(stripped) and stripped != "]" and \
            NOTE_RE.search(re.sub(r"\[[A-Z]:[^\]]*\]", "", stripped))
        if not is_real_bar:
            out_segs.append(seg)
            continue
        if skip_pickup and idx == -1:
            idx = 0
            out_segs.append(seg)
            continue
        if idx >= len(bar_labels):
            out_segs.append(seg)
            continue
        out_segs.append(inject_labels(seg, bar_labels[idx]))
        idx += 1
    return header + "|".join(out_segs), idx


def compute_pedal_labels_per_bar(legacy: dict, n_bars: int) -> list[str]:
    """Compute a per-bar pedal-braille label. Entry is empty string if no
    diagram should be shown at that bar.

    Shown on:
      - bar 1 of the piece (initial key-sig state)
      - any bar where the consolidation planner emits at least one event
    The displayed state is the pedal state *after* all events in that bar
    are applied, so the player can see where the pedals need to end up.
    """
    labels = [""] * n_bars
    if not legacy:
        return labels
    src_key_root = legacy["music"]["key_root"]
    src_mode = legacy["music"]["mode"]
    state = initial_pedal_state(src_key_root, src_mode)

    beats = legacy.get("beats", [])
    by_bar: dict[int, list[dict]] = {}
    for b in beats:
        by_bar.setdefault(b["bar"], []).append(b)
    for bar_beats in by_bar.values():
        bar_beats.sort(key=lambda x: x.get("beat", 0))

    labels[0] = pedals_to_braille(state)
    sorted_bars = sorted(by_bar.keys())
    prev_bar_had_change = False
    for bar_num in sorted_bars:
        idx = bar_num - 1
        if idx < 0 or idx >= n_bars:
            continue
        bar_beats = by_bar[bar_num]
        events = plan_bar_pedal_events(bar_beats, state)
        if events:
            for _beat, changes in sorted(events.items()):
                state = {**state, **changes}
            if idx != 0:
                labels[idx] = pedals_to_braille(state)
    return labels


def annotate_abc(abc_src: str, bars: list[dict], legacy: dict | None) -> str:
    chord_labels = [legacy_label(b.get("chord")) for b in bars]
    pedal_labels = compute_pedal_labels_per_bar(legacy, len(bars)) \
        if legacy else [""] * len(bars)
    # Per-bar annotation list: [pedal, chord]  — pedal closer to staff.
    bar_labels = [
        [pedal_labels[i], chord_labels[i]] for i in range(len(bars))
    ]
    n_bars = len(bar_labels)

    lines = abc_src.split("\n")
    voice = pick_top_voice(abc_src)
    top_lines = list(top_voice_line_iter(lines, voice))
    total_segs = sum(count_bar_segments(ln) for _, ln in top_lines)

    skip_pickup = (total_segs == n_bars + 1)

    idx = -1 if skip_pickup else 0
    for i, ln in top_lines:
        lines[i], idx = annotate_line(ln, bar_labels, idx, skip_pickup)
        skip_pickup = False
    return "\n".join(lines)


def preprocess_abc(src: str) -> str:
    src = src.replace("%%combinevoices", "%%voicecombine")
    src = re.sub(r"!s?intro!", "", src)
    src = re.sub(r"!e?intro!", "", src)
    return src


def render_abc_to_svg(abc_text: str, out_path: Path) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".abc", delete=False) as f:
        f.write(abc_text)
        tmp = f.name
    try:
        result = subprocess.run(
            [str(ABC2SVG), tmp],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            out_path.write_text(result.stdout)
        return result.returncode == 0, result.stderr
    finally:
        Path(tmp).unlink(missing_ok=True)


SLUG_PAT = re.compile(r"_+")


def build_legacy_map() -> dict[str, Path]:
    m = {}
    for p in LEGACY.glob("*.json"):
        slug = SLUG_PAT.sub("_", p.stem.lower()).strip("_")
        m[slug] = p
    return m


def build_one(json_path: Path, out_dir: Path,
              legacy_path: Path | None) -> tuple[bool, str]:
    d = json.loads(json_path.read_text())
    abc = d.get("_abc_source", "")
    if not abc:
        return False, "no _abc_source"
    bars = d.get("bars", [])
    legacy = json.loads(legacy_path.read_text()) if legacy_path else None
    annotated = annotate_abc(abc, bars, legacy)
    annotated = preprocess_abc(annotated)
    slug = json_path.stem
    return render_abc_to_svg(annotated, out_dir / f"{slug}.html")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    legacy_map = build_legacy_map()
    hymns = sorted(HYMNS.glob("*.json"))
    ok = 0
    fail = []
    for j in hymns:
        legacy_path = legacy_map.get(j.stem)
        success, err = build_one(j, OUT, legacy_path)
        if success:
            ok += 1
        else:
            fail.append((j.name, err.strip().splitlines()[:2] if err else ["?"]))
    print(f"ok: {ok}  failed: {len(fail)}")
    for name, errs in fail[:10]:
        print(f"  {name}: {errs}")


if __name__ == "__main__":
    main()
