# Beautiful Patterns Handout

Quick reference of shape patterns under the harp shape encoding. To turn
any pattern into a complete shape, prepend a position prefix
`<octave><hand>^<mode>` (where `<hand>` is `x`, `L`, or `R`) and read the
result as a shape code. See `README.md` for the full notation, `DRILLS.md`
for practice sequences.

All patterns below are **interval-only** — the digits between the mode
and any operators. They describe the shape, not where on the harp it sits.

-----

## Universal-winner patterns (12 shapes that sound good in every mode)

These are the dependable anchors — pick any mode 1–7 and any octave, and
the result will sound musical. They all share the **open-top profile**
(large index–thumb interval at the top).

|Pattern|Notes (in mode 1, octave 3, key C)|Character                         |
|-------|----------------------------------|----------------------------------|
|`35`   |C3 E3 B3                          |Open major-7 with no 5th          |
|`335`  |C3 E3 G3 D4                       |Cmaj9 (no 7)                      |
|`336`  |C3 E3 G3 E4                       |Cmaj triad with octaved 3rd on top|
|`344`  |C3 E3 A3 D4                       |Add 6/9 voicing                   |
|`345`  |C3 E3 A3 E4                       |Add 6 with octaved 3rd            |
|`346`  |C3 E3 A3 F4                       |Add 6 + 11 — open color           |
|`355`  |C3 E3 B3 F4                       |Cmaj7 + 11                        |
|`356`  |C3 E3 B3 G4                       |Cmaj9 spread (5 on top)           |
|`435`  |C3 F3 A3 E4                       |Sus + 6 + 3                       |
|`436`  |C3 F3 A3 F4                       |Add 11 + 6 + octaved 11           |
|`446`  |C3 F3 B3 G4                       |Add 11 + maj7 + 9                 |
|`456`  |C3 F3 B3 A4                       |Add 11 + maj7 + 13 — wide spread  |

To play any of these in mode 5 (Mixolydian) at octave 2, write
`2x^5<pattern>` — e.g. `2x^5346` = `G2 B2 E3 C4`.

-----

## Mode-conditional gems

Some shapes only sing in specific modes:

|Pattern|Mode(s)                             |Notes (key C, mode-relevant octave)|Why it works there                            |
|-------|------------------------------------|-----------------------------------|----------------------------------------------|
|`444`  |Lydian only                         |F1 B1 E2 A2                        |Quartal stack with the Lydian #4              |
|`45`   |Lydian only                         |F2 C3                              |The 4-step gap — F to C in F Lydian is the 5th|
|`246`  |Phrygian only                       |E E F D                            |Stepwise + wide top                           |
|`255`  |Phrygian only                       |E F C G                            |Phrygian’s bII flavor                         |
|`34`   |All except Locrian                  |C E A                              |Open triad                                    |
|`353`  |All except Locrian                  |C E B F                            |Bright open triad with maj7                   |
|`426`  |Dorian, Phrygian, Lydian, Locrian   |varies                             |Quartal blend                                 |
|`443`  |Ionian, Phrygian, Lydian, Mixolydian|varies                             |Quartal+third spread                          |

-----

## Common shape forms

### Single notes

```
1x^1   = C1                  (key C — bottom of the harp)
3x^4   = F3                  (mode 4 in octave 3 in key C)
+2x^1  = prior octave + 2, mode 1 (relative octave)
1x^6   = A1                  (mode 6 = Aeolian root in oct 1)
```

### Dyads

For dyad intervals up to a 4th, the player uses ring + middle. For wider
dyads, ring + thumb (skipping middle and index entirely). The encoding
itself is silent on which fingers are used — the choice falls out of the
interval size.

```
3x^13   = C3 E3      (3rd, ring + middle)
3x^15   = C3 G3      (5th, ring + thumb territory)
3x^18   = C3 C4      (octave, ring + thumb)
3x^1d   = C3 A4      (13th, ring + thumb at full stretch)
3x^1f   = C3 C5      (double octave, max dyad)
```

### Universal-winner triads and tetrads

```
3x^135   = C3 E3 B3        (open Cmaj7-no-5)
3x^244   = D3 F3 B3 D4     (Dm 6/9 — actually a tetrad, mode 2)
3x^534   = G3 B3 E4 A4     (G mixolydian add-6, tetrad)
```

```
3x^1335  = C3 E3 G3 D4     (Cmaj9-no-7)
3x^1344  = C3 E3 A3 D4     (Cadd6/9)
3x^1346  = C3 E3 A3 F4     (Cadd6+11)
3x^1355  = C3 E3 B3 F4     (Cmaj7+11)
3x^1356  = C3 E3 B3 G4     (Cmaj9 spread)
3x^1456  = C3 F3 B3 A4     (Cadd11+maj7+13)
```

