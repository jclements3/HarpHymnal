# Harp Shape Encoding System

## Why this encoding exists

On the pedal harp, the hand commits to a configuration **before it touches the strings**. You form the shape in the air — fingers spread to specific intervals, each finger aimed at a specific string — and only then do you bring the hand down to engage. You cannot search for the notes once you’ve made contact; by then it’s too late. The shape has to be right in the air, a foot from the harp, or it won’t be right at all.

This encoding is built around that fact. Every code in the system describes a **pre-contact hand shape**: exactly what spread the fingers must form, which finger is assigned to which string, and (when it matters) the order in which the fingers land during the approach. The notation’s job ends the moment the hand reaches the strings. Everything after contact — rhythm, articulation, strike order, dynamics, sustain, roll vs. block — is the player’s interpretation.

This is why the encoding looks the way it does:

- **Fingers map to fixed positions** (ring, middle, index, thumb) so the hand can be pre-formed without ambiguity.
- **Intervals read bottom-up** because that’s how the hand opens outward as it forms the spread.
- **Per-finger-pair reach limits are first-class** — a shape the hand can’t pre-form is unplayable, regardless of what the strings would sound like.
- **Rhythm and strike order are absent** because those happen *after* the encoding’s job is done.
- **Chord names are absent** because the player needs the physical configuration, not a harmonic label that still has to be translated into one.

A piece in this system is a sequence of these pre-shapes — what each hand commits to, snapshot by snapshot — separated by spaces.

-----

## Goals

This encoding is the input format for an optimization problem: **given a piece of music, choose the sequence of shapes and the pedal-change schedule that plays the piece on a pedal harp.**

The optimizer takes a score (raw ABC, currently) and produces an encoded piece in this format. The encoding’s job is to make the optimizer’s output playable, comparable, and scoreable from text alone — no audio, no MIDI, no score lookup needed downstream.

### Optimizer objectives

Hard constraints (the optimizer must satisfy these or report failure):

- **Setability** — every shape’s interval digits fit within the per-finger-pair reach limits (see *Physical constraints*).
- **Pedal feasibility** — every pedal change has enough physical time for the foot to move; pedal state at each shape supports the pitches that shape names.
- **Coverage** — at every moment the music sounds, the held shape’s pitch-set contains the pitches the optimizer commits to playing (typically melody + bass; inner voices are the optimizer’s choice). A **moment** is a point where the encoder commits to a held configuration; the optimizer chooses moment boundaries. Coverage applies at every moment including single-voice anacrusis, mid-phrase voice entries, and voices that drop out before the next harmonic change. A single sounding pitch is covered by a single-note shape (one finger).

Soft objectives (the optimizer weighs these against each other; weighting is left to the algorithm):

- **Coast** — fewer, denser shapes are preferred over more, sparser ones. The hand should hold one configuration as long as the music allows.
- **Pedal economy** — fewer pedal changes are preferred over more; pedal-change moments cluster at phrase boundaries rather than mid-phrase.
- **Voice-leading** — adjacent shapes share fingers when possible; shape-to-shape moves minimize finger travel.
- **Acoustic quality** — shapes from the universal-winner / mode-conditional vocabulary (see *Aesthetic scoring*) are preferred over lower-scoring shapes that satisfy the same coverage.
- **Aggressive setup** — when several shapes can cover the same harmonic stretch, prefer the one with more fingers planted (tetrad over triad over dyad). Front-load the hand work so the music can coast.

The optimizer is not required to reproduce every voice in the source. SATB hymns, in particular, are inputs whose four voices the optimizer reads to determine harmony, melody, and bass — not voices the optimizer must clone. Interior voice details are the optimizer’s discretion, subject to the coverage constraint above.

### Why this encoding makes the optimizer tractable

The properties enumerated under *Algorithmic properties* below aren’t accidental — they’re the contract the encoding offers the optimizer. Setability is a per-position bounds check; voice-leading distance is a digit-by-digit comparison; transposition is a header swap; the full shape vocabulary is enumerable. Each cost-function term the optimizer needs reduces to text operations on the encoding.

-----

## What’s deliberately out of scope

Because the encoding describes pre-contact configurations and nothing else, several things you might expect to find are not here:

