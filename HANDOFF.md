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

### What happened in the 2026-04-21 lab evening session (top of `origin/main` is `9d7136f` — update and re-pick)

The lab had the tablet plugged in and did a big UX/audio pass on the
Amazing Grace survey page. All 9 commits below are on main; the
tablet (P90YPDU16Y251200164, package `com.harp.jazzhymnal`) has the
latest APK installed.

Ordered by what matters most for anyone touching this next:

1. **`9d7136f` — Jazz Version reference track** next to Full Baseline.
   See `jazz/test_amazing_grace.html` lines ~230-260 for the two
   `<section class="baseline">` blocks. The Jazz MIDI is rendered
   from `data/reharm/variations/amazing_grace/v24.json` (picked
   from 40 generated seeds by a jazz-tag weighting script). If the
   user wants a different jazz feel, re-run the selector with a
   higher `--n`, adjust the weights in the compose script (history
   is in the commit message), pick a different winner, re-render via
   `trefoil.reharm.render_midi.render_variation_midi`, commit
   `data/reharm/tests/amazing_grace/_jazz.mid`.

2. **`e26fcab`, `8546816` — playback fixes**: volume slider (0–300%,
   default 200%), master `GainNode`, note-off honored with 1.2s
   release, sqrt-velocity curve. The storage key is
   `amazing_grace.volume.v2`; do NOT revert to v1. If the user's
   tablet system media volume is still low (`settings get system
   volume_music` returned 5 out of ~15), they may need to bump it on
   hardware — there's no reliable way to set it from adb on this
   device.

3. **`d011ce8` — offline MIDI stack bundled** under `jazz/vendor/`.
   NEVER revert these scripts to CDN URLs — the tablet has no wifi
   and will crash with "Soundfont is not defined". Bundle size is
   ~1.8 MB total (mostly the MusyngKite orchestral_harp soundfont).
   If switching soundfonts, download the new sample bank to
   `jazz/vendor/soundfont/<instrument>-mp3.js` and update the
   `instrument` name in `_loadHarp()`.

4. **`c55d000` — all 79 tactic notes + all 12 dimension notes**
   populated in `data/reharm/tactics.json`. If the user says a
   specific note reads wrong, fix just that `note` field; no
   pipeline regeneration needed.

5. **`5349c62` — saxophone launcher icon** replaces the drill on the
   home screen. PNGs in `jazzhymnal/app/src/main/res/mipmap-*/
   ic_launcher*.png` regenerated via NotoColorEmoji. The user earlier
   confused the `JazzHymnal` and `Drills` icons (both were brown
   drill icons); now they're visually distinct.

6. **`df38417` — `syncJazzAssets` Gradle fix**. If an installDebug
   still ships stale HTML, fall back to `./gradlew clean
   installDebug`.

### Direct brief so you can pick up quickly without re-deriving everything:

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

- **2026-04-21 lab** — `9d7136f` `survey: Jazz Version reference track
  alongside Full Baseline` — generated 40 Amazing Grace variations via
  `trefoil.reharm.selector`, scored them by a jazz-tag weight, and
  rendered the winner (`v24`: 7× chord_offbeat, 6× rolled, 5× each
  of sus/quartal/diatonic/anticipate/common_tone, 4× syncopated) to
  `data/reharm/tests/amazing_grace/_jazz.mid`. Added a second
  `<section class="baseline">` block with a ▶ `jazz-btn`, wired the
  same way as `baseline-btn`.
- **2026-04-21 lab** — `e26fcab` `survey: louder default + wider slider
  range + sqrt-velocity curve` — tablet reported "can barely hear".
  Slider range 0–100 → 0–300, default 80% → 200%, storage key bumped
  to `amazing_grace.volume.v2` so the legacy cached value can't keep
  it quiet. Per-note gain switched from `velocity/127` to
  `sqrt(velocity/127)` to lift mid-velocity notes. Tablet's system
  `volume_music=5` (low) suggests users may also need to bump the
  hardware media volume.
- **2026-04-21 lab** — `8546816` `survey: volume slider + note-off
  honored in MIDI playback` — added `🔈 [slider] %` widget to top bar
  driving a master `GainNode`. Rewrote the `MidiPlayer` event
  callback: Note-on starts a note with no hardcoded duration (rings
  naturally), Note-off stops it with a 1.2s release tail. Active
  notes tracked in `Map<noteNumber, note>` so the right voice
  releases. `endOfFile` frees the UI but leaves the final chord
  ringing for 2.5s before a forced silence. Volume persists via
  `localStorage`.
- **2026-04-21 lab** — `d011ce8` `survey: bundle MIDI playback libs
  offline (tablet has no wifi)` — root cause of "Soundfont is not
  defined" error was `cdn.jsdelivr.net` failing to load on an offline
  tablet. Vendored `midi-player-js@2.0.16` + `soundfont-player@0.12.0`
  + the MusyngKite `orchestral_harp-mp3.js` (~1.7 MB) into
  `jazz/vendor/`, swapped the CDN `<script src>` for local paths,
  and passed a `nameToUrl` override to `Soundfont.instrument`.
- **2026-04-21 lab** — `105b1b1` `HANDOFF.md: direct brief section for
  home-laptop Claude` — added the "Notes for home-laptop Claude on
  next pickup" block.
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
