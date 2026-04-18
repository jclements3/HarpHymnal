# Software Design Document — HarpHymnal

_v1 — 2026-04-18_

HarpHymnal is a data pipeline that turns one large ABC source (`OpenHymnal.abc`, 370 hymns) into harp-playable grand-staff piano scores, lead-sheet reharm views, and diatonic-reharm drill pages. The system is strictly diatonic by design — all chords stay inside the 7-note scale of the current key. This document specifies the **grammar, vocabulary, and architecture** that every script in the ecosystem adheres to.

Companion docs:
- `PLAN.md` — living plan for the piano-score effort
- `ISSUES.md` — bugs and vocabulary gaps
- `HARP_CHORD_SYSTEM.md` — 118-chord vocabulary pedagogy
- `CLAUDE.md` — repo orientation for future sessions

---

## 1. Purpose

Take a hymn (or any song/piece) and produce three kinds of output:

1. **Comprehensive export** — machine-readable JSON carrying melody, harmony, phrases, lyrics, and chord assignments.
2. **Reharm view** — lead-sheet-style JSON + LaTeX showing the chord-fraction choices per bar, one chord per bar.
3. **Piano score** — LilyPond-engraved grand-staff arrangement with pedal grace notes, chord labels, ornamented melody, and printable PDF / SVG / MIDI output.
4. **Drill pages** — HTML tables of chord-to-chord practice exercises organized by technique.

There is no server, test suite, or build system — just a small set of Python scripts run from the command line plus LilyPond for engraving.

---

## 2. Pipeline

```
OpenHymnal.abc                          (source of truth)
    │
    ▼  hymn_parser.py
parsed voices + SATB + RN regions + phrases    (in-memory)
    │
    ▼  export_hymn.py
hymnal_export/<Title>.json              (comprehensive record — THE dataset)
    │
    ▼  export_to_reharm.py
hymnal_html/reharms/<Title>.json        (one chord per bar, phrase letters, mood tags)
    │
    ├──▶ fill_template.py + HymnReharmTemplate.tex
    │        └─▶ LaTeX → PDF lead sheet
    │
    └──▶ build_piano_score.py
             └─▶ LilyPond → PDF + SVG + MIDI grand-staff arrangement
                 (consumed by hymnal_html/HarpHymnal.html viewer)

drills/index.html                       (technique-drill tables; hand-authored v1)
```

Each stage consumes the previous stage's output. The grammar in Section 4 is the contract each stage obeys.

---

## 3. Vocabulary

Terms in dependency order (smallest → largest). See the grammar in §4 for formal productions.

### 3.1 Atoms
- **interval** — `2 | 3 | 4` — inter-finger step count inside a shape.
- **degree** — `1..7` — scale-degree anchor in the current key.
- **roman** — decomposed: `numeral + quality + inversion` (e.g. `IΔ7`, `vii○7`, `iii¹`).

### 3.2 Voicings (hand configurations)
- **intervals** — sequence of `interval`s, e.g. `"333"`. Identifies a hand *shape class* (14 total in the HarpChordSystem).
- **shape** — `degree + intervals` — one hand's concrete voicing. *The teacher's term*: shape is what the fingers do, locked in before the strings are engaged, ending on the thumb.
- **bishape** — two shapes stacked (LH + RH) — a two-hand voicing.

### 3.3 Chord names (abstract)
- **chord** — a roman numeral (`I`, `V7`, `IΔ7`, `iii`, `vii○`). Names the chord independent of voicing.
- **bichord** — two chords layered top-over-bottom (e.g. `iii/I`). Structurally `chord chord`; slash is a rendering choice.

### 3.4 Pool — paths + reserve
The **pool** is the full 118-fraction vocabulary. It splits into two disjoint subsets:

- **paths** (42 fractions) — the voicings that instantiate the six diatonic trefoil cycles (2nds / 3rds / 4ths × CW / CCW). Every trefoil walk uses only path fractions.
- **reserve** (76 fractions) — coloristic single-sonority voicings held in reserve for substitution and variety. Not on any cycle.

**pool = paths ∪ reserve.** Every fraction is in exactly one subset.

- **ipool** — a 3-digit index identifying one fraction in the pool. First digit is the LH scale-degree (1..7); last two digits are the rank within that degree (01 = cleanest, ascending as more ornamented). Within each degree the path fractions occupy the lowest ranks; reserve fractions fill the rest. Label only; the structural atom is `shape` or `bishape`.

