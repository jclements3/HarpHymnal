# Lab Claude Handoff — HarpHymnal Refactor

Continue the HarpHymnal refactor. State is on `origin/main` at commit **`b8ee165`**. Scaffold is done, all tests green. Read the docs, then execute the build order below. Commit + push after each numbered step.

---

## End goal

A tablet-friendly web app — the **Harp Trefoil** — that serves both **hymn piano scores** and **reharm drills** from one place. The user will load it on their tablet to practice drills and play through hymns.

---

## Read these first, in order

1. `SDD.md` — software design document (architecture, pipeline, directory layout)
2. `GRAMMAR.md` — authoritative EBNF v4
3. `ROADMAP.md` — living plan (formerly PLAN.md)
4. `TREFOIL.md` — 118-fraction pedagogy (the user has re-taught this across sessions; do **not** re-teach)
5. `CLAUDE.md` — memory hooks + file-precedence rules

Memory index: `/home/clementsj/.claude/projects/-home-clementsj-projects-HarpHymnal/memory/MEMORY.md` — read for the user's locked-in preferences.

---

## Hard constraints (non-negotiable)

- **`source/HarpChordSystem.tex` is sacred** — never modify. It is the canonical pedagogy.
- **`source/HarpTrefoil.tex` must stay byte-exact** to the above. `tests/test_pool_fidelity.py` rejects drift. Any pedagogy edit goes into `HarpChordSystem.tex` first, then `cp` to `HarpTrefoil.tex`.
- **`legacy/` is frozen** — never import from `legacy.*`. Everything under it is a reference monument, not a library.
- **Strictly diatonic** — use only the 118-fraction pool. No chromatic substitutes, no tritone subs, no modal interchange.

---

## What's already in place

- **Directory scaffold**: `grammar/`, `trefoil/`, `techniques/`, `parsers/`, `renderers/`, `mapper/`, `reharm/`, `drills/`, `cli/`, `data/`, `viewer/`, `tests/`, `legacy/`.
- **`grammar/types.py`** — `Roman`, `Shape`, `Bichord`, `Bishape`, `Bar`, `Song`, `Piece`, `Ornament`, `PedalState`, `Key`, `Meter`, `Tempo`.
- **`grammar/parse.py`** — `parse_roman()`, `parse_figure()`, `parse_shape()`.
- **`grammar/emit.py`** — `emit_roman()`, `emit_shape()`.
- **`tests/test_grammar.py`** — 16 round-trip tests, all green.
- **`tests/test_pool_fidelity.py`** — enforces the `HarpChordSystem.tex` ≡ `HarpTrefoil.tex` invariant.
- **`source/`** — canonical `HarpChordSystem.tex`, byte-exact `HarpTrefoil.tex` mirror, `OpenHymnal.abc`.
- **`legacy/`** — complete snapshot of everything pre-refactor (`tools/`, `hymnal_export/`, `hymnal_html/`, `samples/`, `drills/index.html`).

All other domain dirs are empty `__init__.py` stubs ready to fill.

---

## Build order

Each numbered step should be a separate commit + push.

1. **`trefoil/rebuild.py`** — port `legacy/tools/rebuild_chord_system_json.py` to read `source/HarpTrefoil.tex` and emit `data/trefoil/HarpTrefoil.json` using `grammar/types.py` (typed `Shape` / `Bishape` records, not loose dicts). Add tests verifying the rebuild matches the legacy JSON structurally.

2. **`trefoil/pool.py`** — load the JSON; expose `get(ipool)`, `all_voicings_of(chord)`, `ipool_of(shape)`. Assigns canonical `001..118` indices (walk patterns in list order, then degrees 1..7, numbering non-null entries).

3. **`parsers/abc.py`** — port `legacy/tools/hymn_parser.py` + `legacy/tools/export_hymn.py` to produce typed `Song` objects from `source/OpenHymnal.abc`. Write hymns to `data/hymns/*.json` (grammar-conformant JSON).

