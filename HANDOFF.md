# HANDOFF.md — lab-Claude ↔ home-laptop-Claude sync

Two Claude sessions touch this repo. They share one `origin/main`; neither
has a persistent view of the other's memory. This file is how they stay
aligned. **Both sides update this file when they push.**

`PROMPT.md` is the long-form task handoff (what-to-do-next brief).
`HANDOFF.md` (this file) is the short, running ledger of *who owns what,
what just landed, what's blocked*.

---

## Role split (refreshed 2026-04-24 after consolidation `5f2b46b`)

### LAB machine (beefy, CPU-heavy, usually not wired to the tablet)
- **Owns** all Python pipelines: `retab/build_hymnal.py`,
  `reharm/build_hymnal.py`, `retab/retab_hymnal.py`,
  `reharm/reharm_hymnal.py`, the drill builders, audio bakes, etc.
- **Owns** `data/hymns/*.json`, `data/reharm/*` (new layout — the old
  tactics/variations tree was deleted in `5f2b46b`), and everything
  under `data/audio/` (gitignored m4a bundle).
- **Reads** `PROMPT.md` at session start for the long-form task brief.

### HOME laptop (has the tablet plugged in)
- **Owns** `tablet_app/` (Android WebView app, package
  `com.harp.harphymnal.drills`, app name **HarpHymnal**).
- **Builds + installs** the APK:
  ```bash
  cd tablet_app
  ./gradlew installDebug               # build + install to connected device
  # fallback if assets look stale:
  ./gradlew clean installDebug
  ```
  **There is no `syncJazzAssets` task anymore.** The consolidation moved
  all tablet-bound assets directly into
  `tablet_app/app/src/main/assets/` (flat layout: `index.html`,
  `retab/`, `reharm/`, `hymns/`, `audio/`, `docs/`, `vendor/`,
  `docs.html`, `harphymnal_*.js`). Gradle picks them up via the default
  `mergeDebugAssets`.
- Tablet: Lenovo P90, serial `P90YPDU16Y251200164`, connected via USB
  at the lab this week. If it shows up only as "MIDI" under `lsusb`,
  swipe down → switch USB mode to File Transfer → re-enable USB debugging.

### USER
- Moves any tablet-side exports off the device and commits them under
  the relevant `data/…` path when a rating/feedback loop is live.
- Pulls on the tablet-connected machine and runs the `installDebug`
  when new UI changes need to land.

### Note to the home laptop
**HANDOFF.md was stale for 3 days before this rewrite.** Everything
below pre-dating 2026-04-24 talked about `jazzhymnal/` + package
`com.harp.jazzhymnal` + `syncJazzAssets` — all three are gone. Trust
the filesystem and `git log`, not any older push-entry prose.

---

## Push protocol (keep the ledger honest)

When either side pushes:

1. **Prepend a dated bullet** under *Recent pushes* below (newest first).
2. **Move any now-unblocked items** out of *Outstanding blockers*.
3. If a role boundary just shifted — note it under *Role overrides this week*.

Commit the HANDOFF.md change in the **same push** as the actual work.
This file should never lag `origin/main`.

---

## Current state (2026-04-29)

`origin/main` head is `de2681a` — Chopin Hymnal home-screen tile,
key-signature-aware chopin ABC, and the orphan piano-prototype CLI
removed. Tablet has the matching APK installed (`com.harp.harphymnal.drills`,
P90YPDU16Y251200164).

Home grid is now **7 tiles** (added Chopin Hymnal between Reharm
Hymnal and Reharm): Retab · Retab Hymnal · Reharm Hymnal · **Chopin
Hymnal (new, deep-purple `#3A1B36`)** · Reharm · Docs · Shapes. The
new tile taps straight to `shapes/chopin/index.html` (the existing
A-Z navigator), mirroring how Retab Hymnal / Reharm Hymnal jump
directly into their hymn lists rather than routing through a
sub-index.

### Encoding-system rewrite — in progress this session, not yet committed

