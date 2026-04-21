# PROMPT.md — lab-Claude handoff (tablet deployment pass)

State is on `origin/main` at the commit pushed alongside this file. The
**Reharm Tactics subproject is complete** (8 phases + 3.5 shape-library
extension + snippet A/B + 0-5 scoring UI). The user took the first round
of single-tactic surveys on Amazing Grace from the web UI served locally
via `python3 -m http.server`.

**Your job this pass: get the single-tactic audition rig onto the tablet
so the user can take surveys offline and generate the data-collection
JSON that drives drill mode and generator bug fixes.**

---

## Read these first (unchanged from prior handoffs)

1. `CLAUDE.md` — memory hooks, file-precedence rules
2. `REHARM_TACTICS.md` — the subproject's canonical design (12 tactic
   dimensions, 4 biases, 8 phases marked done; decisions on modal minor,
   phrase-role inference, coverage-vs-bias picks)
3. `TREFOIL.md` — 118-fraction pedagogy (corrected this pass: 118
   distinct fingerings, not 109; inversion-encoding parser contract)
4. `SDD.md` + `GRAMMAR.md` + `ROADMAP.md` + `ISSUES.md` — broader project
5. `trefoil/parse_roman.py` — canonical inversion-aware parser for
   `HarpTrefoil.json` / `HarpChordSystem.json` roman-numeral strings

Memory bootstrap: if `~/.claude/projects/-home-clementsj-projects-HarpHymnal/memory/`
doesn't exist, bootstrap the same way prior PROMPT.md versions did.
Preserved user preferences worth respecting:
- Commit + push per logical chunk (user follows from the tablet).
- Parallelize by hymn via `multiprocessing.Pool` — abundant CPU + storage.
- Never reintroduce Magenta's `html-midi-player`; use strict-GM stack
  (`midi-player-js` + `soundfont-player` + MusyngKite orchestral_harp).

---

## What shipped this session

### Reharm Tactics — complete subproject

Design: `REHARM_TACTICS.md` (repo root). Spec: `data/reharm/tactics.json`
(79 tactics × 12 dimensions + 4 biases + symmetric `conflicts`/`requires`
edges). Modal-minor: Aeolian default, per-hymn Dorian override via
`data/reharm/mode_overrides.json`, no lever flips during minor hymns.