- **Rhythm, articulation, strike order, dynamics, timing — including how long a shape is held and which fingers pluck within it.** Outside the scope of what the hand commits to in the air.
- **Traditional chord names and harmonic function.** No roman numerals, no `Cmaj7` / `Dm7sus4` quality labels, no tonic/dominant categories. The vocabulary is the set of hand configurations that pass two filters: the hand can reach them, and they sound musical.

-----

## Document structure

A piece is written as a **header block** followed by one or more **rows** of shapes:

```
Title:  <piece title>     (optional)
Number: <NNN>             (required, zero-padded 3 digits)
Tonic:  <pitch class>     (required)
Pedals: <braille cell>    (required)
---
<row of shapes>
<row of shapes>
...
```

`Number:` is the piece’s index within its book (hymnal, drill set, etc.) — each book has its own independent numbering sequence.

`Tonic:` is the pitch class that mode digit 1 points at. A piece in C major has `Tonic: C`. A piece in E natural minor has `Tonic: E`. A piece in D Dorian has `Tonic: D`. The tonic is the home note of the piece — wherever its phrases resolve. The value is a single pitch class (`C`, `D`, `E`, `F`, `G`, `A`, `B`) optionally followed by `#` or `b`.

`Pedals:` is the initial pedal-position braille cell string (see *Pedal positions* below) — exactly 4 braille characters, no other form is legal. It specifies which 7 pitches are live on the strings — the diatonic pitch set the shapes operate on. The tonic must be one of those 7 pitches. Pedal cells appearing inline mid-piece signal pedal changes.

Together, `Tonic:` and `Pedals:` fully resolve every shape: the digits name scale degrees relative to the tonic, and the pedal state determines what pitch each scale degree actually sounds. Major, minor, and modal pieces all use the same two fields — only their values differ. A piece in E natural minor has `Tonic: E` plus G-major-signature pedals; a piece in C major has `Tonic: C` plus C-major-signature pedals; harmonic-minor and melodic-minor inflections appear as inline pedal cells, not as a different tonic.

Below the `---` separator, each row is a sequence of shapes separated by spaces. Rows are sequential phrases; position resets between rows.

For **songs**, the first shape of each row must include an absolute octave prefix (since registration on the harp matters). For **drills**, the first shape may omit the octave prefix entirely — the player chooses any octave to practice in, and subsequent shapes inherit from there.

-----

## Pedal positions

A pedal harp has 7 pedals, one per pitch class (D, C, B, E, F, G, A), each with three positions: flat (raised), natural (middle notch), and sharp (depressed). The pedal state determines which 7 pitches the strings sound — i.e., the diatonic pitch set the shapes operate on.

Pedal positions are notated as **4 braille cells = 8 columns**:

```
  cell 1   cell 2   cell 3   cell 4
   D C      B ⫶      E F      G A
```

|Column|Pedal       |Foot |
|------|------------|-----|
|1     |D           |left |
|2     |C           |left |
|3     |B           |left |
|4     |split marker|—    |
|5     |E           |right|
|6     |F           |right|
|7     |G           |right|
|8     |A           |right|

Column 4 is the **always-on split marker** between the two feet — all three of its dots are filled (dots 4, 5, 6 of cell 2). It carries no pedal information; it just visually divides left from right.

**Dot height within a column = pedal position:**

|Row|Dot position|Pedal position   |
|---|------------|-----------------|
|1  |top         |flat (raised)    |
|2  |middle      |natural          |
|3  |bottom      |sharp (depressed)|

Each pedal column has exactly one dot raised, showing its current position. A complete pedal cell therefore has 7 informational dots (one per pedal) plus 3 split-marker dots = 10 dots across the 4 cells.

### Example: B♭ major

`Pedals: ⠒⠹⠑⠒`

Reading: D♮ C♮ B♭ | E♭ F♮ G♮ A♮ (the textual decomposition is gloss for the reader, not a legal value).

```
cell 1   cell 2   cell 3   cell 4
· ·      ● ●      ● ·      · ·
● ●      · ●      · ●      ● ●
· ·      · ●      · ·      · ·
 D C      B ⫶      E F      G A
```

