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

## Current state (2026-05-04 — abccomposer wired as desktop PWA + tablet tile)

`abccomposer/` (landed earlier today as `64d7ef3`) is now installable
as a real desktop app and reachable as the **Composer** tile on the
P90 home grid. Same source files for both — single bundle, three
delivery shapes (browser tab / installed PWA / WebView tile).

### What this push landed (on top of `64d7ef3`)

- `abccomposer/manifest.webmanifest` — PWA manifest (name, start_url,
  display:standalone, theme-color `#bd93f9`, icons 192 + 512).
- `abccomposer/sw.js` — cache-first service worker for the app shell.
  Same-origin GETs for `*.html|css|js|webmanifest|png|svg|woff*` get
  cached on success; cross-origin and non-GET pass through (so the
  POST to `api.anthropic.com` is never intercepted). Bump
  `CACHE_NAME` to invalidate.
- `abccomposer/icon-192.png` + `icon-512.png` — purple square with
  a centered eighth-note glyph, generated from PIL/DejaVu-Sans-Bold.
- `abccomposer/index.html` — added `<link rel=manifest>`,
  `theme-color` meta, and a guarded
  `navigator.serviceWorker.register("sw.js")` (only on http(s), so
  it's a no-op under `file://` and `file:///android_asset/`).
- `abccomposer/README.md` — three-mode run guide (browser tab /
  installable PWA / tablet tile).

### Tablet wiring

- `tablet_app/app/src/main/AndroidManifest.xml` — added
  `<uses-permission android:name="android.permission.INTERNET" />`.
  `usesCleartextTraffic="false"` is fine because anthropic is HTTPS.
- `tablet_app/app/src/main/assets/abccomposer/` — full mirror of the
  top-level `abccomposer/` tree minus README/examples (Gradle picks
  up via the default `mergeDebugAssets`).
- `tablet_app/app/src/main/assets/index.html` — 13th tile **Composer**
  (family `composer`, banner `#6B46C1`, opens
  `abccomposer/index.html`).

Tablet still pending reinstall this week on top of the earlier
`9278b16` + `26abe7a` + this commit.

### Catalog drift risk (extended)

`abccomposer/` is now mirrored across **two** trees:
`/abccomposer/` (canonical, dev-served) and
`/tablet_app/app/src/main/assets/abccomposer/` (APK bundle). Plain
recursive copy on every change is the current pattern. If this
becomes painful, switch to a Gradle `sourceSets.main.assets.srcDirs`
override pointing at `../../abccomposer` so the APK reads the
canonical tree directly — non-blocking until then.

### Smoke test (this push)

`python3 -m http.server 8765` + `google-chrome --headless --dump-dom`:
page loads, CodeMirror mounts, abcjs renders default tune, no
console errors, `manifest.webmanifest` link in DOM, SW registration
line in DOM, `/manifest.webmanifest` returns
`application/manifest+json`, `/sw.js` returns `text/javascript`.

---

## Current state (2026-05-04 — abccomposer: in-browser ABC editor + Claude chat)

New top-level app `abccomposer/` — single self-contained `index.html`
with a horizontal **40 / 40 / 20** layout: vim-mode CodeMirror editor
(40%), live abcjs render (40%), Claude chat pane (20%). No build step,
no server (the chat pane calls `api.anthropic.com` directly with a key
the user pastes into a settings dialog and which is stored in
`localStorage` only).

### What this push landed

- `abccomposer/index.html` — toolbar (filename, New / Open / Save /
  Play / Stop / settings) + 3 panes. Editor is CodeMirror 5.65.18 with
  the official `vim` keymap (full motion/operator/text-object/
  visual-block/macro/register/dot-repeat support — substantially
  beyond the hand-rolled `easyabc_vim/` subset). Inline `abc` syntax
  mode coloring header lines, `%` comments, `!decoration!`,
  `"chord symbol"`, bar lines, accidentals, notes. Custom vim ex
  commands `:w` (download `.abc`), `:play`, `:stop`.
- `abccomposer/vendor/` — CodeMirror 5 core + dracula theme + vim
  keymap + dialog/search/matchbrackets addons + abcjs 6.4.4
  basic-min. All MIT/BSD, all flat files, no bundler.
- `abccomposer/README.md` — run/setup instructions, why CM5 not CM6,
  why a separate app rather than a tablet tile.

### How the chat pane talks to Claude

Each `POST /v1/messages` includes:
- `system` = saved system prompt + `<current_abc>` ... `</current_abc>`
  (the editor's full buffer, sent fresh each turn so Claude always
  sees what the user is currently composing)
- `messages` = visible user/assistant turn history (persisted in
  `localStorage` as `abccomposer.chatHistory`)
- header `anthropic-dangerous-direct-browser-access: true` so the API
  accepts requests with a `*` Origin

Assistant messages with fenced ` ```abc ` blocks render an
**→ Apply to editor** button under the block — replaces the editor
buffer in one click.

### What's queued / not started

- **Smoke-test on a real browser**. Was authored but not actually
  loaded yet — first thing for whichever box opens this.
- Optional: bundle a couple of HarpHymnal sample tunes into
  `abccomposer/examples/` (currently the dir is empty) so you can
  pick one with `:e examples/foo.abc` rather than only typing from
  scratch.
- Stripchart visualizer (queued from 2026-05-03) is now arguably
  obsolete — abcjs already exposes timing events; if a piano-roll is
  wanted, hang it off this composer's render pane instead of patching
  EasyABC.

### Relationship to easyabc_vim/ (2026-05-03)

`easyabc_vim/` still works as a lab-box fallback if anyone wants the
EasyABC GUI specifically. But the browser path is now the primary
recommended editor: full vim keymap, runs anywhere with a browser,
no wxPython/Z:-share fragility, no Python install required.

---

## Current state (2026-05-03 — easyabc_vim: vim mode for EasyABC)

New top-level dir `easyabc_vim/` packages an embedded vi keybinding layer
+ file-watcher mode for [jwdj/EasyABC](https://github.com/jwdj/EasyABC).
Home-laptop session; user is on a corporate Windows box with the project
mounted as `Z:\` from a Linux dev machine, so all build/run actually
happens on the Linux side.

### What this push landed

- `easyabc_vim/` — six Python modules + install script + idempotent
  patcher + README, all driven from this repo so a fresh box (lab box,
  reinstalls) gets a working `easyabc` with vim bindings via one command:
  ```bash
  ./easyabc_vim/install.sh
  ```
  That clones `jwdj/EasyABC` into `tmp/EasyABC`, drops the vi modules
  in, runs `patch.py` against the upstream `easy_abc.py`, and writes
  `~/.local/bin/easyabc` pointing at the patched copy.
- The vi layer (built by four parallel sub-agents and integrated by a
  fifth):
  - `vi_motions.py` — pure-position motions (`hjkl`, words, line, doc, %, fFtT)
  - `vi_operators.py` — `d/c/y` + paste + register state
  - `vi_search.py`    — `/ ? n N`, `:s/pat/rep/[g]`, `:%s/...`
  - `vi_mode.py`      — mode state machine, key dispatch, F12 toggle
- `aui_compat.py` — monkeypatches wxPython 4.x `auibar.DrawSeparator`
  to use integer division (the shipped method does
  `rect.x += rect.width/2` and crashes the paint loop on Py3 — was
  spamming hundreds of tracebacks per session).
- `test_vi.py` — self-contained harness that mocks `wx`/`wx.stc`,
  fakes a Scintilla buffer, drives synthetic key events through ViMode
  and asserts buffer/cursor state. ~27 tests covering motions,
  operators, modes, ex commands, undo/redo, F12 toggle. **Not yet
  run on a real Python install** — home-laptop has only the Windows
  Python stub. Lab box: `python3 ~/projects/HarpHymnal/tmp/EasyABC/test_vi.py`
  is the first thing to run after install; anything failing there is
  what to fix before the user touches the GUI.
- Vim-as-editor workflow: ex command `:watch` polls the loaded file's
  mtime every 500 ms and reloads on change (editor goes read-only so
  vim is the source of truth). Pair with `vim foo.abc` in another
  terminal — save in vim, EasyABC re-renders the score within 500 ms.
  `:play` / `:stop` route to EasyABC's existing transport.
- `.gitignore` — adds `tmp/` (the upstream-clone scratch dir) and
  `stripchart.mp4` (a reference screen-record dropped at repo root).

### Vi feature subset implemented

`hjkl`, `wWbBeE`, `0 ^ $`, `gg G`, `%`, `f F t T`, counts, operators
`d c y` + motion (or doubled for line), shortcuts `x X D C Y dd cc yy
s S r{c} ~`, insert entries `i a I A o O`, visual mode (`v V`), `u`
/ `Ctrl-R`, search `/ ? n N`, ex `:w :q :wq :s/pat/rep/ :%s/...
:e <file> :reload :play :stop :watch :nowatch`. F12 disables vi mode
entirely (escape hatch — useful if it's misbehaving).

Intentionally NOT implemented: marks, named registers, macros (`q`),
text objects (`iw`, `i"`), Ctrl-D/U/F/B scroll, dot-repeat,
visual-block. Add later if needed.

### What lab needs to do once

1. `git pull`
2. `sudo apt install python3-wxgtk4.0 fluidsynth git`  (skip any already
   present)
3. `./easyabc_vim/install.sh`
4. `python3 ~/projects/HarpHymnal/tmp/EasyABC/test_vi.py` and **report
   any FAIL/ERROR back** — that's the fastest fix loop.
5. `easyabc` to launch. Should land in NORMAL mode immediately;
   status bar shows `-- NORMAL --`. F12 to disable vi mode if needed.

### What's queued but not started: stripchart visualizer

The user wants a piano-roll view alongside (or replacing) the music
score pane — see `stripchart.mp4` at repo root for the target look.
Confirmed scope:
- **Data source**: live ABC text in the editor (NOT HarpHymnal's
  export pipeline — needs to work on any tune, not just hymns).
- **Rendering**: another way to view/play the MIDI; new pane in the
  AUI layout.
- **Colors**: rainbow assigned to the diatonic scale degrees; the
  chord track below uses the same rainbow, colored by chord root's
  scale degree.
- **Playhead**: synced to EasyABC's MIDI playback (`OnPlayTimer` at
  `easy_abc.py:4810`).