### 3.5 Drill algebra
- **brace** — an alternation set: either a list of `ipool`s that realize the same chord, or a `chord` nonterminal.
- **step** — one drill line; a sequence of `brace`s.
- **drill** — one technique practised along one path: `technique + path + steps`.
- **instance** — one concrete playthrough of a step (pick one fraction from each brace).

### 3.6 Techniques (the reharm vocabulary)
Four top-level tags, 18 techniques total:
- **Substitution** (5): Third sub, Quality sub, Modal reframing, Deceptive sub, Common-tone pivot
- **Approach** (5): Step, Third, Dominant, Suspension, Double
- **Voicing** (6): Inversion, Density, Stacking, Pedal, Voice leading, Open/closed spread
- **Placement** (2): Anticipation, Delay

### 3.7 Paths (the trefoil)
Six diatonic cycles — three axes × two directions:
- **2nds CW / CCW** — stepwise
- **3rds CW / CCW** — tertian
- **4ths CW / CCW** — cycle of fifths (in C: `I → IV → vii○ → iii → vi → ii → V → I`)

### 3.8 Music
- **music** — `song | piece`; a song has lyrics, a piece does not.
- **song** / **piece** — metadata + bars (+ lyrics).
- **bar** — `melody + (chord | bichord) + [shape | bishape] + ornaments + [pedal changes] + [technique annotation]`.
- **melody** — ordered notes and rests inside a bar.
- **ornament** — harp-idiomatic decoration (arpeggio, grace, enclosure, neighbor, glissando, damping, harmonic, bisbigliando).
- **pedals** / **pedal_change** — pedal-harp initial setup and optional mid-piece flips.

### 3.9 Index conventions
Three cross-reference indices, consistently `i`-prefixed:
- **ipool** — into the 118-fraction pool (paths + reserve)
- **ibar** — 1-based position into `bars`
- **inote** — 0-based position inside a bar's `melody`

---

## 4. Grammar (EBNF v4)

```ebnf
(* ═════════════════════════════════════════════════════════════════
   HarpHymnal Grammar v4 — authoritative
   ═════════════════════════════════════════════════════════════════ *)

(* ------- Atoms ------- *)
interval   = "2" | "3" | "4" ;
degree     = "1" | "2" | "3" | "4" | "5" | "6" | "7" ;
digit      = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
number     = digit, { digit } ;
text       = ? free string ? ;
letter     = "A" | "B" | "C" | "D" | "E" | "F" | "G" ;
accidental = "♭" | "♯" ;

(* ------- Roman numerals ------- *)
roman      = numeral, [ quality ], [ inversion ] ;
numeral    = "I"  | "ii"  | "iii" | "IV" | "V"  | "vi"  | "vii○"
           | "i"  | "ii○" | "III" | "iv" | "v"  | "VI"  | "VII" ;
quality    = "Δ" | "Δ7" | "7" | "ø7" | "○7"
           | "6" | "9" | "s2" | "s4" | "q" | "q7" | "+8" ;
inversion  = "¹" | "²" | "³" ;

(* ------- Voicings ------- *)
intervals  = interval, interval, { interval } ;
shape      = degree, intervals ;
bishape    = shape, shape ;

(* ------- Chord names ------- *)
chord      = roman ;
bichord    = chord, chord ;

(* ------- Pool ------- *)
ipool      = digit, digit, digit ;                      (* 001..118 *)

(* ------- Drill algebra ------- *)
brace      = ipool, { ipool } | chord ;
step       = brace, { brace } ;
drill      = technique, path, step, { step } ;
instance   = (shape | bishape), { shape | bishape } ;

(* ------- Techniques ------- *)
technique    = substitution | approach | voicing | placement ;
substitution = "Third sub" | "Quality sub" | "Modal reframing"
             | "Deceptive sub" | "Common-tone pivot" ;
approach     = "Step approach" | "Third approach" | "Dominant approach"
             | "Suspension approach" | "Double approach" ;
voicing      = "Inversion" | "Density" | "Stacking" | "Pedal"
             | "Voice leading" | "Open/closed spread" ;
placement    = "Anticipation" | "Delay" ;

(* ------- Paths ------- *)
path       = ("2nds" | "3rds" | "4ths"), ("CW" | "CCW") ;

(* ═════════ Music side ═════════ *)

music      = song | piece ;
song       = metadata, bars, lyrics ;
piece      = metadata, bars ;

metadata   = title, key, meter, tempo, [ pedals ],
             [ phrases ], [ form ] ;
title      = text ;
key        = root, mode ;
root       = letter, [ accidental ] ;
mode       = "major" | "minor"
           | "dorian" | "phrygian" | "lydian"
           | "mixolydian" | "aeolian" | "locrian" ;
meter      = beats, unit ;
beats      = number ;
unit       = "1" | "2" | "4" | "8" | "16" | "32" ;
tempo      = number, unit ;

(* ------- Bars ------- *)
bars       = bar, { bar } ;
bar        = melody, (chord | bichord), [ shape | bishape ],
             { ornament }, { pedal_change }, [ technique ] ;
melody     = { note | rest } ;
note       = pitch, duration, { ornament } ;
rest       = duration ;
pitch      = letter, [ accidental ], number ;
duration   = ? quarter-length, e.g. 0.5, 1, 1.5 ? ;

(* ------- Ornaments (lever-harp idiom) ------- *)
ornament     = arpeggio | grace | enclosure | neighbor
             | glissando | damping | harmonic | bisbigliando ;
arpeggio     = "arp" ;
grace        = "grace", pitch ;
enclosure    = "enc", pitch, pitch ;
neighbor     = ("upper" | "lower"), pitch ;
glissando    = "gliss", pitch, pitch ;
damping      = "damp", ("LH" | "RH") ;
harmonic     = "harm" ;
bisbigliando = "bisb", pitch ;

(* ------- Pedal harp (7 pedals, 3 positions) ------- *)
pedals       = pedal_pos, pedal_pos, pedal_pos,        (* D C B — left foot  *)
               pedal_pos, pedal_pos, pedal_pos, pedal_pos ;  (* E F G A — right  *)
pedal_pos    = "flat" | "natural" | "sharp" ;
pedal_change = pedal_letter, pedal_pos ;
pedal_letter = letter ;

(* ------- Lyrics ------- *)
lyrics     = verse, { verse } ;
verse      = syllable, { syllable } ;
syllable   = ibar, inote, text, [ melisma ] ;
melisma    = "continues" ;

(* ------- Phrases ------- *)
phrases    = phrase, { phrase } ;
phrase     = ibar, { ibar }, [ path ] ;

(* ------- Form ------- *)
form       = section, { section } ;
section    = label, ibar, ibar ;
label      = "intro" | "verse" | "chorus" | "bridge" | "refrain" | "outro" ;

(* ------- Refs ------- *)
ibar       = number ;    (* 1-based position in `bars` *)
inote      = number ;    (* 0-based position inside a bar's melody *)
```

