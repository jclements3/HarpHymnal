# Diatonic Chord Stacks — Generic-Interval Table

A table of diatonic chord names for stacks of generic intervals starting on each scale degree of the major scale. Naming follows the harp handout system (`HarpChordSystem.json`).

## How to read the table

- **Columns**: scale degree (I – VII) of the *bottom* note of the stack.
- **Rows**: a stack of 1, 2, or 3 generic intervals. `3,3` means "stack a third, then another third"; `3,3,3` means three stacked thirds.
- **Cells**: the most-abbreviated chord name. The caret-digit (I, II…) marks the **root** of the chord, not the bottom note. Quality follows: empty for major triads, `m` for minor, `°` for diminished, `Δ` for major-7th, `7` for dominant-7th, `m7`, `ø7`, `°7`, `s2`, `s4`, `q` for quartal. Superscripts ¹²³ mark inversions (bass = 3rd, 5th, or 7th of the chord). `+8` marks octave doubling of any chord tone.
- **Empty cells**: diatonic stacks that don't form a recognized tertian, sus, quartal, or added-6 sonority (genuine clusters like `I-II-III` or `I-II-IV`).

Constraints: each interval ≤ 12, sum of intervals ≤ 12. All combinations are ordered (`3,2 ≠ 2,3`).

## The table