Estimated 1-2 days of wxPython panel work. Should hook in next to
`MusicScorePanel` in the existing AUI manager. Will need its own
`StripchartPanel` class with `wx.PaintDC` rendering, plus a tap on
the play timer for playhead position. Not started — flagged here for
the lab box if it picks this up first.

### Known issues to investigate

- The lab box is a **pure Linux machine** (the user said "if you
  were on a pure ubuntu machine like in the lab you could do it") —
  so test_vi.py + future iterative work is much faster there than
  on the home Windows box, where the project lives behind a Z:
  network share that WSL/Windows-Python can't reach. **Lab Claude
  should run test_vi.py and the GUI directly via Bash**, no shim
  pipeline needed.
- GTK warnings during launch (`gtk_box_gadget_distribute: assertion
  'size >= 0' failed`, `Unable to load sb_h_double_arrow from the
  cursor theme`) are upstream wxPython/GTK on Ubuntu 22.04 — not
  caused by anything we did, can be ignored.

---

## Current state (2026-05-02 — second push: VS Code ABC tooling)

`origin/main` head is `7623c9a` — workspace `.vscode/` configs for
ABC playback + PostScript preview via Ubuntu tools. Home-laptop
session, independent of the earlier chord-handout push (`26abe7a`).

### What this push landed

- `.vscode/tasks.json` — three tasks that delegate to Ubuntu CLI tools,
  spawning via `cmd.exe` (no PowerShell, no recursive WSL wrapping):
  - **ABC: Play (abc2midi + fluidsynth)** — generates one .mid per `X:`
    block, plays through fluidsynth with FluidR3_GM soundfont, cleans
    up temp .mid files on exit.
  - **ABC: Render PS (abcm2ps)** — `abcm2ps -O preview.ps`, opens it in
    VS Code, then SendKeys to trigger the PostScript Preview extension
    and close the redundant `preview.ps` editor tab — leaves you with
    just the rendered preview pane next to your `.abc` source.
  - **ABC: Export MIDI (abc2midi)** — writes `<basename>.mid` next to
    the source.
- `.vscode/abc-tasks.sh` — bash helper script the tasks invoke.
  Resolves `${relativeFile}` (with backslash-to-slash conversion for
  Windows paths), runs the right Ubuntu tool, opens results via
  `cmd.exe /c code -r` and `cmd.exe /c start`.
- `.vscode/settings.json` — workspace-scoped terminal config:
  - Default terminal profile: `WSL Ubuntu-22.04 (HarpHymnal)` that
    `--cd`'s into `/home/clementsj/projects/HarpHymnal` on open
    (eliminates the `Failed to translate Z:\...` warning that fires
    when a WSL terminal inherits the Z:-mapped workspace cwd).
  - `automationProfile.windows` set to `cmd.exe` so tasks bypass the
    user's WSL-default integrated terminal and avoid recursive
    `wsl.exe -e wsl.exe` wrapping.
- `.gitignore` — replaced bare `.vscode/` with `.vscode/*` + explicit
  un-ignores for the three files above. Same pattern as the
  pre-existing `.claude/*` block.

### What lab needs to do once

1. `git pull` to get the new `.vscode/` and `.gitignore`.
2. One-time install (only Ubuntu side, only if not already there):
   ```bash
   sudo apt install fluidsynth fluid-soundfont-gm abcm2ps abcmidi
   ```
   (`abcm2ps` + `abcmidi` are usually already installed per the project
   tooling; `fluidsynth` was added 2026-05-02 specifically for this.)
3. **User-level keybindings live outside the repo** (in
   `%APPDATA%\Code\User\keybindings.json` on Windows). To match the
   home-laptop hotkey scheme, add:
   - `Ctrl+Alt+P` → run task `ABC: Play (abc2midi + fluidsynth)`
   - `Ctrl+Alt+V` → run task `ABC: Render PS (abcm2ps)`
   - `Ctrl+Alt+E` → run task `ABC: Export MIDI (abc2midi)`
   - `Ctrl+Alt+Shift+V` → command `postscript-preview.sidePreview`
   - `Ctrl+K 9` → `runCommands` chain
     [`focusFirstEditorGroup`, `closeActiveEditor`] (used internally by
     the SendKeys close-the-`preview.ps`-tab trick)
   - VS Code extensions assumed: `softaware.abc-music` (live preview),
     `ishiharaf.abc-tools` (alt preview + MIDI export),
     `ahnafnafee.postscript-preview` (PS preview pane).

### Why none of this is in the repo at user level

VS Code `keybindings.json` is per-user, per-machine, and not project-
scoped — there is no clean way to ship it from the workspace.

---

## Current state (2026-05-02)

`origin/main` head is `26abe7a` — chord handout PDF (4-page, US Letter,
B&W, XeLaTeX/JuliaMono) plus a comprehensive audit-driven cleanup of
the polychord catalog labels that's been mirrored across handout.tex,
shapedrills.html, polychords.html, and drills.html. Home-laptop session.
**Tablet still needs reinstall** — lab has the device this week.

### What this session landed (on top of yesterday's 9278b16)

- `tablet_app/app/src/main/assets/handout.pdf` (+ `.tex`) — new chord
  handout. Generated by `tablet_app/scripts/build_handout_pdf.py`.
  Catalog mirror of shapedrills.html: every chord rendered as an inline
  30-string lever-harp layout (key of C, lowest C2) plus chord symbol,
  letter-stack/equivalent, and prose description. **Black & white, no
  color**: single-hand notes in bold uppercase, polychord LH in
  lowercase + RH in UPPERCASE (project convention), unplayed dots in
  light gray. 4-column longtable with hanging-indent ragged-right
  descriptions. JuliaMono Medium/SemiBold for chord notation (no
  FakeBold — distorted combining marks); DejaVu Serif for prose.

- **Polychord chord-name cleanup** — re-derived every chord-equivalent
  label by computing the actually-played notes. Big patterns fixed:
  - Spurious "13" claims dropped from labels where the 13th wasn't
    played (1̂9 13, 4̂̂9 13, 5̂9 13, 6̂m11 13, 2̂m11 13).
  - Double-caret typos (1̂̂9, 4̂̂9, 6̂m̂9) replaced with correct labels.
  - Diatonic-handout consistency: ♭9 / ♯11 / ♭13 stripped from chord
    labels (a strictly-diatonic-in-C voicing has no actual accidentals;
    those markers were chord-theory artifacts). Prose comments still
    note "chord-theory ♯11" etc. where the disambiguation helps.
  - Space-separated extension lists (`X̂9 13`, `X̂m9 11`) replaced with
    a single highest-extension chord name and `_<hex>` subscripts to
    subtract missing tones — e.g. `5̂13_7` = dominant 13 minus 7,
    `1̂Δ13_B` = major 13 minus 11 (B = 11 in hex).
  - Parenthetical commentary moved out of the chord column ("1̂̂9 (no
    root in RH)" → "1̂Δ" + clarified comment; "(rare)" / "(variant)"
    → comment prefix).

  ~20 of 35 polychord labels rewritten. Same fixes mirrored in
  `shapedrills.html` (SECTIONS_POLY + SECTIONS_SINGLE) and
  `polychords.html` (SECTIONS) so the HTML view matches the PDF.
  `drills.html` got the SECTIONS_SINGLE flat-stripping too.

