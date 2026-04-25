# Harp Setup Encoding System

A compact notation for diatonic music on a lever harp. **The system encodes hand setups — moments where the hands are placed on specific strings — and progressions of those setups. It is not a music notation: rhythm, articulation, strike order after assembly, dynamics, and timing are deliberately outside its scope.** What it captures is *what is set on the strings*; how those strings are subsequently played is the player's interpretation.

The system also ignores traditional chord names and harmonic function. There are no roman numerals, no `Cmaj7` / `Dm7sus4` quality labels, no tonic/dominant categories. The vocabulary is the set of hand configurations that pass two filters: the hand can reach them, and they sound musical.

---

## Document structure

A piece is written as a **header block** followed by one or more **rows** of setup codes:

```
Title: <piece title>     (optional)
Key:   <key root>        (required)
---
<row of setups>
<row of setups>
...
```

`Key:` resolves what mode digits mean — the mode digit is the scale degree of the bottom finger within the named key (e.g. in `Key: C`, mode 1 = C; in `Key: G`, mode 1 = G). One header per piece.

Below the `---` separator, each row is a sequence of setups. Rows are sequential phrases; position resets between rows, so each row's first setup must be fully-positioned.

---

## Setups

A **setup** is one moment where the hands are placed on the strings. Setups are separated by dashes (`-`); the dash means *both hands lift and reset to the next position*.

Within a setup, you can specify a single shape (one hand sets it) or two shapes (both hands set together):

```
<shape>           — bare shape: either hand sets it (player picks)
L<shape>          — left hand sets this shape
R<shape>          — right hand sets this shape
<shape> R <shape> — both hands set together: first is LH, second is RH
```

The `R` between two shapes within a setup is a **divider**, not a prefix. It signals that the prior shape is for the LH and the following shape is for the RH (both placed simultaneously).

Most setups are bare (no marker) — the markers cluster around the exceptions where a specific hand or both-hands assignment matters.

---

## Shape syntax

A shape is one hand's placement: 1–4 fingers on specific strings, all set simultaneously. Each shape takes one of three forms:

```
absolute:      [octave] x [mode] [interval] [interval] [interval]
                   ↑          ↑       ↑          ↑          ↑
                  1-7        1-7    2-f        2-f        2-f

relative:    ^ [count] x [mode] [interval] [interval] [interval]
                  ↑          ↑       ↑          ↑          ↑
                 0-7        1-7    2-f        2-f        2-f

continuation:  [gap] [interval] [interval] [interval]
                  ↑       ↑           ↑           ↑
                 2-f     2-f         2-f         2-f
```

The first character of the shape decides its form:

- **Digit followed by `x`** → **absolute**: explicit harp octave (1–7, indexed bottom up); digit after `x` is the mode (1–7) of the bottom finger; remaining digits are intra-shape intervals from one finger to the next, reading bottom (ring) to top (thumb).
- **`^` followed by digit and `x`** → **relative**: octave is the prior shape's octave + count; otherwise identical to absolute. `^0x` is "same octave as prior."
- **Bare digit (no `x`)** → **continuation**: first digit is the **gap interval** from the prior shape's top finger to this shape's bottom finger; remaining digits are intra-shape intervals.

A row's first setup must use an absolute shape (no prior to chain from). Within a row, any mix is allowed.

Mode digits: `1` Ionian, `2` Dorian, `3` Phrygian, `4` Lydian, `5` Mixolydian, `6` Aeolian, `7` Locrian.

The number of intervals tells you the chord size: 0 intervals → single note; 1 → dyad; 2 → triad; 3 → tetrad. A continuation shape with only the gap digit is a single melodic note placed at the gap above the prior top finger.

---

## Interval digits

Codes use single hex characters for every digit. Interval names count the endpoints (a 3rd is two scale steps apart):

| Digit | Interval name | Scale steps |
|---|---|---|
| `2` | 2nd | 1 |
| `3` | 3rd | 2 |
| `4` | 4th | 3 |
| `5` | 5th | 4 |
| `6` | 6th | 5 |
| `7` | 7th | 6 |
| `8` | 8th (octave) | 7 |
| `9` | 9th | 8 |
| `a` | 10th | 9 |
| `b` | 11th | 10 |
| `c` | 12th | 11 |
| `d` | 13th | 12 |
| `e` | 14th | 13 |
| `f` | 15th (double octave) | 14 |

