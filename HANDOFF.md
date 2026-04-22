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
- **Per-hymn variation pages**: `jazz/variations.<slug>.html` (gitignored)
  need `data/reharm/catalog.json` + `shape_library.json` first. Lab →
  after running selector/catalog, run `python3 trefoil/build_variations_pages.py`
  and push the generated HTML. Home → needs them in the APK; the next
  `./gradlew installDebug` will pick them up automatically via
  `syncJazzAssets`.
- ~~Theory notes for tactics~~ **resolved in `c55d000`** — all 79
  tactics now have populated `note` fields and all 12 dimensions have
  theory notes (from `97861fd`). Every 🎷 help button in the Amazing
  Grace survey opens a substantive pedagogy paragraph.

### Role overrides this week
- 2026-04-21 — home-Claude (tablet was plugged in) scaffolded
  `jazzhymnal/` and wired the survey export bridge. Normally the lab
  would own the bundled-app path.
- 2026-04-21 — lab-Claude installed the APK directly on the tablet
  (device was plugged into the lab today, contrary to the usual role
  split). The tablet already has `38a89c9` installed; home doesn't
  need to re-run `./gradlew installDebug` unless the user has worked
  on the repo since.

---

## Notes for home-laptop Claude on next pickup

Direct brief so you can pick up quickly without re-deriving everything:

1. **Tablet already has `38a89c9` installed from the lab.** No
   reinstall needed unless something has landed between that commit
   and your pickup. Check: `adb shell dumpsys package com.harp.jazzhymnal
   | grep versionName` then compare against `git log` — or just skip
   the install if the user isn't asking for new UI.

2. **`syncJazzAssets` was broken.** The old `tasks.whenTaskAdded
   { if (t.name == 'preBuild') … }` missed variant-specific tasks and
   let stale HTML ship. Fix landed in `df38417` via
   `tasks.configureEach` that hooks every `pre*Build` and `merge*Assets`
   task. If an `./gradlew installDebug` still seems to serve an old
   view, fall back to `./gradlew clean installDebug`.

3. **Launcher icon is now 🎷** (`5349c62`). If the user complains it
   looks off on a specific density bucket, PNGs live under
   `jazzhymnal/app/src/main/res/mipmap-*/ic_launcher*.png`, regenerated
   via NotoColorEmoji. Source generator is ad-hoc Python — if it needs
   to be rerun, the script is in the commit message and `/tmp/`.

4. **All 79 tactics + 12 dimensions have pedagogy notes** populated in
   `data/reharm/tactics.json`. The 🎷 help buttons in the Amazing Grace
   survey (`jazz/test_amazing_grace.html`) now open substantive theory
   paragraphs on every row and every section header. If the user
   reports a specific note reads wrong, fix just that `note` field
   and push — no pipeline re-run required.

5. **Survey audio fixtures are tracked now** (`d4dfb63`). The
   `.gitignore` line `data/reharm/tests/*/*.mid` was removed; the 158
   per-tactic MIDIs + `_baseline.mid` under `data/reharm/tests/amazing_grace/`
   are in the repo and bundled into the APK via `syncJazzAssets`. Do
   not re-add that ignore line — the comment above it explains why.

6. **Expect the user to commit `scores_<timestamp>.json` files** under
   `data/reharm/tests/amazing_grace/` from the tablet. When those
   arrive, the lab will fold them back into the generator. If they
   show up in your session, just verify they parse cleanly and leave
   them for the lab to act on.

7. **Still open**: per-hymn variation pages `jazz/variations.<slug>.html`
   are gitignored and blocked on `catalog.json` + `shape_library.json`
   being generated. If the user asks for variations on a hymn other
   than Amazing Grace, you likely can't build them from the home
   laptop — redirect to the lab or do a lightweight static stub.

---

## Recent pushes (newest first)

- **2026-04-21 lab** — `c55d000` `tactics: populate music-theory notes
  for all 79 tactics` — filled the `note` field on all 73 previously-
  empty tactics across 12 dimensions (shape/register/lh_activity/
  rh_activity/connect_from/connect_to/substitution/density/texture/
  lever/range/phrase_role). Each note is 1–3 sentences framed for a
  harpist, grounded in the 118-fraction pool vocabulary. APK rebuilt +
  installed on the tablet.
- **2026-04-21 lab** — `5349c62` `jazzhymnal: saxophone launcher icon`
  — replaced the drill launcher icon with 🎷 rendered from
  NotoColorEmoji at all 5 mipmap densities. Also earlier
  `df38417` fixed the `syncJazzAssets` Gradle hook so future builds
  don't ship stale HTML.
- **2026-04-21 lab** — `97861fd` `tactics survey: dimension-level help
  buttons + theory notes` — added `?` help button to each dim-section
  `<summary>` in `test_amazing_grace.html` + `openDimHelp()` handler;
  populated `note` field on all 12 dimensions in `tactics.json` (shape,
  register, lh_activity, rh_activity, connect_from/to, substitution,
  density, texture, lever, range, phrase_role). APK rebuilt and
  installed on the tablet from the lab (device was connected).
- **2026-04-21 lab** — `d4dfb63` `reharm_solo: land Amazing Grace survey-audio
  fixtures` — ran `cli.reharm_solo --hymn amazing_grace --all`, committed
  158 tactic/original MIDI pairs + `_baseline.mid`. Narrowed `.gitignore`:
  `data/reharm/tests/<slug>/*.mid` are now tracked (survey fixture, not
  bulk render). Unblocks the ▶ A / ▶ B survey buttons — home-Claude will
  pick them up on the next `./gradlew installDebug`.
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