- **HTML subscript rendering** — added `renderChord()` helper to all
  three HTML files. Converts `_<hex>+` markers into `<sub>X</sub>` tags
  so labels like `1̂Δ13_B` render visually as `1̂Δ13ᴮ` in the browser,
  matching the PDF. The PDF generator's `render_chord_latex` was also
  bumped from single-char to multi-char greedy hex (so `_79` becomes
  one subscript with two digits).

### QRG cross-check

User has a comprehensive `chordqrg.md` (Chord Quick Reference Guide) in
their Downloads folder describing the scale-degree chord notation
system. The handout/HTML data is **fully consistent** with the QRG:
caret-digit roots, Δ for major-7 vs bare-7 for dominant, ⌀ for
half-dim, slash bass with carets on both sides, extension stacking
("higher implies lower"), etc. The `_<hex>` subscript convention isn't
in the QRG — it's a project-specific compact form for the diatonic
catalog where many voicings genuinely omit standard chord tones. No
conflicts. Could extend the QRG with a section on this convention if
useful.

### Tablet state

Tablet still on `2610908` — yesterday's `9278b16` (Shape Drills) and
today's `26abe7a` (handout + cleanup) both await install on the P90.
Lab side: `cd tablet_app && ./gradlew installDebug` will land both.

### Catalog data drift risk

