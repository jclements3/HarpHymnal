# Diatonic Chord Stacks — Generic-Interval Table

A table of diatonic chord names for stacks of generic intervals starting on each scale degree of the major scale. Naming follows the harp handout system (`HarpChordSystem.json`).

## How to read the table

- **Columns**: scale degree (1̂ – 7̂) of the *bottom* note of the stack.
- **Rows**: a stack of 1, 2, or 3 generic intervals. `3,3` means "stack a third, then another third"; `3,3,3` means three stacked thirds.
- **Cells**: the most-abbreviated chord name. The caret-digit (1̂, 2̂…) marks the **root** of the chord, not the bottom note. Quality follows: empty for major triads, `m` for minor, `°` for diminished, `Δ` for major-7th, `7` for dominant-7th, `m7`, `ø7`, `°7`, `s2`, `s4`, `q` for quartal. Superscripts ¹²³ mark inversions (bass = 3rd, 5th, or 7th of the chord). `+8` marks octave doubling of any chord tone.
- **Empty cells**: diatonic stacks that don't form a recognized tertian, sus, quartal, or added-6 sonority (genuine clusters like `1̂-2̂-3̂` or `1̂-2̂-4̂`).

Constraints: each interval ≤ 12, sum of intervals ≤ 12. All combinations are ordered (`3,2 ≠ 2,3`).

## The table