- Cell 1 `⠒` (dots 2,5):     D♮ C♮       — both naturals, middle row
- Cell 2 `⠹` (dots 1,4,5,6): B♭ + split  — B flat top dot, split column full
- Cell 3 `⠑` (dots 1,5):     E♭ F♮       — E flat top dot, F natural middle
- Cell 4 `⠒` (dots 2,5):     G♮ A♮       — both naturals, middle row

### Inline pedal changes

A pedal cell may also appear inline between shapes whenever the pedal state changes. Inline cells are written in full — every pedal’s position is re-specified, not just the ones that moved. This keeps each cell self-contained: at any point in the piece you can read the most recent pedal cell and know the complete pedal state.

Inline pedal cells provide the chromatic-alteration mechanism the rest of the encoding doesn’t address. The shape grammar itself is purely diatonic to the current pedal state; pedal cells are the only way non-diatonic pitches enter the piece.

**Syntax.** Inline cells are standalone tokens, space-separated like shapes. Every shape after a cell uses the new pedal state until the next cell:

```
3R^5333 ⠒⠹⠑⠒ 3R^5333
```

Pedal-change physical timing (when the foot actually moves) is the player’s interpretation, subject to the optimizer’s pedal-feasibility constraint.

**Tonic does not change inline — only `Pedals:` does.** `Tonic:` is fixed for the whole piece. Local tonicizations and modulations are encoded as shapes whose mode digit reflects the chord’s relationship to the *piece’s* tonic (a B♭ chord in a piece with `Tonic: F` is mode 4, not mode 1). Inline pedal cells handle the chromatic pitches the local harmony requires.

-----

A **shape** is one hand’s pre-contact configuration — what one hand commits to in the air before landing on the strings. Shapes are separated by spaces; each space means the hand lifts off, resets in the air, and forms the next configuration before approaching the strings again.

A shape can also be **held** while individual fingers pluck within it. The shape describes the configuration the hand commits to; how long it stays committed and which fingers strike when are the player’s interpretation. A new shape is only needed when the harmony moves outside what the held shape can cover, or when the melody leaves the fingers currently planted. A bar of music where the harmony stays put and the melody walks across notes already in the hand is **one shape**, not several.

Whether two adjacent shapes are played sequentially or simultaneously is the player’s interpretation, the same way rhythm and articulation are. The encoding does not enforce a separate notion of “moment” over and above the shape itself.

-----

## Shape syntax

A shape has up to three parts: an optional octave prefix, a degree, and zero to seven intervals. Operators may be appended to expand a shape into a sequence.

```
shape:     octave? degree intervals? repeat?
  octave:    [+-]?[1-7][xLR]
  degree:    '^' [1-7] subscript?
  intervals: interval (,? interval){0,6}    with comma required if total intervals >= 4
  interval:  [2-f] subscript?
  subscript: [₁-₈]
  repeat:    (back_to_back | octave_climb) (count | * | ~)?
  back_to_back: '$'{1,7}                    N dollar signs = last N digits as repeating unit
  octave_climb: '&'
  count:     [1-9]+
```

The maximum of 7 intervals corresponds to 8 fingers (2 hands × 4 fingers): 7 inter-finger gaps among 8 fingers. The `intervals` rule is optional because zero-interval shapes (single notes, e.g. `1L^1`) are valid one-finger shapes used heavily in two-hand textures (LH bass + RH chord).

The `back_to_back` rule’s count of `$` signs is **semantic, not stylistic**: `$` repeats the last 1 digit as the unit, `$$` the last 2, `$$$` the last 3, and so on (see *Operators* for the table).

### Octave prefix

The octave prefix is **optional**. It has three forms:

- **Absolute**: `1x` … `7x` (or with `L`/`R` in the letter slot) — explicit harp octave 1–7, indexed bottom up. **Octave N spans the pitches C(N) through B(N).** Octave 1 = C1–B1 (with C1 at MIDI note 24, the lowest C on a typical 47-string concert pedal harp); octave 2 = C2–B2; octave 4 contains middle C (C4); octave 7 = C7–B7. The bottom finger of a shape with prefix `Nx` sits on the named degree’s pitch within octave N.
- **Relative**: `+1x`, `-2L`, etc. — the prior shape’s octave plus or minus N. Sign required.
- **Absent**: same octave as the prior shape (sticky inheritance). If the prior octave was itself unstated (drill context), this one is also unstated and the player picks.

