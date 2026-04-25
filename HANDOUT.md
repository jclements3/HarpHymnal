# Beautiful Patterns Handout

Quick reference of shape patterns under the harp setup encoding. To turn
any pattern into a complete setup, prepend a position prefix
`<octave>x<mode>` (or `^<count>x<mode>`) and read the result as a setup
code. See `README.md` for the full notation, `DRILLS.md` for practice
sequences.

All patterns below are **interval-only** — the digits between the mode
and any operators. They describe the shape, not where on the harp it sits.

---

## Universal-winner patterns (12 shapes that sound good in every mode)

These are the dependable anchors — pick any mode 1-7 and any octave, and
the result will sound musical. They all share the **open-top profile**
(large index-thumb interval at the top).

| Pattern | Notes (in mode 1, octave 3, key C) | Character |
|---|---|---|
| `35`   | C3 E3 B3            | Open major-7 with no 5th |
| `335`  | C3 E3 G3 D4         | Cmaj9 (no 7) |
| `336`  | C3 E3 G3 E4         | Cmaj triad with octaved 3rd on top |
| `344`  | C3 E3 A3 D4         | Add 6/9 voicing |
| `345`  | C3 E3 A3 E4         | Add 6 with octaved 3rd |
| `346`  | C3 E3 A3 F4         | Add 6 + 11 — open color |
| `355`  | C3 E3 B3 F4         | Cmaj7 + 11 |
| `356`  | C3 E3 B3 G4         | Cmaj9 spread (5 on top) |
| `435`  | C3 F3 A3 E4         | Sus + 6 + 3 |
| `436`  | C3 F3 A3 F4         | Add 11 + 6 + octaved 11 |
| `446`  | C3 F3 B3 G4         | Add 11 + maj7 + 9 |
| `456`  | C3 F3 B3 A4         | Add 11 + maj7 + 13 — wide spread |

To play any of these in mode 5 (Mixolydian) at octave 2, write
`2x5<pattern>` — e.g. `2x5346` = `G2 B2 E3 C4`.

---

## Mode-conditional gems

Some shapes only sing in specific modes:

| Pattern | Mode(s) | Notes (key C, mode-relevant octave) | Why it works there |
|---|---|---|---|
| `444` | Lydian only       | F1 B1 E2 A2 | Quartal stack with the Lydian #4 |
| `45`  | Lydian only       | F2 C3       | The 4-step gap — F to C in F Lydian is the 5th |
| `246` | Phrygian only     | E E F D     | Stepwise + wide top |
| `255` | Phrygian only     | E F C G     | Phrygian's bII flavor |
| `34`  | All except Locrian | C E A      | Open triad |
| `353` | All except Locrian | C E B F    | Bright open triad with maj7 |
| `426` | Dorian, Phrygian, Lydian, Locrian | varies | Quartal blend |
| `443` | Ionian, Phrygian, Lydian, Mixolydian | varies | Quartal+third spread |

---

## Common setup forms

### Single notes

```
1x1   = C1                  (key C — bottom of the harp)
3x4   = F3                  (mode 4 in octave 3 in key C)
^2x1  = same shape as prior, advanced 2 octaves
1x6   = A1                  (mode 6 = Aeolian root in oct 1)
```

### Dyads

For dyad intervals up to a 4th, the player uses ring + middle. For wider
dyads, ring + thumb (skipping middle and index entirely). The encoding
itself is silent on which fingers are used — the choice falls out of the
interval size.

```
3x13   = C3 E3      (3rd, ring + middle)
3x15   = C3 G3      (5th, ring + thumb territory)
3x18   = C3 C4      (octave, ring + thumb)
3x1d   = C3 A4      (13th, ring + thumb at full stretch)
3x1f   = C3 C5      (double octave, max dyad)
```

### Universal-winner triads

```
3x135   = C3 E3 B3        (open Cmaj7-no-5)
3x244   = D3 F3 B3 D4     (Dm 6/9 — actually a tetrad, mode 2)
3x534   = G3 B3 E4 A4     (G mixolydian add-6, tetrad)
```

