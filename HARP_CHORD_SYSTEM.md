# The Harp Chord System — Authoritative Pedagogy

> **Source of truth:** `HarpChordSystem.tex` and the PDF it compiles to.
> This document explains what that PDF is. If this document disagrees with
> the PDF, **the PDF wins** — fix this document.
> This exists so that a fresh Claude session can learn the system in one read,
> without the user having to re-teach it.

---

## Elevator pitch

The Harp Chord System is a strictly-diatonic chord vocabulary for lever harp, organized around a **trefoil** of 6 cycle paths. It has **~118 unique two-hand chord fractions**. Every song is a walk on the trefoil, starting from the tonic, with occasional trips into a complementary pool of fractions for variety.

---

## The trefoil: tonic-centric grammar

- The tonic (**I**) sits at the center of the trefoil. **Every song starts at I.**
- Three cycles radiate out: **2nds (cyan)**, **3rds (red)**, **4ths (yellow)**.
- Each cycle is a closed 7-step loop of diatonic chords that ends back at I.
- Each cycle has **two directions** — CW and CCW — giving **6 paths total**.
- **All chord progressions are walks on these 6 paths.** The paths are the compositional grammar; they are not merely one option among many.

| Cycle | Direction | Ordered walk |
|---|---|---|
| 2nds | CW | I → ii → iii → IV → V → vi → vii° → I |
| 2nds | CCW | I → vii° → vi → V → IV → iii → ii → I |
| 3rds | CW | I → iii → V → vii° → ii → IV → vi → I |
| 3rds | CCW | I → vi → IV → ii → vii° → V → iii → I |
| 4ths | CW | I → IV → vii° → iii → vi → ii → V → I |
| 4ths | CCW | I → V → ii → vi → iii → vii° → IV → I |

**Melodic contour selects direction:**
- Ascending melody → **CW** edges (moods: Resolving, Lifting, Exploring, Triumphing, Galvanizing, Deepening, Warming, Tensing, Deceptive, Darkening, Releasing, …)
- Descending melody → **CCW** edges (moods: Landing, Lofting, Dreaming, Brooding, Homecoming, Grounding, Easing, Cooling, Calming, Pivoting, Reposing, Fracturing, …)

---

## Chord fractions

A **chord fraction** is a two-hand voicing written as **LH figure stacked over RH figure** (a typographic fraction). The LH plays the lower voicing on the lower strings; the RH plays the upper voicing on the higher strings.

Fractions come in **two shapes**:

### 1. Stacked fractions (single sonority)

Both hands render the **same** roman numeral. The result is a single held chord with both hands contributing. Each has **one mood word**.