Catalog data is now in **four** places:
- `tablet_app/app/src/main/assets/drills.html` (single-hand only)
- `tablet_app/app/src/main/assets/polychords.html` (polychord only)
- `tablet_app/app/src/main/assets/shapedrills.html` (both)
- `tablet_app/scripts/build_handout_pdf.py` (both, Python literal)

Mirrored manually in this push. Cleanup candidate: extract to a single
JSON file consumed by all four. Non-blocking.

---

## Current state (2026-05-01)

`origin/main` head is `9278b16` — **Shape Drills** feature (combined
single-hand + polychord catalog with a By-Shape mode + one-page
XeLaTeX practice PDF). Home-laptop session. **Tablet has not been
reinstalled from this machine** — per the 2026-04-30 entries, the lab
side has the device plugged in this week, so the lab needs to run
`cd tablet_app && ./gradlew installDebug` to land the new tile.

Home grid is now **12 tiles** (added one after Shapes): Retab · Retab
Hymnal · Reharm Hymnal · Chopin Hymnal · Boddie Hymnal · Boddie
Drills · Boddie Source · Eb Shapes · Reharm · Docs · Shapes ·
**Shape Drills (new, red `#8B2A1A`, `↗`)**.

### What this session landed

- `tablet_app/app/src/main/assets/shapedrills.html` — combined catalog
  of single-hand chord drills + two-hand polychords. Three toggles:
  **Mode** (Catalog / By Shape), **Show** (All / Single / Poly),
  Harp (Lever 30 / Pedal 47), plus 15 keys. By-Shape mode groups
  every chord by its interval-step signature — `33` for all root-pos
  triads, `33~3~33` for polychords with a 3rd between hands, etc.
  26 single-hand shapes + 6 polychord shapes cover all 154 chord
  variants from both source catalogs. The shape-grouping insight is
  the practice payoff: drill the shape once, you've got every chord
  it produces.