The repo-root encoding spec has been rewritten end-to-end today. The
**previous** README described a chord-naming system (Roman numeral chords
+ mode/intervals + handout chord labels). The **current** README describes
a fundamentally different system: a **shape-setup encoding** that catalogs
hand placements on the strings and progressions of those placements,
explicitly *not* music notation.

**Key reframe (do not lose this):** the system encodes *what is set on
the strings before playing*. Rhythm, articulation, strike order after
assembly, timing, and dynamics are deliberately outside scope. Most of
what looks like "playing notation" (operators, hand markers, the dash
separator) is actually about sequences of *setups*, not sequences of
*played notes*. There's a project-memory entry under
`memory/project_encoding_scope.md` — read that first if you didn't
participate in today's session.

**What changed in the file system today (uncommitted):**

- `README.md` — full rewrite. Three shape forms: absolute
  `Nx<mode><intervals>`, relative `^Nx<mode><intervals>`, continuation
  `<gap><intervals>`. Disambiguator is the first character class.
  Subscripts now mean **assembly order** (which finger plants 1st-4th
  in the set sequence), not finger labels — the previous README had
  this wrong. Hand markers: bare shape = either hand; `L<shape>` /
  `R<shape>` pin a hand; `<shape> R <shape>` is a two-hand setup
  (LH-then-RH simultaneous). Header block: `Title:` + `Key:` (no
  `Meter:` — rhythm is out of scope).
- `VERIFY.md` — reach-calibration drills. User has not run these yet;
  when they do, the per-finger reach ceilings in the README's table
  will be replaced with calibrated numbers.
- `DRILLS.md` — full replacement. Old chord-pool letter notation
  (`cegDFA` etc.) is gone. Ten drills under the new grammar, including
  the canonical thirds sweep (`1x1333-3333*5~`), modal cycle, two-hand
  bass+chord progression, and a top-down assembly study.
- `HANDOUT.md` — new file. Quick-reference catalog of the 12
  universal-winner shape patterns plus mode-conditional gems, common
  setup forms (single notes, dyads, triads, tetrads), and sequence
  patterns. Different in purpose from the older `handout.md`/`handout.tex`
  which use the previous chord-name system; those are unchanged.

**What did NOT change:**

- `tablet_app/` — untouched. The Android app's docs viewer still points
  at `docs/*.md` files (older system). No tablet-side updates today.
- `retab/`, `reharm/` — untouched. Their CLAUDE.md files still describe
  Roman-numeral pipelines. The new encoding system hasn't been wired
  into those pipelines yet.
- `data/`, `legacy/`, `source/` — untouched.

**For the home-laptop Claude:**

If you're picking up this session, read in order:
1. `memory/project_encoding_scope.md` (scope clarification)
2. `README.md` (the new spec)
3. `DRILLS.md` (sample sequences under the new grammar)
4. `HANDOUT.md` (the pattern catalog)
5. `VERIFY.md` (calibration drills, awaiting user results)

Open questions still on the table:
- Reach calibration — user hasn't run VERIFY.md yet; default reach
  ceilings in README's table are best-guess until then.
- Minor-key encoding convention (`Key: Am` vs relative-major-with-mode-6)
  — was raised in session, not resolved. Defer until the first minor-key
  piece needs to be encoded.
- Multi-row composition is sequential phrases (decided); true
  simultaneity (parallel rows or `&` operator) is deferred.
- The retab/reharm pipelines still use the OLD chord-name system; if
  the user wants those rewritten under the new encoding, that's a
  separate large piece of work.

### Tablet state (updated today)

