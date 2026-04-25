# Drills

Practice patterns under the harp setup encoding. See `README.md` for the
full notation; `VERIFY.md` for reach calibration; `HANDOUT.md` for the
catalog of beautiful patterns.

Each drill is a sequence of **setups** separated by dashes. The operators
`*N` (literal repeat), `~` (palindrome), and `^Nx` (relative octave)
compress repetitive material.

All drills below use header `Key: C`. To play in another key, change the
key — every code stays the same.

```
Title: <drill title>
Key:   C
---
<drill code>
```

---

## 1. Thirds sweep — workhorse warmup

```
1x1333-3333*5~
```

Six third-stacked tetrads spanning the harp from C1 to G7, then mirrored.

Shapes: `C1 E1 G1 B1` / `D2 F2 A2 C3` / `E3 G3 B3 D4` / `F4 A4 C5 E5` /
`G5 B5 D6 F6` / `A6 C7 E7 G7`. Continuation `3333` chains by a 3rd (gap)
plus three more 3rds (intervals), so every consecutive note across the
whole chain is a 3rd apart. All reaches comfortable.

---

## 2. Single-line third walk

```
1x1-3*23~
```

24 single notes ascending in melodic 3rds: `C1 E1 G1 B1 D2 F2 A2 ... E7 G7`,
then descending. No chord shapes — pure single-finger work, alternating
fingers (or hands) on each note. Trains cross-under and finger-over.

---

## 3. Open Imaj7 (no-5) arpeggio — six-octave spread

```
1x135-^1x135*5~
```

The triad C-E-B in every octave. Six shapes, oct 1-6. The relative form
`^1x135` advances exactly one octave from the prior shape. Builds
middle-index reach (E to B is a 5th, at the comfortable limit).

---

## 4. Cmaj9 (no-3-no-5) octave climb — sparkle

```
1x1355-^1x1355*5~
```

The tetrad `C E B F` in every octave: `C1 E1 B1 F2` / `C2 E2 B2 F3` /
... / `C6 E6 B6 F7`. Six octaves up and back. The 11 (F) on top of every
shape is a clean modern color — root, 3rd, 7th, 11th, no 5th.

---

## 5. Lydian quartal stack — modern color

```
1x4444-4444*2~
```

Three tetrads of stacked 4ths starting on F (mode 4 = Lydian in key C):
`F1 B1 E2 A2` / `D3 G3 C4 F4` / `B4 E5 A5 D6`. The F→B is the Lydian #4.

**Ring-middle is at the hard ceiling (a 4th)** — also doubles as a
stretch test. Drop to `1x4334-^2x4334*2~` for a milder Fmaj7 climb if
the ring strains.

---

## 6. Modal exploration — same shape, every mode

```
3x1333-3x2333-3x3333-3x4333-3x5333-3x6333-3x7333~
```

The same `333` interval pattern (three 3rds stacked) starting on every
mode of C major, all in octave 3. Hear the mode colors:

| Setup | Mode | Sounds like |
|---|---|---|
| `3x1333` | Ionian | Cmaj7 |
| `3x2333` | Dorian | Dm7 |
| `3x3333` | Phrygian | Em7 |
| `3x4333` | Lydian | Fmaj7 |
| `3x5333` | Mixolydian | G7 |
| `3x6333` | Aeolian | Am7 |
| `3x7333` | Locrian | Bø7 |

Seven setups, palindromed.

---

## 7. Open-top tetrad cycle

```
1x1346-^1x1346*5~
```

A `346` tetrad (universal-winner pattern) climbed octave-by-octave:
`C1 E1 A1 F2` / `C2 E2 A2 F3` / ... / `C6 E6 A6 F7`. Open major spread —
root, 3rd, 6th, 11th. Six octaves, palindromed.

---

## 8. Two-hand chord progression — bass under chord

```
1x1 R 3x1333 - 1x4 R 3x4333 - 1x5 R 3x5333 - 1x1 R 3x1333
```

Four setups, both hands set together at each dash. LH plays a single
bass note (root of the chord, low octave); RH plays the corresponding
maj7 / 7 tetrad in middle range. Progression: I → IV → V → I in C.

| Setup | LH | RH |
|---|---|---|
| 1 | C1 | C3 E3 G3 B3 (Cmaj7) |
| 2 | F1 | F3 A3 C4 E4 (Fmaj7) |
| 3 | G1 | G3 B3 D4 F4 (G7) |
| 4 | C1 | C3 E3 G3 B3 (Cmaj7) |

No palindrome — let the I sit at the end as resolution.

---

## 9. Top-down assembly — anchor the apex

```
1x1₄3₃3₂3₁-^1x1₄3₃3₂3₁*5~
```

Same shape and chain as drill 7-ish, but with subscript-marked assembly
order: thumb plants first (₁), then index (₂), middle (₃), ring last (₄).
Useful when you want to anchor the top note before the lower fingers
arrive — common for arrival chords where the melody sits on top.

The default for the same shape would just be `1x1336` (no subscripts),
which sets all fingers together or rolls bottom-up.

---

## 10. Palindrome study — small but expressive

```
1x1336~
```

Just one shape, palindromed. Plays C1 E1 G1 E2, then reverses for
E2 G1 E1 C1. Seven notes total (the apex E2 is not re-struck on the way
back). Useful for hearing how the palindrome operator behaves on a
single shape.

---

## Reading the codes

If a code looks dense, parse it like this:

1. Split on `-` to get individual setups.
2. For each setup, look for `R` divider or `L`/`R` prefix to assign hands.
3. For each shape inside, the first character decides the form:
   - Digit + `x` → absolute (`Nx<mode><intervals>`)
   - `^` + digit + `x` → relative octave (`^Nx<mode><intervals>`)
   - Bare digit → continuation (first digit = gap from prior top finger)

Subscripts `₁₂₃₄` on digits indicate non-default assembly order; without
subscripts the default is block-strike or bottom-up roll.

---

## Practice notes

- Most drills are written to span the whole harp's range. If you can't
  reach the highest setups yet, drop the trailing repetitions: e.g.
  `*5` → `*3` covers four octaves instead of six.
- `~` palindromes the prior expression as-given. To make a drill stop
  at a specific point on the way back (e.g., go up to the 4th octave
  but only return to oct 2), write the descent explicitly.
- The relative form `^Nx` always advances from the **immediately prior**
  shape, not from a fixed origin. So a chain `1x... -^1x... -^1x...`
  goes oct 1 → 2 → 3.
