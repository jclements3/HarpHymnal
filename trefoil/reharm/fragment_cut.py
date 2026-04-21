"""Phrase-aligned fragment cutter for reharm variations.

Phase 8 of the Reharm Tactics pipeline.  Given a full-variation MIDI +
LilyPond render (Phase 7 output), carve it into phrase-aligned fragments
the harpist can drill individually.

The boundary source is the hymn parser's precomputed ``phrases`` list in
``data/hymns/<slug>.json``.  Each phrase is an object shaped roughly as
``{"ibars": [1, 2, 3, 4], "path": ...}`` with **1-indexed bar numbers**.

The public entry point is :func:`cut_fragments`.  It:

1. Builds one slimmed variation dict per phrase by selecting the bars
   whose 1-based index appears in ``phrases[i]["ibars"]``.
2. Builds a matching slimmed hymn dict (same bar subset).
3. Re-invokes :func:`trefoil.reharm.render_midi.render_variation_midi`
   and :func:`trefoil.reharm.render_lily.render_variation_lily` on the
   slimmed pair to emit ``<out_dir>/v##_p<N>.mid`` and ``.ly``.
4. Returns a list of compact manifest dicts the catalog builder can
   consume without re-reading every bar.

Parallel use (over hymns, one worker per hymn) is supported via
:func:`cut_hymn`, designed for :class:`multiprocessing.Pool`.

Stdlib only.
"""
from __future__ import annotations

import copy
import json
import os
import string
import sys
import time
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Iterable, Optional


# ------------------------------------------------------------------ #
# Package-relative import with script-mode fallback                  #
# ------------------------------------------------------------------ #
try:
    from trefoil.reharm.render_midi import render_variation_midi
    from trefoil.reharm.render_lily import render_variation_lily
except ImportError:  # pragma: no cover
    here = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(here))
    from trefoil.reharm.render_midi import render_variation_midi  # type: ignore
    from trefoil.reharm.render_lily import render_variation_lily  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_VARIATIONS = REPO_ROOT / "data" / "reharm" / "variations"
DEFAULT_HYMNS = REPO_ROOT / "data" / "hymns"
DEFAULT_FRAGMENTS = REPO_ROOT / "data" / "reharm" / "fragments"
DEFAULT_RENDERS = REPO_ROOT / "data" / "reharm" / "renders"


# ------------------------------------------------------------------ #
# Phrase-letter assignment (A, B, C, ..., Z, AA, AB, ...)            #
# ------------------------------------------------------------------ #
def _phrase_letter(idx: int) -> str:
    """Return phrase letter for 0-based index (0→A, 25→Z, 26→AA, ...)."""
    if idx < 0:
        return "?"
    letters = string.ascii_uppercase
    if idx < 26:
        return letters[idx]
    first, second = divmod(idx, 26)
    return letters[first - 1] + letters[second]


# ------------------------------------------------------------------ #
# Phrase-shape extraction (tolerant of a couple of shapes we've seen #
# in the parser, to avoid bit-rot if the hymn parser changes later)  #
# ------------------------------------------------------------------ #
def _phrase_bar_indices(phrase: dict) -> list[int]:
    """Return 1-based bar indices for a phrase entry.

    Accepts:
      - ``{"ibars": [1, 2, 3]}``  — current parser shape
      - ``{"bars":  [1, 2, 3]}``  — fallback (historical alias)
      - ``{"start": 1, "end": 3}`` — inclusive range shape
    """
    if not isinstance(phrase, dict):
        return []
    ibars = phrase.get("ibars") or phrase.get("bars")
    if isinstance(ibars, list) and ibars:
        return [int(b) for b in ibars]
    start = phrase.get("start")
    end = phrase.get("end")
    if start is not None and end is not None:
        try:
            return list(range(int(start), int(end) + 1))
        except (TypeError, ValueError):
            return []
    return []


