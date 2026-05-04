# Stacks, Diads & Fingerings

Reference tables for **generic-interval** harp work. The caret digits
^1–^7 name *scale-degree positions in the major scale*, not chord
function. Where Roman numerals say "in this key, this is the dominant",
caret digits say "stack these intervals on degree N and you get this
sonority — true in every key."

Quality glyphs follow the canonical handout:
`Δ` = M7, `°` = dim, `ø7` = half-dim 7, `7` = dom 7, `m7`, `q` = quartal,
`s2`/`s4` = sus, `+8` = octave doubling, `¹²³` = inversion (bass tone).

Companion PDFs (printable, full landscape layout) live under
[`docs/handouts/`](../docs/handouts/):

- `diatonic-chord-stacks.pdf` (also generates the table below)
- `diatonic-fingerings.pdf` (chord name → every stack-fingering)
- `diatonic-diads.pdf` (the 13 diatonic diads, semitones + quality)
- `chromatic-intervals.pdf` (enharmonic-spelling chart — general theory)

-----

## 1. Diatonic chord stacks — generic-interval table

How to read this:

- **Columns**: scale degree of the **bottom** note of the stack.
- **Rows**: a stack of generic intervals. `3,3` = stack a third, then
  another third; `3,3,3` = three stacked thirds.
- **Cells**: most-abbreviated chord name. The caret digit (^1, ^2, …)
  marks the **root** of the chord, not the bottom note. Quality follows.
  Empty cells are diatonic stacks that don't form a recognized tertian /
  sus / quartal / added-6 sonority (genuine clusters like ^1-^2-^3).

Constraints: each interval ≤ 12, sum ≤ 12, ordered (`3,2 ≠ 2,3`).
All-empty rows omitted; the generator script in the standalone PDF
produces the full 130-row version.

