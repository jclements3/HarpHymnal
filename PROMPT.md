# PROMPT.md — home-laptop Claude handoff

Continue the HarpHymnal refactor. State is on `origin/main` at commit **`87f0f09`**.
The 8-step refactor build order is done; this handoff picks up from the end of the "drill ↔ hymn reharm" gap-closing pass.

Read these first, in order:

1. `CLAUDE.md` — memory hooks, file-precedence rules
2. `SDD.md` — pipeline, grammar v4, directory layout
3. `GRAMMAR.md` — authoritative EBNF v4
4. `ROADMAP.md` — living plan
5. `ISSUES.md` — known bugs + Trefoil vocabulary gaps
6. `TREFOIL.md` — 118-fraction pedagogy (do **not** re-teach)

Memory index: `~/.claude/projects/-home-james-clements-projects-HarpHymnal/memory/MEMORY.md` — user's locked-in preferences (parallelism defaults, commit-per-step, frozen paths, etc.).

---

## Hard constraints (non-negotiable, same as before)

- **`source/HarpChordSystem.tex` is sacred** — never modify.
- **`source/HarpTrefoil.tex`** must stay byte-exact to the above (`tests/test_pool_fidelity.py` rejects drift).
- **`legacy/` is frozen** — never import from `legacy.*`.
- **Strictly diatonic** — only the 118-fraction pool; no chromatic substitutes, no tritone subs, no modal interchange.
- **Parallelize aggressively** — user has 40 CPUs. Use `--jobs 40` for batches; spawn multi-agent worktrees for independent subtasks.
- **Commit + push after every numbered step** below so the user can track progress from the tablet.

---

## What shipped last session (commits `eafa654..87f0f09`)

1. **`mapper.harp_mapper.pick_with_techniques()`** — Third sub / Deceptive sub / Common-tone pivot / Quality sub as candidate RN alternates, gated by cycle-edge / phrase-end / repeated-chord context so the trefoil-path pedagogy wins on cycle moves. `Pick.technique` field records which technique (if any) was applied.
2. **Approach pickup** in `renderers/lilypond.py::layout_bar_approach_pickup` — `dominant_approach` as a V-chord pickup on the last beat of interior pre-cadence bars. Other 4 approaches (step/third/suspension/double) exist as pure functions in `techniques/approach.py` but are **not yet wired**.
3. **Voicing hints** — `_voicing_plan` / `_apply_voicing_hint` / `_inject_pedal_tone` wire **inversion / density / pedal**. Other 3 (stacking / open-closed-spread / voice-leading) are **not yet wired**.
4. **Full 279-hymn re-render** at `data/scores/tech_full/` — 1 326 label swaps (28% of 4 681 bars), 1 001 approach pickups across 269/279 hymns; 57 untouched (mostly minor). Run takes ~58 s with `--jobs 40`.
5. **LilyPond duplicate-time-signature fix** — `\once \omit Staff.TimeSignature` before `\voiceTwo` in `upper` and before the first LH event in `lower`. Killed the pre-existing `3/4 3/4` that appeared on every hymn's first grand staff.
6. **Tablet app** (`tablet_app/`) — bundled 294 reharmed SVGs; Hymns tile opens an in-WebView **A–Z collapsible left index** (all groups start collapsed) + right-pane SVG score viewer; search input auto-expands matching letter groups. Installs on device `P90YPDU16Y251200164` as `com.harp.harphymnal.drills`. Build with `cd tablet_app && ./gradlew assembleDebug`.

---

## Open queue — do in order, commit+push after each

### Step 1 — fix composite pool-label rendering (`viii`, `V7iii`, …)

Some pool reserve bichords have composite LH/RH Roman names like `V7iii` (= V7 over iii) that get emitted directly as `\bold "V7iii"` or even `\bold "viii"` in the score markup — reading like a nonsense roman numeral. Visible on e.g. Silent Night bar 3 (ipool 521).

- Start: `grep -n 'viii\|V7iii' data/scores/tech_full/silent_night.ly` and trace back through `renderers/lilypond.py::_rn_string` / `chord_label_markup` to where composite numerals get stringified.
- Fix: split composite numerals (two Roman-numeral runs glued together) into stacked top/bottom labels inside the markup, or slashed `V7 / iii` form.
- Verify: rebuild `silent_night.ly` — bar 3 LH label reads stacked/slashed, not `viii`.

Commit: `renderer: split composite pool labels in score markup (PROMPT step 1)`

### Step 2 — wire the 4 remaining Approach techniques

`techniques/approach.py` has 5 pure functions; only `dominant_approach` is wired. Add context-aware selection:

- `step_approach` — when next bar's root is a diatonic 2nd away
- `third_approach` — when the current bar is a repeated chord (variety)
- `suspension_approach` — phrase-final cadence bars (a 4th above target, held)
- `double_approach` — rare escape for long plain-I stretches