# ------------------------------------------------------------------ #
# Slimming helpers                                                   #
# ------------------------------------------------------------------ #
def _slim_variation(variation: dict, bar_ibars_1based: list[int]) -> dict:
    """Return a shallow copy of ``variation`` with only the named bars.

    We don't try to recompute ``tactic_coverage`` — it's redundant with
    per-bar manifests for fragment use, and the full-variation coverage
    still lives at the parent level.
    """
    out = {
        "seed": variation.get("seed"),
        "mode": variation.get("mode"),
        "key":  variation.get("key"),
        "title": variation.get("title"),
        "tactics_hash": variation.get("tactics_hash"),
        "slug": variation.get("slug"),
        "variation_index": variation.get("variation_index"),
    }
    bar_index_set = set(bar_ibars_1based)
    bars_in = variation.get("bars") or []
    bars_out: list[dict] = []
    # Variation bars use their own 1-based "bar" field; match on that.
    for b in bars_in:
        n = b.get("bar")
        if n in bar_index_set:
            bars_out.append(b)
    # Fallback: if "bar" field absent, positional 1-based.
    if not bars_out:
        for i, b in enumerate(bars_in, start=1):
            if i in bar_index_set:
                bars_out.append(b)
    out["bars"] = bars_out
    return out


def _slim_hymn(hymn: dict, bar_ibars_1based: list[int]) -> dict:
    """Return a shallow clone of ``hymn`` with only the named bars, keeping
    top-level meta (title/key/meter/tempo/mode) the renderers need."""
    bars_in = hymn.get("bars") or []
    idxs = [i for i in bar_ibars_1based if 1 <= i <= len(bars_in)]
    bars_out = [bars_in[i - 1] for i in idxs]
    out = {
        "title": hymn.get("title"),
        "key":   hymn.get("key"),
        "meter": hymn.get("meter"),
        "tempo": hymn.get("tempo"),
        "_modal_name": hymn.get("_modal_name"),
        "bars":  bars_out,
    }
    return out


# ------------------------------------------------------------------ #
# Per-fragment manifest construction                                 #
# ------------------------------------------------------------------ #
def _bar_tactic_compact(bar: dict) -> dict[str, str]:
    """Strip the "dimension." prefix from each manifest id for compactness.

    ``{"substitution": "substitution.as_written", ...}`` →
    ``{"substitution": "as_written", ...}``.
    """
    manifest = bar.get("tactic_manifest") or {}
    out: dict[str, str] = {}
    for dim, tid in manifest.items():
        if not isinstance(tid, str):
            continue
        short = tid.split(".", 1)[1] if "." in tid else tid
        out[dim] = short
    return out


def _bar_chord_str(bar: dict) -> str:
    ch = bar.get("chord_used") or {}
    s = ch.get("translated") or ch.get("numeral") or ""
    q = ch.get("quality")
    return f"{s}{q}" if q else s


def _phrase_total_score(variation: dict) -> Optional[float]:
    """Return the total score of the parent variation, recomputing via
    :mod:`trefoil.reharm.legality` if it's not already stamped.
    """
    cached = variation.get("_resolved_total_score")
    if cached is not None:
        try:
            return float(cached)
        except (TypeError, ValueError):
            pass
    try:
        from trefoil.reharm.legality import score_variation  # type: ignore
    except Exception:  # pragma: no cover
        return None
    try:
        sc = score_variation(variation)
        return float(sc.get("total_score") or 0.0)
    except Exception:  # pragma: no cover
        return None


def _length_beats(bars: list[dict], hymn_meter: dict) -> float:
    beats_per_bar = 1
    try:
        beats_per_bar = int((hymn_meter or {}).get("beats") or 4)
    except (TypeError, ValueError):
        beats_per_bar = 4
    return float(beats_per_bar * max(0, len(bars)))


