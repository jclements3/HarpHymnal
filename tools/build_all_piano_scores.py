#!/usr/bin/env python3
"""Batch-render every hymn's piano score (.ly + .pdf + .svg + .midi).

Scans hymnal_export/*.json, pairs each with hymnal_html/reharms/<name>.json,
runs tools/build_piano_score.py, and writes files into hymnal_html/ using
the same slug scheme as review.html (lowercased, non-alnum → underscore).

Per-hymn successes and failures are appended to hymnal_html/batch_report.log.
"""
import glob
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = ROOT / 'hymnal_export'
REHARM_DIR = ROOT / 'hymnal_html' / 'reharms'
OUT_DIR = ROOT / 'hymnal_html'
LOG_PATH = OUT_DIR / 'batch_report.log'


def slug_from_title(title):
    """Same rule as tools/build_review_html.py hymn_slug(), lowercased
    so the filename matches HarpHymnal.html's fetch-HEAD probe."""
    s = re.sub(r'[^A-Za-z0-9]+', '_', title).strip('_')
    return s.lower()


def main():
    exports = sorted(glob.glob(str(EXPORT_DIR / '*.json')))
    if not exports:
        sys.exit(f'No exports found in {EXPORT_DIR}')

    log = open(LOG_PATH, 'w')
    log.write(f'# Batch piano-score run — {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    log.write(f'# {len(exports)} hymns to process\n\n')
    log.flush()

    ok = 0
    fail = 0
    start = time.time()
    for i, export_path in enumerate(exports, 1):
        import json
        try:
            title = json.load(open(export_path)).get('title', Path(export_path).stem)
        except Exception as e:
            log.write(f'[{i:03d}] SKIP  {export_path} — could not read title ({e})\n')
            log.flush()
            fail += 1
            continue

        slug = slug_from_title(title)
        # Reharm JSON basename matches export JSON basename (Title_With_Underscores.json).
        reharm_path = REHARM_DIR / Path(export_path).name
        if not reharm_path.exists():
            log.write(f'[{i:03d}] SKIP  {slug} — no reharm JSON\n')
            log.flush()
            fail += 1
            continue

        ly_out = OUT_DIR / f'{slug}.ly'
        cmd = [
            sys.executable, str(ROOT / 'tools' / 'build_piano_score.py'),
            str(export_path), str(reharm_path),
            '-o', str(ly_out),
            '--svg',
        ]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        dt = time.time() - t0
        if proc.returncode == 0:
            log.write(f'[{i:03d}] OK    {slug}  ({dt:.1f}s)\n')
            ok += 1
        else:
            tail = (proc.stderr or proc.stdout).splitlines()[-3:]
            log.write(f'[{i:03d}] FAIL  {slug}  ({dt:.1f}s) — rc={proc.returncode}\n')
            for ln in tail:
                log.write(f'         {ln}\n')
            fail += 1
        log.flush()

        # Per-100 progress echo to stderr
        if i % 25 == 0 or i == len(exports):
            elapsed = time.time() - start
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(exports) - i) / rate if rate > 0 else 0
            print(f'[{i}/{len(exports)}]  ok={ok}  fail={fail}  '
                  f'elapsed={elapsed:.0f}s  eta={eta:.0f}s', file=sys.stderr)

    total = time.time() - start
    log.write(f'\n# Done: {ok} ok, {fail} fail, {total:.0f}s\n')
    log.close()
    print(f'Done: {ok} ok, {fail} fail, {total:.0f}s', file=sys.stderr)


if __name__ == '__main__':
    main()