- `tablet_app/app/src/main/assets/shape-practice.pdf` (+ `.tex`) —
  one-page A4 practice list mirroring By-Shape mode. Generated by
  `tablet_app/scripts/build_shape_practice_pdf.py`. XeLaTeX with
  JuliaMono Medium / SemiBold (already shipped at `viewer/font/`)
  for the chord notation + DejaVu Serif for descriptions;
  ragged-right two columns; hanging indent; FakeBold=2.5 on the
  shape signatures so they read as proper bold (only Medium +
  SemiBold ship — no native Bold weight available); body sized at
  **13.7pt** to fill the page without overflowing. Re-run the script
  any time the catalogs change.
- `tablet_app/app/src/main/assets/drills.html`,
  `tablet_app/app/src/main/assets/polychords.html` — the user's
  source pages from earlier in the session. Retained on disk for
  reference but **NOT linked** from the home grid; superseded by
  `shapedrills.html`. Two interim tiles ("Diatonic Drills" +
  "Polychords") were added then removed in the same session in favor
  of the single Shape Drills tile.

### Catalog data drift risk

The single-hand chord catalog (`SECTIONS_SINGLE`, ~70 chords) and the
polychord catalog (`SECTIONS_POLY`, ~35 polychords) are inlined as JS
in `shapedrills.html` AND as Python in
`tablet_app/scripts/build_shape_practice_pdf.py`. If either is edited
without mirroring, the PDF will drift from the HTML view. Cleanup
candidate: extract to a shared JSON file consumed by both. Non-blocking
for now.