Extend `_should_use_approach_pickup` / `_approach_pickup_fig` in `renderers/lilypond.py` to pick among the 5 based on context. Surface the chosen technique name in `assignment['technique']`.

Verify: rebuild the 8-hymn sample (`silent_night, amazing_grace, o_come_o_come_emmanuel, hark_the_herald_angels_sing, joy_to_the_world, a_mighty_fortress_is_our_god, beautiful_savior, what_child_is_this`) and confirm 2–5 approach pickups per hymn with a **mix** of approach techniques (not all Dominant).

Commit: `renderer: wire step/third/suspension/double approaches (PROMPT step 2)`

### Step 3 — wire remaining Voicing techniques

Extend `_voicing_plan` + `_apply_voicing_hint`:

- `stacking` — add a quartal voice on long cadence bars
- `open_closed_spread` — alternate per phrase (closed voicing on verse opening, open on cadence)
- `voice_leading` — re-rank voicings when multiple entries tie on `score_entry`

Commit: `renderer: wire stacking / open-closed spread / voice-leading (PROMPT step 3)`

### Step 4 — relax minor-mode technique guard

`pick_with_techniques` short-circuits on `if mode == 'minor'`; 57/279 hymns get zero substitution activity. Minimum useful enablement:

- **Quality sub** in minor (v ↔ v7, i ↔ iΔ both stay diatonic)
- **Deceptive sub** in minor (V → VI is as musical as V → vi in major)
- **Keep Third sub / Common-tone pivot skipped** — the Ionian ladder in `_third_sub_alternates` / `_common_tone_pivot_alternates` isn't valid in Aeolian; relaxing them needs an Aeolian-aware ladder first.

Verify on `o_come_o_come_emmanuel` and `what_child_is_this` (currently 0 swaps → expect a handful).

Commit: `mapper: enable Quality sub + Deceptive sub in minor mode (PROMPT step 4)`

### Step 5 — wire Placement techniques

`techniques/placement.py` has `anticipation` and `delay` — currently unused. Wire them as **rhythmic shifts** on the LH first-beat block chord:

- `anticipation` — pull the beat-1 block chord into the previous bar's last 8th (syncopated push)
- `delay` — push the beat-1 block to beat 1.5 (suspension feel)

Apply rarely (1–2 per hymn) to avoid rhythmic chaos. Fire only on non-cadence interior bars.

Commit: `renderer: wire anticipation / delay as rhythmic shifts (PROMPT step 5)`

### Step 6 — re-render 279 + rebundle tablet app

```bash
python3 -m cli.scores_build --all --jobs 40 --out-dir data/scores/tech_full
python3 tablet_app/build_hymns_bundle.py
cd tablet_app && ./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.harp.harphymnal.drills/.MainActivity
```

Diff a few hymns visually on the tablet vs. the pre-step-1 versions.

Commit: `tablet_app: re-render 279 + rebundle with steps 1–5 applied (PROMPT step 6)`

---

## Backlog (not numbered — grab when a step finishes fast)

- **Tighten the 24 high-swap-rate hymns** (>50% bars swapped). Log per-hymn observations to `ISSUES.md`.
- **Tablet app UX**: persistent `← Home` button while a hymn is open (currently you have to close the letter group first); favorites marker; a "recent hymns" row.
- **Time-sig fix verification on compound meters** (6/8, 9/8) and minor hymns — the `\once \omit` fix was tested on Silent Night (3/4 major) only. Spot-check a 6/8 hymn and a minor hymn; widen the fix if duplicates persist.
- **Drill icon after the hymns/ asset bundling** — the 60 MB of SVGs could have shifted mipmap priorities; check the Drills icon still shows correctly in the launcher.
- **Dead code**: `Bridge.launchHymns()` in `MainActivity.java` + related string constants are now unused — remove them. Same for the `Trefoil Hymnal app not installed` Toast.

---

## Things NOT to touch

- `source/HarpChordSystem.tex`, `source/HarpTrefoil.tex`, anything in `legacy/`.
- `data/trefoil/HarpTrefoil.json` (the 118-fraction pool data) — the loader can change; the data file cannot.
- The ipool numbering scheme `{degree}{rank:02d}` — the drills app and handout both parse it.
- `grammar/` dataclass field names — these are the stable interface. Adding new fields is OK; renaming is not.
- `hymnal_export/` — the old 294 comprehensive-JSON records, superseded by `data/hymns/` but still referenced in CLAUDE.md.

---

## Startup sanity check

```bash
cd /home/james.clements/projects/HarpHymnal    # adjust path for home laptop
git log --oneline -5      # expect 87f0f09 on top
git status --short        # should be clean
pytest tests/ -q          # should pass (158 tests last run)
python3 -m cli.scores_build --title silent_night --out-dir /tmp/verify --no-compile
```

If any of those are unexpected, investigate before starting step 1.