### Universal-winner tetrads (the workhorses)

```
3x1335  = C3 E3 G3 D4     (Cmaj9-no-7)
3x1344  = C3 E3 A3 D4     (Cadd6/9)
3x1346  = C3 E3 A3 F4     (Cadd6+11)
3x1355  = C3 E3 B3 F4     (Cmaj7+11)
3x1356  = C3 E3 B3 G4     (Cmaj9 spread)
3x1456  = C3 F3 B3 A4     (Cadd11+maj7+13)
```

---

## Sequence patterns

### Octave climb (every octave)

```
<absolute>-^1x<pattern>*N~
```

The relative form `^1x` advances exactly one octave per repeat. Useful
when you want to hear the same voicing in every register.

Examples:
- `1x135-^1x135*5~` — six-octave climb of the open Imaj7 triad.
- `1x1346-^1x1346*5~` — six-octave climb of the `346` open tetrad.
- `1x4444-^1x4444*5~` — six-octave climb of Lydian quartal.

### Continuation chain (chains by the shape's last interval)

```
1x<mode><intervals>-<intervals>*N~
```

When a shape's last interval matches the desired chain interval, the
continuation form chains continuously across dashes. Works best for
self-similar shapes (all 3rds, all 4ths, etc.).

Examples:
- `1x1333-3333*5~` — continuous third-stack from C1 to G7.
- `1x1444-4444*N~` — continuous fourth-stack (where range allows).
- `1x1-3*23~` — single-note third-step walk (single notes chain by 3rds).

### Modal cycle

```
<oct>x1<intervals>-<oct>x2<intervals>-<oct>x3<intervals>-...-<oct>x7<intervals>~
```

Seven setups in one octave, varying mode digit 1→7. Same intervals each
time, so the shape stays constant — only the mode-color changes.

### Two-hand setup (LH bass + RH chord)

```
<lh-shape> R <rh-shape>
```

The `R` divider says: prior shape is LH, following is RH; both set
simultaneously. Useful for chord-progression accompaniments.

Examples:
- `1x1 R 3x1335` — single-note bass C1 under a Cmaj9-no-7 voicing.
- `1x4 R 3x4335` — F1 bass under Fmaj9-no-7.
- `1x5 R 3x5333` — G1 bass under G7.

---

## Quick-pick by situation

| Situation | Pattern |
|---|---|
| **Warmup / hand-spread** | Drill 1: `1x1333-3333*5~` |
| **Calibrate reach** | `VERIFY.md` drills |
| **Mode exploration** | Drill 6: same intervals, varying mode digit |
| **Voicing study** | Universal-winner tetrads at one octave, varying mode |
| **Sustained color** | `1x4444` (Lydian quartal) — set, ring, listen |
| **Bass + chord progression** | Drill 8 — I-IV-V-I with two-hand setups |
| **Octave-by-octave climb** | Any pattern with `^1x<...>*5~` |
| **Continuous arpeggio** | Continuation form `1x1<...>-<...>*N~` |
| **Sparse top-note color** | Tetrads ending in 5 or 6 (e.g. `1335`, `1346`, `1456`) |

---

## Patterns to avoid

These are setable but rarely musical:

- **All 2nds in the low octave** — `1x1222` in oct 1 sounds muddy
  (stepwise clash penalty stacks).
- **Three adjacent stepwise intervals** — heavy aesthetic penalty.
- **Locrian root-position voicings** — the tonic instability of mode 7
  makes most root-rooted Locrian shapes feel unresolved. Use mode 7
  shapes as passing color (e.g., as a bø7 in a progression), not as a
  home.
- **Bottom-heavy spreads** — large ring-middle interval with small upper
  pairs (e.g., `1x1622`). Hand geometry favors open-top, not open-bottom.

---

## Practice tip

Pick one universal-winner tetrad and run drill 6 on it (modal cycle).
You'll hear the same shape recolored seven different ways without ever
moving the hand far. Then pick another and repeat. Twelve patterns × 7
modes = 84 distinct voicings — enough vocabulary for any hymn arrangement.