| Stack | ^1 | ^2 | ^3 | ^4 | ^5 | ^6 | ^7 |
|---|---|---|---|---|---|---|---|
| 2 | ^1^2 | ^2^3 | ^3^4 | ^4^5 | ^5^6 | ^6^7 | ^7^1 |
| 3 | ^1^3 | ^2^4 | ^3^5 | ^4^6 | ^5^7 | ^6^1 | ^7^2 |
| 4 | ^1^4 | ^2^5 | ^3^6 | ^4^7 | ^5^1 | ^6^2 | ^7^3 |
| 5 | ^1^5 | ^2^6 | ^3^7 | ^4^1 | ^5^2 | ^6^3 | ^7^4 |
| 6 | ^1^6 | ^2^7 | ^3^1 | ^4^2 | ^5^3 | ^6^4 | ^7^5 |
| 7 | ^1^7 | ^2^1 | ^3^2 | ^4^3 | ^5^4 | ^6^5 | ^7^6 |
| 8 | ^1^1 | ^2^2 | ^3^3 | ^4^4 | ^5^5 | ^6^6 | ^7^7 |
| 2,4 | ^1s2 | ^2s2 |  | ^4s2 | ^5s2 | ^6s2 |  |
| 2,7 | ^1^2+8 | ^2^3+8 | ^3^4+8 | ^4^5+8 | ^5^6+8 | ^6^7+8 | ^7^1+8 |
| 2,8 | ^1^2+8 | ^2^3+8 | ^3^4+8 | ^4^5+8 | ^5^6+8 | ^6^7+8 | ^7^1+8 |
| 3,3 | ^1 | ^2m | ^3m | ^4 | ^5 | ^6m | ^7° |
| 3,4 | ^6m¹ | ^7°¹ | ^1¹ | ^2m¹ | ^3m¹ | ^4¹ | ^5¹ |
| 3,6 | ^1^3+8 | ^2^4+8 | ^3^5+8 | ^4^6+8 | ^5^7+8 | ^6^1+8 | ^7^2+8 |
| 3,8 | ^1^3+8 | ^2^4+8 | ^3^5+8 | ^4^6+8 | ^5^7+8 | ^6^1+8 | ^7^2+8 |
| 4,2 | ^1s4 | ^2s4 | ^3s4 |  | ^5s4 | ^6s4 |  |
| 4,3 | ^4² | ^5² | ^6m² | ^7°² | ^1² | ^2m² | ^3m² |
| 4,4 |  | ^2q | ^3q |  | ^5q | ^6q | ^7q |
| 4,5 | ^1^4+8 | ^2^5+8 | ^3^6+8 | ^4^7+8 | ^5^1+8 | ^6^2+8 | ^7^3+8 |
| 4,8 | ^1^4+8 | ^2^5+8 | ^3^6+8 | ^4^7+8 | ^5^1+8 | ^6^2+8 | ^7^3+8 |
| 5,4 | ^1^5+8 | ^2^6+8 | ^3^7+8 | ^4^1+8 | ^5^2+8 | ^6^3+8 | ^7^4+8 |
| 5,5 | ^1s2 | ^2s2 |  | ^4s2 | ^5s2 | ^6s2 |  |
| 5,6 | ^1 | ^2m | ^3m | ^4 | ^5 | ^6m | ^7° |
| 5,7 | ^1s4 | ^2s4 | ^3s4 |  | ^5s4 | ^6s4 |  |
| 6,3 | ^1^6+8 | ^2^7+8 | ^3^1+8 | ^4^2+8 | ^5^3+8 | ^6^4+8 | ^7^5+8 |
| 6,5 | ^6m¹ | ^7°¹ | ^1¹ | ^2m¹ | ^3m¹ | ^4¹ | ^5¹ |
| 6,6 | ^4² | ^5² | ^6m² | ^7°² | ^1² | ^2m² | ^3m² |
| 7,2 | ^1^7+8 | ^2^1+8 | ^3^2+8 | ^4^3+8 | ^5^4+8 | ^6^5+8 | ^7^6+8 |
| 7,5 |  | ^2q | ^3q |  | ^5q | ^6q | ^7q |
| 8,2 | ^1^2+8 | ^2^3+8 | ^3^4+8 | ^4^5+8 | ^5^6+8 | ^6^7+8 | ^7^1+8 |
| 8,3 | ^1^3+8 | ^2^4+8 | ^3^5+8 | ^4^6+8 | ^5^7+8 | ^6^1+8 | ^7^2+8 |
| 8,4 | ^1^4+8 | ^2^5+8 | ^3^6+8 | ^4^7+8 | ^5^1+8 | ^6^2+8 | ^7^3+8 |
| 2,3,3 | ^2m7³ | ^3m7³ | ^4Δ³ | ^57³ | ^6m7³ | ^7ø7³ | ^1Δ³ |
| 2,4,4 | ^1s2+8 | ^2s2+8 |  | ^4s2+8 | ^5s2+8 | ^6s2+8 |  |
| 2,4,5 | ^1s2+8 | ^2s2+8 |  | ^4s2+8 | ^5s2+8 | ^6s2+8 |  |
| 2,7,2 | ^1^2+8 | ^2^3+8 | ^3^4+8 | ^4^5+8 | ^5^6+8 | ^6^7+8 | ^7^1+8 |
| 3,2,3 | ^4Δ² | ^57² | ^6m7² | ^7ø7² | ^1Δ² | ^2m7² | ^3m7² |
| 3,2,4 |  | ^2q7 | ^3q7 |  |  | ^6q7 | ^7q7 |
| 3,3,2 | ^16 | ^2m6 | ^1Δ¹ | ^46 | ^56 | ^4Δ¹ | ^57¹ |
| 3,3,3 | ^1Δ | ^2m7 | ^3m7 | ^4Δ | ^57 | ^6m7 | ^7ø7 |
| 3,3,4 | ^1+8 | ^2m+8 | ^3m+8 | ^4+8 | ^5+8 | ^6m+8 | ^7°+8 |
| 3,3,6 | ^1+8 | ^2m+8 | ^3m+8 | ^4+8 | ^5+8 | ^6m+8 | ^7°+8 |
| 3,4,3 | ^6m¹+8 | ^7°¹+8 | ^1¹+8 | ^2m¹+8 | ^3m¹+8 | ^4¹+8 | ^5¹+8 |
| 3,4,5 | ^6m¹+8 | ^7°¹+8 | ^1¹+8 | ^2m¹+8 | ^3m¹+8 | ^4¹+8 | ^5¹+8 |
| 3,6,3 | ^1^3+8 | ^2^4+8 | ^3^5+8 | ^4^6+8 | ^5^7+8 | ^6^1+8 | ^7^2+8 |
| 4,2,4 | ^1s4+8 | ^2s4+8 | ^3s4+8 |  | ^5s4+8 | ^6s4+8 |  |
| 4,3,3 | ^4²+8 | ^5²+8 | ^6m²+8 | ^7°²+8 | ^1²+8 | ^2m²+8 | ^3m²+8 |
| 4,3,4 | ^2m7³ | ^3m7³ | ^4Δ³ | ^57³ | ^6m7³ | ^7ø7³ | ^1Δ³ |
| 4,3,5 | ^4Δ² | ^57² | ^6m7² | ^7ø7² | ^1Δ² | ^2m7² | ^3m7² |
| 4,4,2 |  | ^2q+8 | ^3q+8 |  | ^5q+8 | ^6q+8 | ^7q+8 |
| 4,4,4 |  | ^2q7 | ^3q7 |  |  | ^6q7 | ^7q7 |
| 5,2,5 | ^16 | ^2m6 | ^1Δ¹ | ^46 | ^56 | ^4Δ¹ | ^57¹ |
| 5,3,4 | ^1Δ | ^2m7 | ^3m7 | ^4Δ | ^57 | ^6m7 | ^7ø7 |
| 5,4,2 | ^1s2+8 | ^2s2+8 |  | ^4s2+8 | ^5s2+8 | ^6s2+8 |  |
| 5,4,3 | ^1+8 | ^2m+8 | ^3m+8 | ^4+8 | ^5+8 | ^6m+8 | ^7°+8 |
| 6,3,3 | ^6m¹+8 | ^7°¹+8 | ^1¹+8 | ^2m¹+8 | ^3m¹+8 | ^4¹+8 | ^5¹+8 |