Hex `f` is the cap. Wider intervals exceed any single-hand voicing and aren't expressible in one digit.

The digit `1` (a unison) is **invalid in any interval position** — two fingers can't sound the same string. `1` only ever appears as a mode digit or octave digit.

---

## Subscripts: assembly order

Digits in a shape map to fingers by position: **1st digit = ring, 2nd = middle, 3rd = index, 4th = thumb**. This mapping is fixed.

By default, the fingers all settle on the strings together (block-strike) or in natural bottom-up order (default roll). The encoding doesn't distinguish these — the player picks based on context.

**Subscripts mark exceptions to the default assembly order.** A subscript on a digit says *when that digit's finger plants in the assembly sequence*:

| Subscript | Plants |
|---|---|
| `₁` | first  |
| `₂` | second |
| `₃` | third  |
| `₄` | fourth (last) |

So `1x1₁3₂3₃3₄` is the default bottom-up assembly written explicitly: ring plants 1st, middle 2nd, index 3rd, thumb 4th.

`1x1₄3₃3₂3₁` reverses the order: thumb plants 1st, then index, middle, ring last. A top-down assembly.

`1x1₂3₁3₄3₃` plants middle 1st (anchor), then ring 2nd, then thumb 3rd, index last.

If you use subscripts, mark all four fingers — partial subscripts are ambiguous.

The subscripts describe the *recipe for assembling the shape*, not the order in which the strings are struck after assembly.

---

## Operators

| Operator | Meaning |
|---|---|
| `-` | Setup separator. Both hands lift and reset to the next setup. |
| `*N` | Literal repeat. The prior atom (a setup or parenthesized group) is repeated `N` times in succession. For continuation shapes, each iteration chains from the prior repeat's top finger, so the position evolves. |
| `~` | Palindrome with apex de-duplication. The prior expression is then traversed in reverse; the topmost note isn't re-entered on the way back. |

`R` and `L` are markers, not operators — they mark which hand sets a shape, sticky-inheriting forward through subsequent shapes until overridden.

---

## Reserved meanings

- **Digit `1`** appears only as a mode digit or octave digit (in fully-positioned shapes). Never as an interval digit (unison) or continuation gap.
- **`x` is a literal character**, not a digit. It signals absolute or relative form.
- **`^` is a literal character**, not a digit. It signals the relative form, always followed by a digit and `x`.
- **Hex `f` is the cap on every interval.** A 15th is the widest interval expressible in one digit.
- **No descending intervals** within a shape. Every interval reads upward.
- **Continuation gap is also upward** — from prior top finger to next bottom finger.
- **Hand markers** (`R`, `L`) are non-hex alphabetics, so the parser distinguishes them by character class. No separator needed: `R1x1333` parses cleanly.

---

## Examples

| Code | Reading |
|---|---|
| `1x13` | Ionian dyad in octave 1: C1 + 3rd up = C1–E1 (key C). |
| `2x2d` | Dorian dyad in octave 2: D2 + 13th = D2–B3. |
| `2x233` | Dorian triad: D2–F2–A2. |
| `1x7333` | Locrian tetrad: B1–D2–F2–A2 (root-position Bø7 voicing). |
| `1x1333-3333` | Two third-stacked tetrads chained by continuation: C1–E1–G1–B1 then D2–F2–A2–C3. |
| `1x1333-3333*5~` | Thirds-up sweep across the harp: C1 to G7 in 4-note tetrads, then mirrored back. |
| `1x135-^1x135*5~` | Open-Imaj7 voicing climbed octave-by-octave (relative-octave compression), then mirrored. |
| `1x1-3*23~` | Single-note 3rd-step walk: C1 ascending in melodic 3rds to G7 and back. |
| `R1x1333` | RH alone sets a third-stack tetrad. |
| `1x6 R 1x1333` | Two-hand setup: LH on a single bass note (mode 6 = A1), RH on the third-stack tetrad. |
| `1x1₄3₃3₂3₁` | Single shape, top-down assembly: thumb anchors first, ring lands last. |

