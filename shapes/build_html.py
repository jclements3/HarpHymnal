#!/usr/bin/env python3
r"""Render the shape-encoding markdown docs into HTML.

Each `^N` in the source becomes:

    <span class="deg">N̂</span>

where the inner text is the digit followed by Unicode combining
circumflex U+0302. The hat renders via the vendored DejaVu Sans Mono
font (style.css ships it as a webfont) — DejaVu has glyph metrics
for combining diacritics over digits, where most system monospace
fonts do not. The .deg span tints the hatted digit in the accent
color for extra visual contrast. Copy-paste yields literal `1̂`,
round-trippable through any Unicode-aware tool.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
DOCS = ['QRG', 'README', 'DRILLS', 'SAMPLES', 'HANDOUT', 'STACKS', 'VERIFY', 'HANDOFF', 'NEXTSESSION']

DEG_RE = re.compile(r'\^([1-7])')


def patch_caret(html: str) -> str:
    return DEG_RE.sub(lambda m: f'<span class="deg">{m.group(1)}̂</span>', html)


def main() -> None:
    for name in DOCS:
        md = HERE / f'{name}.md'
        out = HERE / f'{name}.html'
        subprocess.run(
            ['pandoc', '-f', 'gfm', '-t', 'html5', '-s',
             '--metadata', f'title={name}',
             '-c', 'style.css',
             '-B', str(HERE / '_nav.html'),
             str(md), '-o', str(out)],
            check=True,
        )
        out.write_text(patch_caret(out.read_text()))


if __name__ == '__main__':
    main()