### Rendering vs structure
The grammar is pure structure. Rendering choices made by downstream layers:

| Concept | Structure | Typical rendering |
|---|---|---|
| `bichord = chord, chord` | two chords | `I/V`, `I` over `V`, space-separated |
| `meter = beats, unit` | two numbers | `3/4`, `C`, `𝄵` |
| `brace = ipool, { ipool }` | list of ipools | `{006\|015\|029}` or `{006,015,029}` |
| `pedal_pos` | abstract state | `♭/♮/♯`, `↑/—/↓`, `up/mid/down` |
| Cycle color on a phrase | derived from `path` | `leafblue`, `leafgreen`, etc. via stylesheet |

No rendering artifacts in grammar. Parsers emit structure; renderers choose glyphs.

---

## 5. Codebase layout

```
OpenHymnal.abc                       source of truth — 370 hymns
HarpChordSystem.{tex,pdf,json}       118-chord vocabulary handout
HARP_CHORD_SYSTEM.md                 vocabulary pedagogy doc
PLAN.md                              living plan for piano-score work
ISSUES.md                            known bugs / vocab gaps
SDD.md                               ← this document

tools/                               pipeline scripts (run from repo root)
├── hymn_parser.py                   ABC → structured music data
├── harp_mapper.py                   RN + key + melody → best fraction
├── export_hymn.py                   produces hymnal_export/*.json
├── export_to_reharm.py              → hymnal_html/reharms/*.json
├── fill_template.py                 reharm JSON → LaTeX lead sheet
├── build_piano_score.py             reharm + export → LilyPond → PDF/SVG/MIDI
├── build_all_piano_scores.py        batch driver over 294 hymns
├── build_harphymnal_html.py         builds hymnal_html/HarpHymnal.html viewer
├── build_review_html.py             builds hymnal_html/review.html (294-hymn nav)
├── build_chord_system_html.py       builds hymnal_html/chord_system.html
├── build_piano_book.py              (future) bound piano-score book
├── rebuild_chord_system_json.py     HarpChordSystem.tex → HarpChordSystem.json
└── analyze_chord_system.py          curation audit
    apply_new_curation.py

hymnal_export/                       294 comprehensive-export JSONs (checked in)
hymnal_html/                         web-servable output
├── HarpHymnal.html                  main viewer (left nav + right split)
├── review.html                      294-hymn reharm review
├── chord_system.html                handout
├── drills/... ??                    (empty — drills live one level up)
├── reharms/*.json                   294 reharm JSONs
├── book/*.lytex, *.pdf              per-hymn bound LaTeX piano-score sources
└── <slug>.{ly,pdf,svg,midi}         batch-rendered piano scores (293 OK, 1 FAIL)

drills/                              reharm-drill pages
└── index.html                       Third sub drill (v1, 6 steps)

samples/                             reference PDFs (read-only artifacts)
```

