"""CLI: rebuild the tablet viewer's index.json (and optionally stage a bundle).

Usage:
    python -m cli.viewer_build
    python -m cli.viewer_build --data data/ --viewer viewer/
    python -m cli.viewer_build --bundle dist/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow ``python -m cli.viewer_build`` from the repo root without install.
_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from renderers.html import build_index, write_viewer


def _default_data(repo: Path) -> Path:
    return repo / "data"


def _default_viewer(repo: Path) -> Path:
    return repo / "viewer"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="viewer_build",
        description="Rebuild data/index.json (and optionally stage a viewer bundle).",
    )
    parser.add_argument(
        "--data", type=Path, default=_default_data(_REPO),
        help="Data root (default: ./data)",
    )
    parser.add_argument(
        "--viewer", type=Path, default=_default_viewer(_REPO),
        help="Viewer-source root (default: ./viewer)",
    )
    parser.add_argument(
        "--bundle", type=Path, default=None,
        help="Optional target dir for a deployable viewer bundle",
    )
    args = parser.parse_args(argv)

    index_path = write_viewer(
        data_root=args.data,
        viewer_root=args.viewer,
        target=args.bundle,
    )

    manifest = json.loads(index_path.read_text(encoding="utf-8"))
    print(
        f"wrote {index_path} "
        f"({len(manifest['hymns'])} hymns, {len(manifest['drills'])} drills)"
    )
    if args.bundle is not None:
        print(f"staged bundle at {args.bundle}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