### What lab-Claude needs to do

1. `git pull` on the lab machine.
2. `cd tablet_app && ./gradlew installDebug` to push the new tile + 
   pages onto the P90.
3. Verify the **Shape Drills** tile appears at the bottom of the home
   grid (row 3 col 3 in the current 4-col layout) and that the two
   intermediate tiles (Diatonic Drills, Polychords) are NOT showing.
4. Optional sanity: open `shapedrills.html`, switch to **By Shape**
   mode, confirm the shape signatures (e.g. `33`, `33~3~33`) and
   chord rosters render with proper combining circumflex (1̂, 2̂m, …)
   in JuliaMono.

`shape-practice.pdf` is bundled in assets but not linked from the
home grid — accessible at the file path from the WebView if needed,
or just open from the desktop / tablet file manager.

---

## Current state (2026-04-30)

`origin/main` head is `2610908` — Boddie Source 44-page facsimile.
This session landed the entire **Boddie Hymnal** feature end-to-end
(four commits, 4ab1641 → c64a9a6 → 35d46da → 2610908). APK rebuilt +
installed on the P90 from this machine; home doesn't need to
reinstall.

Home grid is now **11 tiles** (added three Boddie tiles after Chopin
Hymnal plus Eb Shapes after Boddie Source): Retab · Retab Hymnal ·
Reharm Hymnal · Chopin Hymnal · **Boddie Hymnal (new, deep blue
`#1F3A5F`, 279)** · **Boddie Drills (new, lighter blue `#4178A8`,
131)** · **Boddie Source (new, purple `#6F4A8A`, 44 pages)** ·
**Eb Shapes (new, green `#2C7C5A`, 24)** · Reharm · Docs · Shapes.

The Boddie family is **conceptually orthogonal** to Retab/Reharm/
Chopin: those families transform texture / harmony / voicing across
multiple sophistication levels (L1-L7 etc.). Boddie is a *single
voice* — Brook Boddie's published arrangement idiom — so it has one
output per hymn, no level switcher. User explicitly said "do not do
multiple levels like you did for retab, reharm, and chopin. This is
just one shot to mimic the Boddie style." Don't refactor it into a
ladder.

Memory pointers added this session:
- `project_boddie_hymnal.md` — what the Boddie style is
- `project_boddie_range_policy.md` — 47-string pedal-harp range
  policy (C1-C2 drone-only, >G7 glissando-only, regular C2-G7)

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
- **2026-05-02 — home-laptop-Claude pushed `26abe7a` (chord handout
  PDF + polychord label cleanup) without installing.** Builds on
  yesterday's `9278b16`; both still await `./gradlew installDebug` from
  whichever machine has the tablet plugged in.
- **2026-05-01 — home-laptop-Claude pushed `9278b16` (Shape Drills
  feature) without installing.** Home doesn't have the tablet plugged
  in; lab does this week. Lab-Claude needs to `git pull` and run
  `./gradlew installDebug` to land it on the P90.
- **2026-04-30 — lab-Claude ran `./gradlew assembleDebug` + `adb
  install -r` directly** (tablet plugged into the lab again this
  week). Tablet now has commit `2610908` installed. Home doesn't
  need to re-install unless something lands after this handoff.
- **2026-04-30 — lab-Claude did the Boddie feature end-to-end**
  (Python emitter + drill generator + tablet UI + APK install).
  Three Boddie tiles + viewer panels are all in `tablet_app/...`,
  the catalog JS lives at `tablet_app/...assets/boddie/boddie_*.js`,
  and 410 SVGs + 44 source PNGs are bundled. Safe to pick up.
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

