# HANDOFF — reharm

Cross-machine sync notes for working on `reharm/` from multiple Claude Code
sessions. Read on entry, append when leaving. Latest entry at the bottom.

---

## 2026-04-24 (bootstrapped from within the `retab/` session)

**Where this project came from.** The Retab Hymnal landed well — 279 hymns
produced at L6-partial-L7, harp-idiomatic LH (no piano stomping), and
shipped end-to-end on the tablet app. The user's direction:

> "the retab you did was a big success. create a new project ../reharm
> that focuses on jazz version of the open hymnal. the other reharm was
> a big disaster. you 7 levels of improvements and limited chord pool
> really helped the effort."

**Target:** same 47-string lever harp. Same tactics that made Retab land:

1. 7-level ladder (`REHARM.md`) as the steering document.
2. Strictly enumerated chord pool (~16 chord types).
3. Single-file emitter + single bulk builder.
4. End-to-end deliverable at every level.

**What was scaffolded in this bootstrap session** (from the retab working
directory):

- `CLAUDE.md` — project guide.
- `REHARM.md` — the 7-level ladder. Read this before writing code.
- `HANDOFF.md` — this file.
- `hymnal/reharm_hymnal.py` — emitter, with L1 implemented and
  L2–L7 clearly stubbed (see the `apply_level_*` functions).
- `hymnal/build_hymnal.py` — bulk builder mirroring retab's.

**What was NOT done** (deliberately left for the first in-project session):

- Run the L1 emitter on a single hymn to confirm it compiles.
- Run the bulk builder — no output directory chosen yet.
- L2 implementation (diatonic 7ths — the smallest real step).
- Tablet integration (new "Reharm Hymnal" tile). Deferred until L4+.

**First-order tasks for next session:**

1. `cd /home/james.clements/projects/reharm`.
2. Read `REHARM.md` in full. The ladder is the product roadmap.
3. Run L1 on `abide_with_me` and eyeball the ABC. Commit no expectations
   about what "good" looks like until L1 compiles.
4. Implement L2 (the easiest step — pool expansion only, no root motion).
5. Bulk-build L1 and L2 side by side, inspect 5–10 hymns in the browser.

**Old-reharm pitfalls to avoid.** See `../HarpHymnal/reharm/`,
`trefoil/reharm/`, `data/reharm/tactics.json`. That effort spread across
schema/selector/renderer/catalog modules before emitting a playable hymn.
**Do not touch those directories.** Reharm-new is a standalone project.

**Memory notes to preserve across sessions:**

- `feedback_no_piano_stomp.md` — carried over from retab memory. Applies
  unchanged: never re-strike the same triad on consecutive beats on a
  harp. Walking arpeggios or single strike + ring.

**Shared dependencies with retab:** melody/pitch/duration rendering
(`pitch_to_abc`, `_safe_note_dur`, `render_melody_bar`, etc.) was
**duplicated** into `reharm/hymnal/reharm_hymnal.py` rather than
imported. Short-term duplication is fine; both codebases will diverge.
