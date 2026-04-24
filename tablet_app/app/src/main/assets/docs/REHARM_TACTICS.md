# Reharm Tactics

Living reference for the Reharm Tactics subproject of HarpHymnal. Source of
truth for *intent, rationale, biases, open questions*. The machine-readable
tactic pool lives in `data/reharm/tactics.json`; the web view is generated
from both by `trefoil/build_reharm_tactics.py`.

> **Precedence when docs disagree:** this file > `data/reharm/tactics.json` >
> generated HTML. Hand-edit either file; regenerate HTML. Never hand-edit HTML.

## Goal

A Python tool that models a diatonic jazz harpist preparing Sunday prelude
improvisations on a **47-string lever harp**. Not a real-time performer —
a **practice-week exploration assistant**. Across the week, it generates MIDI
+ score candidates exploring different treatments. The harpist auditions,
curates, and drills favorite fragments. On Sunday, the harpist improvises by
recombining drilled fragments in real time.

## Existing assets (as of first pass)

- 240 hymns in ABC-SATB notation with verses and identified chord symbols
- `trefoil/pretty_fraction.py` — scoring + generation, **29-string C-major**
  (STRING_MIN=1 at C2, STRING_MAX=29 at C6) — needs 47-string extension
- `trefoil/sabt2jazz.py` — per-bar converter with 4 harvested techniques
  (`third_sub`, `quality_sub`, `deceptive_sub`, `common_tone_pivot`)
- `data/jazz/*.json` — 279 per-hymn outputs (spec, lh, rh, technique, score)
- `trefoil/pedal.py` — pedal state + braille (built for SATB; diatonic jazz
  barely touches it)
- `legacy/hymnal_export/*.json` — per-beat S/A/T/B data
- `data/trefoil/HarpTrefoil.json` — 42 path + 76 reserve shapes with
  mood / cycle metadata

## Physical constraints

- 47 strings, diatonic, lever-operated (levers raise a string by a semitone)
- Player has 8 fingers (4 per hand, no pinkies)
- Each hand spans **≤ 10 strings** (≈ a diatonic 10th)
- Lever flips during performance are expensive: occasional single-bar
  flip-and-flip-back is acceptable, sustained flips across a section are fine,
  frequent flipping is not
- Shapes are **pre-curated**; the tool selects from them, it does not invent
- String damping and sympathetic ringing matter to texture

## Workflow

1. **Monday:** hymns arrive. Tool generates a breadth of candidates per hymn.
2. **Across the week:** harpist auditions MIDI + score, marks favorites.
3. **Curate:** favorite fragments are cut and indexed into a drill catalog.
4. **Practice:** drill fragments; build a reach-graph so transitions between
   fragments are known-playable.
5. **Sunday:** improvise by recombining drilled fragments in real time.

## Two structural biases the selector must respect

1. **Density axis.** SATB attacks 4 notes per beat in the middle register.
   Jazz harp wants density 1–4 per beat, **weighted toward 1–2**, with 3–4
   reserved for arrivals (phrase-end, cadence, climax).
2. **Vertical spread axis.** SATB spans ~2 octaves. Jazz harp wants
   **3–5 octaves** most of the time, exploiting the full 47-string range.

The selector should be biased *against* tactic combinations that cluster in the
**SATB zone**: high density + narrow spread + middle register + on-the-beat
block attacks. This isn't a hard ban; it's a *penalty* — deliberate, rare use
is fine.

## Tactic pool (12 dimensions)

The structured pool lives in `data/reharm/tactics.json`. Each tactic has an id
of the form `<dimension>.<name>`, a human-readable label, a free-form tag
list, and an optional `conflicts` list of tactic ids it can't co-occur with.

The twelve dimensions:

| dimension | axis of decision |
|---|---|
| `shape` | which voicing is struck under the melody note |
| `register` | which octave band the shape sits in |
| `lh_activity` | what the non-melody hand does rhythmically |
| `rh_activity` | what the melody hand does beyond the melody note |
| `connect_from` | how this measure relates to the previous |
| `connect_to` | how this measure prepares the next |
| `substitution` | harmonic substitution at measure scale |
| `density` | number and placement of attacks in the measure |
| `texture` | attack-timing relationship between hands |
| `lever` | lever state plan within the measure |
| `range` | horizontal motion across the 47 strings |
| `phrase_role` | *(new)* measure's role in its phrase (opening, middle, cadence approach, cadence, release) — added to address the phrase-scale gap in the first pass |

See `data/reharm/tactics.json` for the current catalog; see the web view at
`jazz/reharm_tactics.html` for a browsable rendering.

## Lever vs lever state

