# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## STOP — read these first

1. **`SDD.md`** — software design document: pipeline, grammar v4, directory layout.
2. **`GRAMMAR.md`** — authoritative EBNF v4. Every script parses through `grammar/` primitives.
3. **`ROADMAP.md`** — living plan (formerly `PLAN.md`).
4. **`ISSUES.md`** — known bugs, bad-sounding moments, Trefoil vocabulary gaps.
5. **`TREFOIL.md`** — pedagogy of the 118-fraction vocabulary (formerly `HARP_CHORD_SYSTEM.md`).

**File precedence when docs disagree:**
`source/HarpChordSystem.tex` > `source/HarpTrefoil.tex` (byte-mirror) > `TREFOIL.md` > derived `data/trefoil/HarpTrefoil.json`

`source/HarpChordSystem.tex` is the canonical pedagogy — never modify. `source/HarpTrefoil.tex` is the new-brand byte-exact mirror; `tests/test_pool_fidelity.py` rejects drift. Derived JSON/PDF live under `data/trefoil/` and are rebuilt by `trefoil/rebuild.py`.

## Directory layout (new)

```
source/        READ-ONLY canonical inputs (HarpChordSystem.tex, HarpTrefoil.tex, OpenHymnal.abc)
grammar/       @dataclass types, parse/, emit/, validate/ — heart of the refactor
trefoil/       the 118-fraction pool + 6 trefoil paths
techniques/    18 pure-function operators (substitution/approach/voicing/placement)
parsers/       ABC/... → grammar objects
renderers/     grammar objects → LilyPond/LaTeX/HTML/ABC
mapper/        RN + key + melody → best fraction
reharm/        apply techniques to hymns
drills/        generate drill pages procedurally
cli/           command-line entry points (python -m cli.<name>)
data/          generated artifacts (hymns/, reharms/, scores/, drills/, trefoil/)
viewer/        web front-end
tests/         pytest
legacy/        old code and data, frozen — nothing new imports from here
```

Nothing in `legacy/` is ever modified; new scripts never import from `legacy.*`.

## Project purpose

HarpHymnal is a **data-pipeline project**, not an application. It turns one large ABC source file (`OpenHymnal.abc`, 370 hymns) into 294 self-contained JSON records (`hymnal_export/*.json`) that carry enough structural information to rebuild grand-staff / SSAATTBB / organ-pedal / lead-sheet renderings downstream. There is no server, test suite, or build system — just a small set of Python scripts run from the command line.

## Dependencies

Only one: `music21`. Install once with:

```bash
pip install music21 --break-system-packages
```

## Commands

All scripts live in `tools/` and have hard-coded default paths `/mnt/project/OpenHymnal.abc` and `/mnt/project/HarpChordSystem.json` (an artifact of the environment they were originally authored in). From this repo you must pass `--hymnal` and `--vocab` explicitly, or run from a working dir where those paths resolve.

```bash
# Export a single hymn (title is a substring match)
python3 tools/export_hymn.py "Amazing Grace" \
    --hymnal OpenHymnal.abc --vocab HarpChordSystem.json \
    -o hymnal_export/Amazing_Grace.json

# Re-export the full corpus (~5 min)
python3 tools/export_hymn.py --all \
    --hymnal OpenHymnal.abc --vocab HarpChordSystem.json \
    -o hymnal_export/

# Inspect the parser's intermediate output for one hymn
python3 tools/hymn_parser.py "Joy to the World" --hymnal OpenHymnal.abc

# Query the chord mapper directly (RN, key, optional melody note)
python3 tools/harp_mapper.py V7 D G4 --vocab HarpChordSystem.json

# Convert a comprehensive export JSON to a lead-sheet-ready "reharm" JSON
python3 tools/export_to_reharm.py hymnal_export/Silent_Night.json -o reharm/Silent_Night.json
python3 tools/export_to_reharm.py --all hymnal_export/ --out-dir reharm/

# Render a reharm JSON into a LaTeX lead sheet (consumed by HymnReharmTemplate.tex)
python3 tools/fill_template.py reharm/Silent_Night.json -o Silent_Night.tex
```

There are no linters, tests, or CI. "Does it work" means: the script runs, and the JSON it produces round-trips cleanly through the next stage of the pipeline.

## Pipeline architecture

The stages are **strictly linear** — each consumes the previous stage's output. Understanding this ordering is the key to working in this repo:

```
OpenHymnal.abc                            (ground-truth source)
    │
    ▼   hymn_parser.py
parsed voices + SATB beats + RN regions + phrases   (in-memory only; CLI prints it)
    │
    ▼   export_hymn.py  (calls hymn_parser internally + harp_mapper)
hymnal_export/<Title>.json                (comprehensive machine record — THE dataset)
    │
    ▼   export_to_reharm.py
reharm JSON                               (lead-sheet view: one chord/bar, phrase letters, LaTeX-escaped)
    │
    ▼   fill_template.py  (+ HymnReharmTemplate.tex)
LaTeX → PDF lead sheet                    (see samples/*.pdf for output examples)
```

`harp_mapper.py` is a pure library used by `export_hymn.py` during stage 2, and also exposed as a CLI for manual lookups. It does not read or write files of its own.