Tablet now has commit `806b86f` installed (encoding rewrite + new docs
tiles). `lastUpdateTime` per `dumpsys`: 2026-04-25. Built and installed
from the lab via `./gradlew installDebug` (tablet still plugged in here
from yesterday's session). Home doesn't need to reinstall.

### What's live on the tablet (installed today from the lab)
- **Home screen**: 5 tiles — Retab, Retab Hymnal, Reharm Hymnal, Reharm,
  **Docs** (new, deep-blue banner).
- **Retab** — style drills + RH pockets (existing).
- **Retab Hymnal** — trefoil LH patterns over all hymns, L1–L7 selectors.
- **Reharm Hymnal** — diatonic jazz reharmonisation of all hymns,
  L1–L7 selectors.
- **Reharm** — jazz/pool/substitution/approach/voicing drill jumps.
- **Docs (NEW, `4899801`)** — in-app markdown viewer at `docs.html`,
  renders 6 user-facing .md files with a vendored `marked.min.js`. All
  offline, no wifi. Top-nav per doc, deep-linkable via `#slug` hash.
  Files:
  - `tablet_app/app/src/main/assets/docs.html` — the viewer
  - `tablet_app/app/src/main/assets/docs/TREFOIL.md`
  - `tablet_app/app/src/main/assets/docs/RECIPE.md`
  - `tablet_app/app/src/main/assets/docs/REHARM_TACTICS.md`
  - `tablet_app/app/src/main/assets/docs/ChordAnalysis.md`
  - `tablet_app/app/src/main/assets/docs/handout.md`
  - `tablet_app/app/src/main/assets/docs/HARP_IDIOM.md`
  - `tablet_app/app/src/main/assets/vendor/marked.min.js` (35 KB)
  Note: these .md files are **copies** of the repo-root canonical docs
  (except `HARP_IDIOM.md` whose source lives under `docs/`). If a doc
  is edited at the repo root, re-copy into `tablet_app/…/docs/` before
  building. A Gradle sync task to dedupe is a good future clean-up but
  is not in place yet.

### Consolidation summary (`5f2b46b`, 2026-04-24)
- `jazzhymnal/` — **deleted.** Package `com.harp.jazzhymnal` uninstalled
  from the tablet. `tablet_app/` is the only Android project now.
- `trefoil/reharm/` — deleted. Old reharm Python.
- `data/reharm/` — old tactics/variations/fixture tree deleted.
- `retab/` and `reharm/` — imported as subtrees of this repo (not git
  subtrees; plain `cp`). Their upstream standalone repos are orphaned.
- Launcher icon: pink-notes-on-burgundy (visible on the tablet).
- `jazz/` — still tracked (25 HTML files), but **nothing references
  it anymore.** Orphaned pre-consolidation artifact. Do not edit
  anything in `jazz/` expecting it to reach the tablet.

### Outstanding
- **Root-level pedagogy docs drift risk.** `tablet_app/…/docs/*.md`
  are manually-maintained copies of the repo-root `.md` files. If
  someone edits `TREFOIL.md` at the root and doesn't re-copy, the
  tablet view will lag. A ~5-line Gradle copy task (or a pre-build
  shell script) would make this self-healing. Non-blocking.
- **HANDOFF.md's pre-2026-04-24 entries** (below) reference `jazz/`,
  `jazzhymnal/`, `tactics.json`, per-tactic survey MIDIs under
  `data/reharm/tests/amazing_grace/` — none of that is live anymore.
  Left in place as historical record but should not be acted on.

### Role overrides this week
- **2026-04-24 — lab-Claude ran `./gradlew installDebug` directly**
  (tablet plugged into the lab, not home). Tablet now has commit
  `4899801` installed. Home doesn't need to re-install unless something
  lands after this handoff.
- **2026-04-24 — lab-Claude did the Docs feature end-to-end** (normally
  UI is home territory). Safe to pick up where it left off; all files
  are in the live `tablet_app/` tree.

---

## Notes for home-laptop Claude on next pickup

### What happened in the 2026-04-24 lab session (top of `origin/main` is `4899801`)

1. **Consolidation (`5f2b46b`) — read this first.** Anything you
   remembered about `jazzhymnal/`, `com.harp.jazzhymnal`, or
   `syncJazzAssets` is dead. The tablet app is now `tablet_app/`,
   package `com.harp.harphymnal.drills`, flat assets at
   `tablet_app/app/src/main/assets/`. Build with
   `cd tablet_app && ./gradlew installDebug` — no special asset-sync
   plumbing, just standard Gradle.

2. **Docs feature shipped (`4899801`)**: new **Docs** tile on the home
   screen (5th, deep-blue) → opens `docs.html`, which is a vendored
   `marked.min.js` markdown viewer. It XHR-loads from `./docs/*.md`
   (fetch is still blocked on `file://` in WebView; the viewer uses
   `XMLHttpRequest` directly — do not "modernize" this to `fetch()`).
   Six docs currently exposed: Trefoil, Recipe, Reharm Tactics, Chord
   Analysis, Handout, Harp Idiom.

3. **There was a false-start push `2f9f3c2`** — first attempt landed
   the Docs feature into `jazz/` (the orphaned pre-consolidation tree).
   Build ran UP-TO-DATE and nothing shipped. `4899801` is the correct
   re-land into `tablet_app/`. If git log looks confusing in that
   stretch, that's why.

4. **Tablet already has `4899801` installed** from the lab today.
   Check via:
   ```bash
   adb shell dumpsys package com.harp.harphymnal.drills | grep versionName
   ```
   No reinstall needed unless you push new UI changes.

5. **The orphan `jazz/` tree** will probably be deleted eventually.
   Don't accidentally edit a file there thinking it'll ship.

### Still open (non-blocking)
- Deduplicate docs: make `tablet_app/…/docs/` a build-time copy of
  repo-root `.md` files instead of a manual mirror.
- Refresh HANDOFF.md further if retab/reharm story evolves — the
  pre-2026-04-24 Recent pushes below are frozen historical context.

---

## Recent pushes (newest first)

- **2026-04-29 home** — `de2681a` `tablet_app: home-screen Chopin
  Hymnal tile`. New 4th tile on the home grid (deep purple `#3A1B36`,
  count 279) navigates straight to `shapes/chopin/index.html`. Sits
  between Reharm Hymnal and Reharm so the three Hymnal tiles cluster
  visually. Native Android Back from inside chopin returns to the home
  grid via WebView history. APK reinstalled on the P90.
- **2026-04-29 home** — `03dbbf3` `shapes/chopin: respect key
  signature when emitting accidentals`. Fixes a long-running visual
  bug where every sharped/flatted note in a chopin phrase ABC was
  marked twice — once via `K:` and once via an explicit `^`/`_`
  marker on each note. Added `_key_accidentals(root, mode)` (returns
  `{letter: '#'|'b'}` for what the key sig already alters) and a
  per-bar `bar_state` dict threaded through `_abc_pitch`,
  `_melody_to_abc`, `_chord_token`, `_l2_bar_bass_abc`, and
  `_melody_to_abc_l3`. Now: a pitch matching the key sig emits no
  marker; a contradicting natural emits `=`; an unusual chromatic
  still emits `^`/`_` correctly. Verified against G-major (V7's F#
  goes bare), Eb-major-with-chromatic (`^F` for F#, `=A` for an A
  natural), and key-sig persistence across the bar. All 279 chopin
  pages rebuilt + synced into `tablet_app/app/src/main/assets/shapes/chopin/`,
  APK reinstalled.
- **2026-04-29 home** — `f57a62e` `shapes/chopin: drop standalone
  piano-prototype CLI`. Removed the orphan
  `shapes/chopin/piano/silent_night.html` prototype and the
  whole-hymn `render_page` / `main` / `build_abc` / `argparse` block
  from `render_chopin_piano.py` (only the phrase-level
  `build_phrase_abc{,_l2,_l3}` + `render_phrase_piano_svg{,_l2,_l3}`
  functions remain — those are what `build_hymn_view.py` actually
  calls). APK reinstalled.
- **2026-04-27 home** — Chopin pages now have a 3-level sub-selector:
  **L1 sustained pad** (default — held ATB whole-notes beneath rhythmic
  melody), **L2 arpeggiated** (LH oom-pah-pah: bass quarter on beat 1,
  `[tenor+alto]` chord on each remaining beat; melody-only RH), and
  **L3 ornamented** (held pad like L1, but the soprano gets one
  diatonic passing tone inserted between any two adjacent melody notes
  a 3rd or wider apart). Same harmonic skeleton across all three —
  only the surface texture changes. Each phrase emits all three SVGs
  inline; CSS `.clvl-svg` toggles visibility, JS swaps on button click.
  Implementations (`build_phrase_abc_l2/l3` + `_l2_*` / `_l3_*`
  helpers) live in `shapes/render_chopin_piano.py`. The Hymns-tab
  per-bar table is unchanged (the L1/L2/L3 split is purely a chopin
  surface-texture concept). All 279 chopin pages rebuilt; APK
  reinstalled. Hymns-tab pages were untouched, so the previous push's
  Strings column / Shape table layout still applies there.
- **2026-04-27 home** — `e6916b2` Shapes area is now a full sub-app
  under the Shapes tile (6th tile on home, plum `#4A2545`). Major
  work that landed:
  - **Hymns + Chopin sub-tabs.** Both top-nav tabs land on A-Z navigators
    over all 279 hymns. Shared "Recent" bar above search records hymn
    visits in `localStorage['shapes.recent']` (capped at 10, cleared via
    inline link). Letter groups now lay out in a 3-column CSS grid so all
    20 letters in the corpus fit on one screen at 1920×1200 — tap a
    letter card to expand its hymn list inline within its column.
  - **Chopin pages** = grand-staff piano arrangement of each hymn:
    melody at original rhythm on top, voice-led ATB pad held per chord
    change beneath. Renders via `shapes/render_chopin_piano.py` (one ABC
    score per phrase → abcm2ps → inline SVG). Replaced the prior
    whole-note phrase grid (`render_phrase_svg.py`) on chopin pages.
  - **Strings column.** New first column on every per-bar shape table:
    a 47-character monospace row mapping the active level's pitches onto
    the harp's 47 strings — `·` for unplayed, the natural letter
    (C/D/E/F/G/A/B) for touched (sharps/flats share a string with the
    natural). Swaps with the level selector exactly like Shape and
    Chord. Source pitches: chopin = the Voicing's S/A/T/B; SATB =
    the bar's actual SATB; retab/reharm = expanded shape templates.
  - **QRG tab.** New `shapes/QRG.html` between `index` and `README` —
    one-page reference for reading a token (octave, hand, hatted
    degree, intervals). Linked into all 558 per-hymn pages.
  - **Layout.** Bumped body `max-width: 56rem → 100rem` so the nav fits
    on one line and the per-bar table stops wrapping.
  - **Bug fix.** Added `E#`, `B#`, `Cb`, `Fb` to `voice_lead.py`'s
    `PC` dict — the only two F#-minor hymns
    (`if_god_had_not_been_on_our_side`, `none_other_lamb`) had been
    failing on a `KeyError: 'E#'` and were absent from the corpus.
    Coverage is now 279/279.
  - APK reinstalled on the tablet (`com.harp.harphymnal.drills`,
    P90YPDU16Y251200164). Tablet's `tablet_app/app/src/main/assets/shapes/`
    mirror is checked in — gradle's default `mergeDebugAssets` picks
    it up; no extra sync task.
- **2026-04-24 lab** — `4899801` `tablet_app: Docs tile + markdown viewer
  (re-land from dead jazz/)` — landed `docs.html` + vendored
  `marked.min.js` + 6 bundled markdown files into
  `tablet_app/app/src/main/assets/`. Added the 5th Docs tile (deep-blue
  `#1F4E79`) to the home grid. Reverted the stale `jazz/index.html`
  edit from `2f9f3c2`. APK installed on the tablet.
- **2026-04-24 lab** — `2f9f3c2` `jazzhymnal: Docs tile + in-app markdown
  viewer` — **SUPERSEDED by `4899801`.** Landed under `jazz/`, which
  was already dead after `5f2b46b`; nothing from this push reached the
  APK. Kept for history only.
- **2026-04-24 lab** — `5f2b46b` `Consolidate retab + reharm into
  HarpHymnal, drop OBE subprojects` — major restructure. Deleted
  `jazzhymnal/`, `trefoil/reharm/`, `data/reharm/` (old), old top-level
  `reharm/`. Imported `retab/` and `reharm/` as non-subtree copies.
  Renamed app to "HarpHymnal" and shipped pink-notes-on-burgundy
  launcher icons. Tablet has `com.harp.jazzhymnal` uninstalled.

--- everything below here pre-dates the 2026-04-24 consolidation ---
--- treat as historical context; do not act on it ---

- **2026-04-21 lab** — `17ac251` `HANDOFF.md: log 2026-04-21 evening
  lab session (9d7136f back to d011ce8)` — pure docs entry.
- **2026-04-21 lab** — `9d7136f` `survey: Jazz Version reference track
  alongside Full Baseline` — generated 40 Amazing Grace variations via
  `trefoil.reharm.selector`, scored them by a jazz-tag weight, and
  rendered the winner (`v24`: 7× chord_offbeat, 6× rolled, 5× each
  of sus/quartal/diatonic/anticipate/common_tone, 4× syncopated) to
  `data/reharm/tests/amazing_grace/_jazz.mid`. Added a second
  `<section class="baseline">` block with a ▶ `jazz-btn`, wired the
  same way as `baseline-btn`. (`data/reharm/tests/` and `jazz/` now
  obsolete.)
- **2026-04-21 lab** — `e26fcab` `survey: louder default + wider slider
  range + sqrt-velocity curve` — tablet reported "can barely hear".
  Slider range 0–100 → 0–300, default 80% → 200%, storage key bumped
  to `amazing_grace.volume.v2`. Per-note gain switched from
  `velocity/127` to `sqrt(velocity/127)` to lift mid-velocity notes.
- **2026-04-21 lab** — `8546816` `survey: volume slider + note-off
  honored in MIDI playback` — added `🔈 [slider] %` widget driving a
  master `GainNode`. Rewrote the `MidiPlayer` event callback so
  Note-on/Note-off are honored with a 1.2s release tail.
- **2026-04-21 lab** — `d011ce8` `survey: bundle MIDI playback libs
  offline (tablet has no wifi)` — vendored `midi-player-js@2.0.16` +
  `soundfont-player@0.12.0` + MusyngKite `orchestral_harp-mp3.js` into
  `jazz/vendor/` (now orphaned post-consolidation, but the "no wifi,
  bundle offline" principle still holds for anything shipped to the
  tablet).
- **2026-04-21 lab** — `105b1b1` `HANDOFF.md: direct brief section for
  home-laptop Claude`.
- **2026-04-21 lab** — `c55d000` `tactics: populate music-theory notes
  for all 79 tactics` — filled the `note` field on all 73 previously-
  empty tactics across 12 dimensions. (`data/reharm/tactics.json` was
  deleted in `5f2b46b`.)
- **2026-04-21 lab** — `5349c62` `jazzhymnal: saxophone launcher icon`
  — replaced the drill launcher icon with 🎷. (Replaced again by the
  pink-notes-on-burgundy icon in `5f2b46b`.)
- **2026-04-21 lab** — `97861fd` `tactics survey: dimension-level help
  buttons + theory notes`.
- **2026-04-21 lab** — `d4dfb63` `reharm_solo: land Amazing Grace survey-audio
  fixtures` — committed 158 tactic/original MIDI pairs. (Deleted in
  `5f2b46b`.)
- **2026-04-21 home** — `3e1b638` `jazzhymnal: new WebView-wrapper tablet
  app` — scaffolded `jazzhymnal/`. (Project deleted in `5f2b46b`.)
- **2026-04-21 home** — (same push) Help-icon modal on tactic rows in
  `test_amazing_grace.html`.
- **2026-04-21 lab** — `b06dde6` `Audition rig → snippet A/B + 0-5
  scoring; TREFOIL corrections; lab handoff`.
- **2026-04-20 lab** — `74c3472` `Reharm Tactics: 8-phase pipeline from
  tactic pool to tablet UI`.

---

## When in doubt

- Look at `PROMPT.md` for the full task brief.
- Look at `CLAUDE.md` for file-precedence rules.
- Look at `tablet_app/app/build.gradle` if asset plumbing behaves oddly.
- `git log --stat 5f2b46b` if you want to see exactly what the
  consolidation moved or deleted.
