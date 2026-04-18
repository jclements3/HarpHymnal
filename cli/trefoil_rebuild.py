"""CLI entry point: ``python -m cli.trefoil_rebuild``.

Rebuilds ``data/trefoil/HarpTrefoil.json`` by parsing the authoritative
``source/HarpTrefoil.tex`` macros and inheriting prose sections from
``source/HarpChordSystem.json``.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from trefoil.rebuild import rebuild, write_rebuilt


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_TEX = _REPO_ROOT / 'source' / 'HarpTrefoil.tex'
_DEFAULT_PROSE = _REPO_ROOT / 'source' / 'HarpChordSystem.json'
_DEFAULT_OUT = _REPO_ROOT / 'data' / 'trefoil' / 'HarpTrefoil.json'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description='Rebuild data/trefoil/HarpTrefoil.json from source/HarpTrefoil.tex.',
    )
    ap.add_argument('--tex', type=Path, default=_DEFAULT_TEX,
                    help=f'Input TeX source (default: {_DEFAULT_TEX})')
    ap.add_argument('--prose', type=Path, default=_DEFAULT_PROSE,
                    help=f'Existing JSON for prose pass-through (default: {_DEFAULT_PROSE})')
    ap.add_argument('-o', '--output', type=Path, default=_DEFAULT_OUT,
                    help=f'Output JSON path (default: {_DEFAULT_OUT})')
    args = ap.parse_args(argv)

    rebuilt = rebuild(args.tex, args.prose)

    paths = rebuilt['paths']['entries']
    reserve = rebuilt['reserve']['entries']
    by_cycle: dict[str, int] = {}
    for e in paths:
        by_cycle[e['cycle']] = by_cycle.get(e['cycle'], 0) + 1

    print(f'Extracted {len(paths)} path entries (expected 42)')
    print(f'Extracted {len(reserve)} reserve entries (expected 76)')
    print(f'pool = paths ∪ reserve = {len(paths) + len(reserve)} fractions')
    print(f'Cycle breakdown: {by_cycle}')

    write_rebuilt(rebuilt, args.output)
    print(f'Wrote {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