---

## 6. Data-model mapping

The grammar in §4 maps onto the JSON shapes each pipeline stage produces. Key correspondences:

### `hymnal_export/<Title>.json` → music
- `title`, `music.key_root`, `music.mode`, `music.meter`, `music.bpm` → `metadata` fields.
- `voices.S1V1` → `bar.melody` (one entry per bar derived from S1V1 events).
- `harmony_regions` → `bar.chord` or `bar.bichord`.
- `harp_chord_assignments[*].lh_fig` / `rh_fig` → `bar.shape` / `bar.bishape`.
- `harp_chord_assignments[*].harmonic_substitution` → `bar.technique`.
- `phrases[*].bars` → `phrase.ibar` list.
- `lyrics.verses[*].syllables` → `verse.syllable` list.

### `hymnal_html/reharms/<Title>.json` → drill-adjacent subset
- `assignments[*]` → one bar's `(chord | bichord, shape | bishape, technique)` triple.
- `phrases[*]` → `phrase` with `cycle_color` derived from `path`.

### `data/trefoil/HarpTrefoil.json` → pool
- `paths.entries[*]` → the 42 trefoil-cycle voicings (each row carries `cycle` + `cw_label` / `ccw_label`). Together these walk the six cycles.
- `reserve.entries[*]` → the 76 coloristic reserve voicings (each row carries `mood`).
- `patterns[*]` → `intervals` productions (14 total); `chords_by_pattern_and_degree` is the pedagogy cross-reference table, not the pool itself.
- Each pool entry is loaded as a typed `Bishape` by `trefoil.pool.load_pool()` and assigned an ipool `{degree}{rank:02d}` — first digit from the LH scale-degree, last two digits rank-within-degree (paths first, then reserve).

### Reference conventions
- File slugs lowercase, collapse non-alnum runs to `_` (matches `tools/build_review_html.py::hymn_slug`). This is the slug used by `HarpHymnal.html`'s fetch-HEAD nav swap.
- `hymnal_export/*.json` filenames use per-character underscore. `hymnal_html/reharms/*.json` filenames use collapsed underscore. Batch scripts must match by canonical slug, not filename.

---

## 7. Drill workflow

For each technique × path, produce a drill page.

1. Pick a technique (e.g. Third sub) and a path (e.g. 4ths CW).
2. Derive `steps`. Each step's braces are named chord nonterminals (`I`, `iii`, `vi`).
3. Expand each nonterminal to its ipool set — the fractions in the pool that realize that chord.
4. Render as an enumerated 2-column HTML table (step ABC + comment).
5. Optionally parameterize by `shape` to expose the 14-way fingering axis.

`drills/index.html` is the prototype. Remaining 17 techniques to follow the same shape.

---

## 8. Known constraints and deferred work

### Constraints (by design, not bugs)
- **Strictly diatonic** — no chromatic chords in the vocabulary. Chromatic needs resolve by substitution, not vocabulary expansion.
- **Lever-harp default** — levers are set at tuning and don't change mid-piece. `pedals` and `pedal_change` apply only if a pedal harp is the target instrument.
- **One key per piece** — modulation isn't expressible. Project is a 118-chord diatonic dataset.
- **LH never shifts into treble** — pedal unison with LH bottom is accepted as an idiomatic grace-note re-strike.

### Deferred (layer in when consumed)
- Formal `duration` production (currently prose placeholder).
- Repeat markers / first-and-second endings.
- Author / composer metadata beyond `title`.
- Fingering marks at the string level (harp fingering is implicit in `shape`).
- Drills for the other 17 techniques.
- Pool coverage analysis (which ipools are unreachable by any drill).
- `instance` production is declared but not referenced by other productions — kept as a descriptive type only.

### Known issues
- `every_morning_mercies_new` fails LilyPond compile with `KeyError 'G'` — bad figure in the vocab (log in `ISSUES.md`).
- Some hymnal titles have inconsistent filename slugification between `hymnal_export/` (per-char underscore) and `hymnal_html/reharms/` (collapsed underscore). Batch scripts must match by canonical slug.