For a diatonic lever harp, the default is "tune once, play through." The
`lever` dimension covers performance-time flips: when to flip a lever to
reach a chromatic passing tone, when to hold a flipped state, when to
pre-flip ahead of the next measure. `trefoil/pedal.py` already models state
updates at beat-level granularity from SATB accidentals; the lever tactics
here are the *jazz-side* decisions about when to bring chromaticism in.

## Compatibility model

Not every combination of the 12 dimensions is legal.

- **Hard conflicts** — tactic pair that can't be rendered. E.g. `lh.no_lh` ∧
  `lh.bass_chord_chord`. These are edges in the `conflicts` graph in
  `tactics.json`.
- **Soft conflicts** — physically playable but musically self-defeating.
  Primarily: the **SATB zone** (see biases above). These get penalty weight,
  not a ban.
- **Derived labels vs chosen levers.** Some tactics are *decisions* the
  selector makes (shape, substitution, density); others are *labels* that
  fall out of the choice (e.g. "single-line only" is forced when lh is silent
  and rh plays just the melody). The pool must distinguish so we don't
  double-count in coverage metrics.
- **Natural pick order.** `substitution` → `shape` → `register` → `density` →
  `texture` → `lh_activity` + `rh_activity` → `connect_from` / `connect_to` →
  `lever`. Each layer narrows the legal options for the next.

## Decisions (resolved scope flags)

1. **Shape library — resolved 2026-04-21.** Optimize for **47-string**. Extend
   `pretty_fraction.py` (not a hand-curated separate set). Constants: C1..G7,
   STRING_MIN=1 at C1, STRING_MAX=47 at G7, seven octaves. Each hand still
   bounded to ≤10 strings, but the **gap between LH top and RH bottom is
   flexible** — the selector chooses wide or narrow gap per register/voicing
   goal rather than being penalized toward a fixed target.
2. **v1 activity / texture tactics — resolved 2026-04-21.** Full pool is
   selectable. Don't lock in a walking-skeleton subset; build the foundation
   so any tactic can be picked, then let empirical use narrow what gets used
   in practice. Every tactic in `tactics.json` must be renderable by the v1
   MIDI + score pipeline.
3. **Fragment length — resolved 2026-04-21.** Use the **phrase boundaries
   already computed** by the parser (`data/hymns/<slug>.json → phrases[]`).
   Fragments are phrase-aligned; no fixed 2-bar or variable-length policy.
4. **Shape count — resolved 2026-04-21 (implied).** The "300+" figure in the
   original brief stands as an *output expectation* of the 47-string extension
   of `pretty_fraction` — across all qualities × registers, the generator
   will produce that many candidate shapes. The existing 29-string C-major
   output (~91) is the lower bound. (Phase 3 produced 1680.)
6. **Phrase-role inference — resolved 2026-04-21.** Hybrid rule for labeling
   each bar with its `phrase_role` tactic:

   *Step 1 — positional default.* For a phrase of N bars:
   - bar 1 → `opening`
   - bar N → `cadence`
   - bar N-1 → `cadence_approach` (when N ≥ 3)
   - bar N+1 (first bar of next phrase, if it feels like a breath) → `release`
   - all others → `middle`

   *Step 2 — chord-motion override.* Walk the bar-level chord sequence within
   the phrase. A bar is marked `cadence` when its chord is the target of a
   recognizable motion from the prior bar:
   - `V → I` (authentic)
   - `V → vi` (deceptive)
   - `IV → I` (plagal)
   - `anything → V` at phrase end (half cadence)
   The predecessor becomes `cadence_approach`. Any bar immediately after a
   detected cadence becomes `release`.

   *Step 3 — conflict resolution.* When positional and motion-based labels
   disagree, **motion wins** for the specific bar where motion fires
   cleanly; **positional wins** on ambiguity (e.g., motion reads V→V as
   half-cadence but phrase has 16 bars left; keep positional `middle`).