-----

## 2. Diatonic diads — semitones & quality

13 distinct diads from the major scale, sorted by stack length (2nds,
3rds, 4ths, 5ths, 6ths, 7ths, octaves). **Semis** = pitch distance.
**Quality** follows letter-distance: P=perfect, M=major, m=minor,
A=augmented, d=diminished.

| Cell | Semis | Quality |  | Cell | Semis | Quality |  | Cell | Semis | Quality |  | Cell | Semis | Quality |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ^1^2 | 2 | M2 |  | ^7^2 | 3 | m3 |  | ^6^3 | 7 | P5 |  | ^5^4 | 10 | m7 |
| ^2^3 | 2 | M2 |  | ^1^4 | 5 | P4 |  | ^7^4 | 6 | d5 |  | ^6^5 | 10 | m7 |
| ^3^4 | 1 | m2 |  | ^2^5 | 5 | P4 |  | ^1^6 | 9 | M6 |  | ^7^6 | 10 | m7 |
| ^4^5 | 2 | M2 |  | ^3^6 | 5 | P4 |  | ^2^7 | 9 | M6 |  | ^1^1 | 12 | P8 |
| ^5^6 | 2 | M2 |  | ^4^7 | 6 | A4 |  | ^3^1 | 8 | m6 |  | ^2^2 | 12 | P8 |
| ^6^7 | 2 | M2 |  | ^5^1 | 5 | P4 |  | ^4^2 | 9 | M6 |  | ^3^3 | 12 | P8 |
| ^7^1 | 1 | m2 |  | ^6^2 | 5 | P4 |  | ^5^3 | 9 | M6 |  | ^4^4 | 12 | P8 |
| ^1^3 | 4 | M3 |  | ^7^3 | 5 | P4 |  | ^6^4 | 8 | m6 |  | ^5^5 | 12 | P8 |
| ^2^4 | 3 | m3 |  | ^1^5 | 7 | P5 |  | ^7^5 | 8 | m6 |  | ^6^6 | 12 | P8 |
| ^3^5 | 3 | m3 |  | ^2^6 | 7 | P5 |  | ^1^7 | 11 | M7 |  | ^7^7 | 12 | P8 |
| ^4^6 | 4 | M3 |  | ^3^7 | 7 | P5 |  | ^2^1 | 10 | m7 |  |  |  |  |
| ^5^7 | 4 | M3 |  | ^4^1 | 7 | P5 |  | ^3^2 | 10 | m7 |  |  |  |  |
| ^6^1 | 3 | m3 |  | ^5^2 | 7 | P5 |  | ^4^3 | 11 | M7 |  |  |  |  |