| Stack | 1̂ | 2̂ | 3̂ | 4̂ | 5̂ | 6̂ | 7̂ |
|---|---|---|---|---|---|---|---|
| 2 | 1̂2̂ | 2̂3̂ | 3̂4̂ | 4̂5̂ | 5̂6̂ | 6̂7̂ | 7̂1̂ |
| 3 | 1̂3̂ | 2̂4̂ | 3̂5̂ | 4̂6̂ | 5̂7̂ | 6̂1̂ | 7̂2̂ |
| 4 | 1̂4̂ | 2̂5̂ | 3̂6̂ | 4̂7̂ | 5̂1̂ | 6̂2̂ | 7̂3̂ |
| 5 | 1̂5̂ | 2̂6̂ | 3̂7̂ | 4̂1̂ | 5̂2̂ | 6̂3̂ | 7̂4̂ |
| 6 | 1̂6̂ | 2̂7̂ | 3̂1̂ | 4̂2̂ | 5̂3̂ | 6̂4̂ | 7̂5̂ |
| 7 | 1̂7̂ | 2̂1̂ | 3̂2̂ | 4̂3̂ | 5̂4̂ | 6̂5̂ | 7̂6̂ |
| 8 | 1̂1̂ | 2̂2̂ | 3̂3̂ | 4̂4̂ | 5̂5̂ | 6̂6̂ | 7̂7̂ |
| 2,4 | 1̂s2 | 2̂s2 |  | 4̂s2 | 5̂s2 | 6̂s2 |  |
| 2,7 | 1̂2̂+8 | 2̂3̂+8 | 3̂4̂+8 | 4̂5̂+8 | 5̂6̂+8 | 6̂7̂+8 | 7̂1̂+8 |
| 2,8 | 1̂2̂+8 | 2̂3̂+8 | 3̂4̂+8 | 4̂5̂+8 | 5̂6̂+8 | 6̂7̂+8 | 7̂1̂+8 |
| 3,3 | 1̂ | 2̂m | 3̂m | 4̂ | 5̂ | 6̂m | 7̂° |
| 3,4 | 6̂m¹ | 7̂°¹ | 1̂¹ | 2̂m¹ | 3̂m¹ | 4̂¹ | 5̂¹ |
| 3,6 | 1̂3̂+8 | 2̂4̂+8 | 3̂5̂+8 | 4̂6̂+8 | 5̂7̂+8 | 6̂1̂+8 | 7̂2̂+8 |
| 3,8 | 1̂3̂+8 | 2̂4̂+8 | 3̂5̂+8 | 4̂6̂+8 | 5̂7̂+8 | 6̂1̂+8 | 7̂2̂+8 |
| 4,2 | 1̂s4 | 2̂s4 | 3̂s4 |  | 5̂s4 | 6̂s4 |  |
| 4,3 | 4̂² | 5̂² | 6̂m² | 7̂°² | 1̂² | 2̂m² | 3̂m² |
| 4,4 |  | 2̂q | 3̂q |  | 5̂q | 6̂q | 7̂q |
| 4,5 | 1̂4̂+8 | 2̂5̂+8 | 3̂6̂+8 | 4̂7̂+8 | 5̂1̂+8 | 6̂2̂+8 | 7̂3̂+8 |
| 4,8 | 1̂4̂+8 | 2̂5̂+8 | 3̂6̂+8 | 4̂7̂+8 | 5̂1̂+8 | 6̂2̂+8 | 7̂3̂+8 |
| 5,4 | 1̂5̂+8 | 2̂6̂+8 | 3̂7̂+8 | 4̂1̂+8 | 5̂2̂+8 | 6̂3̂+8 | 7̂4̂+8 |
| 5,5 | 1̂s2 | 2̂s2 |  | 4̂s2 | 5̂s2 | 6̂s2 |  |
| 5,6 | 1̂ | 2̂m | 3̂m | 4̂ | 5̂ | 6̂m | 7̂° |
| 5,7 | 1̂s4 | 2̂s4 | 3̂s4 |  | 5̂s4 | 6̂s4 |  |
| 6,3 | 1̂6̂+8 | 2̂7̂+8 | 3̂1̂+8 | 4̂2̂+8 | 5̂3̂+8 | 6̂4̂+8 | 7̂5̂+8 |
| 6,5 | 6̂m¹ | 7̂°¹ | 1̂¹ | 2̂m¹ | 3̂m¹ | 4̂¹ | 5̂¹ |
| 6,6 | 4̂² | 5̂² | 6̂m² | 7̂°² | 1̂² | 2̂m² | 3̂m² |
| 7,2 | 1̂7̂+8 | 2̂1̂+8 | 3̂2̂+8 | 4̂3̂+8 | 5̂4̂+8 | 6̂5̂+8 | 7̂6̂+8 |
| 7,5 |  | 2̂q | 3̂q |  | 5̂q | 6̂q | 7̂q |
| 8,2 | 1̂2̂+8 | 2̂3̂+8 | 3̂4̂+8 | 4̂5̂+8 | 5̂6̂+8 | 6̂7̂+8 | 7̂1̂+8 |
| 8,3 | 1̂3̂+8 | 2̂4̂+8 | 3̂5̂+8 | 4̂6̂+8 | 5̂7̂+8 | 6̂1̂+8 | 7̂2̂+8 |
| 8,4 | 1̂4̂+8 | 2̂5̂+8 | 3̂6̂+8 | 4̂7̂+8 | 5̂1̂+8 | 6̂2̂+8 | 7̂3̂+8 |
| 2,3,3 | 2̂m7³ | 3̂m7³ | 4̂Δ³ | 5̂7³ | 6̂m7³ | 7̂ø7³ | 1̂Δ³ |
| 2,4,4 | 1̂s2+8 | 2̂s2+8 |  | 4̂s2+8 | 5̂s2+8 | 6̂s2+8 |  |
| 2,4,5 | 1̂s2+8 | 2̂s2+8 |  | 4̂s2+8 | 5̂s2+8 | 6̂s2+8 |  |
| 2,7,2 | 1̂2̂+8 | 2̂3̂+8 | 3̂4̂+8 | 4̂5̂+8 | 5̂6̂+8 | 6̂7̂+8 | 7̂1̂+8 |
| 3,2,3 | 4̂Δ² | 5̂7² | 6̂m7² | 7̂ø7² | 1̂Δ² | 2̂m7² | 3̂m7² |
| 3,2,4 |  | 2̂q7 | 3̂q7 |  |  | 6̂q7 | 7̂q7 |
| 3,3,2 | 1̂6 | 2̂m6 | 1̂Δ¹ | 4̂6 | 5̂6 | 4̂Δ¹ | 5̂7¹ |
| 3,3,3 | 1̂Δ | 2̂m7 | 3̂m7 | 4̂Δ | 5̂7 | 6̂m7 | 7̂ø7 |
| 3,3,4 | 1̂+8 | 2̂m+8 | 3̂m+8 | 4̂+8 | 5̂+8 | 6̂m+8 | 7̂°+8 |
| 3,3,6 | 1̂+8 | 2̂m+8 | 3̂m+8 | 4̂+8 | 5̂+8 | 6̂m+8 | 7̂°+8 |
| 3,4,3 | 6̂m¹+8 | 7̂°¹+8 | 1̂¹+8 | 2̂m¹+8 | 3̂m¹+8 | 4̂¹+8 | 5̂¹+8 |
| 3,4,5 | 6̂m¹+8 | 7̂°¹+8 | 1̂¹+8 | 2̂m¹+8 | 3̂m¹+8 | 4̂¹+8 | 5̂¹+8 |
| 3,6,3 | 1̂3̂+8 | 2̂4̂+8 | 3̂5̂+8 | 4̂6̂+8 | 5̂7̂+8 | 6̂1̂+8 | 7̂2̂+8 |
| 4,2,4 | 1̂s4+8 | 2̂s4+8 | 3̂s4+8 |  | 5̂s4+8 | 6̂s4+8 |  |
| 4,3,3 | 4̂²+8 | 5̂²+8 | 6̂m²+8 | 7̂°²+8 | 1̂²+8 | 2̂m²+8 | 3̂m²+8 |
| 4,3,4 | 2̂m7³ | 3̂m7³ | 4̂Δ³ | 5̂7³ | 6̂m7³ | 7̂ø7³ | 1̂Δ³ |
| 4,3,5 | 4̂Δ² | 5̂7² | 6̂m7² | 7̂ø7² | 1̂Δ² | 2̂m7² | 3̂m7² |
| 4,4,2 |  | 2̂q+8 | 3̂q+8 |  | 5̂q+8 | 6̂q+8 | 7̂q+8 |
| 4,4,4 |  | 2̂q7 | 3̂q7 |  |  | 6̂q7 | 7̂q7 |
| 5,2,5 | 1̂6 | 2̂m6 | 1̂Δ¹ | 4̂6 | 5̂6 | 4̂Δ¹ | 5̂7¹ |
| 5,3,4 | 1̂Δ | 2̂m7 | 3̂m7 | 4̂Δ | 5̂7 | 6̂m7 | 7̂ø7 |
| 5,4,2 | 1̂s2+8 | 2̂s2+8 |  | 4̂s2+8 | 5̂s2+8 | 6̂s2+8 |  |
| 5,4,3 | 1̂+8 | 2̂m+8 | 3̂m+8 | 4̂+8 | 5̂+8 | 6̂m+8 | 7̂°+8 |
| 6,3,3 | 6̂m¹+8 | 7̂°¹+8 | 1̂¹+8 | 2̂m¹+8 | 3̂m¹+8 | 4̂¹+8 | 5̂¹+8 |

*All-empty rows (clusters and unrecognized sonorities) are omitted. Run the script below to see the full 130-row version.*

## Generator script

```python
"""
Build a table of diatonic chord names for stacks of generic intervals.
Naming follows the harp handout system (HarpChordSystem.json).
"""
from itertools import product

CARET = {1: "1̂", 2: "2̂", 3: "3̂", 4: "4̂", 5: "5̂", 6: "6̂", 7: "7̂"}
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