# ------------------------------------------------------------------ #
# Public: cut one variation                                          #
# ------------------------------------------------------------------ #
def cut_fragments(
    variation_json: dict,
    hymn_json: dict,
    src_mid_path: Optional[Path],
    out_dir: Path,
) -> list[dict]:
    """Cut one variation into phrase-aligned fragments.

    Parameters
    ----------
    variation_json
        Full variation dict (from ``data/reharm/variations/<slug>/v##.json``).
    hymn_json
        Full hymn dict (from ``data/hymns/<slug>.json``).
    src_mid_path
        Path to the **full** variation's ``.mid`` (Phase 7 output).
        Retained as a back-reference in the manifest; we do not
        byte-slice it.  May be ``None`` when unknown.
    out_dir
        Directory to write fragment ``.mid`` and ``.ly`` files into.
        Created if missing.

    Returns
    -------
    list[dict]
        One manifest per phrase fragment.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = variation_json.get("slug") or hymn_json.get("title") or "unknown"
    vidx = variation_json.get("variation_index") or 0
    phrases = hymn_json.get("phrases") or []
    total_score = _phrase_total_score(variation_json)

    manifests: list[dict] = []
    for pi, phrase in enumerate(phrases):
        bar_idxs = _phrase_bar_indices(phrase)
        if not bar_idxs:
            continue

        slim_var = _slim_variation(variation_json, bar_idxs)
        slim_hymn = _slim_hymn(hymn_json, bar_idxs)

        # Defensive: if no bars survived (e.g. phrase bar indices don't match
        # any variation bar), skip rather than emit an empty file.
        if not slim_var.get("bars") or not slim_hymn.get("bars"):
            continue

        frag_name = f"v{vidx:02d}_p{pi}"
        mid_p = out_dir / f"{frag_name}.mid"
        ly_p = out_dir / f"{frag_name}.ly"

        try:
            render_variation_midi(slim_var, slim_hymn, mid_p)
        except Exception as exc:  # pragma: no cover
            # Skip this fragment but don't fail the whole hymn
            mid_p = None  # type: ignore[assignment]
            print(f"fragment_cut: MIDI fail {slug}/{frag_name}: {exc}",
                  file=sys.stderr)
        try:
            render_variation_lily(slim_var, slim_hymn, ly_p)
        except Exception as exc:  # pragma: no cover
            ly_p = None  # type: ignore[assignment]
            print(f"fragment_cut: Lily fail {slug}/{frag_name}: {exc}",
                  file=sys.stderr)

        bars_out = slim_var.get("bars") or []
        tactic_per_bar: list[dict[str, str]] = [
            _bar_tactic_compact(b) for b in bars_out
        ]
        chord_traj = [_bar_chord_str(b) for b in bars_out]

        first_bar = min(bar_idxs)
        last_bar = max(bar_idxs)

        manifests.append({
            "slug": slug,
            "variation_index": vidx,
            "phrase_index": pi,
            "phrase_letter": _phrase_letter(pi),
            "bars": [first_bar, last_bar],
            "bar_indices": list(bar_idxs),
            "tactic_manifest_per_bar": tactic_per_bar,
            "chord_trajectory": chord_traj,
            "total_score_of_parent_variation": total_score,
            "length_beats": _length_beats(bars_out, hymn_json.get("meter") or {}),
            "mid_path": str(mid_p) if mid_p else None,
            "ly_path": str(ly_p) if ly_p else None,
            "src_mid_path": str(src_mid_path) if src_mid_path else None,
        })

    return manifests


# ------------------------------------------------------------------ #
# Hymn-level driver (one process-pool task == one hymn)              #
# ------------------------------------------------------------------ #
def _stamp_path(hymn_out: Path, vname: str) -> Path:
    return hymn_out / f"{vname}.stamp"


def cut_hymn(
    slug: str,
    variations_dir: Path | str = DEFAULT_VARIATIONS,
    hymns_dir: Path | str = DEFAULT_HYMNS,
    fragments_dir: Path | str = DEFAULT_FRAGMENTS,
    renders_dir: Path | str = DEFAULT_RENDERS,
    force: bool = False,
) -> dict:
    """Cut every variation of one hymn into phrase fragments.

    Designed as a :class:`multiprocessing.Pool` worker.

    Incremental: per-variation, skipped if the fragment ``.stamp`` sidecar
    on the **first phrase** fragment matches the variation's
    ``tactics_hash``.
    """
    variations_dir = Path(variations_dir)
    hymns_dir = Path(hymns_dir)
    fragments_dir = Path(fragments_dir)
    renders_dir = Path(renders_dir)

    hymn_path = hymns_dir / f"{slug}.json"
    v_dir = variations_dir / slug
    if not hymn_path.is_file() or not v_dir.is_dir():
        return {"slug": slug, "wrote": 0, "skipped": 0, "failed": 0,
                "fragments": 0, "errors": ["missing inputs"]}

    out_dir = fragments_dir / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    render_dir = renders_dir / slug

    try:
        with hymn_path.open("r", encoding="utf-8") as f:
            hymn = json.load(f)
    except Exception as exc:
        return {"slug": slug, "wrote": 0, "skipped": 0, "failed": 1,
                "fragments": 0, "errors": [f"hymn load: {exc}"]}

    wrote = skipped = failed = 0
    total_frags = 0
    errors: list[str] = []
    all_manifests: list[dict] = []
    vpaths = sorted(v_dir.glob("v*.json"))

    for vp in vpaths:
        vname = vp.stem  # "v01"
        stamp_p = _stamp_path(out_dir, vname)
        try:
            with vp.open("r", encoding="utf-8") as f:
                variation = json.load(f)
        except Exception as exc:
            failed += 1
            errors.append(f"{vname}: load {exc}")
            continue

        cur_hash = variation.get("tactics_hash", "")
        if not force and stamp_p.exists():
            try:
                if stamp_p.read_text(encoding="utf-8").strip() == cur_hash:
                    skipped += 1
                    # Still need manifests for catalog; re-derive cheaply
                    # from existing files (just re-list without re-rendering
                    # by passing dummy out_dir? — simpler: re-run cut_fragments
                    # which will re-render, so we *do* honor the skip by just
                    # reading previously-written manifest copy.  We stash per
                    # variation manifest under .manifest.json for this.
                    mf_p = out_dir / f"{vname}.manifest.json"
                    if mf_p.exists():
                        try:
                            with mf_p.open("r", encoding="utf-8") as f:
                                all_manifests.extend(json.load(f))
                        except Exception:
                            pass
                    # But if the .manifest.json is missing, fall through to
                    # re-cut so the catalog always has full data.
                    if mf_p.exists():
                        total_frags += (hymn.get("phrases") and
                                        sum(1 for _ in hymn["phrases"]) or 0)
                        continue
            except Exception:
                pass

        # Fresh cut
        src_mid = render_dir / f"{vname}.mid"
        try:
            manifests = cut_fragments(
                variation, hymn,
                src_mid_path=src_mid if src_mid.exists() else None,
                out_dir=out_dir,
            )
            all_manifests.extend(manifests)
            # Cache manifests per variation so future skips still populate
            # the catalog without re-rendering.
            (out_dir / f"{vname}.manifest.json").write_text(
                json.dumps(manifests), encoding="utf-8"
            )
            stamp_p.write_text(cur_hash, encoding="utf-8")
            wrote += 1
            total_frags += len(manifests)
        except Exception as exc:
            failed += 1
            errors.append(f"{vname}: cut {exc}")

    return {
        "slug": slug,
        "wrote": wrote,
        "skipped": skipped,
        "failed": failed,
        "fragments": total_frags,
        "errors": errors,
        "manifests": all_manifests,
    }


# ------------------------------------------------------------------ #
# Convenience: cut every hymn in a pool                              #
# ------------------------------------------------------------------ #
def cut_all(
    variations_dir: Path | str = DEFAULT_VARIATIONS,
    hymns_dir: Path | str = DEFAULT_HYMNS,
    fragments_dir: Path | str = DEFAULT_FRAGMENTS,
    renders_dir: Path | str = DEFAULT_RENDERS,
    workers: Optional[int] = None,
    force: bool = False,
    progress: bool = True,
) -> dict:
    """Bulk-cut all hymns.  Returns an aggregate report dict."""
    variations_dir = Path(variations_dir)
    slugs = sorted(p.name for p in variations_dir.iterdir() if p.is_dir())
    workers = workers or os.cpu_count() or 1

    t0 = time.time()
    results: list[dict] = []
    args = [(slug, variations_dir, hymns_dir, fragments_dir, renders_dir, force)
            for slug in slugs]

    if workers <= 1:
        for a in args:
            r = _cut_hymn_wrap(a)
            results.append(r)
            if progress:
                print(f"[{len(results):>3}/{len(slugs)}] {r['slug']}: "
                      f"{r['fragments']} frags "
                      f"({r['wrote']} wrote, {r['skipped']} skip, "
                      f"{r['failed']} fail)",
                      flush=True)
    else:
        with Pool(processes=workers) as pool:
            for r in pool.imap_unordered(_cut_hymn_wrap, args):
                results.append(r)
                if progress:
                    print(f"[{len(results):>3}/{len(slugs)}] {r['slug']}: "
                          f"{r['fragments']} frags "
                          f"({r['wrote']} wrote, {r['skipped']} skip, "
                          f"{r['failed']} fail)",
                          flush=True)

    dt = time.time() - t0
    total_frags = sum(r["fragments"] for r in results)
    total_wrote = sum(r["wrote"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    return {
        "hymns": len(slugs),
        "fragments": total_frags,
        "wrote": total_wrote,
        "skipped": total_skipped,
        "failed": total_failed,
        "wall_seconds": dt,
        "errors": [e for r in results for e in r.get("errors") or []][:200],
    }


def _cut_hymn_wrap(a: tuple) -> dict:
    slug, vd, hd, fd, rd, force = a
    return cut_hymn(slug, vd, hd, fd, rd, force=force)


__all__ = ["cut_fragments", "cut_hymn", "cut_all"]
