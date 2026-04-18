"""CLI entry point: ``python -m cli.mapper_query V7 D G4 --mode major``.

Runs ``pick_fraction`` against the default pool and prints the top-N results
in the legacy one-line-per-pick format.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mapper.harp_mapper import Pick, pick_fraction
from trefoil.pool import DEFAULT_POOL_PATH, load_pool


def _fmt_roman(r) -> str:
    """Rebuild the raw pool-string form of a Roman for display."""
    return (r.numeral or '') + (r.quality or '') + (r.inversion or '')


def _fmt_pick(p: Pick) -> str:
    lh_str = _fmt_roman(p.lh_chord)
    rh_str = _fmt_roman(p.rh_chord)
    label = f"{lh_str:>6} / {rh_str:<6}   "
    lh_fig = _reassemble_figure(p.bishape.lh.degree, p.bishape.lh.intervals)
    rh_fig = _reassemble_figure(p.bishape.rh.degree, p.bishape.rh.intervals)
    fig = f"lh={lh_fig:<6} rh={rh_fig:<6}"
    mood = p.meta.get('mood') or p.meta.get('cw_label') or ''
    return f"  {p.score:>5.1f}  {label}{fig}   [{p.source}: {mood}]"


def _hex_digit(n: int) -> str:
    """0..15 → '0'..'9','A'..'F' (figures use this convention)."""
    if n < 10:
        return str(n)
    return chr(ord('A') + n - 10)


def _reassemble_figure(degree: int, intervals) -> str:
    """Rebuild the wire-format figure string from a ``Shape``'s fields."""
    return _hex_digit(degree) + ''.join(str(i) for i in intervals)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description='Query the 118-fraction pool for the best fraction matching '
                    'a roman numeral + key + optional melody note.',
    )
    ap.add_argument('rn', help='Roman numeral, e.g. V7, I64, iii6')
    ap.add_argument('key', help='Key root, e.g. D, F, Bb, A')
    ap.add_argument('melody', nargs='?', default=None,
                    help='Optional melody pitch, e.g. G4, C#5')
    ap.add_argument('--mode', default='major', choices=('major', 'minor'))
    ap.add_argument('--top', type=int, default=3)
    ap.add_argument('--pool', type=Path, default=DEFAULT_POOL_PATH,
                    help=f'Pool JSON (default: {DEFAULT_POOL_PATH})')
    args = ap.parse_args(argv)

    pool = load_pool(args.pool)
    results = pick_fraction(pool, args.rn, args.key, args.melody,
                            args.mode, args.top)
    if not results:
        print(f"No matches for RN={args.rn} in key {args.key} {args.mode}")
        return 1

    melody_msg = f", melody={args.melody}" if args.melody else ""
    print(f"\nTop {len(results)} matches for {args.rn} in {args.key} {args.mode}{melody_msg}")
    print("─" * 80)
    for r in results:
        print(_fmt_pick(r))
    return 0


if __name__ == '__main__':
    sys.exit(main())
