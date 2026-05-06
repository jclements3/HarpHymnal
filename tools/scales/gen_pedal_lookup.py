#!/usr/bin/env python3
"""Generate a JSON lookup table: braille pedal string -> scale identity.

For all 4 families x 7 modes x 12 circle-of-fifths tonics (with enharmonic
fallbacks for unreachable spellings) the pedal-matrix encodes the same
4-braille-cell pattern that the abccomposer hexpad shows in its left
gutter. This script computes every (family, mode, tonic) -> braille
mapping and inverts it so the composer can reverse-lookup "what scale am
I in right now?" from the current pedal state.

Output: data/pedal_lookup.json
  { brailleString: [ { family, mode, tonic, popularName, alteration }, ... ] }
"""
import json, os, sys

PARENTS = {
    1: [0, 2, 4, 5, 7, 9, 11],   # Ionian (major)
    2: [0, 2, 3, 5, 7, 9, 11],   # Dorian #7   (melodic minor)
    3: [0, 2, 3, 5, 7, 8, 11],   # Aeolian #7  (harmonic minor)
    4: [0, 2, 4, 5, 7, 8, 11],   # Ionian b6   (harmonic major)
}
FAMILY_POPULAR = {
    1: "major scale",
    2: "melodic minor",
    3: "harmonic minor",
    4: "harmonic major",
}
MODES = ["Ionian","Dorian","Phrygian","Lydian","Mixolydian","Aeolian","Locrian"]
ROTATION_INDEX = {
    1: {"Ionian":0,"Dorian":1,"Phrygian":2,"Lydian":3,"Mixolydian":4,"Aeolian":5,"Locrian":6},
    2: {"Dorian":0,"Phrygian":1,"Lydian":2,"Mixolydian":3,"Aeolian":4,"Locrian":5,"Ionian":6},
    3: {"Aeolian":0,"Locrian":1,"Ionian":2,"Dorian":3,"Phrygian":4,"Lydian":5,"Mixolydian":6},
    4: {"Ionian":0,"Dorian":1,"Phrygian":2,"Lydian":3,"Mixolydian":4,"Aeolian":5,"Locrian":6},
}
ALTERATION = {
    1: {m: "" for m in MODES},
    2: {"Ionian":" #1","Dorian":" #7","Phrygian":" #6","Lydian":" #5",
        "Mixolydian":" #4","Aeolian":" #3","Locrian":" #2"},
    3: {"Ionian":" #5","Dorian":" #4","Phrygian":" #3","Lydian":" #2",
        "Mixolydian":" #1","Aeolian":" #7","Locrian":" #6"},
    4: {"Ionian":" b6","Dorian":" b5","Phrygian":" b4","Lydian":" b3",
        "Mixolydian":" b2","Aeolian":" b1","Locrian":" b7"},
}

LETTERS  = ["C","D","E","F","G","A","B"]
LETTER_PC= {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}
ACC_OFF  = {"f":-1,"n":0,"s":1}

COLUMNS = [
    ("C","n"),("G","n"),("D","n"),("A","n"),
    ("E","n"),("B","n"),("F","s"),
    ("F","n"),("B","f"),("E","f"),("A","f"),
    ("D","f"),("G","f"),
]
ENHARMONIC = {
    ("C","n"): [("B","s"),("D","f")],
    ("G","n"): [("F","s"),("A","f")],
    ("D","n"): [("C","s"),("E","f")],
    ("A","n"): [("G","s"),("B","f")],
    ("E","n"): [("D","s"),("F","f")],
    ("B","n"): [("A","s"),("C","f")],
    ("F","s"): [("G","f"),("E","s")],
    ("F","n"): [("E","s")],
    ("B","f"): [("A","s")],
    ("E","f"): [("D","s")],
    ("A","f"): [("G","s")],
    ("D","f"): [("C","s")],
    ("G","f"): [("F","s")],
}

LEFT_DOT  = {"f":0,"n":1,"s":2}
RIGHT_DOT = {"f":3,"n":4,"s":5}

def rotate(parent, i):
    base = parent[i]
    return [(parent[(i + k) % 7] - base) % 12 for k in range(7)]

def pc_to_pos(letter, pc):
    diff = (pc - LETTER_PC[letter]) % 12
    if diff == 0:  return "n"
    if diff == 1:  return "s"
    if diff == 11: return "f"
    return None

def try_spell(scale_pcs, tL, tA):
    tonic_pc = (LETTER_PC[tL] + ACC_OFF[tA]) % 12
    start = LETTERS.index(tL)
    out = {}
    for k, ival in enumerate(scale_pcs):
        L = LETTERS[(start + k) % 7]
        a = pc_to_pos(L, (tonic_pc + ival) % 12)
        if a is None: return None
        out[L] = a
    return out

def spell_for_column(scale_pcs, col):
    for cand in [col] + ENHARMONIC.get(col, []):
        accs = try_spell(scale_pcs, *cand)
        if accs is not None:
            return cand, accs
    return None, None

def braille_cell(left, right, sep=False):
    bits = 0
    if left  is not None: bits |= 1 << LEFT_DOT[left]
    if right is not None: bits |= 1 << RIGHT_DOT[right]
    if sep: bits |= (1<<3)|(1<<4)|(1<<5)
    return chr(0x2800 + bits)

def braille_pedal(accs):
    return (braille_cell(accs["D"], accs["C"]) +
            braille_cell(accs["B"], None, sep=True) +
            braille_cell(accs["E"], accs["F"]) +
            braille_cell(accs["G"], accs["A"]))

def col_label(col):
    L, A = col
    return L + {"f":"♭","n":"","s":"♯"}[A]

def main():
    out = {}
    for fam in (1,2,3,4):
        parent = PARENTS[fam]
        for mode in MODES:
            rot = ROTATION_INDEX[fam][mode]
            pcs = rotate(parent, rot)
            for col in COLUMNS:
                spelled, accs = spell_for_column(pcs, col)
                if accs is None: continue
                glyph = braille_pedal(accs)
                entry = {
                    "family":      f"F{fam}",
                    "popularName": FAMILY_POPULAR[fam],
                    "mode":        mode + ALTERATION[fam][mode],
                    "tonic":       col_label(col),
                    "spelled":     col_label(spelled),
                    "respelled":   spelled != col,
                }
                out.setdefault(glyph, []).append(entry)

    out_path = "data/pedal_lookup.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"Wrote {out_path} — {len(out)} unique braille patterns covering"
          f" {sum(len(v) for v in out.values())} (family, mode, tonic) cells")

if __name__ == "__main__":
    main()
