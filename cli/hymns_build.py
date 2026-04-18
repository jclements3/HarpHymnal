"""python -m cli.hymns_build — build hymn JSONs under data/hymns/.

Usage:
    python -m cli.hymns_build --all
    python -m cli.hymns_build --title "Amazing Grace"
    python -m cli.hymns_build --all --abc source/OpenHymnal.abc --out-dir data/hymns/
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from parsers.abc import (
    hymn_slug,
    iter_tunes,
    parse_hymn,
    write_song_json,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m cli.hymns_build")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true",
                      help="Build every hymn in the ABC file.")
    mode.add_argument("--title", type=str,
                      help="Build a single hymn (substring match on T:).")
    ap.add_argument("--abc", type=Path, default=Path("source/OpenHymnal.abc"),
                    help="Path to the ABC source (default: source/OpenHymnal.abc).")
    ap.add_argument("--out-dir", type=Path, default=Path("data/hymns"),
                    help="Output directory (default: data/hymns/).")
    args = ap.parse_args(argv)

    if not args.abc.exists():
        print(f"error: ABC source not found: {args.abc}", file=sys.stderr)
        return 2

    text = args.abc.read_text()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.title:
        song = parse_hymn(text, args.title)
        path = write_song_json(song, args.out_dir)
        print(f"wrote {path}")
        return 0

    # --all
    titles = [t for t, _ in iter_tunes(text)]
    print(f"building {len(titles)} hymns → {args.out_dir}/")
    ok = 0
    fail = 0
    for t in titles:
        try:
            song = parse_hymn(text, t)
            write_song_json(song, args.out_dir)
            ok += 1
            if ok % 25 == 0:
                print(f"  {ok}/{len(titles)} done")
        except Exception as e:
            fail += 1
            print(f"  ! skip {t!r}: {e}", file=sys.stderr)
    print(f"done: {ok} succeeded, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
