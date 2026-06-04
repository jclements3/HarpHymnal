#!/usr/bin/env python3
"""Split downloaded multi-tune .abc collections into one small .abc per tune,
and emit an index.json the Tunes viewer reads.

Input : tunes_src/**/*.abc  (collections, possibly many X: tunes each)
Output: tablet_app/app/src/main/assets/tunes/abc/NNNNN.abc  (one tune each)
        tablet_app/app/src/main/assets/tunes/index.json
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tunes_src")
OUT = os.path.join(ROOT, "tablet_app/app/src/main/assets/tunes")
ABCDIR = os.path.join(OUT, "abc")


def field(lines, tag):
    for ln in lines:
        if ln.startswith(tag):
            return ln[len(tag):].strip()
    return ""


def split_file(text):
    """Yield blocks each beginning with an X: line."""
    blocks, cur = [], []
    for ln in text.splitlines():
        if ln.startswith("X:") and cur:
            blocks.append(cur)
            cur = [ln]
        elif ln.startswith("X:"):
            cur = [ln]
        elif cur:
            cur.append(ln)
    if cur:
        blocks.append(cur)
    return blocks


NOTE = re.compile(r"[A-Ga-gxz]")


def has_music(lines):
    """A real tune has a body line (after K:) with actual note/rest tokens,
    not just lyrics (W:), info headers, or %% formatting directives."""
    seen_key = False
    for ln in lines:
        if ln.startswith("K:"):
            seen_key = True
            continue
        if not seen_key:
            continue
        s = ln.strip()
        if not s or s.startswith("%") or re.match(r"^[A-Za-z]:", ln):
            continue
        # strip inline voice/field markers like [V:1] before scanning for notes
        body = re.sub(r"\[[A-Za-z]:[^\]]*\]", "", ln)
        if NOTE.search(body):
            return True
    return False


def main():
    os.makedirs(ABCDIR, exist_ok=True)
    for f in os.listdir(ABCDIR):
        os.remove(os.path.join(ABCDIR, f))

    index, n = [], 0
    for dirpath, _, files in os.walk(SRC):
        for fn in sorted(files):
            if not fn.endswith(".abc"):
                continue
            rel = os.path.relpath(dirpath, SRC)
            collection = rel.split(os.sep)[0] if rel != "." else "misc"
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            for block in split_file(text):
                if not has_music(block):
                    continue
                title = field(block, "T:") or field(block, "P:") or "(untitled)"
                title = title.strip().strip('"').strip()
                title = re.sub(r"\s{2,}\d+\s*$", "", title)  # drop trailing catalog no.
                title = re.sub(r"\s{2,}", " ", title).strip() or "(untitled)"
                n += 1
                tid = f"{n:05d}"
                abc = "\n".join(block).rstrip() + "\n"
                with open(os.path.join(ABCDIR, tid + ".abc"), "w", encoding="utf-8") as out:
                    out.write(abc)
                index.append({
                    "id": tid,
                    "title": title,
                    "collection": collection,
                    "rhythm": field(block, "R:"),
                    "meter": field(block, "M:"),
                    "key": field(block, "K:"),
                })
    index.sort(key=lambda t: (t["collection"].lower(), t["title"].lower()))
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as out:
        json.dump(index, out, ensure_ascii=False, indent=0, separators=(",", ":"))
    cols = {}
    for t in index:
        cols[t["collection"]] = cols.get(t["collection"], 0) + 1
    print(f"wrote {len(index)} tunes to {ABCDIR}")
    print("collections:", cols)


if __name__ == "__main__":
    main()
