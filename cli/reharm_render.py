"""CLI: render reharm-selector variations to MIDI + LilyPond.

Phase 7.  For every selector variation under
``data/reharm/variations/<slug>/v##.json``, emit:

  * ``data/reharm/renders/<slug>/v##.mid``  — playable MIDI, GM harp.
  * ``data/reharm/renders/<slug>/v##.ly``   — LilyPond source (no PDF).

Usage::

    python3 -m cli.reharm_render --all [--workers N]
    python3 -m cli.reharm_render <slug>
    python3 -m cli.reharm_render --pdf <slug>    # optional: run lilypond→PDF

``--pdf`` requires the ``lilypond`` binary on PATH.  Without it the step
is skipped with a notice.

Incremental: a variation is skipped if both ``.mid`` and ``.ly`` exist
and the on-disk ``.stamp`` sidecar's ``tactics_hash`` matches the
variation's.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Optional


try:
    from trefoil.reharm.render_midi import render_variation_midi
    from trefoil.reharm.render_lily import render_variation_lily
except ImportError:  # pragma: no cover — script fallback
    here = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(here))
    from trefoil.reharm.render_midi import render_variation_midi  # type: ignore
    from trefoil.reharm.render_lily import render_variation_lily  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VARIATIONS = REPO_ROOT / "data" / "reharm" / "variations"
DEFAULT_HYMNS = REPO_ROOT / "data" / "hymns"
DEFAULT_OUT = REPO_ROOT / "data" / "reharm" / "renders"


def _load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _render_one(variation_path: Path, hymn_path: Path, out_dir: Path,
                 force: bool = False) -> tuple[str, bool, Optional[str]]:
    """Render a single variation.  Returns (name, wrote, error_or_None)."""
    try:
        variation = _load_json(variation_path)
        hymn = _load_json(hymn_path)
        name = variation_path.stem  # e.g. "v28"
        mid_p = out_dir / f"{name}.mid"
        ly_p = out_dir / f"{name}.ly"
        stamp_p = out_dir / f"{name}.stamp"

        cur_hash = variation.get("tactics_hash", "")
        if (not force
                and mid_p.exists() and ly_p.exists() and stamp_p.exists()):
            try:
                if stamp_p.read_text(encoding="utf-8").strip() == cur_hash:
                    return (name, False, None)
            except Exception:
                pass

        render_variation_midi(variation, hymn, mid_p)
        render_variation_lily(variation, hymn, ly_p)
        stamp_p.write_text(cur_hash, encoding="utf-8")
        return (name, True, None)
    except Exception as exc:  # pragma: no cover
        return (variation_path.stem, False, f"{type(exc).__name__}: {exc}")


def _render_hymn(slug: str, variations_dir: Path, hymns_dir: Path,
                  out_dir: Path, force: bool = False) -> dict:
    """Render all variations for one hymn.  Runs in a worker process."""
    v_dir = variations_dir / slug
    hymn_path = hymns_dir / f"{slug}.json"
    if not v_dir.is_dir() or not hymn_path.is_file():
        return {"slug": slug, "error": "missing inputs", "wrote": 0, "skipped": 0, "failed": 0}

    hymn_out_dir = out_dir / slug
    hymn_out_dir.mkdir(parents=True, exist_ok=True)

    wrote = skipped = failed = 0
    errors: list[str] = []
    variation_paths = sorted(v_dir.glob("v*.json"))
    for vp in variation_paths:
        name, did_write, err = _render_one(vp, hymn_path, hymn_out_dir, force=force)
        if err:
            failed += 1
            errors.append(f"{name}: {err}")
        elif did_write:
            wrote += 1
        else:
            skipped += 1
    return {
        "slug": slug,
        "wrote": wrote,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
        "count": len(variation_paths),
    }


def _run_pdf(slug: str, out_dir: Path) -> int:
    """Try to invoke ``lilypond`` over every .ly file for one hymn."""
    binary = shutil.which("lilypond")
    if not binary:
        print("notice: lilypond binary not found on PATH; skipping PDF step.",
              file=sys.stderr)
        return 0
    hymn_out = out_dir / slug
    ok = 0
    for ly in sorted(hymn_out.glob("v*.ly")):
        try:
            subprocess.run(
                [binary, "--pdf", "-o", str(ly.with_suffix("")), str(ly)],
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
            ok += 1
        except Exception as e:  # pragma: no cover
            print(f"lilypond fail on {ly.name}: {e}", file=sys.stderr)
    return ok


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m cli.reharm_render",
        description="Render reharm variations to MIDI + LilyPond.",
    )
    ap.add_argument("slug", nargs="?", help="Hymn slug (e.g. amazing_grace).")
    ap.add_argument("--all", action="store_true",
                    help="Render every hymn with variations under the default dir.")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1,
                    help="Parallel workers for --all (default: CPU count).")
    ap.add_argument("--variations-dir", type=Path, default=DEFAULT_VARIATIONS)
    ap.add_argument("--hymns-dir", type=Path, default=DEFAULT_HYMNS)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--force", action="store_true",
                    help="Re-render even when stamps match (default: incremental).")
    ap.add_argument("--pdf", action="store_true",
                    help="Run lilypond on rendered .ly files (requires lilypond on PATH).")
    args = ap.parse_args(argv)

    variations_dir = args.variations_dir
    hymns_dir = args.hymns_dir
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()

    if args.all:
        slugs = sorted(p.name for p in variations_dir.iterdir() if p.is_dir())
        total_variations = 0
        total_wrote = total_skipped = total_failed = 0
        errors: list[str] = []

        if args.workers <= 1:
            for slug in slugs:
                r = _render_hymn(slug, variations_dir, hymns_dir, out_dir,
                                  force=args.force)
                total_variations += r["count"]
                total_wrote += r["wrote"]
                total_skipped += r["skipped"]
                total_failed += r["failed"]
                errors.extend(r["errors"])
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                futs = {
                    ex.submit(_render_hymn, slug, variations_dir, hymns_dir,
                              out_dir, args.force): slug
                    for slug in slugs
                }
                for fut in as_completed(futs):
                    slug = futs[fut]
                    try:
                        r = fut.result()
                    except Exception as exc:  # pragma: no cover
                        print(f"ERROR {slug}: {exc}", file=sys.stderr)
                        total_failed += 40  # assume full-hymn failure
                        continue
                    total_variations += r["count"]
                    total_wrote += r["wrote"]
                    total_skipped += r["skipped"]
                    total_failed += r["failed"]
                    errors.extend(r["errors"])

        dt = time.time() - t0
        print(f"hymns processed: {len(slugs)}")
        print(f"variations     : {total_variations}")
        print(f"  wrote        : {total_wrote}")
        print(f"  skipped      : {total_skipped}")
        print(f"  failed       : {total_failed}")
        print(f"wall time      : {dt:.1f}s")
        # Size report
        total_bytes = 0
        for p in out_dir.rglob("*"):
            if p.is_file():
                total_bytes += p.stat().st_size
        print(f"output size    : {total_bytes/1024/1024:.1f} MiB")
        if errors and len(errors) < 20:
            print("\nerrors:")
            for e in errors:
                print(f"  {e}")
        return 0 if total_failed == 0 else 1

    if not args.slug:
        ap.error("provide a slug or use --all")

    r = _render_hymn(args.slug, variations_dir, hymns_dir, out_dir, force=args.force)
    dt = time.time() - t0
    print(f"{r['slug']}: {r['wrote']} wrote, {r['skipped']} skipped, "
          f"{r['failed']} failed ({dt:.1f}s)")
    for e in r["errors"][:10]:
        print(f"  {e}")

    if args.pdf:
        n = _run_pdf(args.slug, out_dir)
        print(f"lilypond PDFs generated: {n}")

    return 0 if r["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