### Letter slot

When the octave prefix is present, it ends with a letter:

- `x` — either hand (player picks)
- `L` — left hand
- `R` — right hand

When the octave prefix is absent, the letter slot is also absent. Hand assignment is inherited from the prior shape.

### Degree

A `^` caret followed by a single digit `1`–`7` naming the scale degree of the bottom finger relative to the header’s `Tonic:`. The caret marks the digit as the degree (mode root) and disambiguates it from the interval digits that follow. This is the mode root of the shape:

- `^1` Ionian, `^2` Dorian, `^3` Phrygian, `^4` Lydian, `^5` Mixolydian, `^6` Aeolian, `^7` Locrian.

### Intervals

Zero to seven hex digits `2`–`f`, each an interval gap between adjacent fingers reading bottom-up:

- 0 intervals → single note (one finger)
- 1 interval → dyad (two fingers)
- 2 intervals → triad
- 3 intervals → tetrad (one full hand)
- 4–7 intervals → two-hand shape (more fingers than one hand can pre-form)

When a shape has **4 or more intervals**, both hands are involved. The intervals before a comma are LH; the intervals after are RH:

```
1x^1336,33   — 6 fingers: LH on degree 1 with intervals 336, RH picks up with intervals 33
```

The comma marks where LH’s top finger ends and RH’s bottom finger begins. For one-hand shapes (≤ 3 intervals), no comma is used.

**When to use the comma form vs. separate shapes.** The comma form (`1x^1333,3333`) describes one held 8-finger tower — both hands committed to a single contiguous stack. This fits sustained-harmony textures (drones, plainsong cadences, final chords). It rarely fits hymn-style writing, where the harmony moves before a single tower pays off. For LH-bass + RH-chord textures with a register gap between the hands, or any texture where the two hands re-set independently, write separate space-separated shapes with explicit `L`/`R` letters: `1L^1 3R^5333`. The two forms are not interchangeable: comma = one held configuration, separate = two independent configurations.

-----

## Interval digits

Interval names count the endpoints (a 3rd is two scale steps apart):

|Digit|Interval name       |Scale steps|
|-----|--------------------|-----------|
|`2`  |2nd                 |1          |
|`3`  |3rd                 |2          |
|`4`  |4th                 |3          |
|`5`  |5th                 |4          |
|`6`  |6th                 |5          |
|`7`  |7th                 |6          |
|`8`  |8th (octave)        |7          |
|`9`  |9th                 |8          |
|`a`  |10th                |9          |
|`b`  |11th                |10         |
|`c`  |12th                |11         |
|`d`  |13th                |12         |
|`e`  |14th                |13         |
|`f`  |15th (double octave)|14         |

Hex `f` is the cap. Wider intervals exceed any two-hand voicing and aren’t expressible in one digit.

The digit `1` is **invalid as an intra-shape interval** — two fingers in a single hand can’t sound the same string.

-----

## Subscripts: assembly order

Digits in a shape map to fingers by position: **1st digit = ring, 2nd = middle, 3rd = index, 4th = thumb** (for each hand independently when the shape is two-hand). This mapping is fixed.

By default, the fingers all settle on the strings together (block-strike) or in natural bottom-up order (default roll). The encoding doesn’t distinguish these — the player picks based on context.

**Subscripts mark exceptions to the default assembly order.** A subscript on a digit says *when that digit’s finger plants in the assembly sequence*:

The degree digit also takes a subscript — it represents the bottom finger (ring), so it gets a subscript when subscripts are used at all (see the rule below: “if you use subscripts, mark every finger”).

|Subscript|Plants       |
|---------|-------------|
|`₁`      |first        |
|`₂`      |second       |
|`₃`      |third        |
|`₄`      |fourth       |
|`₅`      |fifth        |
|`₆`      |sixth        |
|`₇`      |seventh      |
|`₈`      |eighth (last)|

So `1x^1₁3₂3₃3₄` is the default bottom-up assembly written explicitly: ring plants 1st, middle 2nd, index 3rd, thumb 4th.

