"""CLI: phrase-align fragment-cut + catalog build.

Phase 8 driver.  For every variation under ``data/reharm/variations/<slug>/``,
carves phrase-aligned fragment MIDIs + LilyPond sources into
``data/reharm/fragments/<slug>/v##_p<N>.{mid,ly}``, then rebuilds the
corpus catalog at ``data/reharm/catalog.json``.

Usage::

    python3 -m cli.reharm_cut --all [--workers N] [--force]
    python3 -m cli.reharm_cut <slug>
    python3 -m cli.reharm_cut --catalog-only

``--force`` ignores the mtime / tactics_hash stamp and re-cuts everything.
``--catalog-only`` skips the cut phase and just rebuilds ``catalog.json``
from whatever fragments are currently on disk.

Stdlib only.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional


try:
    from trefoil.reharm.fragment_cut import cut_all, cut_hymn
    from trefoil.reharm.catalog import build_catalog
except ImportError:  # pragma: no cover — script fallback
    here = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(here))
    from trefoil.reharm.fragment_cut import cut_all, cut_hymn  # type: ignore
    from trefoil.reharm.catalog import build_catalog  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VARIATIONS = REPO_ROOT / "data" / "reharm" / "variations"
DEFAULT_HYMNS = REPO_ROOT / "data" / "hymns"
DEFAULT_FRAGMENTS = REPO_ROOT / "data" / "reharm" / "fragments"
DEFAULT_RENDERS = REPO_ROOT / "data" / "reharm" / "renders"
DEFAULT_CATALOG = REPO_ROOT / "data" / "reharm" / "catalog.json"


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m cli.reharm_cut",
        description="Phrase-align fragment cut + catalog build.",
    )
    ap.add_argument("slug", nargs="?", help="Single hymn slug to cut.")
    ap.add_argument("--all", action="store_true",
                    help="Cut every hymn under the default variations dir.")
    ap.add_argument("--catalog-only", action="store_true",
                    help="Skip the cut step, only rebuild catalog.json.")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1,
                    help="Parallel workers (default: CPU count).")
    ap.add_argument("--variations-dir", type=Path, default=DEFAULT_VARIATIONS)
    ap.add_argument("--hymns-dir", type=Path, default=DEFAULT_HYMNS)
    ap.add_argument("--fragments-dir", type=Path, default=DEFAULT_FRAGMENTS)
    ap.add_argument("--renders-dir", type=Path, default=DEFAULT_RENDERS)
    ap.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    ap.add_argument("--force", action="store_true",
                    help="Ignore stamps / mtime; re-cut everything.")
    ap.add_argument("--force-full-catalog", action="store_true",
                    help="Re-scan every hymn when building catalog (default: "
                         "only slugs whose fragment dir mtime is newer than "
                         "the previous catalog).")
    args = ap.parse_args(argv)

    t0 = time.time()

    if not args.catalog_only:
        if args.all:
            summary = cut_all(
                variations_dir=args.variations_dir,
                hymns_dir=args.hymns_dir,
                fragments_dir=args.fragments_dir,
                renders_dir=args.renders_dir,
                workers=args.workers,
                force=args.force,
                progress=True,
            )
            print(f"\n=== bulk cut complete ===")
            print(f"hymns processed : {summary['hymns']}")
            print(f"fragments       : {summary['fragments']}")
            print(f"  wrote         : {summary['wrote']}")
            print(f"  skipped       : {summary['skipped']}")
            print(f"  failed        : {summary['failed']}")
            print(f"wall time (cut) : {summary['wall_seconds']:.1f}s")
            if summary.get("errors"):
                print(f"\nfirst few errors:")
                for e in summary["errors"][:10]:
                    print(f"  {e}")
        elif args.slug:
            r = cut_hymn(
                args.slug,
                variations_dir=args.variations_dir,
                hymns_dir=args.hymns_dir,
                fragments_dir=args.fragments_dir,
                renders_dir=args.renders_dir,
                force=args.force,
            )
            print(f"{r['slug']}: {r['fragments']} frags, "
                  f"{r['wrote']} wrote, {r['skipped']} skip, "
                  f"{r['failed']} fail")
            for e in r.get("errors") or []:
                print(f"  {e}")
        else:
            ap.error("provide a slug, or --all, or --catalog-only")

    # Always rebuild the catalog after a cut run.
    t1 = time.time()
    print("\nbuilding catalog…")
    catalog = build_catalog(
        variations_dir=args.variations_dir,
        fragments_dir=args.fragments_dir,
        renders_dir=args.renders_dir,
        hymns_dir=args.hymns_dir,
        out_path=args.catalog,
        force_full=args.force_full_catalog,
    )
    cat_dt = time.time() - t1
    cat_size = args.catalog.stat().st_size if args.catalog.is_file() else 0
    stats = catalog.get("corpus_stats", {})
    print(f"catalog: {args.catalog}")
    print(f"  size          : {cat_size/1024:.1f} KB ({cat_size} bytes)")
    print(f"  hymns         : {stats.get('total_hymns')}")
    print(f"  variations    : {stats.get('total_variations')}")
    print(f"  fragments     : {stats.get('total_fragments')}")
    mean_s = stats.get('mean_total_score')
    print(f"  mean score    : {mean_s:.3f}" if isinstance(mean_s, float)
          else f"  mean score    : {mean_s}")
    print(f"  build (cat)   : {cat_dt:.1f}s")
    print(f"  wall total    : {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
