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

Memory index (if it exists): `~/.claude/projects/-home-james-clements-projects-HarpHymnal/memory/MEMORY.md` — user's locked-in preferences. **If this directory does not exist on the home laptop, bootstrap it first (see next section).**

---

## Bootstrap Claude's memory (do this FIRST on a fresh laptop)

Memory is per-machine. The lab machine built up a set of preference files across sessions; the home laptop's `~/.claude/projects/.../memory/` dir is empty until you recreate it. **Before executing step 1**, check:

```bash
ls ~/.claude/projects/-home-james-clements-projects-HarpHymnal/memory/ 2>&1
```

If that directory is empty or missing, **write the following 8 files verbatim** (Claude has Write permission to its own memory dir by default — just create each file at the path shown). The `MEMORY.md` index goes at the top level; the others are sibling files.

The exact parent directory path depends on where the repo lives on the home laptop. Find it with:

```bash
# Claude's working dir → escape chars for the memory dir name
echo "~/.claude/projects/$(pwd | sed 's|/|-|g')/memory/"
```

Adjust the paths below to match.

### Memory file 1 — `MEMORY.md` (the index)

```markdown
- [Parallelize with agents](feedback_parallel_agents.md) — user said "I have 40 cpus. use multiple agents" — default to aggressive parallelism on this repo.
- [Refactor handoff via PROMPT.md](project_refactor_handoff.md) — lab-Claude starts each session by reading PROMPT.md and continuing the 8-step build order.
- [Commit+push per numbered step](feedback_commit_per_step.md) — PROMPT.md mandates a separate commit + push per numbered build step so the user can follow from the tablet.
- [legacy/ and source/HarpChordSystem.tex are frozen](feedback_frozen_paths.md) — never modify. HarpTrefoil.tex must stay byte-exact to HarpChordSystem.tex.
- [vii° vs vii○ Unicode gotcha](project_vii_unicode_gotcha.md) — pool JSON stores U+00B0, grammar uses U+25CB; bridge at query boundary.
- [pool = paths ∪ reserve](project_pool_paths_reserve.md) — canonical vocabulary terminology the user settled on mid-refactor.
- [Stop asking, just execute](feedback_stop_asking_execute.md) — once the goal is stated, pick a sane default and keep moving; only ask at real forks.
- [git stash is shared across worktrees](feedback_stash_across_worktrees.md) — stashing in main while an agent-worktree is active can let the agent pop and claim those changes.
```

### Memory file 2 — `feedback_parallel_agents.md`

```markdown
---
name: Parallelize with agents
description: User has 40 CPUs and prefers parallel subagents over sequential execution on this repo.
type: feedback
---
The user explicitly said "I have 40 cpus. use multiple agents" early in the HarpHymnal refactor.

**Why:** the build order in PROMPT.md is multi-step, and many of the steps are mechanical ports of independent files. Serial execution wastes the box.

**How to apply:** when starting a multi-step task here, identify which steps are independent and spawn them in parallel worktree-isolated agents. Merge + commit from the main worktree in dependency order. Don't let agents commit/push — serialize git operations in the main thread. Still respect the dependency DAG (e.g. pool.py → mapper.py → piano-score renderer).
```

### Memory file 3 — `feedback_commit_per_step.md`

```markdown
---
name: Commit+push per numbered step
description: Each numbered build step in PROMPT.md gets its own commit + push so the user can follow progress from the tablet.
type: feedback
---
For the HarpHymnal refactor, land one commit per numbered step and push after each.

**Why:** the user watches progress asynchronously from a tablet; per-step commits let them review each landing independently without digging through a big merged diff.

**How to apply:** never batch multiple steps into one commit. Run `python3 -m pytest tests/ -q` before each commit — all green required. Commit message HEREDOC ending with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`. Push to `origin main` after each commit.
```

### Memory file 4 — `feedback_frozen_paths.md`

```markdown
---
name: legacy/ and source/HarpChordSystem.tex are frozen
description: Never modify legacy/ or source/HarpChordSystem.tex; HarpTrefoil.tex must stay byte-exact to HarpChordSystem.tex.
type: feedback
---
Hard rules on the HarpHymnal repo:

- `legacy/` is a frozen snapshot of the pre-refactor code — read for reference, never modify, never import from `legacy.*`.
- `source/HarpChordSystem.tex` is the canonical pedagogy — sacred, no edits.
- `source/HarpTrefoil.tex` must stay byte-exact to HarpChordSystem.tex. Pedagogy edits land in HarpChordSystem.tex first, then `cp source/HarpChordSystem.tex source/HarpTrefoil.tex`. `tests/test_pool_fidelity.py` enforces this.
- New scripts live under `grammar/`, `trefoil/`, `parsers/`, `mapper/`, `techniques/`, `drills/`, `renderers/`, `viewer/`, `cli/`, `data/`, `tests/`.

**Why:** the legacy tree is a reference monument for the user to compare against; drift in the pedagogy source would corrupt the 118-fraction vocabulary the entire project is built around.

**How to apply:** if a fix requires editing legacy code, instead port the logic to the new layout and leave the legacy copy untouched. If a pedagogy change is truly needed, flag it to the user — never silently edit HarpChordSystem.tex.
```

### Memory file 5 — `feedback_stop_asking_execute.md`

```markdown
---
name: Stop asking, just execute
description: Once the goal is stated, do not pause to confirm direction — ship the work
type: feedback
---
Do not pause mid-task to ask "should I do X or Y?" or "want me to loosen/tighten?" when the overall goal is clear. Execute the obvious next step and report what you did.

**Why:** The user set the goal at the start. Repeated "which option?" prompts are noise that slow the loop. User explicitly called it out: "why do you keep asking me questions. Is the goal unclear?"