`1x^1₄3₃3₂3₁` reverses the order: thumb plants 1st, then index, middle, ring last. A top-down assembly.

`1x^1₂3₁3₄3₃` plants middle 1st (anchor), then ring 2nd, then thumb 3rd, index last.

If you use subscripts, mark every finger in the shape — partial subscripts are ambiguous. A one-hand shape uses ₁–₄; a two-hand shape numbers globally across both hands (₁–₈), so the very first finger to plant in either hand gets ₁, regardless of which hand it’s in.

The subscripts describe the *recipe for assembling the shape*, not the order in which the strings are struck after assembly.

-----

## Operators

Operators expand a shape into a **sequence of shapes**. They appear at the end of a shape token.

|Operator          |Meaning                                                                                                                       |
|------------------|------------------------------------------------------------------------------------------------------------------------------|
|`$N`              |Repeat back-to-back. Take the last 1 digit as the repeating unit; append the unit N more times as new shapes.                 |
|`$$N`             |Same, with the last 2 digits as the unit.                                                                                     |
|`$$$N`, `$$$$N`, …|Last 3, 4, … digits as the unit.                                                                                              |
|`&N`              |Repeat octave-aligned. The whole shape is re-stamped one octave higher per iteration; N is the count of additional iterations.|

The count `N` may be:

- a numeric literal (`1`, `2`, …) — append exactly N iterations
- `*` — fill until the harp’s range cap is reached
- `~` — fill to cap, then mirror back down with apex de-duplication (the topmost shape isn’t re-entered on the way back)

Default count (operator with no count) is **once** — one additional iteration.

Operators expand purely textually within a single shape token. Inline pedal cells are separate tokens and cannot appear inside an operator expansion. To change pedals during what would otherwise be one operator expansion, split it: `1x^135&3 ⠒⠹⠑⠒ +4x^135&3`.

### Worked examples (with `Tonic: C`)

|Code     |Expansion                                   |Notes produced                           |
|---------|--------------------------------------------|-----------------------------------------|
|`1x^14$`  |`1x^14 4`                                    |C1-F1, then F1-B1                        |
|`1x^14$3` |`1x^14 4 4 4`                                |Quartal climb: C1-F1, F1-B1, B1-E2, E2-A2|
|`1x^135&` |`1x^135 +1x^135`                              |Cmaj triad in octave 1, then octave 2    |
|`1x^135&3`|Cmaj triads in octaves 1, 2, 3, 4           |Stacked triads climbing                  |
|`1x^135&*`|Cmaj triads from octave 1 to as high as fits|Full-range climb                         |
|`1x^135&~`|Climb to top, then mirror back down         |Full-range there-and-back                |

-----

## Reserved meanings

- **`^`** marks the degree (mode root). Every shape has exactly one `^`, immediately preceding the degree digit. Bare digits not preceded by `^` are intervals (or operator continuations after `$`).
- **Digit `1`** is valid as a mode digit (when prefixed with `^`), an octave digit, or a relative-octave count. It is **not** valid as an intra-shape interval.
- **`x`, `L`, `R`** are letter-slot characters, not digits. They follow the octave digit and declare hand assignment: `x` = either, `L` = left, `R` = right.
- **`+` / `-` signs** turn an absolute octave digit into a relative one (`+1x` = prior octave + 1; `-2L` = prior octave − 2).
- **Hex `f` is the cap on every interval.** A 15th is the widest interval expressible in one digit.
- **No descending intervals** within a shape. Every interval reads upward.
- **The comma** in a shape’s interval list marks the LH/RH split for two-hand shapes (≥ 4 intervals).
- **`$`, `&`, `*`, `~`** are operators; they appear at the end of a shape.

-----

## Examples

With `Tonic: C`:

