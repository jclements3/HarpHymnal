# HANDOFF.md — lab-Claude ↔ home-laptop-Claude sync

Two Claude sessions touch this repo. They share one `origin/main`; neither
has a persistent view of the other's memory. This file is how they stay
aligned. **Both sides update this file when they push.**

`PROMPT.md` is the long-form task handoff (what-to-do-next brief).
`HANDOFF.md` (this file) is the short, running ledger of *who owns what,
what just landed, what's blocked*.

---

## Role split

### LAB machine (beefy, CPU-heavy)
- **Runs** the expensive build pipelines that produce gitignored bulk
  artifacts:
  - `python3 -m trefoil.reharm.shape_gen` → `data/reharm/shape_library.json`
  - `python3 -m trefoil.reharm.selector --all` → 11,160 variation JSONs
  - `python3 -m cli.reharm_render --all` → 11,160 `.mid` + `.ly`
  - `python3 -m cli.reharm_cut --all` → 57,280 fragments
  - `python3 -m cli.reharm_solo --hymn <slug> --all` → per-tactic snippet
    MIDIs (e.g. `data/reharm/tests/amazing_grace/*.mid`)
  - `python3 trefoil/build_variations_pages.py` → `jazz/variations.<slug>.html`
  - `python3 -m cli.audio_build …` → `data/audio/*.m4a`
- **Owns** content of `data/reharm/`, `data/audio/`, `data/scores/`, the
  generated `jazz/variations.*.html`.
- **Reads** `PROMPT.md` at session start (that's the lab-Claude onboarding).
- **Does NOT normally** plug the tablet in or build the APK — see below.

### HOME laptop (has the tablet)
- **Owns** `jazzhymnal/` (Android WebView wrapper for the tablet).
- **Builds + installs** the APK when the tablet is physically plugged in:
  ```bash
  cd jazzhymnal
  ./gradlew installDebug        # build + install to the connected device
  # or: ./gradlew assembleDebug; adb install -r app/build/outputs/apk/debug/app-debug.apk
  ```
  The `syncJazzAssets` Gradle task copies `jazz/` + `data/reharm/` into
  the APK at build time, so there is no checked-in duplicate.
- **Does NOT** usually have compute or time to run the `--all` pipelines.
- The user warned: the home laptop cannot reliably update the tablet
  or build an app on a given day. Treat tablet deployment as
  opportunistic — whenever the tablet happens to be plugged in at home.

### USER
- Moves `*_scores.json` exports off the tablet and commits them under
  `data/reharm/tests/<slug>/scores_<timestamp>.json` so the lab can
  drive generator fixes from real ratings.
- Pulls on the tablet-connected machine and runs the installDebug when
  a new UI change needs to land on the device.

---

## Push protocol (keep the ledger honest)

When either side pushes:

1. **Prepend a dated bullet** under *Recent pushes* below (newest first).
2. **Move any now-unblocked items** out of *Outstanding blockers*.
3. If a role boundary just shifted (e.g. "home-Claude took over task X
   from lab because tablet was plugged in") — note it under *Role
   overrides this week*.

Commit the HANDOFF.md change in the **same push** as the actual work.
This file should never lag `origin/main`.

---

## Current state (2026-04-21)

### What's on `origin/main`
- Reharm Tactics engine shipped: `trefoil/reharm/` module + `cli/reharm_*`
  CLIs + 6 test suites (59/59 pass). Bulk artifacts are gitignored.
- `jazz/` static UI shipped: `index.html`, `hymns.html`, `jazz.html`,
  `variations.html` (template, per-hymn files generated locally),
  `test_amazing_grace.html` (survey rig), etc.
- `jazzhymnal/` Android app (this push, `3e1b638…`): WebView wrapper
  loading `file:///android_asset/jazz/index.html`. Includes XHR fetch
  shim (WebView blocks `fetch()` on `file://` origins even with the
  universal-file-access flags) and `window.Android.saveScores` bridge
  writing `Downloads/JazzHymnal/<slug>_scores.json` via MediaStore.
- `test_amazing_grace.html` Help-icon modal (`?` per tactic row, shows
  name · dimension · note · tags · requires · conflicts · derived_from).
  Modal closes on backdrop / `×` / Escape.

### Outstanding blockers
- **Audio for the survey**: the per-tactic MIDIs
  (`data/reharm/tests/amazing_grace/*.mid`) are gitignored and not yet
  pushed by the lab. Until they land, the ▶ A / ▶ B buttons fail.
  Lab → run `python3 -m cli.reharm_solo --hymn amazing_grace --all`
  and commit the `.mid` + `_baseline.mid` + `_notes.json` (the latter
  two are already in the repo; confirm they're still current).
- **Per-hymn variation pages**: `jazz/variations.<slug>.html` (gitignored)
  need `data/reharm/catalog.json` + `shape_library.json` first. Lab →
  after running selector/catalog, run `python3 trefoil/build_variations_pages.py`
  and push the generated HTML. Home → needs them in the APK; the next
  `./gradlew installDebug` will pick them up automatically via
  `syncJazzAssets`.
- **Theory notes for tactics** (the Help modal surfaces whatever is in
  `tactics.json`'s `note` field; 6/79 have content today). Filling the
  remaining 73 is low priority but user-visible — either side can
  incrementally edit `data/reharm/tactics.json`.

### Role overrides this week
- 2026-04-21 — home-Claude (tablet was plugged in) scaffolded
  `jazzhymnal/` and wired the survey export bridge. Normally the lab
  would own the bundled-app path.

---

## Recent pushes (newest first)

- **2026-04-21 home** — `3e1b638` `jazzhymnal: new WebView-wrapper tablet
  app` — scaffolded `jazzhymnal/`, added "Evaluate (Amazing Grace)" tile
  on `jazz/index.html`, XHR fetch shim + `window.Android.saveScores`
  bridge in `test_amazing_grace.html`. Installed + verified on tablet.
- **2026-04-21 home** — (same push) Help-icon modal on tactic rows in
  `test_amazing_grace.html`; shows all `tactics.json` metadata.
- **2026-04-21 lab** — `b06dde6` `Audition rig → snippet A/B + 0-5
  scoring; TREFOIL corrections; lab handoff` (see `PROMPT.md` for the
  accompanying brief).
- **2026-04-20 lab** — `74c3472` `Reharm Tactics: 8-phase pipeline from
  tactic pool to tablet UI`.

---

## When in doubt

- Look at `PROMPT.md` for the full task brief.
- Look at `CLAUDE.md` for file-precedence rules.
- Look at `REHARM_TACTICS.md` for subproject pedagogy.
- Look at `jazzhymnal/app/build.gradle` for how assets are synced at
  build time (no committed duplicates).