-----

## 3. Diatonic chord fingerings — alternative voicings

Quick lookup: chord name → every interval-stack fingering that produces
it. Format: caret digit = bottom degree, digits after = stacked
intervals. Example: **^1534** = start on ^1, stack a 5th, then a 3rd,
then a 4th. Sorted by stack length and lex order. Full table is in
`docs/handouts/diatonic-fingerings.pdf` (landscape print layout); a
selection of the most-played voicings:

| Chord | Fingerings | Chord | Fingerings |
|---|---|---|---|
| **^1** (I triad)        | ^133  ^156   | **^4** (IV triad)       | ^433  ^456 |
| **^2m**                 | ^233  ^256   | **^5** (V triad)        | ^533  ^556 |
| **^3m**                 | ^333  ^356   | **^6m**                 | ^633  ^656 |
| **^7°**                 | ^733  ^756   | **^1Δ** (Imaj7)          | ^1333  ^1534 |
| **^2m7**                | ^2333  ^2534 | **^3m7**                | ^3333  ^3534 |
| **^4Δ**                 | ^4333  ^4534 | **^57** (V7)            | ^5333  ^5534 |
| **^6m7**                | ^6333  ^6534 | **^7ø7** (vii ø7)       | ^7333  ^7534 |
| **^1¹** (I, 1st inv)    | ^334  ^365   | **^4¹** (IV, 1st inv)   | ^634  ^665 |
| **^5¹** (V, 1st inv)    | ^734  ^765   | **^4²** (IV, 2nd inv)   | ^143  ^166 |
| **^5²** (V, 2nd inv)    | ^243  ^266   | **^16** (I add6)        | ^1332  ^1525 |
| **^46** (IV add6)       | ^4332  ^4525 | **^56** (V add6)        | ^5332  ^5525 |
| **^1Δ¹** (Imaj7, 1st)   | ^3332  ^3525 | **^4Δ¹** (IVmaj7, 1st)  | ^6332  ^6525 |
| **^57¹** (V7, 1st inv)  | ^7332  ^7525 | **^2q** (quartal on 2)  | ^244  ^275 |
| **^3q**                 | ^344  ^375   | **^5q**                 | ^544  ^575 |
| **^6q**                 | ^644  ^675   | **^7q**                 | ^744  ^775 |
| **^1s2** (I sus2)       | ^124  ^155   | **^1s4** (I sus4)       | ^142  ^157 |
| **^4s2** (IV sus2)      | ^424  ^455   | **^5s2** (V sus2)       | ^524  ^555 |

The full PDF has 4-finger and octave-doubled (`+8`) variants too — the
list above is the everyday subset.

-----

## Why caret digits here, not Roman numerals?

Both notations name the same scale degrees, but they answer different
questions. **Roman numerals** assert *function* — `V7` is "the dominant
seventh of the key"; `IV²` is "the subdominant in second inversion". They
carry harmonic intent.

**Caret digits** assert *interval geometry* — `^57` is "stack three
thirds on degree V"; `^4²` is "stack a 4th and a 3rd starting from IV".
They're true in every key and stay silent on what the chord means
*harmonically*.

This whole page is interval geometry: which stacks produce which
sonorities, which fingerings produce which chords, what the interval
quality of a diatonic diad is. Roman numerals would drag in functional
baggage that isn't part of the question. Carets keep the geometry
pure.

When the question *is* harmonic — "what's the bar's chord function in
this hymn?" — Roman numerals come back. The mapper output, lead-sheet
labels, and cycle-progression tables stay RN.