**How to apply:** For HarpHymnal refactor tasks, when a tuning parameter or scope choice comes up mid-execution, pick a reasonable default and keep moving. Flag the choice in the end-of-turn report so the user can steer if they disagree. Only stop to ask when the path genuinely forks between two materially different outcomes that can't be reversed.
```

### Memory file 6 — `feedback_stash_across_worktrees.md`

```markdown
---
name: git stash is shared across worktrees
description: Stashing in main while an agent-worktree is active can let the agent pop and claim those changes
type: feedback
---
`git stash` pushes to a single stash list shared by every worktree of the repo. Launching an agent with `isolation: "worktree"` does NOT give that agent a separate stash space. If you stash uncommitted work in main and then an agent does `git stash pop` in its worktree, your changes are now committed on the agent's branch (not lost, but the naive `git stash pop` in your shell will say "no stash entries found").

**Why:** This happened during the HarpHymnal Task #10 gap-closing — stashed `mapper/harp_mapper.py` + `renderers/lilypond.py` WIP to run `git merge <agent-branch>`, and the already-running agent popped the stash in its worktree, then committed it. Recovery path: `git reflog` + find the agent branch that holds the commit.

**How to apply:** Before stashing in a repo that has active agent worktrees, either (a) commit the WIP to a scratch branch instead, or (b) include the WIP in the agent's prompt so it's deliberately carried forward. Also, after running `cd` / working across worktrees, always `pwd && git branch --show-current` before destructive operations — the `claude-code` session can land in a worktree without realizing it.
```

### Memory file 7 — `project_refactor_handoff.md`

```markdown
---
name: Refactor handoff via PROMPT.md
description: PROMPT.md is the canonical session-start handoff for the HarpHymnal grammar-native refactor.
type: project
---
HarpHymnal is in a multi-session grammar-native refactor. Each session starts by reading `PROMPT.md` at the repo root, which carries the current step queue, file precedence rules, and locked-in style/pedagogy choices.

**Why:** work spans multiple sessions / multiple machines (lab, home laptop, tablet). PROMPT.md is the shared state — the user treats it as the standing instruction.

**How to apply:** at the start of a session, read `PROMPT.md` + `SDD.md` + `GRAMMAR.md` + `TREFOIL.md` before touching code. Cross-check against git log (`git log --oneline -5`) to see what's already landed. Execute steps in order.
```

### Memory file 8 — `project_pool_paths_reserve.md`

```markdown
---
name: pool = paths ∪ reserve — canonical terminology
description: The user's canonical taxonomy: pool (118) = paths (42 cycle) + reserve (76 color). Use these names, not the legacy jazz_progressions/stacked_chords.
type: project
---
The HarpHymnal vocabulary model:

- **pool** = the full 118-fraction vocabulary.
- **paths** = the 42 fractions that walk the six trefoil cycles (2nds/3rds/4ths × CW/CCW).
- **reserve** = the 76 coloristic single-sonority fractions held for substitution and variety.
- `pool = paths ∪ reserve`.

**Why:** the legacy TeX used `jazz_progressions` / `stacked_chords` as section names, and TREFOIL.md briefly used "pool" for just the 76 leftover — creating a collision where "pool" could mean 118 OR 76. The user settled the terminology explicitly: pool is all 118, and the two subsets are named for their pedagogical role (on-path vs reserved-for-substitution).

**How to apply:**
- In new code, use `source='paths'` and `source='reserve'` on PoolEntry.
- In JSON: top-level keys are `paths` and `reserve` (not `jazz_progressions` / `stacked_chords`).
- In prose/docs: say "paths" and "reserve"; reserve the word "pool" for the full 118.
- The legacy TeX is frozen and still uses `\sexcA/B/C` (paths) and `\spt` (reserve) — don't rename those, just bridge at the rebuild layer.
- ipool scheme is `{degree}{rank:02d}`: first digit = LH scale-degree 1..7, last two digits = rank within that degree. Paths occupy the low ranks in each column; reserve occupies the high ranks. Numerically, path chords have the lowest ipools within their own degree column (not globally — `121` < `201` even though `201` is a path chord).
```

### Memory file 9 — `project_vii_unicode_gotcha.md`

```markdown
---
name: vii° vs vii○ — pool/grammar Unicode mismatch
description: Leading-tone chord is stored as U+00B0 (°) in the pool JSON but U+25CB (○) in the grammar — expect to bridge at lookup boundaries.
type: project
---
The 118-fraction pool stores the leading-tone chord as `vii°` (U+00B0 DEGREE SIGN — inherited from `source/HarpTrefoil.tex`), but `grammar/parse.py` and the rest of the grammar use `vii○` (U+25CB WHITE CIRCLE).

`parse_roman('vii○')` succeeds; `parse_roman('vii°')` raises `ValueError`. A naive `pool.all_voicings_of('vii○')` returns zero matches because the stored entries don't match.

**Why:** the TeX is the sacred pedagogy source and uses `°`. The grammar EBNF v4 adopted `○` (whitespace-free, visually unambiguous) as the canonical form. Both existed before the fidelity gate landed, and neither side can be edited unilaterally (TeX is sacred, grammar is frozen).

**How to apply:** when a new module queries the pool with a grammar-form numeral, translate `vii○ → vii°` at the query boundary. `drills/build.py::_pool_numeral` is the current reference implementation. Longer-term fix would be a normalizer inside `trefoil/pool._build_entry` that rewrites stored romans to grammar form on load — then consumers can query with either spelling. Defer the global fix until someone explicitly schedules it; don't let it block new work.
```

After writing all 9 files, verify with:

```bash
ls ~/.claude/projects/-home-<user>-<path>-HarpHymnal/memory/
# Should show: MEMORY.md + 8 others
```

Then proceed to the step queue below.

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