---

## Physical constraints

A harp is played with four fingers per hand: thumb (highest pitch), index, middle, ring (lowest pitch). The encoding maps directly onto these:

```
       thumb  ──┐
                │  position 4 (top finger)
       index  ──┤
                │  position 3
       middle ──┤
                │  position 2
       ring   ──┘  position 1 (bottom finger)
```

When reading a shape like `1x1336`, the interval digits correspond to inter-finger gaps from bottom to top:

- **1st interval digit** (`3` here): ring → middle gap
- **2nd interval digit** (`3` here): middle → index gap
- **3rd interval digit** (`6` here): index → thumb gap

Each finger pair has its own physical reach limit. The values below are best-guess defaults; the actual numbers for a given player should be calibrated using the drills in `VERIFY.md`.

| Finger pair | Position in code | Comfortable | Hard ceiling |
|---|---|---|---|
| Ring–middle | 1st interval | 3rd | 4th |
| Middle–index | 2nd interval | 4th | 5th |
| Index–thumb | 3rd interval | 5th | 6th |
| Thumb–ring (dyad only) | only interval | 6th | 13th |

The thumb is the most independent and reaches the farthest. The ring is shortest and weakest. So **the encoding's natural shape is small intervals at the bottom (ring side), larger intervals at the top (thumb side)** — the opposite of how piano voicings are typically organized.

A shape is **physically setable** if every interval digit fits within its position's hard ceiling. Codes that violate this can still be enumerated, but represent setups requiring two hands or assembly that exceeds the calibrated reach.

---

## What the encoding captures

Each setup carries five layers of information simultaneously:

1. **Specific notes**: given the header's key, every shape unambiguously specifies which strings are involved.
2. **Pitch-class set**: the harmonic content.
3. **Voicing**: same notes in different inversions or spreads get different codes. Each physical setup is a distinct entity.
4. **Quality / character**: the combination of mode root and intervals determines whether the setup sounds major, minor, diminished, suspended, etc., without needing a separate quality label.
5. **Setability**: directly readable from the digit positions and finger-pair limits.

Chord names like "Cmaj7" or "Dm7sus4(no5)" are deliberately not part of the encoding. Traditional chord names have inconsistencies around no-3, no-5, sus stacking, and quartal voicings, and the same physical sonority often has multiple legitimate names depending on context. The encoding sidesteps this by describing **what is set on the strings** rather than how the resulting chord should be theoretically labeled.

---

## Algorithmic properties

Because the encoding is purely structural, several operations become mechanical:

- **Sortable** — codes naturally cluster by mode, then by interval shape.
- **Compact** — every setable shape fits in 2–4 characters of intervals plus the position prefix; setup sequences scale linearly, with `*N`, `~`, and `^Nx` compressing repetitive patterns.
- **Self-parsing** — first-character class decides shape form; `-` separates setups; positional rules within a shape make digit roles unambiguous.
- **Generative** — enumerate all combinations of legal digits → derive the full setup vocabulary.
- **Transposable for free** — shapes never reference a specific key, only scale degrees within the header's key. To play in a different key, change the `Key:` header; every shape stays the same.
- **Comparable** — voice-leading distance between two setups is computable from their codes; continuation shapes make inter-setup gaps explicit.
- **Filterable** — physical-reach rules become simple per-position bounds checks.

---

## Aesthetic scoring

Once setability is established, shapes can be ranked by acoustic beauty using rules that operate on the digits themselves, agnostic of chord names:

| Rule | Effect |
|---|---|
| Stepwise clash (interval = `2`) in low octave | penalty |
| Three adjacent stepwise intervals | heavy penalty |
| At least one wide interval (≥ `5`) | reward |
| Top interval (> bottom interval) | reward (open-top profile) |
| Top note on color scale degree (3, 5, 7, 9) | reward |
| Pitch-class diversity (4 distinct pitches in a tetrad) | reward |
| Mode characteristic-tone present | mode-specific reward |
| Mode avoid-note present alongside the major 3rd | mode-specific penalty |
| Locrian tonic-instability | mode-specific penalty |

