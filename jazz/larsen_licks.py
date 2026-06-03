"""Key-agnostic Larsen altered ii-V-I licks (after Jens Larsen, harp adaptation).

Each lick is stored functionally: three cells (ii7 / V7alt / Imaj7), every note a
(semitones-above-tonic, duration) pair -- so a lick transposes into ANY key by
shifting the tonic. `pedal_clean` is an interval property (true in every key):
only licks 1, 6, 8 sit in one harp pedal setting per bar; the rest need the b9
respelled / avoided in any key.

    from jazz.larsen_licks import LICKS, render, clean_licks
    render(LICKS[0], "G")     # Lick 1 as an ABC ii-V-I in G
"""
import json, os

LICKS = json.load(open(os.path.join(os.path.dirname(__file__), "larsen_keyagnostic.json")))

def clean_licks():
    """Licks playable in one pedal setting per bar -- valid in EVERY key."""
    return [l for l in LICKS if l["pedal_clean"]]

_TONIC = {"C":0,"Db":1,"D":2,"Eb":3,"E":4,"F":5,"F#":6,"Gb":6,"G":7,
          "Ab":8,"A":9,"Bb":10,"B":11}
_FLAT  = ["C","_D","D","_E","E","F","_G","G","_A","A","_B","B"]
_SHARP = ["C","^C","D","^D","E","F","^F","G","^G","A","^A","B"]
_FLATKEYS = {"F","Bb","Eb","Ab","Db","Gb","C"}   # melodic-minor harp keys lean flat

_LET = {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}
def _tonic_pc(key):
    k = key[:-1] if key.endswith("m") else key
    pc = _LET[k[0]]
    for c in k[1:]:
        if c in "#♯": pc += 1
        elif c in "b♭": pc -= 1
    return pc % 12

def render(lick, key, octave_shift=0):
    """Render a key-agnostic lick as an ABC 'ii7..|V7alt..|Imaj7..' phrase in `key`.
    The library stores notes as semitones above E-flat (midi 39 = Eb2); shift the
    whole lick by the nearest transposition to the target tonic (-6..+5 semitones)
    so it stays in a comfortable register. octave_shift moves it whole octaves."""
    minor = key.endswith("m")
    k = key[:-1] if minor else key
    flat = (k not in {"E","B","F#","C#","G#"}) if minor else (k in _FLATKEYS)
    names = _FLAT if flat else _SHARP
    t = _tonic_pc(key)
    delta = ((t - 3 + 6) % 12) - 6 + 12 * octave_shift   # Eb pc = 3; nearest shift
    out = []
    for c in lick["cells"]:
        toks = []
        for semi, dur in c["notes"]:
            m = 39 + semi + delta
            pc = m % 12; octv = m // 12 - 1
            nm = names[pc]; letter = nm[-1]
            if octv >= 5:
                enc = nm[:-1] + letter.lower() + ("'" * (octv - 5))
            else:
                enc = nm[:-1] + letter.upper() + ("," * (4 - octv))
            toks.append(enc + (str(dur) if dur != 1 else ""))
        out.append('"%s"%s' % (c["func"], " ".join(toks)))
    return " | ".join(out)
