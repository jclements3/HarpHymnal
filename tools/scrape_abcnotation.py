#!/usr/bin/env python3
"""Scrape individual tunes from abcnotation.com into ./tunes/<source-path>.abc

Each tune is indexed at /tunePage?a=<source-path>/<id>; the ABC lives in a
<pre contenteditable="false">...</pre> block (HTML-escaped). We save one small
.abc per tune, mirroring the source path so collections stay grouped.

Polite + resumable: skips files that already exist, sleeps between requests.
Usage: scrape_abcnotation.py [START_PAGE] [END_PAGE]   (pages 0..1903)
"""
import html
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://abcnotation.com"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tunes")
UA = "Mozilla/5.0 (compatible; harp-tune-collector/1.0)"
DELAY = 0.4  # seconds between tunePage fetches

TUNELINK = re.compile(r'href="/tunePage\?a=([^"]+)"')
PRE = re.compile(r'<pre contenteditable="false">\n?(.*?)</pre>', re.DOTALL)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def browse_links(n):
    url = f"{BASE}/browseTunes?n={n:04d}"
    seen, out = set(), []
    for a in TUNELINK.findall(get(url)):
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out


def save_tune(a):
    dest = os.path.join(OUT, a + ".abc")
    if os.path.exists(dest):
        return "skip"
    qa = urllib.parse.quote(a, safe="/~._-")
    page = get(f"{BASE}/tunePage?a={qa}")
    m = PRE.search(page)
    if not m:
        return "no-abc"
    abc = html.unescape(m.group(1)).rstrip() + "\n"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(abc)
    return "saved"


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 1903
    saved = skipped = errors = 0
    for n in range(start, end + 1):
        try:
            links = browse_links(n)
        except Exception as e:
            print(f"[page {n}] browse error: {e}", flush=True)
            time.sleep(2)
            continue
        for a in links:
            try:
                r = save_tune(a)
                if r == "saved":
                    saved += 1
                    time.sleep(DELAY)
                elif r == "skip":
                    skipped += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"[{a}] {e}", flush=True)
                time.sleep(1)
        print(f"[page {n:04d}/{end}] saved={saved} skipped={skipped} errors={errors}", flush=True)


if __name__ == "__main__":
    main()