| Stack | I | II | III | IV | V | VI | VII |
|---|---|---|---|---|---|---|---|
| 2 | III | IIIII | IIIIV | IVV | VVI | VIVII | VIII |
| 3 | IIII | IIIV | IIIV | IVVI | VVII | VII | VIIII |
| 4 | IIV | IIV | IIIVI | IVVII | VI | VIII | VIIIII |
| 5 | IV | IIVI | IIIVII | IVI | VII | VIIII | VIIIV |
| 6 | IVI | IIVII | IIII | IVII | VIII | VIIV | VIIV |
| 7 | IVII | III | IIIII | IVIII | VIV | VIV | VIIVI |
| 8 | II | IIII | IIIIII | IVIV | VV | VIVI | VIIVII |
| 2,4 | Is2 | IIs2 |  | IVs2 | Vs2 | VIs2 |  |
| 2,7 | III+8 | IIIII+8 | IIIIV+8 | IVV+8 | VVI+8 | VIVII+8 | VIII+8 |
| 2,8 | III+8 | IIIII+8 | IIIIV+8 | IVV+8 | VVI+8 | VIVII+8 | VIII+8 |
| 3,3 | I | ii | iii | IV | V | vi | vii° |
| 3,4 | vi¹ | vii°¹ | I¹ | ii¹ | iii¹ | IV¹ | V¹ |
| 3,6 | IIII+8 | IIIV+8 | IIIV+8 | IVVI+8 | VVII+8 | VII+8 | VIIII+8 |
| 3,8 | IIII+8 | IIIV+8 | IIIV+8 | IVVI+8 | VVII+8 | VII+8 | VIIII+8 |
| 4,2 | Is4 | IIs4 | IIIs4 |  | Vs4 | VIs4 |  |
| 4,3 | IV² | V² | vi² | vii°² | I² | ii² | iii² |
| 4,4 |  | IIq | IIIq |  | Vq | VIq | VIIq |
| 4,5 | IIV+8 | IIV+8 | IIIVI+8 | IVVII+8 | VI+8 | VIII+8 | VIIIII+8 |
| 4,8 | IIV+8 | IIV+8 | IIIVI+8 | IVVII+8 | VI+8 | VIII+8 | VIIIII+8 |
| 5,4 | IV+8 | IIVI+8 | IIIVII+8 | IVI+8 | VII+8 | VIIII+8 | VIIIV+8 |
| 5,5 | Is2 | IIs2 |  | IVs2 | Vs2 | VIs2 |  |
| 5,6 | I | ii | iii | IV | V | vi | vii° |
| 5,7 | Is4 | IIs4 | IIIs4 |  | Vs4 | VIs4 |  |
| 6,3 | IVI+8 | IIVII+8 | IIII+8 | IVII+8 | VIII+8 | VIIV+8 | VIIV+8 |
| 6,5 | vi¹ | vii°¹ | I¹ | ii¹ | iii¹ | IV¹ | V¹ |
| 6,6 | IV² | V² | vi² | vii°² | I² | ii² | iii² |
| 7,2 | IVII+8 | III+8 | IIIII+8 | IVIII+8 | VIV+8 | VIV+8 | VIIVI+8 |
| 7,5 |  | IIq | IIIq |  | Vq | VIq | VIIq |
| 8,2 | III+8 | IIIII+8 | IIIIV+8 | IVV+8 | VVI+8 | VIVII+8 | VIII+8 |
| 8,3 | IIII+8 | IIIV+8 | IIIV+8 | IVVI+8 | VVII+8 | VII+8 | VIIII+8 |
| 8,4 | IIV+8 | IIV+8 | IIIVI+8 | IVVII+8 | VI+8 | VIII+8 | VIIIII+8 |
| 2,3,3 | ii7³ | iii7³ | IVΔ³ | V7³ | vi7³ | VIIø7³ | IΔ³ |
| 2,4,4 | Is2+8 | IIs2+8 |  | IVs2+8 | Vs2+8 | VIs2+8 |  |
| 2,4,5 | Is2+8 | IIs2+8 |  | IVs2+8 | Vs2+8 | VIs2+8 |  |
| 2,7,2 | III+8 | IIIII+8 | IIIIV+8 | IVV+8 | VVI+8 | VIVII+8 | VIII+8 |
| 3,2,3 | IVΔ² | V7² | vi7² | VIIø7² | IΔ² | ii7² | iii7² |
| 3,2,4 |  | IIq7 | IIIq7 |  |  | VIq7 | VIIq7 |
| 3,3,2 | I6 | ii6 | IΔ¹ | IV6 | V6 | IVΔ¹ | V7¹ |
| 3,3,3 | IΔ | ii7 | iii7 | IVΔ | V7 | vi7 | VIIø7 |
| 3,3,4 | I+8 | ii+8 | iii+8 | IV+8 | V+8 | vi+8 | vii°+8 |
| 3,3,6 | I+8 | ii+8 | iii+8 | IV+8 | V+8 | vi+8 | vii°+8 |
| 3,4,3 | vi¹+8 | vii°¹+8 | I¹+8 | ii¹+8 | iii¹+8 | IV¹+8 | V¹+8 |
| 3,4,5 | vi¹+8 | vii°¹+8 | I¹+8 | ii¹+8 | iii¹+8 | IV¹+8 | V¹+8 |
| 3,6,3 | IIII+8 | IIIV+8 | IIIV+8 | IVVI+8 | VVII+8 | VII+8 | VIIII+8 |
| 4,2,4 | Is4+8 | IIs4+8 | IIIs4+8 |  | Vs4+8 | VIs4+8 |  |
| 4,3,3 | IV²+8 | V²+8 | vi²+8 | vii°²+8 | I²+8 | ii²+8 | iii²+8 |
| 4,3,4 | ii7³ | iii7³ | IVΔ³ | V7³ | vi7³ | VIIø7³ | IΔ³ |
| 4,3,5 | IVΔ² | V7² | vi7² | VIIø7² | IΔ² | ii7² | iii7² |
| 4,4,2 |  | IIq+8 | IIIq+8 |  | Vq+8 | VIq+8 | VIIq+8 |
| 4,4,4 |  | IIq7 | IIIq7 |  |  | VIq7 | VIIq7 |
| 5,2,5 | I6 | ii6 | IΔ¹ | IV6 | V6 | IVΔ¹ | V7¹ |
| 5,3,4 | IΔ | ii7 | iii7 | IVΔ | V7 | vi7 | VIIø7 |
| 5,4,2 | Is2+8 | IIs2+8 |  | IVs2+8 | Vs2+8 | VIs2+8 |  |
| 5,4,3 | I+8 | ii+8 | iii+8 | IV+8 | V+8 | vi+8 | vii°+8 |
| 6,3,3 | vi¹+8 | vii°¹+8 | I¹+8 | ii¹+8 | iii¹+8 | IV¹+8 | V¹+8 |

