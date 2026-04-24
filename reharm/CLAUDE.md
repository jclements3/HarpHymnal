# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Reharm** is the companion project to **Retab**. Where Retab changes the
*texture* of an SATB hymn (re-tabulating it as idiomatic harp composition),
Reharm changes the *harmony* — substituting diatonic jazz-idiomatic chords
under the same melody, still playable on a 47-string lever harp.

Reharm is a **new** project. An earlier attempt at reharm lived in
`../HarpHymnal/reharm/`, `../HarpHymnal/trefoil/reharm/`, and
`../HarpHymnal/data/reharm/` — it sprawled across schema/selector/renderer
modules before nailing the product. This rewrite applies the tactics that
made Retab land:

1. **A clear 7-level ladder** (see `REHARM.md`) so each increment is legible.
   The axis is *technique sophistication within the diatonic collection* —
   NOT distance-from-original-key. Every level stays in the hymn's key
   signature.
2. **A strictly limited chord pool** (14 chord symbols total: 7 diatonic
   triads + 7 diatonic 7ths) enumerated in code. Non-diatonic chords
   would require lever flips and are forbidden.
3. **Single-file emitter + single bulk builder**, matching Retab's shape.
4. **End-to-end deliverable each level** — every level produces compilable
   ABC that renders on the tablet, not just intermediate structures.

## The instrument

Same target as Retab: 47-string lever harp. All the Retab harp-idiom rules
apply here unchanged:

- **No piano stomping** — never re-strike the same triad on consecutive
  beats. Let strings ring, or walk through chord tones.
- **C1–B1 is drumming range** — low-bass anchor tones go there only on
  opening + cadence; everywhere else the triad base is octave 2.
- **Zero lever flips.** Hard constraint. Every pitch emitted at every
  level is diatonic to the hymn's key. No secondary dominants, no modal
  interchange, no distant-key modulation, no tritone subs. Anything
  requiring an accidental is a bug. This is the central narrowing that
  distinguishes Reharm's ladder from textbook jazz-reharm pedagogy.

## Project layout

- `REHARM.md` — the 7-level ladder (axis: distance from vocal harmony
  toward idiomatic diatonic-jazz reharm). This is the steering document.
- `HANDOFF.md` — cross-machine sync for when this project is worked on
  from multiple machines.
- `hymnal/reharm_hymnal.py` — the emitter. Reads a HarpHymnal-style hymn
  JSON and emits grand-staff ABC. Takes a `--level` 1–7.
- `hymnal/build_hymnal.py` — bulk builder. Iterates `data/hymns/*.json`
  from the HarpHymnal data tree, runs the emitter, invokes `abcm2ps -g`,
  installs SVGs to the tablet app under `assets/reharm/`.

## Data

Hymn source: `../HarpHymnal/data/hymns/*.json` (279 hymns, same format
Retab consumes). Each file has:

- `title`, `slug`
- `key.root`, `key.mode` (major/minor)
- `meter.beats`, `meter.unit`
- `bars[].chord = {numeral, quality, inversion}` — the seed harmony
- `bars[].melody[]` — pitch + duration events
- `phrases[].ibars` — phrase bar ranges (for opening/middle/cadence roles)

## Build

No project-local build system. Run the emitter on a single hymn:

```
python hymnal/reharm_hymnal.py --level 2 \
    ../HarpHymnal/data/hymns/abide_with_me.json -o /tmp/abide.abc
abcm2ps /tmp/abide.abc -O /tmp/abide -g
```

Bulk build all 279 hymns at a given level (the builder does `from
reharm_hymnal import ...` as a sibling import, so run it from `hymnal/`):

```
cd hymnal && python build_hymnal.py --level 2
```

Output lands in `hymnal/build/L<level>/` by default; `-o` overrides.
Requires `abcm2ps` on PATH (same dependency as Retab).

## Current implementation state

Only **L1** is implemented (`apply_level_1` — strips chord quality to emit
plain diatonic triads). `apply_level_2` through `apply_level_7` raise
`NotImplementedError`, so bulk builds at L2+ will fail every hymn until
each level is filled in. Next level to implement is L2 (pool expansion
only, no root motion).

## Architecture

The emitter is a **pipeline of level passes** over `hymn["bars"][i]["chord"]`:

1. `REHARM_LEVELS[N]` picks the pass for `--level N` and transforms the
   hymn's chord dicts in place (on a deep copy).
2. `build_abc` validates every resulting chord against `CHORD_POOL` via
   `validate_chord_pool` before rendering. The pool contains exactly 14
   entries (7 diatonic triads + 7 diatonic 7ths). A chord outside the
   pool is a hard failure — this is the flip-free guardrail.
3. `lh_pattern` renders each chord into bass-clef ABC using the harp
   voicing rules (walk through tones mid-phrase, single strike + ring at
   openings and cadences).

Levels are **not strictly additive.** L1–L3 share the pool-substitution
shape and compose cleanly. L4 (relative-minor reharm) and L5 (modal
reharm) re-centre whole phrases and replace the lower passes for those
phrases rather than layering on. L6 (non-functional + slash chords) and
L7 (voice-leading-first) are whole-hymn aesthetics that replace the
chord-choice logic entirely.

### Minor-mode handling

Hymn JSONs in minor keys carry Aeolian-mode numerals (`i`, `iv`, `V`,
`bVII`). The emitter translates these to relative-major Ionian numerals
via `AEOLIAN_TO_IONIAN` at validation- and render-time, then emits in
the relative major key (`relative_major(key_root, mode)`). The chord
pool is expressed in Ionian labels only — don't add minor-mode entries.

## Relationship to Retab

Retab is a sibling project (`../retab/`). Reharm *reuses* Retab's melody
rendering, pitch-to-ABC conversion, and LH-walking rhythm logic — those
are generic harp-idiom building blocks. The reharm-specific novelty is in
the **chord-substitution pipeline** that sits between the hymn's written
chord and the LH voicing.

For now the shared logic is **duplicated** into `reharm/hymnal/` rather
than imported from `../retab/`. Short-term duplication beats cross-project
imports while both codebases are still settling.

## Tablet integration

The HarpHymnal tablet app (`../HarpHymnal/tablet_app/`) has a **Reharm**
tile already wired (the old reharm tile — drill-oriented). A new
**Reharm Hymnal** tile (mirroring the existing Retab Hymnal tile) is the
intended end-state once the emitter reaches L4+. For now, do not wire the
tablet app until the level being produced is worth browsing.

## 7-bit ASCII in code

Keep Python source 7-bit ASCII. Unicode is fine inside generated ABC
strings (superscripts, Δ, ø, °) because abcm2ps renders them, but the
source files themselves should stay ASCII to match the project-family
convention.