- **2026-05-02 home** — `26abe7a` `tablet_app: chord handout PDF +
  audit-driven polychord label cleanup`. New chord handout (4-page A4
  US Letter, B&W, XeLaTeX/JuliaMono) catalog-mirrors shapedrills.html
  with every chord rendered as an inline 30-string layout. Generator at
  `tablet_app/scripts/build_handout_pdf.py`. Same push fixes ~20 of 35
  polychord chord-equivalent labels by re-deriving from played notes —
  drops spurious "13" claims, double-caret typos (1̂̂9), space-separated
  extension lists (`X̂9 13`), and chord-theory accidentals from a
  strictly-diatonic catalog. Adds `_<hex>` subscript notation for
  "subtract this chord tone." HTML files (drills, polychords,
  shapedrills) get a `renderChord()` helper so labels match the PDF
  rendering. **Tablet still not re-installed** — lab side, please run
  `./gradlew installDebug`.
- **2026-05-01 home** — `9278b16` `tablet_app: Shape Drills page
  (drills + polychords + by-shape mode) + 1-page practice PDF`. New
  red `#8B2A1A` "Shape Drills" tile combines single-hand chord drills
  and two-hand polychord catalogs (originally added earlier in the
  session as two separate tiles, now consolidated). Adds a By-Shape
  mode that groups every chord by its interval-step signature — 26
  single-hand shapes + 6 polychord shapes cover all 154 chord variants.
  Also adds `shape-practice.pdf` (+ generator at
  `tablet_app/scripts/build_shape_practice_pdf.py`) — a one-page A4
  reference of the shape-grouped practice list, XeLaTeX with JuliaMono
  for chord notation. **Not installed on the tablet from this push** —
  lab side, please run `./gradlew installDebug`.
- **2026-04-30 lab** — `eb_shapes: 24 shape-sweep drills for the
  33-string Eb harp + tablet tile`. New `eb_shapes/build_drills.py`
  generator that drives from `shapes/build_chord_table.py`'s 24
  interval-pattern rows. **One drill per shape, NOT per cell** — the
  user wants to practice the *shape itself*, not every (shape ×
  scale-degree) instance. Each drill walks every in-range (degree x
  octave) combination of the shape and renders them as quarter-note
  rolled chords sorted low→high. Default range: **C2 to G6** (the
  canonical 33-string Eb lever-harp tuning, 33 diatonic strings
  inclusive). 21-31 positions per drill depending on shape width
  (dyad-3 packs 31; tetrad-456 packs 21). All in K:Eb so the harp's
  natural tuning applies without lever flips. Treble/bass split at G3.
  New green `#2C7C5A` "Eb Shapes" tile (prev/next card flipper, 24
  cards). Note: had to drop to `%%scale 0.72` + 22cm pagewidth + 3
  bars/system to avoid abcm2ps "Line too much shrunk" — adjust upward
  if the user wants larger notation. APK rebuilt + installed on the
  P90 from this machine.
- **2026-04-30 lab** — `2610908` `tablet_app: add Boddie Source tile --
  44-page facsimile of Brook's Vol. 1`. Rasterised the source PDF
  (`The-Brook-Boddie-Hymnal-Vol-1-E-flat-version-j6brq2.pdf`, kept
  untracked — copyright watermark) at 110 DPI to 44 PNG pages under
  `tablet_app/app/src/main/assets/boddie/source/page-NN.png` (5.0 MB
  total). Added a third Boddie tile (purple `#6F4A8A`) plus a simple
  prev/next page-flipper viewer panel. Android WebView does NOT render
  PDFs natively, so the per-page-image route is the cleanest in-app
  solution. `pdftoppm` (poppler) is the converter if the source ever
  needs re-rasterising.
- **2026-04-30 lab** — `35d46da` `tablet_app: home tiles + viewer
  panels for Boddie Hymnal & Boddie Drills`. Two new tiles wired into
  the home grid alongside the existing Hymnal tiles. **Boddie Hymnal**
  (deep blue `#1F3A5F`, 279 entries) clones Reharm Hymnal's
  letter-grouped index + search + SVG pane but **drops the level
  switcher** — Boddie is a single-output style, no L1/L2/L3.
  **Boddie Drills** (lighter blue `#4178A8`, 131 cards) is a simple
  card flipper with no index. Both load catalogs from
  `boddie/boddie_hymns.js` / `boddie/boddie_drills.js`. APK rebuilt +
  installed on the P90 from this machine.
