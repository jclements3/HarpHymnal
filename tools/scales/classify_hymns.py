#!/usr/bin/env python3
"""Classify each hymn in data/hymns/ into one of the 28 pedal-matrix scales.

Reads the comprehensive-export JSON for each hymn and produces:
  data/hymn_scales.json   — { hymn_slug: { family, mode, tonic, raised7_count } }

The classification heuristic (in order):
  1. modal_name = "ionian"     → F1 Ionian
  2. modal_name in {dorian, phrygian, mixolydian}   → F1 <that mode>
  3. modal_name = "aeolian":
       - 4+ raised-7 accidentals in the body  → F3 Aeolian (harmonic minor)
       - otherwise                              → F1 Aeolian (natural minor)
  (F2 melodic minor and F4 harmonic major are not detected here — they
  require checking raised 6 or lowered 6, which is rarer in this corpus.)
"""
import json, os, sys, collections

HYMNS_DIR = "data/hymns"
OUT_PATH  = "data/hymn_scales.json"

LETTERS = ['C','D','E','F','G','A','B']
SEMITONE = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
RAISED_7_THRESHOLD = 4  # >= this many ^7 occurrences -> harmonic minor

def raised_7_letter(root_letter):
    idx = LETTERS.index(root_letter)
    return LETTERS[(idx + 6) % 7]

def count_accidental(abc, letter, sign='^'):
    """Crude scan: count occurrences of sign+letter in the music body
    (skips header / lyric / comment lines)."""
    body = "\n".join(
        l for l in abc.split("\n")
        if l and not l.startswith(("w:","%","T:","X:","M:","L:","K:","Q:","C:","V:","S:","I:","P:","H:","O:","R:","N:","Z:"))
    )
    return body.count(sign + letter) + body.count(sign + letter.lower())

def classify(d):
    root  = d["key"]["root"]                  # e.g. "F", "Eb", "C#"
    mode  = d["key"]["mode"]                  # "major" / "minor"
    modal = d["_modal_name"]                  # ionian/aeolian/dorian/phrygian/mixolydian
    abc   = d["_abc_source"]

    family, scale_mode = "F1", modal
    raised7 = 0

    if modal == "aeolian":
        target = raised_7_letter(root[0])
        raised7 = count_accidental(abc, target, sign="^")
        if raised7 >= RAISED_7_THRESHOLD:
            family = "F3"
    return {
        "family":   family,
        "mode":     scale_mode,
        "tonic":    root,
        "key_mode": mode,
        "raised7":  raised7,
    }

def main():
    out = {}
    stats = collections.Counter()
    for f in sorted(os.listdir(HYMNS_DIR)):
        if not f.endswith(".json"): continue
        slug = f[:-5]
        d = json.load(open(os.path.join(HYMNS_DIR, f)))
        info = classify(d)
        info["title"] = d["title"]
        out[slug] = info
        stats[(info["family"], info["mode"])] += 1

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    json.dump(out, open(OUT_PATH, "w"), indent=2, sort_keys=True)

    print(f"Wrote {OUT_PATH} — {len(out)} hymns")
    print()
    print(f"{'family':<5} {'mode':<12} {'count':>6}")
    for (fam, mode), n in sorted(stats.items(), key=lambda x: (-x[1], x[0])):
        print(f"{fam:<5} {mode:<12} {n:>6}")

if __name__ == "__main__":
    main()
