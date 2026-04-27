# Reach calibration drills

The README’s per-finger reach table is a best guess. Play these drills and
fill in the **Result** column with what your hand actually does. Then the
table can be replaced with calibrated numbers.

For each shape, plant all designated fingers at once and hold for a beat.
The shape passes if every finger lands on its string without releasing
the others. Mark each row:

- `ok`   — comfortable, can plant repeatedly without strain
- `hard` — possible once with effort, can’t sustain
- `no`   — impossible

Run each section twice — once with **right hand**, once with **left hand**.
The hands aren’t always equal.

Header for every drill below:

```
Title: Reach calibration
Tonic: C
---
```

These drills are pure shape tests. They don’t use sequence operators
(`$`, `&`) or subscripts. The encoding’s subscripts indicate assembly
order (when each finger plants), not finger labels — for reach
calibration we want the simplest one-set shapes possible.

-----

## 1. Dyad reach (ring + middle, then ring + thumb)

A 2-digit shape is a dyad. By default the player picks which two fingers
to use — for small intervals, ring + middle is natural; for wide intervals,
ring + thumb (skipping middle and index entirely).

**Play each dyad twice: once with ring + middle, once with ring + thumb.**
Record both columns.

|Code  |Interval            |Ring+middle|Ring+thumb|
|------|--------------------|-----------|----------|
|`3x^12`|2nd                 |           |          |
|`3x^13`|3rd                 |           |          |
|`3x^14`|4th                 |           |          |
|`3x^15`|5th                 |           |          |
|`3x^16`|6th                 |           |          |
|`3x^17`|7th                 |           |          |
|`3x^18`|8th (octave)        |           |          |
|`3x^19`|9th                 |           |          |
|`3x^1a`|10th                |           |          |
|`3x^1b`|11th                |           |          |
|`3x^1c`|12th                |           |          |
|`3x^1d`|13th                |           |          |
|`3x^1e`|14th                |           |          |
|`3x^1f`|15th (double octave)|           |          |

The transition point — where ring + middle gives out and ring + thumb takes
over — is the calibrated **ring-middle ceiling**. The largest interval you
can plant with ring + thumb is the **thumb-ring ceiling**.

-----

## 2. Middle-index reach (within a triad)

A triad with **ring-middle locked at a 2nd** isolates middle-index as the
variable. The ring plants on C3, middle on D3 (just a 2nd up — minimal
stretch), then index varies.

|Code   |Middle-index interval|Result|
|-------|---------------------|------|
|`3x^123`|3rd                  |      |
|`3x^124`|4th                  |      |
|`3x^125`|5th                  |      |
|`3x^126`|6th                  |      |
|`3x^127`|7th                  |      |
|`3x^128`|8th                  |      |
|`3x^129`|9th                  |      |

The largest interval you can plant cleanly is the **middle-index ceiling**.

-----

## 3. Index-thumb reach (within a tetrad)

A tetrad with **ring-middle and middle-index both locked at 2nd** isolates
index-thumb as the variable.

|Code    |Index-thumb interval|Result|
|--------|--------------------|------|
|`3x^1223`|3rd                 |      |
|`3x^1224`|4th                 |      |
|`3x^1225`|5th                 |      |
|`3x^1226`|6th                 |      |
|`3x^1227`|7th                 |      |
|`3x^1228`|8th                 |      |
|`3x^1229`|9th                 |      |

The largest interval you can plant cleanly is the **index-thumb ceiling**.

-----

## 4. Combined hand spread (open-top vs open-bottom)

Real shapes plant all four fingers simultaneously, and the spreads compound.
These drills test cumulative reach.

**Open-top (small bottom intervals, big top):**

|Code    |Top interval|Total span|Result|
|--------|------------|----------|------|
|`3x^1223`|3rd         |6th       |      |
|`3x^1224`|4th         |7th       |      |
|`3x^1225`|5th         |8th       |      |
|`3x^1226`|6th         |9th       |      |
|`3x^1227`|7th         |10th      |      |
|`3x^1228`|8th         |11th      |      |

**Open-bottom (small top intervals, big bottom):**

|Code    |Bottom interval|Total span|Result|
|--------|---------------|----------|------|
|`3x^1322`|3rd            |6th       |      |
|`3x^1422`|4th            |7th       |      |
|`3x^1522`|5th            |8th       |      |
|`3x^1622`|6th            |9th       |      |
|`3x^1722`|7th            |10th      |      |

Open-top tetrads typically reach further than open-bottom — short ring +
long thumb is the natural geometry.

-----

## 5. Inter-shape gap (jump between consecutive shapes)

Tests the hand-jump distance between two consecutive shapes played by the
same hand. Single-note → single-note keeps the test clean.

Each row is a two-shape sequence: the first sets the starting note, the
second relies on sticky-octave inheritance (no octave prefix on the
second shape) or a relative-octave prefix (`+1x`) for jumps that cross
the octave line.

Play at one shape per second. The gap passes if you can re-plant without
hesitation or fishing for the string.

|Code      |Gap to next note|Result|
|----------|----------------|------|
|`1x^1 2`   |2nd             |      |
|`1x^1 3`   |3rd             |      |
|`1x^1 5`   |5th             |      |
|`1x^1 +1x^1`|8th (octave)    |      |
|`1x^1 +1x^3`|10th            |      |
|`1x^1 +1x^6`|13th            |      |
|`1x^1 +2x^1`|15th            |      |

This number isn’t currently in the README’s reach table — there’s no
guidance on how big an inter-shape gap can be in practice. Whatever value
you land on becomes the new entry.

-----

## Reporting

When you’re done, fill in this summary so the README’s reach table can be
replaced with real numbers:

```
Right hand:
  Ring-middle:    comfortable __, ceiling __
  Middle-index:   comfortable __, ceiling __
  Index-thumb:    comfortable __, ceiling __
  Thumb-ring:     comfortable __, ceiling __
  Open-top span:  comfortable __, ceiling __
  Open-bottom:    comfortable __, ceiling __
  Inter-shape gap: comfortable __, ceiling __

Left hand:
  Ring-middle:    comfortable __, ceiling __
  Middle-index:   comfortable __, ceiling __
  Index-thumb:    comfortable __, ceiling __
  Thumb-ring:     comfortable __, ceiling __
  Open-top span:  comfortable __, ceiling __
  Open-bottom:    comfortable __, ceiling __
  Inter-shape gap: comfortable __, ceiling __
```

The sections are arranged so you can stop at any point and still have
useful data. If you only have time for one, do **section 1** — it
calibrates the two most-load-bearing pairs (ring-middle and thumb-ring)
and is the test most likely to show the existing table is wrong.