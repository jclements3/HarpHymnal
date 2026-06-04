#!/usr/bin/env python3
"""Crawl trillian.mit.edu ABC directory listings and download .abc files.

Walks the public directory tree under chosen collection roots (allowed by
trillian's robots.txt), collecting .abc links, and saves them mirroring the
path under tunes_src/. Polite (delay) and bounded (max files per root).
"""
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = "http://trillian.mit.edu/~jc/music/abc/"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tunes_src")
UA = "Mozilla/5.0 (harp-tune-collector)"
DELAY = 0.3
MAX_PER_ROOT = 400

ROOTS = ["xmas/", "Scotland/", "England/", "Sweden/", "France/", "Klezmer/", "Wales/"]
HREF = re.compile(r'href="([^"?#]+)"')


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def crawl(root):
    """BFS the listing under BASE+root, yielding absolute .abc URLs."""
    queue, seen, found = [BASE + root], set(), []
    while queue and len(found) < MAX_PER_ROOT:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            html = get(url).decode("utf-8", "replace")
        except Exception as e:
            print(f"  list err {url}: {e}", flush=True)
            continue
        time.sleep(DELAY)
        for h in HREF.findall(html):
            if h.startswith("/") or h.startswith("..") or h.startswith("http"):
                continue
            full = urllib.parse.urljoin(url, h)
            if not full.startswith(BASE):
                continue
            if h.endswith(".abc"):
                if full not in found:
                    found.append(full)
            elif h.endswith("/"):
                if full not in seen:
                    queue.append(full)
    return found[:MAX_PER_ROOT]


def main():
    total = 0
    for root in ROOTS:
        urls = crawl(root)
        print(f"[{root}] {len(urls)} abc files", flush=True)
        for u in urls:
            rel = u[len(BASE):]
            dest = os.path.join(OUT, rel)
            if os.path.exists(dest):
                continue
            try:
                data = get(u)
            except Exception as e:
                print(f"  dl err {u}: {e}", flush=True)
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            total += 1
            time.sleep(DELAY)
        print(f"[{root}] done, running total saved={total}", flush=True)
    print(f"TOTAL saved {total}", flush=True)


if __name__ == "__main__":
    main()