5. **Minor-key hymns — resolved 2026-04-21.** Treat minor hymns **modally**,
   not with harmonic-minor. Default mode = **Aeolian** (natural minor, minor
   v chord, no raised 7). Optional per-hymn override to **Dorian** when the
   tune uses a prominent raised 6. Lever state is set once at piece start to
   match the mode's key signature; **no lever flips during play**.

   Implementation: *no shape-library expansion needed*. Aeolian and Dorian
   share the Ionian diatonic collection (relative modes). A minor-hymn chord
   roman translates to its Ionian-relative roman via a lookup table and
   queries the existing shape library:

   | Aeolian | Ionian-rel. | Dorian | Ionian-rel. |
   |---|---|---|---|
   | `i`   | `vi`  | `i`   | `ii`  |
   | `ii°` | `vii°`| `ii`  | `iii` |
   | `III` | `I`   | `♭III`| `IV`  |
   | `iv`  | `ii`  | `IV`  | `V`   |
   | `v`   | `iii` | `v`   | `vi`  |
   | `♭VI` | `IV`  | `vi°` | `vii°`|
   | `♭VII`| `V`   | `♭VII`| `I`   |

   The old mapper's harmonic-minor substitutions (`bVII_backdoor`,
   `III_deceptive`, `pedal_i`, `modal_v`) are **dropped** from the new
   selector — modal `v` fills that role directly.

   Per-hymn Dorian overrides live in `data/reharm/mode_overrides.json`
   (empty by default; populated by hand as the harpist's ear decides).

   All 279 hymns in scope for v1.

## Open questions
5. **Verse differentiation.** Hymns have 4+ verses. Does the candidate
   generator treat each verse identically, or vary (register shift, texture
   shift, intensification)? Not in the current 12-dimension pool.
6. **Intro / outro.** The prelude is more than the hymn proper. Are
   intros/outros separate artifacts, or added as `phrase_role` values?
7. **Quotation / allusion.** A tactic slot for brief reference to a related
   tune or a prior hymn in the same service. In or out of scope?
8. **Session-level memory.** If Sunday plays 3 preludes, should tactics
   deliberately vary across them? Needs a session-scope layer above per-hymn.
9. **Liturgical mood.** Lent/Advent restrained; Easter celebratory. A
   session-level mood parameter that skews tactic weights.
10. **Per-hymn deny-list.** Certain hymns' texts preclude certain treatments
    (e.g. no bisbigliando through *Were You There*). Add as a small
    `data/reharm/deny/<slug>.json` or a section in the hymn JSON.

## Evaluation criteria

A good practice-week output satisfies:

- **Legality.** Every candidate is physically playable — no impossible
  stretches, no same-pedal flip inside a sub-beat window, no simultaneous
  two-hand overlap on the same string.
- **Coverage.** Each tactic is exercised across the week's candidates;
  underexplored cells rise in priority next round.
- **Variety.** No two candidates for the same hymn are near-duplicates in
  tactic manifest; within a hymn, no single candidate collapses to one tactic.
- **Bias satisfaction.** Per-measure density and spread distributions match
  the stated targets *at the phrase level*, not just in aggregate.
- **Reachability.** Drilled fragments connect in the reach-graph with enough
  density that Sunday recombination has options.
- **Feedback.** Harpist-marked favorites feed a weighting term for next week.

## Process

Workflow for updating tactics or constraints:

1. Edit the prose in this file for intent / rationale changes.
2. Edit `data/reharm/tactics.json` when adding / removing / modifying tactic
   records or compatibility rules.
3. Regenerate the web view: `python3 trefoil/build_reharm_tactics.py`.
4. Commit all three (MD, JSON, HTML) together so they never drift.

A tactic that doesn't survive contact with real hymn data gets either
redefined, flagged `rare`, or removed — with the reason recorded in its
record's `note` field.

## Phase plan (status as of 2026-04-21)

| # | phase | status |
|---|---|---|
| 1 | Authoring infrastructure (MD + JSON + HTML) | ✅ done |
| 2 | Tactic pool as data (schema.py, 79 tactics, symmetric conflicts) | ✅ done |
| 3 | Shape library — initial (1680 shapes, I/ii/…/vii° × null/Δ/7) | ✅ done |
| 3.5 | Shape library — color extensions (6893 shapes, sus/quartal/add9/11/13, shell_37) | ✅ done |
| 4 | Selector + state (40 variations × 3 sample hymns, 11/11 tests) | ✅ done |
| 5 | Legality + scoring (4 bias scores, warnings, CLI summary) | ✅ done |
| 6 | Comparison table jazz column + bulk variations (279 × 40 = 11,160) | ✅ done |
| 7 | MIDI + LilyPond rendering (11,160 `.mid` + `.ly`) | ✅ done |
| 8 | Weekly artifacts (fragment cut, catalog, tablet UI) | ✅ done |

Total tests across all phases: 59/59 (schema 14 · shape_gen 19 · selector 11 · legality 5 · render 4 · catalog 6).

**Corpus artifacts as of 2026-04-21:**
- 11,160 variation manifests (279 hymns × 40)
- 11,160 MIDI files + 11,160 LilyPond sources (102 MB)
- 57,280 phrase-aligned fragments (608 MB)
- 1 corpus catalog (`data/reharm/catalog.json`, 19.5 MB)
- Tablet-app entry: `jazz/reharm_home.html` (accessed via the gold "Reharm Tactics" tile on the home page)

**Deferred from Phase 8 (explicitly not in v1):**
- Reach graph (fragment-to-fragment transitions)
- Favorites / feedback loop
- Browser-native MIDI playback (file links only for now)
