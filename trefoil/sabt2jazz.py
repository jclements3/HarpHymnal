"""trefoil/sabt2jazz.py — convert SATB hymns to jazz 47-string harp voicings.

Walks a hymn's bars, reads the chord (roman numeral + quality) for each,
and emits a pretty-fraction voicing using the chord pool
(trefoil.pretty_fraction).  Output is a per-bar jazz orchestration ready
to be rendered as a 47-column string strip, SVG, or LilyPond score.

Pipeline:
    hymn JSON (data/hymns/<slug>.json)
      → per-bar chord spec
      → pretty_fraction.pretty()
      → optional voice-lead adjustment (nudge top toward previous bar)
      → jazz orchestration JSON / text report

Usage:
    python3 -m trefoil.sabt2jazz amazing_grace                    # single hymn, text
    python3 -m trefoil.sabt2jazz amazing_grace --out-json out.json
    python3 -m trefoil.sabt2jazz --all                            # all 279 hymns
    python3 -m trefoil.sabt2jazz --all --out-dir data/jazz/       # bulk JSON output
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path

from trefoil.pretty_fraction import pretty, string_index, C_MAJOR_LETTERS, score_fraction


REPO_ROOT = Path(__file__).resolve().parent.parent
HYMNS_DIR = REPO_ROOT / "data" / "hymns"


# ───────────────────── Reharm techniques ─────────────────────
# Ported from mapper/harp_mapper.py::pick_with_techniques, adapted for the
# new pretty-fraction pool. Each function takes a chord spec + context dict
# and returns an alternate chord spec, or None if inapplicable.

_ROMAN_ORDER = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']
_ROMAN_DEG = {r: i + 1 for i, r in enumerate(_ROMAN_ORDER)}


def _shift(numeral: str, steps: int) -> str | None:
    """Shift a roman numeral by N diatonic steps (1-indexed)."""
    d = _ROMAN_DEG.get(numeral)
    if d is None:
        return None
    return _ROMAN_ORDER[(d - 1 + steps) % 7]


def third_sub(spec: dict, ctx: dict) -> dict | None:
    """Slide down 2 degrees (I→vi, IV→ii, V→iii).

    Gated: skip on cycle-edge bars (V→I final cadences) where the
    original root motion is the lesson.
    """
    if ctx.get("is_final_cadence"):
        return None
    alt = _shift(spec["numeral"], -2)
    if alt is None:
        return None
    return {"numeral": alt, "quality": spec.get("quality")}


def deceptive_sub(spec: dict, ctx: dict) -> dict | None:
    """V → vi (or V7 → vi7) — only at a phrase-final V resolving to I."""
    if spec["numeral"] != "V":
        return None
    if ctx.get("next_rn") != "I":
        return None
    if not ctx.get("is_phrase_end") and not ctx.get("is_final_cadence"):
        return None
    q = "7" if spec.get("quality") == "7" else None
    out = {"numeral": "vi"}
    if q:
        out["quality"] = q
    return out


def quality_sub(spec: dict, ctx: dict) -> dict | None:
    """Promote a plain triad to a 7-chord (I → IΔ, ii → ii7, V → V7)."""
    if spec.get("quality"):
        return None  # already has a quality
    num = spec["numeral"]
    if num == "I" or num == "IV":
        q = "Δ"
    elif num == "V":
        q = "7"
    elif num in ("ii", "iii", "vi"):
        q = "7"
    elif num == "vii°":
        q = "h7"
    else:
        return None
    return {"numeral": num, "quality": q}


def common_tone_pivot(spec: dict, ctx: dict) -> dict | None:
    """Slide 1 step to a neighboring chord sharing 2 common tones.
    Only fires on repeated chords (this bar's chord == previous bar's chord)."""
    if ctx.get("prev_rn") != spec["numeral"]:
        return None
    if ctx.get("is_final_cadence"):
        return None
    # Slide up 1 step (I → iii via neighbor, etc. — simplified)
    alt = _shift(spec["numeral"], 2)  # up 2 = shares root+3 tones
    if alt is None:
        return None
    return {"numeral": alt, "quality": spec.get("quality")}


TECHNIQUES = [
    ("deceptive_sub", deceptive_sub),
    ("quality_sub", quality_sub),
    ("third_sub", third_sub),
    ("common_tone_pivot", common_tone_pivot),
]


# ───────────────────── Pick-with-techniques ─────────────────────

def _voice_lead_penalty(prev_top, new_top) -> int:
    """Add penalty proportional to top-voice leap from previous bar."""
    if prev_top is None or new_top is None:
        return 0
    diff = abs(string_index(*new_top) - string_index(*prev_top))
    if diff <= 2:    return 0
    if diff <= 4:    return 1
    if diff <= 7:    return 2
    return 3


def pick_with_techniques(spec: dict, ctx: dict) -> dict:
    """Return the winning pick: {spec, technique, frac, score, source_spec}.

    source_spec is the original bar's chord; spec is after substitution.
    Lower score = better. Technique bonus = -1 per applied technique.
    """
    candidates = []  # (score, spec, technique_name, frac)
    # Baseline (no technique)
    try:
        frac = pretty(spec)
        s = score_fraction(frac, spec)
        top = max(frac["rh"], key=lambda n: string_index(*n)) if frac["rh"] else None
        s += _voice_lead_penalty(ctx.get("prev_top"), top)
        candidates.append((s, spec, None, frac))
    except Exception:
        pass

    # Substitution alternates
    for name, fn in TECHNIQUES:
        alt = fn(spec, ctx)
        if alt is None:
            continue
        try:
            frac = pretty(alt)
            s = score_fraction(frac, alt)
            top = max(frac["rh"], key=lambda n: string_index(*n)) if frac["rh"] else None
            s += _voice_lead_penalty(ctx.get("prev_top"), top)
            s -= 1  # technique application bonus
            candidates.append((s, alt, name, frac))
        except Exception:
            continue

    if not candidates:
        raise ValueError("no valid candidate for " + repr(spec))
    candidates.sort(key=lambda c: c[0])
    score, chosen_spec, tech, frac = candidates[0]
    return {
        "source_spec": spec,
        "spec": chosen_spec,
        "technique": tech,
        "frac": frac,
        "score": score,
    }


# ───────────────────── Chord extraction ─────────────────────

def bar_to_spec(bar: dict) -> dict | None:
    """Extract the chord spec {numeral, quality?} from a bar."""
    ch = bar.get("chord") or {}
    num = ch.get("numeral")
    if not num:
        return None
    spec = {"numeral": num}
    q = ch.get("quality")
    if q:
        spec["quality"] = q
    return spec


def spec_key(spec: dict) -> tuple:
    """Hashable key for chord spec (for pool cache)."""
    return (spec.get("numeral"), spec.get("quality"))


# ───────────────────── Pool cache ─────────────────────

_pool_cache: dict[tuple, dict] = {}

def get_voicing(spec: dict, context: dict | None = None) -> dict:
    """Return the pretty fraction for a chord spec, cached by spec.

    (context / voice leading TBD — current impl is stateless.)
    """
    key = spec_key(spec)
    if key not in _pool_cache:
        _pool_cache[key] = pretty(spec, context=context)
    return _pool_cache[key]


# ───────────────────── Hymn conversion ─────────────────────

def convert_hymn(hymn: dict) -> dict:
    """Convert a hymn dict to its jazz orchestration dict.
    Applies the 4 substitution techniques (deceptive, quality, third, common-tone pivot)
    per bar, picking the top-scoring candidate with voice-leading penalty.
    """
    bars = hymn.get("bars", [])
    bars_out = []
    prev_top = None
    prev_rn = None
    skipped = 0
    tech_counts: dict[str, int] = {}
    n_bars = len(bars)

    for i, bar in enumerate(bars):
        spec = bar_to_spec(bar)
        if spec is None:
            bars_out.append({"bar": i + 1, "skipped": True, "reason": "no chord"})
            skipped += 1
            continue

        next_rn = None
        for j in range(i + 1, n_bars):
            nxt_spec = bar_to_spec(bars[j])
            if nxt_spec is not None:
                next_rn = nxt_spec["numeral"]
                break
        is_final_cadence = (i == n_bars - 2) and spec["numeral"] == "V" and next_rn == "I"
        is_phrase_end = is_final_cadence  # simplified heuristic

        ctx = {
            "prev_rn": prev_rn, "next_rn": next_rn, "prev_top": prev_top,
            "is_phrase_end": is_phrase_end, "is_final_cadence": is_final_cadence,
        }

        try:
            result = pick_with_techniques(spec, ctx)
        except Exception as e:
            bars_out.append({"bar": i + 1, "skipped": True,
                             "reason": str(e), "spec": spec})
            skipped += 1
            prev_rn = spec["numeral"]
            continue

        frac = result["frac"]
        top = max(frac["rh"], key=lambda n: string_index(*n)) if frac["rh"] else None
        bass = min(frac["lh"], key=lambda n: string_index(*n)) if frac["lh"] else None
        rh_bot = min(frac["rh"], key=lambda n: string_index(*n)) if frac["rh"] else None
        lh_top = max(frac["lh"], key=lambda n: string_index(*n)) if frac["lh"] else None
        gap = (string_index(*rh_bot) - string_index(*lh_top) - 1) if rh_bot and lh_top else 0

        bars_out.append({
            "bar": i + 1,
            "source_spec": result["source_spec"],
            "spec": result["spec"],
            "technique": result["technique"],
            "lh": frac["lh"], "rh": frac["rh"],
            "bass": bass, "top": top,
            "gap": gap, "score": result["score"],
        })
        if result["technique"]:
            tech_counts[result["technique"]] = tech_counts.get(result["technique"], 0) + 1
        prev_top = top
        prev_rn = result["spec"]["numeral"]

    return {
        "title": hymn.get("title"),
        "key": hymn.get("key"),
        "meter": hymn.get("meter"),
        "bar_count": n_bars,
        "skipped": skipped,
        "technique_counts": tech_counts,
        "bars": bars_out,
    }


# ───────────────────── Rendering ─────────────────────

def layout_47(notes: list) -> str:
    """Render a list of (deg, oct) notes on a 47-col C1..G7 strip."""
    row = ["."] * 47
    for (d, o) in notes:
        idx = (o - 1) * 7 + (d - 1) + 1
        if 1 <= idx <= 47:
            row[idx - 1] = C_MAJOR_LETTERS[d - 1]
    return "".join(row)


def format_bar(bar: dict) -> str:
    if bar.get("skipped"):
        return f"  {bar['bar']:>3} (skipped: {bar['reason']})"
    spec = bar["spec"]
    label = spec["numeral"] + (spec.get("quality") or "")
    strip = layout_47(bar["lh"] + bar["rh"])
    return f"  {bar['bar']:>3}  {label:<8} {strip}  gap={bar['gap']:>2}  score={bar['score']}"


def report(orch: dict) -> str:
    head = "  1      2      3      4      5      6      7    "
    lines = [f"Jazz orchestration — {orch['title']}  ({orch['key']['root']} "
             f"{orch['key']['mode']}, {orch['meter']['beats']}/{orch['meter']['unit']})"]
    lines.append(f"  bar  chord    {head}")
    for bar in orch["bars"]:
        lines.append(format_bar(bar))
    if orch["skipped"]:
        lines.append(f"  [{orch['skipped']} bars skipped]")
    return "\n".join(lines)


# ───────────────────── CLI ─────────────────────

def load_hymn(slug: str) -> dict:
    p = HYMNS_DIR / f"{slug}.json"
    if not p.exists():
        raise FileNotFoundError(f"no such hymn: {p}")
    return json.loads(p.read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?", help="hymn slug (e.g. amazing_grace)")
    ap.add_argument("--all", action="store_true", help="convert every hymn in data/hymns/")
    ap.add_argument("--out-json", type=str, help="write single-hymn orchestration JSON here")
    ap.add_argument("--out-dir", type=str, help="bulk output directory for --all")
    args = ap.parse_args()

    if args.all:
        out_dir = Path(args.out_dir or (REPO_ROOT / "data" / "jazz"))
        out_dir.mkdir(parents=True, exist_ok=True)
        n_ok = 0; n_fail = 0; total_skipped = 0
        for p in sorted(HYMNS_DIR.glob("*.json")):
            try:
                hymn = json.loads(p.read_text())
                orch = convert_hymn(hymn)
                (out_dir / p.name).write_text(json.dumps(orch, indent=2, ensure_ascii=False))
                total_skipped += orch["skipped"]
                n_ok += 1
            except Exception as e:
                n_fail += 1
                print(f"  FAIL {p.stem}: {e}")
        print(f"\nconverted {n_ok} hymns, {n_fail} failed, {total_skipped} bars skipped total")
        print(f"output → {out_dir}")
        return

    if not args.slug:
        ap.error("provide a hymn slug or --all")
    hymn = load_hymn(args.slug)
    orch = convert_hymn(hymn)
    if args.out_json:
        Path(args.out_json).write_text(json.dumps(orch, indent=2, ensure_ascii=False))
        print(f"wrote {args.out_json}")
    else:
        print(report(orch))


if __name__ == "__main__":
    main()