|Code            |Reading                                                                                           |
|----------------|--------------------------------------------------------------------------------------------------|
|`1x^13`          |Ionian dyad in octave 1: C1 + 3rd up = C1–E1.                                                     |
|`2x^2d`          |Dorian dyad in octave 2: D2 + 13th = D2–B3.                                                       |
|`2x^233`         |Dorian triad: D2–F2–A2.                                                                           |
|`1x^7333`        |Locrian tetrad: B1–D2–F2–A2 (root-position Bø7 voicing).                                          |
|`1x^1333,3333`   |Two-hand stacked-thirds shape spanning 8 fingers: LH on C1-E1-G1-B1, RH picks up with D2-F2-A2-C3.|
|`1x^1333 +1x^1333`|Two shapes: stacked-thirds tetrad in octave 1, then the same tetrad in octave 2.                  |
|`1L^6 1R^1333`    |LH on a single bass note (degree 6 = A1), then RH on the third-stack tetrad.                      |
|`1x^135&3`       |Open Imaj voicing climbed octave by octave, four iterations.                                      |
|`1x^135&~`       |Same voicing climbed to the top of the harp, then mirrored back down.                             |
|`1x^1₄3₃3₂3₁`    |Single shape, top-down assembly: thumb anchors first, ring lands last.                            |

-----

## Physical constraints

A pedal harp is played with four fingers per hand: thumb (highest pitch), index, middle, ring (lowest pitch). The encoding maps directly onto these:

```
       thumb  --+
                |  position 4 (top finger)
       index  --+
                |  position 3
       middle --+
                |  position 2
       ring   --+  position 1 (bottom finger)
```

When reading a shape like `1x^1336`, the interval digits correspond to inter-finger gaps from bottom to top:

- **1st interval digit** (`3` here): ring → middle gap
- **2nd interval digit** (`3` here): middle → index gap
- **3rd interval digit** (`6` here): index → thumb gap

Each finger pair has its own physical reach limit. The values below are best-guess defaults; the actual numbers for a given player should be calibrated using the drills in `VERIFY.md`.

|Finger pair           |Position in code|Comfortable|Hard ceiling|
|----------------------|----------------|-----------|------------|
|Ring–middle           |1st interval    |3rd        |4th         |
|Middle–index          |2nd interval    |4th        |5th         |
|Index–thumb           |3rd interval    |5th        |6th         |
|Thumb–ring (dyad only)|only interval   |6th        |13th        |

The thumb is the most independent and reaches the farthest. The ring is shortest and weakest. So **the encoding’s natural shape is small intervals at the bottom (ring side), larger intervals at the top (thumb side)** — the opposite of how piano voicings are typically organized.

A shape is **physically setable** if every interval digit fits within its position’s hard ceiling. Codes that violate this can still be enumerated, but represent shapes requiring two hands or assembly that exceeds the calibrated reach.

For two-hand shapes (≥ 4 intervals with a comma), each side of the comma is an independent one-hand shape and must satisfy the per-finger-pair limits within itself.

-----

## What the encoding captures

Each shape carries five layers of information simultaneously:

1. **Specific notes**: given the header’s `Tonic:` and `Pedals:`, every shape unambiguously specifies which strings are involved.
1. **Pitch-class set**: the harmonic content.
1. **Voicing**: same notes in different inversions or spreads get different codes. Each physical shape is a distinct entity.
1. **Quality / character**: the combination of mode root and intervals determines whether the shape sounds major, minor, diminished, suspended, etc., without needing a separate quality label.
1. **Setability**: directly readable from the digit positions and finger-pair limits.

Chord names like “Cmaj7” or “Dm7sus4(no5)” are deliberately not part of the encoding. Traditional chord names have inconsistencies around no-3, no-5, sus stacking, and quartal voicings, and the same physical sonority often has multiple legitimate names depending on context. The encoding sidesteps this by describing **the pre-contact configuration of the hand** rather than how the resulting chord should be theoretically labeled.

-----

## Algorithmic properties

Because the encoding is purely structural, several operations become mechanical:

- **Sortable** — codes naturally cluster by mode, then by interval shape.
- **Compact** — every setable shape fits in 2–4 characters of intervals plus the position prefix; shape sequences scale linearly, with `$+`, `&`, `*`, and `~` compressing repetitive patterns.
- **Self-parsing** — first-character class decides shape form; spaces separate shapes; positional rules within a shape make digit roles unambiguous.
- **Generative** — enumerate all combinations of legal digits → derive the full shape vocabulary.
- **Transposable for free** — shapes never reference a specific pitch, only scale degrees relative to the header’s `Tonic:`. To play in a different key, change `Tonic:` and `Pedals:`; every shape stays the same.
- **Comparable** — voice-leading distance between two shapes is computable from their codes.
- **Filterable** — physical-reach rules become simple per-position bounds checks.

