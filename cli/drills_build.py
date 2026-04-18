"""CLI entry point: ``python -m cli.drills_build``.

Loads the default 118-fraction pool, builds every ``(technique, path)``
drill, and writes them under ``data/drills/<technique_slug>/<path_slug>.json``.

Run from the repo root::

    python -m cli.drills_build                 # → data/drills/ (default)
    python -m cli.drills_build -o /tmp/drills  # custom output root
"""
from __future__ import annotations

import argparse
from pathlib import Path

from drills import build_all, write_all
from trefoil.pool import load_pool


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_OUT = _REPO_ROOT / 'data' / 'drills'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description='Build all 108 drill pages (18 techniques × 6 paths).',
    )
    ap.add_argument('-o', '--output', type=Path, default=_DEFAULT_OUT,
                    help=f'Output root (default: {_DEFAULT_OUT})')
    args = ap.parse_args(argv)

    pool = load_pool()
    drills = build_all(pool)
    written = write_all(drills, args.output)

    print(f'Built {len(drills)} drills → {args.output}')
    print(f'Wrote {len(written)} JSON files.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
