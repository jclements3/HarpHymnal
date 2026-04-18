"""CLI entry point: ``python -m cli.scores_build``.

Builds LilyPond piano scores from ``data/hymns/<slug>.json`` records and
compiles to PDF / SVG / MIDI via the system ``lilypond`` binary.

Usage::

    python -m cli.scores_build --title "Silent_Night"     # single hymn
    python -m cli.scores_build --all                      # full corpus
    python -m cli.scores_build --all --jobs 8 --formats pdf,svg

Flags:
    --hymns-dir    input directory (default: data/hymns/)
    --out-dir      output directory (default: data/scores/)
    --formats      comma-separated: pdf,svg,midi (default: all three)
    --jobs N       parallel workers for --all (default: CPU count)
    --no-compile   only write .ly sources (skip LilyPond invocation)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from parsers.abc import hymn_slug
from renderers.lilypond import build_all_scores, build_score
from trefoil.pool import load_pool


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_HYMNS = _REPO_ROOT / 'data' / 'hymns'
_DEFAULT_OUT = _REPO_ROOT / 'data' / 'scores'


def _resolve_title_to_path(title: str, hymns_dir: Path) -> Path:
    """Match ``title`` to a hymn JSON under ``hymns_dir``.

    Tries exact slug match first, then substring match on the slug, then
    substring match on the file's declared ``title`` field.
    """
    slug = hymn_slug(title)
    exact = hymns_dir / f'{slug}.json'
    if exact.exists():
        return exact
    candidates = sorted(hymns_dir.glob('*.json'))
    for p in candidates:
        if slug and slug in p.stem:
            return p
    # Fall back to scanning titles.
    import json
    for p in candidates:
        try:
            with p.open('r', encoding='utf-8') as f:
                d = json.load(f)
            if title.lower() in (d.get('title', '').lower()):
                return p
        except Exception:
            continue
    raise FileNotFoundError(f'no hymn JSON matching title {title!r} in {hymns_dir}')


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog='python -m cli.scores_build',
        description='Build LilyPond piano scores for hymns.',
    )
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--all', action='store_true',
                      help='Build every hymn under --hymns-dir.')
    mode.add_argument('--title', type=str,
                      help='Build one hymn (slug or title substring).')
    ap.add_argument('--hymns-dir', type=Path, default=_DEFAULT_HYMNS,
                    help=f'Input directory (default: {_DEFAULT_HYMNS})')
    ap.add_argument('--out-dir', type=Path, default=_DEFAULT_OUT,
                    help=f'Output directory (default: {_DEFAULT_OUT})')
    ap.add_argument('--formats', type=str, default='pdf,svg,midi',
                    help='Comma-separated formats (default: pdf,svg,midi).')
    ap.add_argument('--jobs', type=int, default=None,
                    help='Parallel workers for --all (default: CPU count).')
    ap.add_argument('--no-compile', action='store_true',
                    help='Write only .ly sources; skip LilyPond invocation.')
    args = ap.parse_args(argv)

    formats = tuple(
        f.strip().lower() for f in args.formats.split(',') if f.strip()
    )
    compile_flag = not args.no_compile

    pool = load_pool()

    if args.title:
        hp = _resolve_title_to_path(args.title, args.hymns_dir)
        try:
            art = build_score(hp, args.out_dir, pool,
                              compile=compile_flag, formats=formats)
            print(f'built {art["slug"]}')
            for k, v in art.items():
                if isinstance(v, Path):
                    print(f'  {k}: {v}')
            return 0
        except Exception as e:
            print(f'error: {type(e).__name__}: {e}', file=sys.stderr)
            return 1

    # --all
    args.out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    report = build_all_scores(args.hymns_dir, args.out_dir, pool,
                               compile=compile_flag, formats=formats,
                               jobs=args.jobs)
    dt = time.time() - t0

    log_path = args.out_dir / '_batch_report.log'
    with log_path.open('w', encoding='utf-8') as f:
        f.write(f'# scores_build --all — {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'# hymns_dir = {args.hymns_dir}\n')
        f.write(f'# out_dir   = {args.out_dir}\n')
        f.write(f'# formats   = {",".join(formats)}\n')
        f.write(f'# jobs      = {args.jobs}\n')
        f.write(f'# compile   = {compile_flag}\n')
        f.write(f'# {len(report["results"])} hymns, '
                f'{report["ok"]} ok, {report["fail"]} fail, {dt:.1f}s\n\n')
        for r in report['results']:
            slug = r.get('slug', '?')
            if r.get('error'):
                f.write(f'FAIL  {slug:40s}  {r["error"]}\n')
            else:
                arts = r.get('artifacts', {})
                keys = ','.join(sorted(k for k in arts if k != 'ly'))
                f.write(f'OK    {slug:40s}  [{keys}]\n')
    print(f'wrote batch report → {log_path}')
    print(f'done: {report["ok"]} ok, {report["fail"]} fail, {dt:.1f}s')
    return 0 if report['fail'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