-----

## Aesthetic scoring

Once setability is established, shapes can be ranked by acoustic beauty using rules that operate on the digits themselves, agnostic of chord names:

|Rule                                                  |Effect                   |
|------------------------------------------------------|-------------------------|
|Stepwise clash (interval = `2`) in low octave         |penalty                  |
|Three adjacent stepwise intervals                     |heavy penalty            |
|At least one wide interval (≥ `5`)                    |reward                   |
|Top interval (> bottom interval)                      |reward (open-top profile)|
|Top note on color scale degree (3, 5, 7, 9)           |reward                   |
|Pitch-class diversity (4 distinct pitches in a tetrad)|reward                   |
|Mode characteristic-tone present                      |mode-specific reward     |
|Mode avoid-note present alongside the major 3rd       |mode-specific penalty    |
|Locrian tonic-instability                             |mode-specific penalty    |

The scoring reveals which shape codes are **universally beautiful** (work in any modal context) versus **mode-conditional**.

-----

## Visualization format

The grid below shows every shape that is both physically setable and aesthetically beautiful in at least one mode. Rows are indexed by interval-only pattern (the mode digit dropped, since each row evaluates the shape across all 7 mode columns). An `x` marks intersections where the shape sounds good rooted on that mode’s tonic.

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

To turn a row pattern into a complete shape, prepend a position prefix: pick a mode column (which becomes the mode digit) and an octave, then write `<octave><hand>^<mode><pattern>` where `<hand>` is `x`, `L`, or `R`. For example, `444` in column 4 (Lydian) at harp octave 3 → `3x^4444` — bottom finger on the 4th scale degree of your key in octave 3, with three 4ths stacked upward, either hand.

-----

## Working pool

For one player’s hand at the default reach guess (ring–middle ≤ 4th, middle–index ≤ 5th, index–thumb ≤ 6th):

|Category                                     |Count    |
|---------------------------------------------|---------|
|Mathematically possible patterns at span ≤ 12|231      |
|Physically setable patterns                  |74       |
|× 7 modal columns                            |518 cells|
|Beautiful and setable (sweet-spot cells)     |≈ 130    |
|Universal-winner patterns                    |≈ 12     |
|Mode-conditional beautiful patterns          |≈ 17     |

These counts depend on the aesthetic threshold and per-finger reach calibration. They define a working shape vocabulary roughly the size of a typical jazz fake-book chord set, but organized by physical setability rather than by harmonic function.

-----

## Limitations

The encoding is the optimizer’s output format, not a universal music-notation system. Several deliberate constraints follow from that:

**Constraints the encoding imposes on the optimizer (not bugs):**

- Shapes are purely diatonic to the current pedal state. Chromatic alterations enter the piece only through pedal-cell changes (see *Pedal positions*); within a stretch of unchanged pedals, every shape is diatonic. The optimizer’s job is to schedule pedal changes so the diatonic regions cover the music.
- Each shape is a single pre-contact configuration. Within a single held shape, any subset of its fingers can be sustained or replucked freely — that’s articulation, not encoding. Sustained voices that cross *between* shapes (a held tone bridging a shape change) aren’t notated; the optimizer either re-attacks the held voice or chooses shape boundaries that don’t break it.
- Shape *function* (tonic, dominant, predominant) is not encoded. Function is the optimizer’s input, derived from the source; the encoded output is the chosen voicings only.
- Rhythm, articulation, strike order, timing, and dynamics are out of scope. The encoding describes the pre-contact configuration of the hand; how the strings are subsequently played is the player’s interpretation. The optimizer chooses *what* to set; the player decides *how* to play it.

**Limits on the encoding itself:**

- Aesthetic scoring uses heuristic rules; calibration against the player’s actual ear is necessary for the final 10–20% of accuracy.
- Hand-reach calibration in the *Physical constraints* table is a best guess. The drills in `VERIFY.md` produce the actual numbers — once those results are available, the table will be replaced.
- `~` and `*` apply to the operator they’re part of — they don’t auto-extend other expressions across the harp’s range.