The scoring reveals which shape codes are **universally beautiful** (work in any modal context) versus **mode-conditional**.

---

## Visualization format

The grid below shows every shape that is both physically setable and aesthetically beautiful in at least one mode. Rows are indexed by interval-only pattern (the mode digit dropped, since each row evaluates the shape across all 7 mode columns). An `x` marks intersections where the shape sounds good rooted on that mode's tonic.

Mode columns: **I**onian, **D**orian, **P**hrygian, **L**ydian, **M**ixolydian, **A**eolian, **L**ocrian.

```
code  I D P L M A L
      1 2 3 4 5 6 7
----- -------------
34    x x x x x x  
35    x x x x x x x
44    x     x x    
45          x      
236       x x      
326     x x x   x  
335   x x x x x x x
344   x x x x x x x
353   x x x x x x  
425   x x x x x x  
434   x x x x x x  
443   x   x x x    
246       x        
255       x        
336   x x x x x x x
345   x x x x x x x
354   x x x x x x  
426     x x x   x x
435   x x x x x x x
444         x      
256       x x      
346   x x x x x x x
355   x x x x x x x
436   x x x x x x x
445   x     x x    
356   x x x x x x x
446   x x x x x x x
455   x x x x x x  
456   x x x x x x x
```

**29 beautiful shape patterns total**, distributed as:

- **12 universal-winner rows** (solid `x x x x x x x`) — shapes that sound good in any mode. The dependable anchors: `35`, `335`, `344`, `336`, `345`, `435`, `346`, `355`, `436`, `356`, `446`, `456`. They all share the open-top profile (large index–thumb interval at the top).
- **17 mode-conditional rows** with partial coverage. Patterns like `45` and `444` only sing in Lydian; `246` and `255` only in Phrygian.

To turn a row pattern into a complete setup, prepend a position prefix: pick a mode column (which becomes the mode digit) and an octave, then write `<octave>x<mode><pattern>`. For example, `444` in column 4 (Lydian) at harp octave 3 → `3x4444` — bottom finger on the 4th scale degree of your key in octave 3, with three 4ths stacked upward.

The patterns themselves aren't usable as continuation codes — the digit roles are different (continuation: 1st digit = gap; setup pattern: digits = intra-shape intervals).

---

## Working pool

For one player's hand at the default reach guess (ring–middle ≤ 4th, middle–index ≤ 5th, index–thumb ≤ 6th):

| Category | Count |
|---|---|
| Mathematically possible patterns at span ≤ 12 | 231 |
| Physically setable patterns | 74 |
| × 7 modal columns | 518 cells |
| Beautiful and setable (sweet-spot cells) | ≈ 130 |
| Universal-winner patterns | ≈ 12 |
| Mode-conditional beautiful patterns | ≈ 17 |

These counts depend on the aesthetic threshold and per-finger reach calibration. They define a working setup vocabulary roughly the size of a typical jazz fake-book chord set, but organized by physical setability rather than by harmonic function.

---

## Limitations

- The encoding is purely diatonic to the header's key. Non-diatonic notes (chromatic alterations, lever flips) are outside its scope.
- **Rhythm, articulation, strike order, timing, and dynamics are out of scope.** The encoding describes what is set on the strings; how those strings are subsequently played is the player's interpretation. There's no way to encode "this setup is held for two beats" or "roll bottom-up at 80 bpm" — those belong to a different layer.
- Setup *function* (tonic, dominant, predominant) is not encoded. Function is a property of progressions, not isolated setups.
- Aesthetic scoring uses heuristic rules; calibration against the player's actual ear is necessary for the final 10–20% of accuracy.
- Hand-reach calibration in the table above is a best guess. The drills in `VERIFY.md` produce the actual numbers — once those results are available, the table here will be replaced.
- True simultaneous polyphony beyond two-hand setups (e.g., overlapping voices held across multiple beats) isn't expressible. Each setup is a single moment of hand placement; sustained voices across setups aren't notated.
- `~` palindromes the prior expression as-given; it does not auto-extend across the harp's range. Range-spanning sweeps must be written explicitly (or compressed via `*N` on continuation / relative shapes).
