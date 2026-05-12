"""Pre-bake harp arrangements for every (hymn, pattern) pair.

Drives ``tools.satb_to_harp.analyzer.analyze`` +
``tools.satb_to_harp.consolidator.consolidate`` across all hymns in
``source/OpenHymnal.abc`` and all Somerset LH patterns plus the default
(no-pattern SATB) mode. Outputs flat ABC files plus a manifest JSON that
the tablet's static UI consumes.

Output layout (relative to repo root by default)::

    <out_dir>/manifest.json
    <out_dir>/abc/<NNN>__<pattern_slug>.abc

    pattern_slug = 'default' for no-pattern mode, otherwise lower-cased
    AVAILABLE name with non-alnum runs collapsed to '_'.

Run::

    python3 -m tools.satb_to_harp.bake_all \\
        --out tablet_app/app/src/main/assets/harparranger \\
        --workers 32

Per-(hymn, pattern) failures are captured in the manifest under
``failures: [{n, title, pattern, error}]`` so the UI can grey out tiles
that didn't bake.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from parsers.abc import iter_tunes  # noqa: E402
from tools.satb_to_harp.somerset import AVAILABLE  # noqa: E402


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower() or "x"


def list_hymns() -> list[tuple[int, str]]:
    src = REPO_ROOT / "source" / "OpenHymnal.abc"
    text = src.read_text(encoding="utf-8", errors="replace")
    titles = sorted({t for t, _ in iter_tunes(text)})
    return [(i + 1, t) for i, t in enumerate(titles)]


def _bake_one(args: tuple[int, str, str | None]) -> dict:
    n, title, pattern = args
    try:
        from tools.satb_to_harp.analyzer import analyze
        from tools.satb_to_harp.consolidator import consolidate
        ledger = analyze(title)
        res = consolidate(ledger, pattern=pattern)
        return {
            "n": n,
            "title": title,
            "pattern": pattern,
            "abc": res.abc,
            "audits": [
                {"beat": a.beat, "severity": a.severity, "message": a.message}
                for a in res.audits
            ],
            "beats": len(ledger.beats),
        }
    except Exception as e:
        return {
            "n": n,
            "title": title,
            "pattern": pattern,
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path,
                   help="Output directory (created if missing).")
    p.add_argument("--workers", type=int, default=16,
                   help="Parallel worker processes (default 16).")
    p.add_argument("--patterns", nargs="*", default=None,
                   help="Subset of patterns to bake (default: all AVAILABLE + default).")
    p.add_argument("--limit", type=int, default=0,
                   help="Bake only first N hymns (smoke test).")
    args = p.parse_args()

    out_dir = args.out.resolve()
    abc_dir = out_dir / "abc"
    abc_dir.mkdir(parents=True, exist_ok=True)

    hymns = list_hymns()
    if args.limit:
        hymns = hymns[: args.limit]

    patterns: list[str | None] = [None]
    candidates = args.patterns if args.patterns is not None else AVAILABLE
    patterns.extend(candidates)

    jobs: list[tuple[int, str, str | None]] = []
    for n, title in hymns:
        for pat in patterns:
            jobs.append((n, title, pat))

    print(f"[bake] {len(hymns)} hymns x {len(patterns)} variants = {len(jobs)} jobs",
          flush=True)

    failures: list[dict] = []
    successes = 0
    audits_summary: dict[str, int] = {"warn": 0, "info": 0, "error": 0}

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(_bake_one, j) for j in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            n, title, pat = r["n"], r["title"], r["pattern"]
            pat_slug = "default" if pat is None else slugify(pat)
            tag = f"{n:03d}__{pat_slug}"
            if "error" in r:
                failures.append({
                    "n": n, "title": title, "pattern": pat,
                    "error": r["error"],
                })
            else:
                (abc_dir / f"{tag}.abc").write_text(r["abc"], encoding="utf-8")
                successes += 1
                for a in r.get("audits", []):
                    sev = a.get("severity") or "warn"
                    audits_summary[sev] = audits_summary.get(sev, 0) + 1
            if i % 100 == 0 or i == len(jobs):
                print(f"[bake] {i}/{len(jobs)}  ok={successes}  fail={len(failures)}",
                      flush=True)

    manifest = {
        "hymns": [{"n": n, "title": t} for n, t in hymns],
        "patterns": list(patterns),
        "pattern_slugs": {
            ("__default__" if p is None else p): ("default" if p is None else slugify(p))
            for p in patterns
        },
        "abc_dir": "abc",
        "stats": {
            "hymns": len(hymns),
            "variants": len(patterns),
            "successes": successes,
            "failures": len(failures),
            "audits": audits_summary,
        },
        "failures": failures,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[bake] manifest → {out_dir / 'manifest.json'}", flush=True)
    print(f"[bake] done: ok={successes}  fail={len(failures)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