-----

## Sequence patterns

Sequences are written as **multiple shapes separated by spaces** within a
row. Operators (`$`, `&`) expand a single shape token into a run of shapes.

### Octave climb (`&` operator)

`&N` re-stamps the whole shape one octave higher per iteration:

```
1x^135&3    — Cmaj7-no-5 in octaves 1, 2, 3, 4
1x^1346&3   — the 346 open tetrad in four consecutive octaves
1x^4444&5   — Lydian quartal climbed octave by octave
1x^135&*    — fill the harp's range upward
1x^135&~    — climb to the top, mirror back down
```

### Repeat-back-to-back (`$` operator)

`$N` repeats the **last digit** of the shape N more times as new shapes,
chaining shape-after-shape across the row. Useful for self-similar climbs
like all-thirds or all-fourths:

```
1x^1333$3    — `1x^1333 3 3 3` — stacked thirds: C1-E1-G1-B1, then D2-F2-A2-C3, then E3-G3-B3-D4, then F4-A4-C5-E5
1x^14$5      — `1x^14 4 4 4 4 4` — quartal climb from C1 upward
1x^1333$~    — third-stack chain to top of harp, then mirror back
```

`$$N` and `$$$N` use the last 2 or 3 digits as the repeating unit.

### Modal cycle (one row, varying mode digit)

Seven shapes in one octave, mode digit walking 1→7. Same intervals each
shape; only the mode-color changes. Example with the `335` universal-
winner pattern, in octave 3:

```
3x^1335 3x^2335 3x^3335 3x^4335 3x^5335 3x^6335 3x^7335
```

### Two-hand shapes (LH + RH on one shape)

When LH and RH both sit on a contiguous stack, write a **single shape
with a comma** separating LH intervals from RH intervals:

```
1x^1333,3333    — LH on C1-E1-G1-B1, RH continues on D2-F2-A2-C3.
```

The comma marks where LH’s top finger ends and RH’s bottom finger begins.

For LH-bass + RH-chord textures where the two hands sit on **separate**
shapes, write two consecutive shapes with explicit hand letters in their
octave prefixes:

```
1L^6 1R^1333     — LH single bass note A1 (degree 6); RH on stacked-thirds tetrad
1L^4 3R^4333     — LH bass F1; RH F-rooted 7-chord tetrad in octave 3
1L^5 3R^5333     — LH bass G1; RH G-rooted 7-chord tetrad
```

The `L` and `R` letters in the octave prefix pin the hand. Whether the two
shapes are played simultaneously or in sequence is the player’s
interpretation — the encoding doesn’t enforce timing.

-----

## Quick-pick by situation

|Situation                   |Pattern                                                 |
|----------------------------|--------------------------------------------------------|
|**Warmup / hand-spread**    |`1x^1333$~` — third-stack chain to the top, mirrored back|
|**Calibrate reach**         |`VERIFY.md` drills                                      |
|**Mode exploration**        |Same intervals, varying mode digit (modal cycle row)    |
|**Voicing study**           |Universal-winner tetrads at one octave, varying mode    |
|**Sustained color**         |`1x^4444` (Lydian quartal) — set, ring, listen           |
|**Bass + chord progression**|`1L^<deg> 3R^<deg>333` per chord, space-separated       |
|**Octave-by-octave climb**  |Any pattern with `&3`, `&*`, or `&~`                    |
|**Continuous arpeggio**     |Self-similar shape with `$~`                            |
|**Sparse top-note color**   |Tetrads ending in 5 or 6 (e.g. `1335`, `1346`, `1456`)  |

-----

## Patterns to avoid

These are setable but rarely musical:

- **All 2nds in the low octave** — `1x^1222` in oct 1 sounds muddy
  (stepwise clash penalty stacks).
- **Three adjacent stepwise intervals** — heavy aesthetic penalty.
- **Locrian root-position voicings** — the tonic instability of mode 7
  makes most root-rooted Locrian shapes feel unresolved. Use mode 7
  shapes as passing color, not as a home.
- **Bottom-heavy spreads** — large ring–middle interval with small upper
  pairs (e.g., `1x^1622`). Hand geometry favors open-top, not open-bottom.

-----

## Practice tip

Pick one universal-winner tetrad and run a modal-cycle row on it (same
intervals, mode digit walking 1→7). You’ll hear the same shape recolored
seven different ways without ever moving the hand far. Then pick another
and repeat. Twelve patterns × 7 modes = 84 distinct voicings — enough
vocabulary for any hymn arrangement.