Example: `I  133 / 933  Warm` — LH plays I at string 1 (C–E–G in key of C), RH plays I-ish voicing up an octave (D–F–A, actually a ii figure which, combined with LH's I, produces an I9 colour); the static sonority is described as *Warm*.

### 2. Cycle-step fractions (transition)

LH and RH render **adjacent** chords on a cycle edge. This is a transitional voicing where one hand holds the departing chord while the other arrives on the next chord. Each cycle-step fraction has **two paired moods**, one for each direction of travel across the edge:

- **CW mood**: how it feels walking CW across the edge
- **CCW mood**: how it feels walking CCW across the same edge

Example (2nds cycle, edge `I ↔ ii`): `LH=I RH=ii  133 / 933  Cloudy / Grounding` — going CW (`I → ii`, away from tonic) feels *Cloudy*; going CCW (`ii → I`, back to tonic) feels *Grounding*. One physical edge on the trefoil, two moods.

---

## The four tables in the handout

| # | Name | Page | What it shows |
|---|---|---|---|
| 1 | **Patterns** | 1 (left) | 14 finger-spacing shapes × 7 scale-degree starting positions → 98 cells of named chords across 7 modes (Ionian → Locrian). The **chord terrain**. |
| 2 | **Simple chord cycles** | 1 (right) | 3 cycles × 7 edges = 21 simple edges. Each row shows `from → to` chord pair + CW mood + CCW mood. **The skeleton of the 6 paths.** |
| 3 | **Complex chord cycles** | 2 (top) | 42 two-hand voicings along the same 6 paths. Each row shows `LH chord`, `RH chord`, `LH figure / RH figure`, CW mood, CCW mood. **The walks rendered for playing.** |
| 4 | **Chord fractions pool** | 2 (bottom) | 76 stacked single-sonority fractions. Each row shows `LH chord`, `RH chord`, `LH figure / RH figure`, mood name. **Curated best-of-the-rest fingerings.** |

**The 118 count:** 42 (complex cycles) + 76 (pool) = 118 total entries, but only **109 unique physical fingerings**.

- The **complex cycles table** holds the curated **best fingering** for each cycle-edge transition — one winner per (cycle, edge, voicing richness). These 42 were selected out of the full playable universe.
- The **pool table** holds the curated **best of the rest** — playable diatonic fingerings that didn't win a cycle-edge slot but are still strong enough to be part of the handout vocabulary.
- **9 of the pool entries are duplicates of complex-cycle entries** (same `(LH-fig, RH-fig)` pair appearing in both tables). These are redundant — the pool includes those fingerings again instead of using the slot for a different fingering. That leaves **9 pool slots of design room** that could be filled with new, non-redundant fingerings.
- The 118 is a **curated subset**, not every possible diatonic fingering. More pool entries could be added from the un-selected universe whenever more variety is wanted.

When a composition is running a pure cycle walk and it gets repetitious, reach into the pool for variety — same universe, different feeling.

---

## Finger patterns & figures

### The 14 patterns

Pattern IDs encode **interval sequences** between adjacent fingers:

| ID | Intervals | Fingers | Span |
|---|---|---|---|
| `24` | 2, 4 | 2 | 5 |
| `33` | 3, 3 | 2 | 5 |
| `34` | 3, 4 | 2 | 6 |
| `42` | 4, 2 | 2 | 5 |
| `43` | 4, 3 | 2 | 6 |
| `44` | 4, 4 | 2 | 7 |
| `233` | 2, 3, 3 | 3 | 6 |
| `323` | 3, 2, 3 | 3 | 6 |
| `332` | 3, 3, 2 | 3 | 6 |
| `333` | 3, 3, 3 | 3 | 7 |
| `334` | 3, 3, 4 | 3 | 8 |
| `433` | 4, 3, 3 | 3 | 8 |
| `434` | 4, 3, 4 | 3 | 9 |
| `444` | 4, 4, 4 | 3 | 10 |

All are **diatonic** — the harp is tuned to one key at a time and these patterns traverse scale positions only.

### How intervals count

All intervals are **inclusive** — a "3rd" counts both endpoints (C up to E = a 3rd, not D).

### What a figure is

A **figure** is a pattern with a **starting scale-degree prefix**. The first character names the harp string / scale degree where the lowest finger begins; each subsequent character is an inclusive interval up to the next finger.

**Hex alphabet for the first character** (starting string / scale degree):

| Symbol | Scale deg | Symbol | Scale deg | Symbol | Scale deg |
|---|---|---|---|---|---|
| `1` | 1 | `7` | 7 | `D` | 13 |
| `2` | 2 | `8` | octave (8) | `E` | 14 |
| `3` | 3 | `9` | 9 (= 2 up one oct) | `F` | 15 (= 1 up two oct) |
| `4` | 4 | `A` | 10 | | |
| `5` | 5 | `B` | 11 | | |
| `6` | 6 | `C` | 12 | | |

The alphabet is **hex** — 15 characters, `1`-`9` and `A`-`F`. Voicings that would have started above string 15 (previously `G`=16, `H`=17) are replaced by inversions at lower positions — this happens to align with the teacher's preference that inversions are more interesting than plain triads.

### Parsing examples (in key of C)

- `133` — start at deg **1** (C), up a 3rd to E, up a 3rd to G → **C–E–G** = **I** chord (root position triad)
- `933` — start at deg **9** = deg 2 up an octave (D5), up a 3rd to F, up a 3rd to A → **D–F–A** = **ii** chord one octave up
- `5333` — start at deg **5** (G), three 3rds → **G–B–D–F** = **V7**
- `1233` — start at deg 1, up a 2nd (D), up a 3rd (F), up a 3rd (A) → **C–D–F–A** = I in first inversion (written **IΔ¹**)
- `1433` — start at deg 1, up a 4th (F), up a 3rd (A), up a 3rd (C) → **C–F–A–C** = sus4 with octave doubled root (**Is4+8**)

### Chord identity comes from the figure alone

A figure uniquely determines its pitches (given the key). The chord label (`ii`, `V7`, `IΔ¹`, `Is4+8`) is what those pitches sound as. **Same pattern + different starting degree = different chord**, because the diatonic interval qualities shift as you move up the scale.

---

## Extended chord-name notation

Traditional roman-numeral analysis loses voicing information. This system captures it explicitly:

| Suffix | Meaning |
|---|---|
| *(none)* | plain triad (quality from roman-numeral case: uppercase major, lowercase minor) |
| `Δ` | major 7th |
| `7` | dominant 7th (on uppercase) or minor 7th (on lowercase) |
| `6` | major 6th |
| `m6` | minor 6th |
| `°` | diminished |
| `ø7` | half-diminished 7th |
| `q` | quartal triad |
| `q7` | quartal 7th |
| `s2` | sus2 |
| `s4` | sus4 |
| `s4+8` | sus4 with octave doubling |
| `+8` | root doubled at the octave |
| `¹` | first inversion (3rd in bass) |
| `²` | second inversion (5th in bass) |
| `³` | third inversion (7th in bass) |

So `Is4+8` is unambiguous: I chord voiced as sus4 with an added octave. `vi³` is vi in third inversion (its 7th in the bass). `IV²+8` is IV in second inversion with octave doubling. This is a deliberate improvement over the ~400-year-old notation that can't express those specifics.

---

## LH / RH figure pair notation

Two figures side by side = a two-hand voicing. **Left figure is the Left Hand; right figure is the Right Hand.**

Examples (key of C):
- `133 / 933` → LH = I (C–E–G at str 1), RH = ii (D–F–A at str 9, one octave up)
- `433 / A43` → LH = IV (F–A–C at str 4), RH = vi¹ (with 10th on top)
- `5333 / D43` → LH = V7, RH = ii in first inversion

---

## The strict-diatonic constraint

The 118 fractions are **strictly diatonic**. Explicitly excluded:

- No tritone substitutions
- No ♭II7
- No modal interchange
- No altered dominants with real ♭9 pitches
- No harmonic-minor V with the raised leading tone

**Why:** the harp is a lever harp — tuned to one key signature at a time. Chromatic notes require mid-piece lever flips, which are avoided. So the vocabulary is restricted to what the instrument can cleanly play.

### Chromatic-bypass via substitution

Some hymns (especially minor-key ones) need chromatic voicings the harp can't produce. The pipeline (`harp_mapper.py`) handles these by **substituting** a diatonic pool fraction in place of the impossible chromatic chord. Four strategies fire depending on context:

| Strategy | When it fires |
|---|---|
| `bVII_backdoor` | V preceded by IV (continues plagal pull) |
| `III_deceptive` | V at a fermata-marked final cadence (dramatic aeolian) |
| `pedal_i` | brief V with tonic-compatible melody |
| `modal_v` | mid-phrase V (default — natural-minor v7, modal feel) |

Each substitution records a `harmonic_substitution` field and preserves the original `requested_rn` so downstream renderers know what was substituted and why.

**This is not a compromise — it's the point.** Chromatic hymns get *translated into* the harp's vocabulary, not forced into impossible voicings.

---

## Pipeline: from hymn to rendered lead sheet

1. **Parse** (`hymn_parser.py`) — read `OpenHymnal.abc`, split into 4 SATB voices, sample beat-by-beat, extract roman numerals from the original harmony.
2. **Analyze transitions** (`harp_mapper.py`) — for each bar, ask: does the motion `(prev_chord → this_chord)` match a documented cycle edge?
3. **Pick a fraction:**
   - If yes: choose a **complex-cycle** entry for that edge. Direction (CW/CCW) is set by melodic contour.
   - If no: choose a **pool** fraction whose roman numeral matches the bar's chord.
   - If the hymn demands chromatic: apply a substitution strategy; pick a diatonic fraction that works; record which strategy fired.
4. **Export** (`export_hymn.py`) — produce a per-hymn comprehensive JSON with assignments + alternates.
5. **Render** — `export_to_reharm.py` + `fill_template.py` produce a LaTeX lead sheet; `build_review_html.py` produces a browser-friendly review page.

**Every rendered bar is one of three things:** a complex-cycle voicing (the hymn walked a path), a pool voicing (the hymn left the paths), or a substitution (the hymn demanded chromatic and the mapper translated it).

---

## Rules and conventions (never-do list)

1. **Don't add chromatic chords to the 118.** The vocabulary stays strictly diatonic. Chromatic needs are handled by substitution, not vocabulary expansion.
2. **Don't swap LH ↔ RH voicings.** They're different harp hand patterns, not display-interchangeable. Fix bad voicings in the mapper's scoring logic.
3. **Don't add melodic-rhythm weighting to phrase detection** without empirical evidence. Has been tried; signal too weak to discriminate.
4. **Don't fork `fill_template.py` into v2/v3.** Output-layer fixes belong in `export_to_reharm.py`.
5. **Don't cross-couple HarpHymnal with Trefoil.** Tablet/device/integration needs are solved inside HarpHymnal.

---

## Authoritative file precedence

When these files disagree, trust this order:

1. **`HarpChordSystem.pdf`** (rendered from the TeX) — ground truth for the user. They verify against this.
2. **`HarpChordSystem.tex`** — source of truth for the pipeline. Compiles to the PDF.
3. **`HarpChordSystem.json`** — machine-readable extraction. Has known drift (some entry labels were historically swapped); treat as derivative until validated.
4. **This document** (`HARP_CHORD_SYSTEM.md`) — pedagogical summary; if it contradicts the PDF, this doc is wrong and should be updated.

A validator script `tools/validate_chord_system.py` checks JSON figure↔roman consistency against the TeX. Run it before trusting any JSON-derived output.

---

## Glossary

- **Fraction** — a two-hand chord voicing written as LH figure over RH figure.
- **Figure** — a full string encoding a voicing: starting scale degree + interval sequence.
- **Pattern** — just the interval sequence, without the starting-degree prefix. 14 patterns total.
- **Pool** — the 76 stacked (single-chord) fractions, collectively. The off-path variety source.
- **Cycle** — one of three closed diatonic loops: 2nds, 3rds, 4ths.
- **Path** — a cycle walked in one specific direction. There are 6 paths (3 × 2).
- **Edge** — one step along a cycle (e.g. `ii ↔ I` in the 2nds cycle). 7 edges per cycle, 21 edges total across the 3 cycles.
- **Walk** — playing chords in the order that traces a path.
- **Mood** — a poetic label for the feeling of a single edge (transition) or a single stacked sonority.
- **Trefoil** — the three-leaf diagram showing all 3 cycles meeting at I at the center.
- **SATB** — the original 4-voice hymn analysis (Soprano/Alto/Tenor/Bass). Source material for what chord the mapper is trying to voice.
