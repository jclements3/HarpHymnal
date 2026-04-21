"""Build ``data/reharm/catalog.json`` — a single browsable index of every
hymn, variation, and phrase-aligned fragment produced by Phase 7 + 8.

Structure (top-level)::

    {
      "version": 1,
      "generated": "<ISO timestamp>",
      "hymns": {
        "<slug>": {
          "title": "...",
          "hymn_number": "###" | null,
          "key":    "<root> <mode>",
          "meter":  "<n>/<u>",
          "mode":   "ionian" | "aeolian" | "dorian" | null,
          "variations": [
            {
              "index": 1,
              "total_score": 0.85,
              "mid_path": "...",
              "ly_path":  "...",
              "fragment_count": 4,
              "tactic_manifest_summary": { "<dim>": [<top-N ids>], ... }
            }, ...
          ],
          "fragments": [
            {
              "phrase_index": 0,
              "phrase_letter": "A",
              "bars": [1, 4],
              "variation_index": 1,
              "mid_path": "...",
              "dominant_tactics": { "<dim>": "<tid>", ... }
            }, ...
          ]
        },
        ...
      },
      "tactic_index": {
        "<tactic_id>": [
          {"slug": "amazing_grace", "phrase_index": 0, "variation_index": 7}, ...
        ],
        ...
      },
      "corpus_stats": {
        "total_hymns":         279,
        "total_variations":    11160,
        "total_fragments":     <int>,
        "mean_total_score":    0.85,
        "tactic_coverage_matrix": { "<tactic_id>": <count>, ... }
      }
    }

Keep the JSON lean.  Per-bar manifests are **not** copied verbatim —
fragment rows carry a ``dominant_tactics`` map (one tactic per dimension,
chosen as the most-common tactic across that fragment's bars).  The
authoritative per-bar data is still on disk in
``data/reharm/fragments/<slug>/v##_p<N>.manifest.json`` (cached by
:func:`trefoil.reharm.fragment_cut.cut_hymn`) and in the variation JSON
itself.

Incremental: only hymn slugs whose fragment directory mtime is newer
than the existing ``catalog.json`` are re-scanned; everything else is
copied forward from the previous catalog.

Stdlib only.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Optional


# ------------------------------------------------------------------ #
# Package-relative import with script-mode fallback                  #
# ------------------------------------------------------------------ #
try:
    from trefoil.reharm.legality import score_variation
except ImportError:  # pragma: no cover
    here = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(here))
    from trefoil.reharm.legality import score_variation  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_VARIATIONS = REPO_ROOT / "data" / "reharm" / "variations"
DEFAULT_FRAGMENTS = REPO_ROOT / "data" / "reharm" / "fragments"
DEFAULT_RENDERS = REPO_ROOT / "data" / "reharm" / "renders"
DEFAULT_HYMNS = REPO_ROOT / "data" / "hymns"
DEFAULT_CATALOG = REPO_ROOT / "data" / "reharm" / "catalog.json"


# The canonical dimension order used for compact positional encoding of
# ``dominant_tactics`` on fragments and ``tactic_manifest_summary`` on
# variations.  The HTML views decode by zipping this with each row.
TACTIC_DIMENSION_ORDER = [
    "substitution", "shape", "register", "density", "texture",
    "lh_activity", "rh_activity", "connect_from", "connect_to",
    "lever", "range", "phrase_role",
]


# ------------------------------------------------------------------ #
# Small utilities                                                    #
# ------------------------------------------------------------------ #
def _now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat(timespec="seconds")


def _dir_mtime(p: Path) -> float:
    """Return max(mtime) across a directory (files + itself)."""
    try:
        st = p.stat().st_mtime
    except FileNotFoundError:
        return 0.0
    mt = st
    try:
        for f in p.iterdir():
            try:
                m = f.stat().st_mtime
            except FileNotFoundError:
                continue
            if m > mt:
                mt = m
    except (FileNotFoundError, NotADirectoryError):
        pass
    return mt


def _key_str(hymn: dict) -> str:
    k = hymn.get("key") or {}
    root = k.get("root") or ""
    mode = k.get("mode") or ""
    if root and mode:
        return f"{root} {mode}"
    return root or mode or ""


def _meter_str(hymn: dict) -> str:
    m = hymn.get("meter") or {}
    b, u = m.get("beats"), m.get("unit")
    if b and u:
        return f"{b}/{u}"
    return ""


# ------------------------------------------------------------------ #
# Tactic-manifest summarization                                      #
# ------------------------------------------------------------------ #
def _dominant_tactic_per_dim(per_bar_manifests: list[dict[str, str]]) -> dict[str, str]:
    """Given a list of compact per-bar manifests
    ({"substitution": "as_written", ...}), return one tactic per dimension
    by majority vote.  Ties broken by first-seen (stable for display)."""
    by_dim: dict[str, Counter] = defaultdict(Counter)
    first_seen: dict[str, str] = {}
    for bar in per_bar_manifests:
        for dim, tid in (bar or {}).items():
            by_dim[dim][tid] += 1
            first_seen.setdefault(f"{dim}|{tid}", tid)
    out: dict[str, str] = {}
    for dim, counter in by_dim.items():
        top_count = max(counter.values())
        # Among ties, prefer the first-seen bar's tactic
        tied = [t for t, c in counter.items() if c == top_count]
        if len(tied) == 1:
            out[dim] = tied[0]
        else:
            for bar in per_bar_manifests:
                if bar.get(dim) in tied:
                    out[dim] = bar[dim]
                    break
            else:
                out[dim] = tied[0]
    return out


def _variation_tactic_summary(variation: dict, top_n: int = 3) -> dict[str, list[str]]:
    """Top-N tactic ids per dimension for a full variation.

    Reads ``variation.tactic_coverage`` (already counted by the selector)
    and truncates to ``top_n`` per dimension — sufficient to render a
    compact "this variation is mostly these tactics" badge line without
    copying the 12-dim × N-bars grid.
    """
    coverage = variation.get("tactic_coverage") or {}
    by_dim: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for tid, count in coverage.items():
        dim = tid.split(".", 1)[0] if "." in tid else tid
        by_dim[dim].append((tid, int(count)))
    summary: dict[str, list[str]] = {}
    for dim, entries in by_dim.items():
        entries.sort(key=lambda x: (-x[1], x[0]))
        summary[dim] = [tid for tid, _ in entries[:top_n]]
    return summary


# ------------------------------------------------------------------ #
# Tactic-name table (shared across all variations + fragments)       #
# ------------------------------------------------------------------ #
class _TacticTable:
    """Growing table that de-duplicates tactic short-names into ints.

    The table is built during scanning and then serialized in
    ``catalog.tactic_name_table``.  Fragments and variations reference
    entries by integer index (``dt`` fields), cutting ~100 bytes per
    fragment at 57k+ fragments.  The UI decodes by
    ``tactic_name_table[dt[dim_idx]]``.
    """

    def __init__(self) -> None:
        self._idx: dict[str, int] = {"": 0}  # "" reserved as index 0
        self._table: list[str] = [""]

    def intern(self, name: str) -> int:
        if name in self._idx:
            return self._idx[name]
        i = len(self._table)
        self._table.append(name)
        self._idx[name] = i
        return i

    def as_list(self) -> list[str]:
        return list(self._table)


# ------------------------------------------------------------------ #
# Per-hymn scan                                                      #
# ------------------------------------------------------------------ #
def _scan_hymn(
    slug: str,
    variations_dir: Path,
    fragments_dir: Path,
    renders_dir: Path,
    hymns_dir: Path,
) -> dict:
    """Build the catalog entry for one hymn.

    Reads:
      - ``data/hymns/<slug>.json``    — meta
      - ``variations_dir/<slug>/v*.json`` — per-variation manifests
      - ``fragments_dir/<slug>/v*.manifest.json`` — per-variation fragments
      - existence of ``renders_dir/<slug>/v*.mid`` / ``.ly``
    """
    hymn_path = hymns_dir / f"{slug}.json"
    try:
        with hymn_path.open("r", encoding="utf-8") as f:
            hymn = json.load(f)
    except Exception:
        hymn = {}

    title = hymn.get("title") or slug.replace("_", " ").title()
    hymn_number = hymn.get("hymn_number")
    key_s = _key_str(hymn)
    meter_s = _meter_str(hymn)
    mode_s = hymn.get("_modal_name") or (hymn.get("mode") or None)

    variations: list[dict] = []
    fragments: list[dict] = []

    v_dir = variations_dir / slug
    if not v_dir.is_dir():
        return {
            "title": title,
            "hymn_number": hymn_number,
            "key": key_s,
            "meter": meter_s,
            "mode": mode_s,
            "variations": variations,
            "fragments": fragments,
        }

    render_dir = renders_dir / slug
    frag_dir = fragments_dir / slug

    for vp in sorted(v_dir.glob("v*.json")):
        try:
            with vp.open("r", encoding="utf-8") as f:
                variation = json.load(f)
        except Exception:
            continue
        vname = vp.stem  # "v01"
        vidx = int(variation.get("variation_index") or 0)
        # Score
        try:
            score = score_variation(variation).get("total_score")
        except Exception:
            score = None

        mid_p = render_dir / f"{vname}.mid"
        ly_p = render_dir / f"{vname}.ly"
        mf_p = frag_dir / f"{vname}.manifest.json"

        # Fragments for this variation — paths are derivable from
        # (slug, variation_index, phrase_index) in the UI, so we omit
        # them from the catalog row to save bytes at 57k+ fragments.
        # Short field names: pi=phrase_index, pl=phrase_letter, b=bars,
        # vi=variation_index, lb=length_beats, ct=chord_trajectory,
        # dt=dominant_tactics (positional, per TACTIC_DIMENSION_ORDER).
        v_fragments: list[dict] = []
        if mf_p.is_file():
            try:
                with mf_p.open("r", encoding="utf-8") as f:
                    for m in json.load(f):
                        per_bar = m.get("tactic_manifest_per_bar") or []
                        dom = _dominant_tactic_per_dim(per_bar)
                        dt_row = [dom.get(d, "") for d in TACTIC_DIMENSION_ORDER]
                        # pl / lb are derivable (letter from pi, length
                        # from meter × len(bar_indices)); omit them here
                        # and compute in the UI to stay under the 20-MB
                        # catalog budget.
                        v_fragments.append({
                            "pi": m.get("phrase_index"),
                            "b":  m.get("bars"),
                            "vi": vidx,
                            "dt": dt_row,
                            # transient, popped post-indexing
                            "_pb": per_bar,
                        })
            except Exception:
                pass

        # Variation row — short fields: idx, score, fc=fragment_count,
        # dt=dominant_tactics (top-1 per dim, positional).
        tms = _variation_tactic_summary(variation, top_n=1)
        top1 = []
        for dim in TACTIC_DIMENSION_ORDER:
            picks = tms.get(dim) or []
            if picks:
                # picks look like "dimension.tactic"; strip prefix
                tid = picks[0]
                top1.append(tid.split(".", 1)[1] if "." in tid else tid)
            else:
                top1.append("")
        variations.append({
            "idx": vidx,
            "score": round(float(score), 4) if isinstance(score, (int, float)) else None,
            "mid": mid_p.exists(),
            "ly":  ly_p.exists(),
            "fc":  len(v_fragments),
            "dt":  top1,
        })
        fragments.extend(v_fragments)

    # sort for display stability
    variations.sort(key=lambda v: v["idx"])
    fragments.sort(key=lambda f: (f.get("vi") or 0, f.get("pi") or 0))
    return {
        "title": title,
        "hymn_number": hymn_number,
        "key": key_s,
        "meter": meter_s,
        "mode": mode_s,
        "variations": variations,
        "fragments": fragments,
    }


# ------------------------------------------------------------------ #
# Entry point                                                        #
# ------------------------------------------------------------------ #
def build_catalog(
    variations_dir: Path | str = DEFAULT_VARIATIONS,
    fragments_dir: Path | str = DEFAULT_FRAGMENTS,
    renders_dir: Path | str = DEFAULT_RENDERS,
    hymns_dir: Path | str = DEFAULT_HYMNS,
    out_path: Path | str = DEFAULT_CATALOG,
    force_full: bool = False,
) -> dict:
    """Build (or incrementally refresh) the corpus catalog.

    Incremental: a slug is re-scanned only when its fragment dir
    (``fragments_dir/<slug>``) has a newer mtime than the previous
    catalog file.  Slugs absent from the previous catalog are always
    scanned.  Passing ``force_full=True`` re-scans everything.
    """
    variations_dir = Path(variations_dir)
    fragments_dir = Path(fragments_dir)
    renders_dir = Path(renders_dir)
    hymns_dir = Path(hymns_dir)
    out_path = Path(out_path)

    # Load previous catalog if present (for incremental carry-over).
    prev_hymns: dict[str, dict] = {}
    prev_mtime: float = 0.0
    if out_path.is_file():
        try:
            prev_mtime = out_path.stat().st_mtime
            with out_path.open("r", encoding="utf-8") as f:
                prev_catalog = json.load(f)
            prev_hymns = prev_catalog.get("hymns") or {}
        except Exception:
            prev_hymns = {}
            prev_mtime = 0.0

    slugs = sorted(p.name for p in variations_dir.iterdir() if p.is_dir())

    hymns: dict[str, dict] = {}
    for slug in slugs:
        frag_dir = fragments_dir / slug
        v_dir = variations_dir / slug
        fresh_needed = force_full or slug not in prev_hymns
        if not fresh_needed:
            # If fragment dir, variation dir, or hymn JSON is newer than
            # our prev catalog, re-scan.
            fm = _dir_mtime(frag_dir)
            vm = _dir_mtime(v_dir)
            hm = 0.0
            hp = hymns_dir / f"{slug}.json"
            if hp.is_file():
                try:
                    hm = hp.stat().st_mtime
                except FileNotFoundError:
                    hm = 0.0
            if max(fm, vm, hm) > prev_mtime:
                fresh_needed = True

        if fresh_needed:
            hymns[slug] = _scan_hymn(
                slug, variations_dir, fragments_dir, renders_dir, hymns_dir
            )
        else:
            hymns[slug] = prev_hymns[slug]

    # ----- tactic_index + corpus_stats -----
    # Compact encoding: slug_table is an ordered list of slugs; each row in
    # tactic_index is a 3-tuple [slug_idx, variation_index, phrase_index].
    # At 57k fragments × ~12 tactics-per-fragment × ~22 bytes per tuple this
    # keeps the tactic_index under ~15 MiB instead of the ~140 MiB a
    # per-row dict would cost.
    slug_table: list[str] = sorted(hymns.keys())
    slug_idx: dict[str, int] = {s: i for i, s in enumerate(slug_table)}

    tactic_index_compact: dict[str, list[list[int]]] = defaultdict(list)
    coverage_matrix: Counter = Counter()
    total_variations = 0
    total_fragments = 0
    score_sum = 0.0
    score_n = 0

    for slug, entry in hymns.items():
        si = slug_idx[slug]
        total_variations += len(entry.get("variations") or [])
        for v in entry.get("variations") or []:
            ts = v.get("score")
            if isinstance(ts, (int, float)):
                score_sum += ts
                score_n += 1
        for frag in entry.get("fragments") or []:
            total_fragments += 1
            vi = int(frag.get("vi") or 0)
            pi = int(frag.get("pi") or 0)
            # Gather every tactic that appears in any bar of this fragment
            seen: set[str] = set()
            for bar in frag.get("_pb") or []:
                for dim, short in bar.items():
                    tid = f"{dim}.{short}"
                    seen.add(tid)
            for tid in seen:
                coverage_matrix[tid] += 1
                tactic_index_compact[tid].append([si, vi, pi])

    # Drop per-bar manifests from fragments now that we've indexed them —
    # catalog.json stays lean.  The per-bar data is still in the on-disk
    # per-variation manifest sidecar.
    for slug, entry in hymns.items():
        for frag in entry.get("fragments") or []:
            frag.pop("_pb", None)

    # -------- tactic short-name interning --------
    # Replace the string arrays in every fragment.dt and variation.dt
    # with integer indices into a shared tactic_name_table.  At ~11k
    # variations + 57k fragments × 12-element arrays this saves ~7 MiB.
    ttable = _TacticTable()
    for slug, entry in hymns.items():
        for v in entry.get("variations") or []:
            v["dt"] = [ttable.intern(x or "") for x in (v.get("dt") or [])]
        for frag in entry.get("fragments") or []:
            frag["dt"] = [ttable.intern(x or "") for x in (frag.get("dt") or [])]
    tactic_name_table = ttable.as_list()

    stats = {
        "total_hymns":       len(hymns),
        "total_variations":  total_variations,
        "total_fragments":   total_fragments,
        "mean_total_score":  (score_sum / score_n) if score_n else None,
        "tactic_coverage_matrix": dict(coverage_matrix),
    }

    # Flatten tactic_index rows into 1-D arrays of triples for compactness:
    # ``[si0, vi0, pi0, si1, vi1, pi1, ...]`` instead of a nested list of
    # 3-element lists.  Saves ~2.5 MiB at 1.7M rows.
    tactic_index_flat: dict[str, list[int]] = {
        tid: [x for row in rows for x in row]
        for tid, rows in sorted(tactic_index_compact.items())
    }

    catalog = {
        "version": 1,
        "generated": _now_iso(),
        "dimension_order": TACTIC_DIMENSION_ORDER,
        "fragment_schema": ["pi", "b", "vi", "dt"],
        "variation_schema": ["idx", "score", "mid", "ly", "fc", "dt"],
        "tactic_name_table": tactic_name_table,
        "hymns": hymns,
        "slug_table": slug_table,
        "tactic_index_schema": ["slug_idx", "variation_index", "phrase_index"],
        "tactic_index_flat_stride": 3,
        "tactic_index": tactic_index_flat,
        "corpus_stats": stats,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, separators=(",", ":"))

    return catalog


__all__ = ["build_catalog"]