*All-empty rows (clusters and unrecognized sonorities) are omitted. Run the script below to see the full 130-row version.*

## Generator script

```python
"""
Build a table of diatonic chord names for stacks of generic intervals.
Naming follows the harp handout system (HarpChordSystem.json).
"""
from itertools import product

CARET = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}
SUPER = {1: "¹", 2: "²", 3: "³"}
DEG_SEMITONE = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}

def deg_at(start_deg, generic_interval):
    """Move generic_interval letter-steps up. Returns (new_deg, octave_jumps)."""
    pos = (start_deg - 1) + (generic_interval - 1)
    return (pos % 7) + 1, pos // 7

def stack_pitches(start_deg, intervals):
    pitches = [(start_deg, 0)]
    cur_deg, cur_oct = start_deg, 0
    for iv in intervals:
        nd, oj = deg_at(cur_deg, iv)
        cur_oct += oj
        pitches.append((nd, cur_oct))
        cur_deg = nd
    return pitches

def triad_quality(root):
    t, _ = deg_at(root, 3); f, _ = deg_at(root, 5)
    ts = (DEG_SEMITONE[t] - DEG_SEMITONE[root]) % 12
    fs = (DEG_SEMITONE[f] - DEG_SEMITONE[root]) % 12
    return {(4,7):"", (3,7):"m", (3,6):"°"}.get((ts, fs), "?")

def seventh_quality(root):
    triad = triad_quality(root)
    s, _ = deg_at(root, 7)
    ss = (DEG_SEMITONE[s] - DEG_SEMITONE[root]) % 12
    if triad == "" and ss == 11: return "Δ"
    if triad == "" and ss == 10: return "7"
    if triad == "m" and ss == 10: return "m7"
    if triad == "°" and ss == 10: return "ø7"
    if triad == "°" and ss == 9:  return "°7"
    return "?7"

def name_stack(start_deg, intervals):
    if len(intervals) == 1:
        top, _ = deg_at(start_deg, intervals[0])
        return f"{CARET[start_deg]}{CARET[top]}"
    pitches = stack_pitches(start_deg, intervals)
    deg_seq = [p[0] for p in pitches]
    unique_degs = set(deg_seq)
    bass_deg = deg_seq[0]
    n_unique = len(unique_degs)
    n_total = len(deg_seq)
    has_doubling = n_total > n_unique
    dbl = "+8" if has_doubling else ""

    # 4-note chord (no doubling)
    if n_unique == 4 and n_total == 4:
        # Prefer added-6 when bass is root of major/minor triad and 6th is M6 (9 semis)
        for root in range(1, 8):
            t, _ = deg_at(root, 3); f, _ = deg_at(root, 5); s6, _ = deg_at(root, 6)
            if unique_degs == {root, t, f, s6} and bass_deg == root:
                tq = triad_quality(root)
                if tq in ("", "m") and (DEG_SEMITONE[s6]-DEG_SEMITONE[root])%12 == 9:
                    return f"{CARET[root]}{'6' if tq == '' else 'm6'}"
        # Standard tertian 7th
        for root in range(1, 8):
            t, _ = deg_at(root, 3); f, _ = deg_at(root, 5); sv, _ = deg_at(root, 7)
            if unique_degs == {root, t, f, sv}:
                inv = ""
                if bass_deg == t:    inv = SUPER[1]
                elif bass_deg == f:  inv = SUPER[2]
                elif bass_deg == sv: inv = SUPER[3]
                return f"{CARET[root]}{seventh_quality(root)}{inv}"
        # Quartal 7th: root + 4 + 4 + 4
        for root in range(1, 8):
            d4, _ = deg_at(root, 4); d7, _ = deg_at(root, 7); d10, _ = deg_at(root, 10)
            if unique_degs == {root, d4, d7, d10} and bass_deg == root:
                a = (DEG_SEMITONE[d4]-DEG_SEMITONE[root])%12
                b = (DEG_SEMITONE[d7]-DEG_SEMITONE[d4])%12
                c = (DEG_SEMITONE[d10]-DEG_SEMITONE[d7])%12
                if a == 5 and b == 5 and c == 5:
                    return f"{CARET[root]}q7"

    # 3-note triad/sus/quartal (possibly with octave doubling -> 4 total)
    if n_unique == 3:
        # FIRST PASS: prefer root-position interpretations
        for root in range(1, 8):
            t, _ = deg_at(root, 3); f, _ = deg_at(root, 5)
            if unique_degs == {root, t, f} and bass_deg == root:
                return f"{CARET[root]}{triad_quality(root)}{dbl}"
            d2, _ = deg_at(root, 2)
            if unique_degs == {root, d2, f} and bass_deg == root \
                    and (DEG_SEMITONE[f]-DEG_SEMITONE[root])%12 == 7 \
                    and (DEG_SEMITONE[d2]-DEG_SEMITONE[root])%12 == 2:
                return f"{CARET[root]}s2{dbl}"
            d4, _ = deg_at(root, 4)
            if unique_degs == {root, d4, f} and bass_deg == root \
                    and (DEG_SEMITONE[f]-DEG_SEMITONE[root])%12 == 7 \
                    and (DEG_SEMITONE[d4]-DEG_SEMITONE[root])%12 == 5:
                return f"{CARET[root]}s4{dbl}"
            d7, _ = deg_at(root, 7)
            if unique_degs == {root, d4, d7} and bass_deg == root \
                    and (DEG_SEMITONE[d4]-DEG_SEMITONE[root])%12 == 5 \
                    and (DEG_SEMITONE[d7]-DEG_SEMITONE[d4])%12 == 5:
                return f"{CARET[root]}q{dbl}"
        # SECOND PASS: inversions
        for root in range(1, 8):
            t, _ = deg_at(root, 3); f, _ = deg_at(root, 5)
            if unique_degs == {root, t, f}:
                inv = ""
                if bass_deg == t:   inv = SUPER[1]
                elif bass_deg == f: inv = SUPER[2]
                return f"{CARET[root]}{triad_quality(root)}{inv}{dbl}"
            d2, _ = deg_at(root, 2)
            if unique_degs == {root, d2, f} \
                    and (DEG_SEMITONE[f]-DEG_SEMITONE[root])%12 == 7 \
                    and (DEG_SEMITONE[d2]-DEG_SEMITONE[root])%12 == 2:
                if bass_deg == d2: return f"{CARET[root]}s2{SUPER[1]}{dbl}"
                if bass_deg == f:  return f"{CARET[root]}s2{SUPER[2]}{dbl}"
            d4, _ = deg_at(root, 4)
            if unique_degs == {root, d4, f} \
                    and (DEG_SEMITONE[f]-DEG_SEMITONE[root])%12 == 7 \
                    and (DEG_SEMITONE[d4]-DEG_SEMITONE[root])%12 == 5:
                if bass_deg == d4: return f"{CARET[root]}s4{SUPER[1]}{dbl}"
                if bass_deg == f:  return f"{CARET[root]}s4{SUPER[2]}{dbl}"

    # 2-note diad with octave doubling
    if n_unique == 2:
        other = [d for d in unique_degs if d != bass_deg][0]
        return f"{CARET[bass_deg]}{CARET[other]}+8"

    return None


# ----- generate all stacks -----
stacks = []
for i in range(2, 9):
    stacks.append([i])
for i, j in product(range(2, 9), repeat=2):
    if i + j <= 12: stacks.append([i, j])
for i, j, k in product(range(2, 9), repeat=3):
    if i + j + k <= 12: stacks.append([i, j, k])
stacks.sort(key=lambda s: (len(s), s))

# ----- write markdown table -----
out = ["| Stack | " + " | ".join(CARET[d] for d in range(1, 8)) + " |",
       "|---" * 8 + "|"]
for stack in stacks:
    cells = [name_stack(deg, stack) or "" for deg in range(1, 8)]
    out.append("| " + ",".join(map(str, stack)) + " | " + " | ".join(cells) + " |")

print("\n".join(out))
```
