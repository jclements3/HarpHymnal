#!/usr/bin/env python3
"""Generate Android launcher-icon PNGs from ``drill.png``.

Produces, for each density bucket (mdpi..xxxhdpi):

* ``mipmap-<d>/ic_launcher_foreground.png`` — transparent PNG at 108dp, with
  the drill artwork inset into the centre ~66% of the canvas so the launcher
  adaptive-icon mask doesn't clip it.
* ``mipmap-<d>/ic_launcher.png`` — square, opaque PNG with the same drill
  artwork composited over ``#7B2B2B`` (the ``ic_launcher_background`` colour).
  Used on pre-Android-8 devices that don't support adaptive icons.

Re-run this script whenever ``drill.png`` changes. Safe to run repeatedly;
outputs are overwritten in place.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

# Paths -----------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent  # .../tablet_app
PROJECT_ROOT = REPO_ROOT.parent                      # .../HarpHymnal
SOURCE = PROJECT_ROOT / "drill.png"
RES_DIR = REPO_ROOT / "app" / "src" / "main" / "res"

# Density bucket → output square size in pixels. 108dp is the Android adaptive
# icon canvas size; the table below gives the pixel equivalent per density.
DENSITIES: dict[str, int] = {
    "mdpi":    108,
    "hdpi":    162,
    "xhdpi":   216,
    "xxhdpi":  324,
    "xxxhdpi": 432,
}

# Background colour for the legacy ``ic_launcher.png``. Kept in sync with
# ``res/values/colors.xml``'s ``ic_launcher_background`` entry.
BACKGROUND = (0x7B, 0x2B, 0x2B, 0xFF)

# Fraction of the canvas occupied by the drill artwork. The Android adaptive
# icon safe zone is the centre 66dp of a 108dp canvas (~61%), so we keep the
# drill inside a 66% inner square to stay within the safe zone.
INNER_FRACTION = 0.66


def resize_drill(src: Image.Image, target_px: int) -> Image.Image:
    """Return an RGBA canvas of ``target_px`` with ``src`` drawn into the
    centre at ``INNER_FRACTION`` of the canvas size, preserving aspect ratio.
    """
    inner = max(1, round(target_px * INNER_FRACTION))

    # Fit the source into an ``inner × inner`` box, preserving aspect ratio.
    sw, sh = src.size
    scale = min(inner / sw, inner / sh)
    rw = max(1, round(sw * scale))
    rh = max(1, round(sh * scale))
    resized = src.resize((rw, rh), Image.LANCZOS)

    canvas = Image.new("RGBA", (target_px, target_px), (0, 0, 0, 0))
    offset = ((target_px - rw) // 2, (target_px - rh) // 2)
    canvas.paste(resized, offset, resized)
    return canvas


def make_launcher(foreground: Image.Image) -> Image.Image:
    """Composite ``foreground`` over the solid background colour to produce
    an opaque legacy launcher icon."""
    bg = Image.new("RGBA", foreground.size, BACKGROUND)
    bg.alpha_composite(foreground)
    return bg.convert("RGB")  # drop alpha — legacy icons are opaque PNG/JPG.


def main() -> int:
    if not SOURCE.exists():
        print(f"error: source image not found at {SOURCE}", file=sys.stderr)
        return 1

    src = Image.open(SOURCE).convert("RGBA")
    print(f"source: {SOURCE} ({src.size[0]}×{src.size[1]} {src.mode})")

    written = 0
    for bucket, px in DENSITIES.items():
        out_dir = RES_DIR / f"mipmap-{bucket}"
        out_dir.mkdir(parents=True, exist_ok=True)

        fg = resize_drill(src, px)
        fg_path = out_dir / "ic_launcher_foreground.png"
        fg.save(fg_path, format="PNG", optimize=True)
        print(f"  wrote {fg_path.relative_to(REPO_ROOT)} ({px}×{px} RGBA)")

        launcher = make_launcher(fg)
        launcher_path = out_dir / "ic_launcher.png"
        launcher.save(launcher_path, format="PNG", optimize=True)
        print(f"  wrote {launcher_path.relative_to(REPO_ROOT)} ({px}×{px} RGB)")

        written += 2

    print(f"done: {written} files written across {len(DENSITIES)} densities.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
