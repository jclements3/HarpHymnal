"""CLI: run Phase 5 legality + bias scoring over one hymn's variations.

Usage::

    python3 -m cli.reharm_legality <slug>
    python3 -m cli.reharm_legality amazing_grace

Prints a per-variation table to stdout:

    v##   legal  warns  dens    sprd    satb    extr    total   notable-warning

plus a summary footer with aggregate pass/warn counts.  Reads variation
JSONs from ``data/reharm/variations/<slug>/``.  Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from trefoil.reharm.legality import (
        check_variation,
        score_variation,
    )
except ImportError:  # pragma: no cover — script-mode fallback
    here = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(here))
    from trefoil.reharm.legality import (  # type: ignore
        check_variation,
        score_variation,
    )


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VARIATIONS_DIR = REPO_ROOT / "data" / "reharm" / "variations"


def _first_warning(warnings: list[str]) -> str:
    """Return a short tag for the first warning, or ''.

    Keeps the summary line compact; full warning text is available via
    ``--verbose``.
    """
    if not warnings:
        return ""
    w = warnings[0]
    # Compress common warning tags.
    if "cross-bar bass reach" in w:
        return "reach(bass)"
    if "cross-bar top reach" in w:
        return "reach(top)"
    if "lever flips" in w:
        return "lever"
    if "lever flips in consecutive" in w:
        return "lever2bar"
    return w.split(":", 1)[0]


def _format_row(
    name: str,
    passed: bool,
    n_warn: int,
    scores: dict,
    notable: str,
) -> str:
    legal = "ok" if passed else "FAIL"
    return (
        f"{name:<8}  {legal:<4}  {n_warn:>3}  "
        f"{scores['density_axis_score']:>5.2f}  "
        f"{scores['spread_axis_score']:>5.2f}  "
        f"{scores['satb_zone_score']:>5.1f}  "
        f"{scores['expose_extremes_score']:>5.2f}  "
        f"{scores['total_score']:>5.2f}  "
        f"{notable}"
    )


def run(slug: str, verbose: bool = False) -> int:
    vdir = DEFAULT_VARIATIONS_DIR / slug
    if not vdir.is_dir():
        print(f"error: variation directory not found: {vdir}", file=sys.stderr)
        return 2

    files = sorted(p for p in vdir.glob("*.json"))
    if not files:
        print(f"error: no *.json in {vdir}", file=sys.stderr)
        return 2

    header = (
        f"{'file':<8}  {'legal':<4}  {'wrn':>3}  "
        f"{'dens':>5}  {'sprd':>5}  {'satb':>5}  {'extr':>5}  {'total':>5}  notable"
    )
    print(f"Phase 5 legality + scores for slug={slug!r}  ({len(files)} variations)")
    print(header)
    print("-" * len(header))

    passed_count = 0
    failed_count = 0
    warn_count = 0
    totals = {
        "density_axis_score":    0.0,
        "spread_axis_score":     0.0,
        "satb_zone_score":       0.0,
        "expose_extremes_score": 0.0,
        "total_score":           0.0,
    }
    worst_satb = (-1.0, "")
    best_total = (-1.0, "")
    worst_total = (9e9, "")

    for f in files:
        var = json.loads(f.read_text())
        rpt = check_variation(var)
        sc = score_variation(var)

        if rpt.passed:
            passed_count += 1
        else:
            failed_count += 1
        if rpt.warnings:
            warn_count += 1

        for k in totals:
            totals[k] += sc[k]
        if sc["satb_zone_score"] > worst_satb[0]:
            worst_satb = (sc["satb_zone_score"], f.stem)
        if sc["total_score"] > best_total[0]:
            best_total = (sc["total_score"], f.stem)
        if sc["total_score"] < worst_total[0]:
            worst_total = (sc["total_score"], f.stem)

        notable = _first_warning(rpt.warnings)
        print(_format_row(f.stem, rpt.passed, len(rpt.warnings), sc, notable))

        if verbose:
            for e in rpt.errors:
                print(f"    ERROR: {e}")
            for w in rpt.warnings:
                print(f"    warn:  {w}")

    n = len(files)
    print()
    print(f"summary: {passed_count}/{n} passed legality, "
          f"{failed_count} failed, {warn_count} with warnings")
    print(
        "means:   "
        f"dens={totals['density_axis_score']/n:.2f}  "
        f"sprd={totals['spread_axis_score']/n:.2f}  "
        f"satb={totals['satb_zone_score']/n:.2f}  "
        f"extr={totals['expose_extremes_score']/n:.2f}  "
        f"total={totals['total_score']/n:.2f}"
    )
    print(
        f"outliers: worst_satb={worst_satb[1]} ({worst_satb[0]:.1f}); "
        f"best_total={best_total[1]} ({best_total[0]:.2f}); "
        f"worst_total={worst_total[1]} ({worst_total[0]:.2f})"
    )
    return 0 if failed_count == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug", help="hymn slug (e.g. amazing_grace)")
    ap.add_argument(
        "--verbose", "-v", action="store_true",
        help="print full warning / error text under each row",
    )
    args = ap.parse_args(argv)
    return run(args.slug, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
