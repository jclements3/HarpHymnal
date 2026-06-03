"""Build the key-agnostic Larsen lick library from the editable source ABC
(../../hymnal/altered_licks_Eb.abc). Re-run after editing a lick.
Stores each lick functionally: ii7 / V7alt / Imaj7 cells, notes as
(semitones-above-Eb-tonic, duration), with in-bar accidental carry resolved."""
import re, json, os
SRC = os.path.join(os.path.dirname(__file__), "..", "..", "hymnal", "altered_licks_Eb.abc")
NAT = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def _oct(note, mk): return (5 if note.islower() else 4) + mk.count("'") - mk.count(',')
def parse_cell(cell):
    cell = re.sub(r'"[^"]*"', '', cell)
    carry, out = {}, []
    for acc, note, mk, dur in re.findall(r"([_=^]*)([A-Ga-g])([,']*)(\d*)", cell):
        L = note.upper(); o = _oct(note, mk); key = (L, o); a = acc[-1] if acc else None
        if a: carry[key] = a
        else: a = carry.get(key)
        m = NAT[L] + (o + 1) * 12
        if a == '_': m -= 1
        elif a == '^': m += 1
        elif a is None and L in ('B', 'E', 'A'): m -= 1        # K:Eb
        out.append([m - 39, int(dur) if dur else 1])
    return out
def v_clean(v):
    v = re.sub(r'"[^"]*"', '', v); req = {}
    for acc, n, mk in re.findall(r"([_=^]*)([A-Ga-g])([,']*)", v):
        if acc: req.setdefault(n.upper(), set()).add(acc[-1])
    return not any(len(s) > 1 for s in req.values())
FUNC = ["ii7", "V7alt", "Imaj7"]
def build():
    txt = open(SRC, encoding="utf-8").read()
    blocks = re.split(r'(?m)^X:\s*\d+\s*$', txt)[1:]
    lib = []
    for k, b in enumerate(blocks):
        nm = re.search(r'^T:\s*(.+)$', b, re.M)
        body = next((ln for ln in b.splitlines() if '|' in ln and '"' in ln), None)
        if not body: continue
        cells = [c.strip() for c in body.replace('|]', '|').split('|') if c.strip()][:3]
        lib.append({"id": k + 1, "name": nm.group(1).strip() if nm else "Lick %d" % (k+1),
                    "pedal_clean": v_clean(cells[1]),
                    "cells": [{"func": FUNC[i], "notes": parse_cell(cells[i])} for i in range(3)]})
    json.dump(lib, open(os.path.join(os.path.dirname(__file__), "larsen_keyagnostic.json"), "w"), indent=0)
    return lib
if __name__ == "__main__":
    lib = build()
    print("built %d licks from %s | pedal-clean: %s" %
          (len(lib), os.path.basename(SRC), [l["id"] for l in lib if l["pedal_clean"]]))