- **2026-04-30 lab** — `c64a9a6` `boddie: 131 Boddie Drills cards
  driven from the Chords.html chord matrix`. Drill set originally a
  naive 7×4 (RN × key) = 28 grid; user redirected it mid-session to
  use the (interval-pattern × scale-degree) chord matrix in
  `shapes/build_chord_table.py` as the basis. Now: one card per
  chord-bearing matrix cell. Skipped 4 dyad rows (28 cells), the `45`
  triad row that degenerates to a 4th-dyad name (7 cells), and 2
  dissonant `(♭9)` cells in row `335` → 131 cards. Each card is a
  2-bar ABC fragment in C major: bar 1 = drone+bass octave pluck then
  7-eighth ascending arpeggio of the cell's exact pitch set; bar 2 =
  wide rolled chord with fermata + the rolled treble vertical above.
  Titled by the matrix's chord name (`Cmaj7`, `F6/D`, `Bø7`, …).
  Imports `PATTERNS`, `shape_pitches`, `short_chord_name` from
  `shapes/build_chord_table.py` so the deck stays in sync if that
  table is ever extended.
- **2026-04-30 lab** — `4ab1641` `boddie: add Boddie Hymnal emitter
  + 279 hymns rendered in Brook Boddie style`. New `boddie/` project
  modelled on `reharm/hymnal/` but **single-output, no level loop**.
  User read in *The Brook Boddie Hymnal Vol. 1* (Seraphim Music 2020,
  16 pieces) and asked the corpus be re-styled in Brook's idiom: bass
  note + ascending eighth-note arpeggio LH, melody pass-through with
  octave doubling on cadence bars, `!arpeggio!` rolls on cadence
  chords + final chord, `!breath!` at non-final phrase ends, fermata
  + L.V. on the close, `Q:1/4=72 "Slowly, with great expression"`.
  Harmony is the Reharm L2 14-chord pool (triads lifted to diatonic
  7ths) — Boddie does NOT reharmonize, just enriches. Range policy
  for the **47-string pedal harp** (NOT lever harp like Brook's
  source): C2-G7 regular, C1-C2 LH octave-pluck drone-only on
  opening + cadence (avoids muddiness), >G7 reserved for glissando
  flourishes (not yet emitted). Style fingerprint in `boddie/BODDIE.md`;
  range policy saved in user memory `project_boddie_range_policy.md`.
  All 279 hymns rendered cleanly (one early failure on
  `lift_high_the_cross` traced to a final-bar with all-zero-duration
  events; fix: skip decoration when no voiced token exists).
- **2026-04-29 home** — `0a9bee4` `shapes/STACKS, viewer fonts:
  caret-digit reference + JuliaMono in viewer`. Reviewed an external
  tarball of harp-theory artifacts (`~/Downloads/harp-theory-artifacts.tar.gz`
  — diatonic chord-stacks, fingerings, diads, chromatic-intervals
  handouts) and folded the directly-relevant parts into the project.
  New `shapes/STACKS.md` consolidates the chord-stacks table, diatonic
  diads, and an alternative-fingerings sampler in caret-digit (^1..^7)
  notation — the user explicitly liked carets over RN for *generic-
  interval / scale-degree* contexts (saved as
  `feedback_caret_digits_in_tables.md` in memory). RN remains in
  *functional* contexts (mapper output, lead-sheet labels,
  `render_rn_markup` over score bars). `shapes/build_html.py` adds
  `STACKS` to the `DOCS` list; `_nav.html` and `index.html` updated
  to expose the new page; pandoc rebuild propagated the new nav link
  through every shape doc. Brought `viewer/` to parity with
  `shapes/style.css`: copied `JuliaMono-{Medium,SemiBold}.ttf` into
  `viewer/font/` and added `@font-face` + `.deg` to `viewer/app.css`.
  Bundled the four standalone PDFs (printable landscape layout) under
  `docs/handouts/` with their .tex sources, plus a tablet-side mirror
  at `tablet_app/app/src/main/assets/docs/handouts/` (PDFs only).
  STACKS.md links to `../docs/handouts/` which resolves on both
  desktop (repo root) and tablet (assets root). Tablet shapes mirror
  rebuilt; existing `shapes/font/` JuliaMono already covers .deg
  rendering on the tablet — no font copy needed there. APK rebuild
  picks up the new asset files via standard `mergeDebugAssets`.
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