### What each stage is responsible for

- **`hymn_parser.py`** — ABC text in, structured music data out. It handles three ABC voice-layout conventions (see README for the full list, including `[V: S1V1..S2V2]` explicit SATB, 2-staff piano reduction with packed chords like `[Ac]`, and 3-staff arrangements with organ pedal). It also re-derives `!fermata!` positions by scanning the raw ABC text because music21's ABC parser silently drops fermata decorations. Tonic detection is weighted voting across six signals (bass-first/last, melody-first/last, common-bass-pc, header); header wins ties.

- **`harp_mapper.py`** — given a roman numeral + key + (optional) melody note, score the 118-chord Harp Chord System vocabulary and return the best LH/RH fraction. The vocabulary is **strictly diatonic by design** — no tritone subs, no ♭II7, no altered dominants, no harmonic-minor V. For minor-key hymns, RNs are translated to the relative major because the 118 vocabulary entries are Ionian-labeled. The mapper is **cycle-aware**: it detects 2nds/3rds/4ths cycle transitions between adjacent RNs and picks `jazz_progressions` entries with CW/CCW direction inferred from melodic contour (ascending → CW, descending → CCW). Harmonic-minor V is handled by one of four substitution strategies (`bVII_backdoor` / `III_deceptive` / `pedal_i` / `modal_v`) and the chosen strategy is recorded on the assignment as `harmonic_substitution`, with the original RN preserved as `requested_rn`.

- **`export_hymn.py`** — the integrator. Produces one JSON per hymn containing: raw ABC source verbatim, metadata, music/key/meter, per-voice note streams, SATB beat grid, bar-level / half-bar / smoothed harmony regions, phrase boundaries, syllable-aligned lyrics per verse, and harp chord assignments with alternates. This JSON is **the** dataset — everything downstream should read it rather than re-parsing ABC.

- **`export_to_reharm.py`** — downsamples the comprehensive JSON into a lead-sheet view. Collapses to one chord per bar, assigns phrase letters (A, B, C...), inherits a cycle color per phrase, infers a strategy hint, splits verse text into per-phrase chunks, and crucially **LaTeX-escapes every user-visible string** (titles, lyrics, metadata — see the `LATEX_ESCAPES` + `UNICODE_MAP` tables at the top of the file; any new user-visible field added downstream must pass through them).

- **`fill_template.py`** — emits LaTeX built around `HymnReharmTemplate.tex`'s `\rn{root}{quality}` macro. Translating mapper output (e.g. `"iii¹"`, `"IV²+8"`) into quality codes the macro's switch table understands is the main complexity here; see the comment at the top of the file for the exact mapping.

## JSON schema

The full comprehensive-export schema is documented in `README.md` and reproduced in the header docstring of `tools/export_hymn.py`. Before modifying it, read the README section "JSON schema per hymn" — downstream consumers (`export_to_reharm.py`, any future renderer) depend on these exact field names, and several fields carry non-obvious invariants:

- `voices.S1V1` / `S1V2` use the **top pitch** of any chord; `S2V1` / `S2V2` use the **bottom pitch**; `pitches_all` carries all pitches so SSAATTBB splitters can redistribute later.
- `extra_voices.S3V2` / `S3V3` is present only for 3-staff arrangements (preserved for future organ-pedal rendering — don't drop it).
- `modal_name` is authoritative for mode-aware rendering (accidentals, key sig). `mode` is only "major" or "minor". Consumers should prefer `modal_name`.
- `lyrics.verses[*].syllables` is exactly `len(Note+Chord events in S1V1)` — rests are excluded, melismas produce entries with empty text and `continues_previous=true`.
- Shared refrains: when an ABC line-group has only one `w:` line while others have several, that single line is broadcast across all verses.
- Each `harp_chord_assignments` entry carries `harmonic_substitution` (nullable) and `requested_rn` so downstream renderers can annotate substitutions.

## Known limitations to respect

These are deliberate design choices, not bugs — do not "fix" them without understanding the tradeoff (all documented in more detail in README):

- **Harmonic-minor V can't live in the 118-chord vocabulary** — it requires a chromatic leading tone. The mapper falls back to one of four substitution strategies; this is by design.
- **Regions on dense chorales can be noisy** — music21 labels passing chords as things like `#IVø7` or `V42`. The per-bar downsampling uses a downbeat-weighted vote but some residue is expected.
- **Phrase detection**: fermatas preferred (~16% of corpus), cadence-based fallback (~84%). Hymns with neither may degrade to one-phrase-per-4-bars.

## Corpus regeneration

`hymnal_export/` is checked in. Don't regenerate it casually — a full `--all` run takes ~5 minutes and will touch 294 files. Prefer exporting single titles for iteration, and only run `--all` when a genuinely cross-corpus change (schema addition, new analytical field, parser bug fix affecting many hymns) is ready to land.

## Housekeeping notes

- `tools/export_to_reharm.py` and `samples/export_to_reharm.py` are duplicates (identical size and purpose). The `tools/` copy is the canonical one; the `samples/` copy appears to be a snapshot and should not be edited.
- `samples/` holds reference PDFs (output examples) plus a `files (1).zip` archive — treat as read-only artifacts, not source.
