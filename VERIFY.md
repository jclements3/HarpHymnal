# Reach calibration drills

The README's per-finger reach table is a best guess. Play these drills and
fill in the **Result** column with what your hand actually does. Then the
table can be replaced with calibrated numbers.

For each shape, plant all designated fingers at once and hold for a beat.
The shape passes if every finger lands on its string without releasing
the others. Mark each row:

- `ok`   — comfortable, can plant repeatedly without strain
- `hard` — possible once with effort, can't sustain
- `no`   — impossible

Run each section twice — once with **right hand**, once with **left hand**.
The hands aren't always equal.

Header for every drill below:

```
Title: Reach calibration
Key:   C
---
```

These drills are pure shape-setup tests. They don't use sequence operators
or subscripts — under the new encoding, subscripts indicate assembly order
(when each finger plants), not finger labels. For reach calibration we
want the simplest setups possible.

---

## 1. Dyad reach (ring + middle, then ring + thumb)

A 2-digit shape is a dyad. By default the player picks which two fingers
to use — for small intervals, ring + middle is natural; for wide intervals,
ring + thumb (skipping middle and index entirely).

**Play each dyad twice: once with ring + middle, once with ring + thumb.**
Record both columns.

| Code   | Interval | Ring+middle | Ring+thumb |
|--------|----------|-------------|------------|
| `3x12` | 2nd      |             |            |
| `3x13` | 3rd      |             |            |
| `3x14` | 4th      |             |            |
| `3x15` | 5th      |             |            |
| `3x16` | 6th      |             |            |
| `3x17` | 7th      |             |            |
| `3x18` | 8th (octave) |         |            |
| `3x19` | 9th      |             |            |
| `3x1a` | 10th     |             |            |
| `3x1b` | 11th     |             |            |
| `3x1c` | 12th     |             |            |
| `3x1d` | 13th     |             |            |
| `3x1e` | 14th     |             |            |
| `3x1f` | 15th (double octave) |  |            |

The transition point — where ring + middle gives out and ring + thumb takes
over — is the calibrated **ring-middle ceiling**. The largest interval you
can plant with ring + thumb is the **thumb-ring ceiling**.

---

## 2. Middle-index reach (within a triad)

A triad with **ring-middle locked at a 2nd** isolates middle-index as the
variable. The ring plants on C3, middle on D3 (just a 2nd up — minimal
stretch), then index varies.

| Code     | Middle-index interval | Result |
|----------|-----------------------|--------|
| `3x123`  | 3rd                   |        |
| `3x124`  | 4th                   |        |
| `3x125`  | 5th                   |        |
| `3x126`  | 6th                   |        |
| `3x127`  | 7th                   |        |
| `3x128`  | 8th                   |        |
| `3x129`  | 9th                   |        |

The largest interval you can plant cleanly is the **middle-index ceiling**.

---

## 3. Index-thumb reach (within a tetrad)

A tetrad with **ring-middle and middle-index both locked at 2nd** isolates
index-thumb as the variable.

| Code      | Index-thumb interval | Result |
|-----------|----------------------|--------|
| `3x1223`  | 3rd                  |        |
| `3x1224`  | 4th                  |        |
| `3x1225`  | 5th                  |        |
| `3x1226`  | 6th                  |        |
| `3x1227`  | 7th                  |        |
| `3x1228`  | 8th                  |        |
| `3x1229`  | 9th                  |        |

The largest interval you can plant cleanly is the **index-thumb ceiling**.

---

## 4. Combined hand spread (open-top vs open-bottom)

Real shapes plant all four fingers simultaneously, and the spreads compound.
These drills test cumulative reach.

**Open-top (small bottom intervals, big top):**

| Code      | Top interval | Total span | Result |
|-----------|--------------|------------|--------|
| `3x1223`  | 3rd          | 6th        |        |
| `3x1224`  | 4th          | 7th        |        |
| `3x1225`  | 5th          | 8th        |        |
| `3x1226`  | 6th          | 9th        |        |
| `3x1227`  | 7th          | 10th       |        |
| `3x1228`  | 8th          | 11th       |        |

**Open-bottom (small top intervals, big bottom):**

| Code      | Bottom interval | Total span | Result |
|-----------|-----------------|------------|--------|
| `3x1322`  | 3rd             | 6th        |        |
| `3x1422`  | 4th             | 7th        |        |
| `3x1522`  | 5th             | 8th        |        |
| `3x1622`  | 6th             | 9th        |        |
| `3x1722`  | 7th             | 10th       |        |

Open-top tetrads typically reach further than open-bottom — short ring +
long thumb is the natural geometry.

---

## 5. Inter-setup gap (continuation jump)

Tests the hand-jump distance between two consecutive setups played by the
same hand. Single-note → single-note keeps the test clean.

Play at one note per second. The gap passes if you can re-plant without
hesitation or fishing for the string.

| Code       | Gap to next note | Result |
|------------|------------------|--------|
| `1x1-2`    | 2nd              |        |
| `1x1-3`    | 3rd              |        |
| `1x1-5`    | 5th              |        |
| `1x1-8`    | 8th (octave)     |        |
| `1x1-a`    | 10th             |        |
| `1x1-d`    | 13th             |        |
| `1x1-f`    | 15th             |        |

This number isn't currently in the README's reach table — there's no
guidance on how big a continuation gap can be in practice. Whatever value
you land on becomes the new entry.

---

## Reporting

When you're done, fill in this summary so the README's reach table can be
replaced with real numbers:

```
Right hand:
  Ring-middle:    comfortable __, ceiling __
  Middle-index:   comfortable __, ceiling __
  Index-thumb:    comfortable __, ceiling __
  Thumb-ring:     comfortable __, ceiling __
  Open-top span:  comfortable __, ceiling __
  Open-bottom:    comfortable __, ceiling __
  Inter-setup gap: comfortable __, ceiling __

Left hand:
  Ring-middle:    comfortable __, ceiling __
  Middle-index:   comfortable __, ceiling __
  Index-thumb:    comfortable __, ceiling __
  Thumb-ring:     comfortable __, ceiling __
  Open-top span:  comfortable __, ceiling __
  Open-bottom:    comfortable __, ceiling __
  Inter-setup gap: comfortable __, ceiling __
```

The sections are arranged so you can stop at any point and still have
useful data. If you only have time for one, do **section 1** — it
calibrates the two most-load-bearing pairs (ring-middle and thumb-ring)
and is the test most likely to show the existing table is wrong.