Python (`trefoil/reharm/`):
- `schema.py`, `shape_gen.py` (6893-shape 47-string library),
  `selector.py` (40 variations/hymn, coverage-targeted, seeded),
  `state.py`, `legality.py`, `render_midi.py` (stdlib SMF writer,
  **program 46** Orchestral Harp — 47 is Timpani, don't flip),
  `render_lily.py`, `satb_baseline.py` (voices-driven, real rhythm),
  `solo_tactic_demo.py` (snippet mode with `snippet_radius`),
  `fragment_cut.py`, `catalog.py`.
- CLI: `cli/reharm_render.py`, `reharm_cut.py`, `reharm_solo.py`,
  `reharm_legality.py`. All parallelize by hymn; incremental via
  `tactics_hash` stamp.
- Tests: 59/59 pass across 6 suites. Stdlib only, no new pip deps.

Rebuild from zero:
```
python3 -m trefoil.reharm.selector --all
python3 -m cli.reharm_render --all
python3 -m cli.reharm_cut --all
python3 trefoil/build_variations_pages.py
python3 -m cli.reharm_solo --hymn amazing_grace --all
```

Bulk artifacts gitignored (rebuildable): 11,160 variation JSONs, 11,160
MIDI + 11,160 LilyPond, 57,280 fragments, catalog (19.5 MB), shape
library (6.2 MB), per-hymn variation HTML pages.

### Web UI under `jazz/`

- `reharm_home.html` — Reharm Tactics entry page (recent pulldown +
  all-jazz-hymns link + tactic-browser + design-brief).
- `variations.html` + generated `variations.<slug>.html` (279) — per-hymn
  variation tree with inlined catalog + 40 JSONs. Strict-GM player.
- `variations_browser.html` — corpus-wide tactic filter.
- `test_amazing_grace.html` — **the priority tablet deliverable.** See
  dedicated section below.
- `compare/<slug>.html` (279), `drills/<slug>.html` (108),
  `reharm_tactics.html` — all static, all use the strict-GM stack when
  they play MIDI.

### Small corrections this pass

- `TREFOIL.md` — "109 unique fingerings (9 reserve duplicates)" →
  **"118 distinct fingerings — every `(LH-figure, RH-figure)` pair is
  unique."** Added a parser-contract block in the chord-notation
  section covering inversion encoding and the `Iii`/`Ii`/`Vii`
  short-prefix ambiguity. Added a sentence connecting the 39-pattern
  handout terrain table to the 14 working patterns.
- `trefoil/parse_roman.py` — **new** canonical parser. Validated against
  all 118 pool entries (118/118 consistent). Use this whenever parsing
  `lh_roman`/`rh_roman` strings.
- `data/trefoil/HarpTrefoil.json`, `source/HarpChordSystem.json`,
  `data/trefoil/page1_chords.json` — added `_schema_version_note` so
  consumers know what v1/v4/v5 represent.
- `harphymnal.txt` — transport archive for web-Claude review
  (gitignored; regenerate with the script in `~/.local/bin/ai-tar.py`
  against `/tmp/harphymnal/`).

---

## The tablet deployment task (priority one this pass)

**File: `jazz/test_amazing_grace.html`** — the single-tactic audition rig.

Flow:
1. ▶ A plays a 3-bar original snippet (baseline SATB).
2. ▶ B plays the same 3 bars with the tactic applied to the middle bar.
3. 0-5 rating buttons unlock after B plays. Meaning: `0` = wrong
   application (generator bug); `1` = applied but hurts; `2` = weak;
   `3` = fine; `4` = good; `5` = drill candidate.
4. Ratings persist in `localStorage` under
   `harphymnal.scores.amazing_grace.<tactic_id>`.
5. Summary bar shows live `rated N/79 · wrong(0) N · drill(4-5) N ·
   avg X.X`. Cards color-coded: red border = bug, amber = 1, neutral =
   2-3, green = 4-5.
6. **Export scores** button downloads `amazing_grace_scores.json`.
7. **Import scores** restores a previous session.

Dependencies:
- MIDI files at `data/reharm/tests/amazing_grace/` — 160 total:
  `_baseline.mid` + `_notes.json` + 79 × (`<dim>__<name>__original.mid`
  + `<dim>__<name>__tactic.mid`).
- JS CDN in the HTML head: `midi-player-js@2.0.16` +
  `soundfont-player@0.12.0`. Soundfont at
  `https://storage.googleapis.com/soundfont-player/soundfonts/MusyngKite`
  (`orchestral_harp` preset).

### What lab-Claude should do

1. **Check tablet connectivity.** If online-capable, the existing CDN
   setup works. Copy `jazz/test_amazing_grace.html` +
   `data/reharm/tests/amazing_grace/*.mid` + `_notes.json` to the
   tablet app's bundle. Include sibling pages if the tablet UI links to
   them (`jazz/index.html`, `reharm_home.html`).

2. **If tablet is offline-first** (likely, based on the existing
   audio-pipeline architecture): pre-render the 159 audition snippets
   to OGG with `fluidsynth /tmp/MuseScore_General.sf3` (the soundfont
   configured in prior handoffs for `cli/audio_build.py`). Add an
   `<audio>` tag fallback per rating card. Keep Web-Audio/midi-player-js
   as "online preference" with auto-detect. Storage cost: ~30 MB for
   159 × ~200 KB OGG files at 48 kbps mono — trivial.

3. **Export flow.** The user exports scores JSON from the tablet. Make
   sure the tablet's download mechanism puts the file somewhere the
   user can sync back to the lab machine (Syncthing, USB, or whatever
   the prior `data/audio/` flow uses).

4. **Optional — integrate into `tablet_app/` (Kotlin/Android)** rather
   than standalone web view. `tablet_app/build_drill_data.py` and
   `build_hymns_bundle.py` are the existing pipelines that pack data
   for the Android UI. Hook the 159 snippet MIDIs + the HTML into that
   bundle if `tablet_app/` is still the active deployment target.

### Things I'm unsure about (check with the user before committing)

- Whether the tablet app is still the Kotlin/Android `tablet_app/` or
  whether `jazz/*.html` served over HTTP *is* the tablet app now.
- Tablet's offline vs online state during survey use.
- Tablet's file-download mechanism for the scores export.

If in doubt, ship the pre-rendered-OGG path — it's lowest-risk.

---

## Data collection flow (end-to-end)

1. User takes survey on tablet → rates some/all 79 tactics.
2. User exports scores JSON; file reaches the lab machine (Syncthing/USB).
3. Lab machine drops the JSON at
   `data/reharm/tests/amazing_grace/scores_<timestamp>.json` (new
   directory fine; add to git to version the data).
4. Home-Claude (me) fixes generator bugs for score=0 tactics and
   regenerates those A/B pairs.
5. Home-Claude builds drill mode around score=4-5 tactics (Phase 5).
6. User takes further surveys as iterations land.

---

## Things NOT to touch

- `source/HarpChordSystem.tex` — byte-frozen, never modify.
- `legacy/` — frozen.
- `REHARM_TACTICS.md` **Decisions** block — settled user choices.
  Open-questions list at the bottom is fair game.
- Magenta's `html-midi-player` — confirmed broken on polyphonic MIDI.
  Keep `soundfont-player` + `midi-player-js`.
- `render_midi.py` program byte: **46** Orchestral Harp; 47 is Timpani.

---

## Startup sanity check

```
# Tests (all should pass)
python3 tests/test_reharm_schema.py
python3 tests/test_shape_gen.py
python3 tests/test_selector.py
python3 tests/test_legality.py
python3 tests/test_render.py
python3 tests/test_catalog.py

# Web UI smoke
python3 -m http.server 8000 &
# http://localhost:8000/jazz/test_amazing_grace.html — snippet A/B +
# rating interface; baseline should play as Orchestral Harp.
```

Ship the survey to the tablet, collect the data, send the JSON back.