4. **`mapper/harp_mapper.py`** — port scoring logic from `legacy/tools/harp_mapper.py`; now returns `Shape` / `Bishape` grammar objects, not dicts. Use `trefoil/pool.py` as the vocabulary source.

5. **`techniques/substitution.py`**, then `approach.py`, `voicing.py`, `placement.py` — 18 pure functions, each `technique(bar) → bar'` or `(bars) → bars'`. See SDD §3.6 for the full list (Third sub, Quality sub, Modal reframing, Deceptive sub, Common-tone pivot; Step/Third/Dominant/Suspension/Double approach; Inversion, Density, Stacking, Pedal, Voice leading, Open/closed spread; Anticipation, Delay). Unit-test each.

6. **`drills/build.py`** — procedural `(technique, path) → Drill`. Walk chord nonterminals (I, ii, iii, IV, V, vi, vii○), expand each to its ipool brace (all voicings realizing that chord), emit drill steps. 18 techniques × 6 paths = 108 drill pages.

7. **`renderers/lilypond.py`** + port `legacy/tools/build_piano_score.py`. Re-emit the 293 working piano scores into `data/scores/<slug>.{ly,svg,pdf,midi}`. Preserve the LH style rules below.

8. **`renderers/html.py`** + **`viewer/index.html`** — tablet-friendly app:
   - Left nav: hymn list (scrollable) + drill list (grouped by technique).
   - Right pane: SVG score or drill table.
   - Mobile-responsive CSS (viewport meta, touch targets ≥ 44px, no hover-only interactions).
   - `fetch`-HEAD slug swap for score assets (pattern from `legacy/hymnal_html/HarpHymnal.html`).
   - Offline-capable if cheap (service worker caching of `data/`).

---

## Style rules the user has locked in — do not re-litigate

**Vocabulary** (single words, consistent):
- `shape`, `bishape`, `chord`, `bichord`, `ipool`, `ibar`, `inote`, `brace`, `step`, `drill`, `instance`.

**Rendering artifacts stay out of grammar**:
- `/` between chords (bichord), `|` between ipools (brace), pedal glyphs, cycle-colors — all these live only in `renderers/*`, never in `grammar/` or in the JSON data format.

**Piano score LH pattern** (3/4 and 4/4):
- Beat 1: block chord (quarter, arpeggiated, with pedal grace).
- Middle beats: eighth-note arpeggio of upper chord tones.
- Final beat: quarter-note pickup tone (upper diatonic neighbor of next chord root) or landing tone (current chord root).

**Pedal grace**:
- `base_octave=1`, `HARP_LOW_MIDI=31` (G1 floor). Places pedal in Bb1–F2 range — always below the bass staff.
- Never shift LH up an octave on pedal clash; accept unison as idiomatic grace-note re-strike.

**Phrase style dispatch**:
- First bar of piece, last bar of piece → `grand_chord` (full-bar block).
- Other phrase-ending bars → `cadence_arp` (chord + eighths + landing on root).
- Interior + phrase-opener bars → `strum_pickup` (chord + eighths + pickup to next root).

**Drill format**:
- Rows = steps, 2 columns per row: ABC text + one-line comment.
- Braces: each slot is an alternation of ipools that realize the same chord.
- Example for tonic family: `{006|015|029|065|074}` for I, `{008|017|031|067}` for iii, `{011|013|027|070}` for vi.

---

## Workflow

- **Commit style**: HEREDOC message, ending with
  `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- **Push after each numbered step** so the user can follow progress from the tablet.
- **Run tests before each commit**: `python3 -m pytest tests/ -q`.
- **Status updates**: after each step lands, post a one-line summary to the user (they're at the lab; asynchronous is fine).

---

## Questions for the user (only if genuinely blocked)

Don't ask for permission to execute the build order — it's pre-approved. Do surface:
- Pool-entry ambiguities that require pedagogy input.
- Design forks where both options have real tradeoffs.
- Anything that would require modifying `legacy/` or `source/HarpChordSystem.tex`.

Otherwise: keep shipping. The user will catch up from the tablet later today.
