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
# Spelling intent per pitch class: letter + the accidental that letter naturally
# carries in this enharmonic direction ('' natural, '_' flat, '^' sharp).  Whether
# the accidental is actually PRINTED is decided later against the key signature and
# the in-bar accidental state (standard notation: print only when the pitch differs
# from the key signature, or to cancel an earlier accidental in the same bar).
_FLAT  = ["C","_D","D","_E","E","F","_G","G","_A","A","_B","B"]
_SHARP = ["C","^C","D","^D","E","F","^F","G","^G","A","^A","B"]
_FLATKEYS = {"F","Bb","Eb","Ab","Db","Gb","C"}   # melodic-minor harp keys lean flat

_LET = {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}
_ORDER = "CDEFGAB"
def _tonic_pc(key):
    k = key[:-1] if key.endswith("m") else key
    pc = _LET[k[0]]
    for c in k[1:]:
        if c in "#♯": pc += 1
        elif c in "b♭": pc -= 1
    return pc % 12

def spell_flat(key):
    """Whether to spell black keys with flats (vs sharps) in this key."""
    minor = key.endswith("m"); k = key[:-1] if minor else key
    return (k not in {"E", "B", "F#", "C#", "G#"}) if minor else (k in _FLATKEYS)

def keysig_acc(key):
    """letter -> accidental the key SIGNATURE gives it ('' natural, '_' flat, '^' sharp).
    Minor uses the natural-minor scale, i.e. its relative-major signature."""
    minor = key.endswith("m"); k = key[:-1] if minor else key
    tpc = _LET[k[0]]
    for c in k[1:]:
        if c in "#♯": tpc += 1
        elif c in "b♭": tpc -= 1
    tpc %= 12
    iv = [0, 2, 3, 5, 7, 8, 10] if minor else [0, 2, 4, 5, 7, 9, 11]
    li = _ORDER.index(k[0]); acc = {}
    for i, step in enumerate(iv):
        letter = _ORDER[(li + i) % 7]; pc = (tpc + step) % 12
        d = (pc - _LET[letter]) % 12; d = d - 12 if d > 6 else d
        acc[letter] = {-1: "_", 0: "", 1: "^"}.get(d, "")
    return acc

def _enc(letter, octv):
    return (letter.lower() + "'" * (octv - 5)) if octv >= 5 else (letter.upper() + "," * (4 - octv))

def _tok(pc, octv, flat, state, ksacc):
    """ABC token for one pitch, printing an accidental only when it differs from the
    key signature or from an earlier accidental on the same (letter, octave) this bar.
    Mutates `state`, the per-bar accidental memory keyed by (letter, octave)."""
    nm = (_FLAT if flat else _SHARP)[pc]; intended = nm[:-1]; letter = nm[-1]
    cur = state.get((letter, octv), ksacc.get(letter, ""))
    if intended == cur:
        pref = ""
    else:
        pref = intended if intended else "="          # natural must be spelled '='
        state[(letter, octv)] = intended
    return pref + _enc(letter, octv)

def spell_note(key, semi, octave, state, ksacc, flat):
    """One bare note token for `semi` semitones above the tonic, low end near `octave`."""
    t = _tonic_pc(key); m = (octave + 1) * 12 + t + semi
    return _tok(m % 12, m // 12 - 1, flat, state, ksacc)

def spell_chord(key, semis, octave, state, ksacc, flat):
    """One ABC chord [..] sharing the bar's accidental `state`."""
    return "[" + "".join(spell_note(key, s, octave, state, ksacc, flat) for s in sorted(semis)) + "]"

def render(lick, key, octave_shift=0):
    """Render a key-agnostic lick as an ABC 'ii7..|V7alt..|Imaj7..' phrase in `key`.
    The library stores notes as semitones above E-flat (midi 39 = Eb2); shift the
    whole lick by the nearest transposition to the target tonic (-6..+5 semitones)
    so it stays in a comfortable register. octave_shift moves it whole octaves.
    Accidentals are printed minimally (key-signature + in-bar carry aware); each cell
    is its own bar, so the accidental memory resets at every barline."""
    flat = spell_flat(key); ksacc = keysig_acc(key); t = _tonic_pc(key)
    delta = ((t - 3 + 6) % 12) - 6 + 12 * octave_shift   # Eb pc = 3; nearest shift
    out = []
    for c in lick["cells"]:
        state = {}; toks = []
        for semi, dur in c["notes"]:
            m = 39 + semi + delta
            toks.append(_tok(m % 12, m // 12 - 1, flat, state, ksacc) + (str(dur) if dur != 1 else ""))
        out.append('"%s"%s' % (c["func"], " ".join(toks)))
    return " | ".join(out)
