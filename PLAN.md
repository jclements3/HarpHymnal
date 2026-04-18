# HarpHymnal Piano-Score Plan

Living plan document. Updated as work progresses, bugs surface, and decisions land. **Always read this first when starting a session on the piano-score effort.**

Companion documents:
- `ISSUES.md` — bugs, bad-sounding moments, HarpChordSystem vocabulary gaps
- `HARP_CHORD_SYSTEM.md` — system pedagogy (do not modify casually)
- `ChordAnalysis.md` — data-driven curation audit

---

## Goal

Render each hymn's reharm data as a **playable grand-staff piano score** suited to a 4-finger-per-hand lever harpist. Output should sound like a jazz interpretation — rolled chords, mellow fills, bebop runs, or grand strikes depending on context — **never** like SATB "stomp stomp" block chords.

---

## Core model (settled)

- **Harp strings ring**: plucked notes sustain until damped. Sequenced plucks build the chord sonority over time rather than striking simultaneously.
- **Melody on RH**: hymn melody (S1V1) plays at its natural rhythm. Those notes sustain.
- **RH chord-fraction fill**: remaining RH fraction fingers pluck in the gaps between melody notes; those also sustain.
- **LH chord-fraction fill**: LH arpeggiates its figure independently on its own rhythm.
- **By end of bar**: melody + full fraction all ringing — the complete chord sonority, delivered as jazz arpeggiation not a block chord.
- **All ornamentation diatonic**: harp is tuned to one key per piece; no chromatic approach tones.
- **LH pedal pluck**: V:3 opens each bar with a deep pluck of the chord's RN-root (at the harp's low octave), then the LH fraction arpeggio on top. Low roots reinforce the harmony — the ringing pedal string sustains under everything. Never pop a root in mid-register; only deep, where it's a foundation instead of a clash.
- **Hands cross freely**: LH and RH string-areas are *not* territorial. LH can start low with a chord figure, sweep up, and hand off to RH; RH can dip below the melody into LH territory and hand back. Hands rendezvous mid-instrument. Idiomatic harp writing — think Tchaikovsky *Sleeping Beauty* cascades — treats the whole register as one continuous surface.

---

## Style palette

Per-bar style is chosen based on phrase cycle color, position in phrase, and mood word.

| Style | When | LH | RH |
|---|---|---|---|
| **Grand chord** | phrase-ending tonics; tight transit budget | `1234` beat 1 | melody + `1234` beat 1 |
| **Rolled** | lyrical mid-phrase | `1-2-3-4` over 2 beats | melody + cascading fills |
| **Bebop** | busy cycle walks | fast `1-2-3-4` on 16ths | melody + offbeat fills |
| **Mellow pair** | held-chord bars | `12-34` beats 1 & 3 | melody + `23-14` |
| **Shimmer** | modal / pool bars | `1-23-4` spread | melody + single-finger sparse |
| **Split triad** | half-cadence moments | `123-4` | `1-234` |

---

## Register & voice-leading guide

Physical range assumed: **34-string lever harp** (≈ A2–F6). Smaller harps clamp the pedal up an octave automatically.

### Target register per voice

| Voice | Range | Role |
|---|---|---|
| **Pedal (grace)** | Bb1–F2 (base_octave=1, clamp at G1) | Deep root anchor — always *below the bass staff* (1–2 ledger lines down). Rings under everything. Always the lowest pitch in the bar. |
| **LH figure** | C3–G4 | Primary harmonic content. Bass-clef register. |
| **RH fill** | A3–F5 | Texture layer — sits *below or around* the melody, never consistently above. |
| **Melody** | as written | Dominant line. Not rewritten, not doubled, not obscured. |

### Spacing rules

- **Pedal → LH-figure bottom**: ≥ a perfect 4th (so the pedal reads as its own register, not a voice-extension of the figure).
- **LH-figure top → RH-fill bottom**: ≥ a minor 3rd (avoid muddy tenor clash).
- **RH fill must not double the melody pitch** in the same octave — causes phase cancellation and flattens the melodic profile.
- **RH fill top ≤ highest melody pitch** in the bar — the melody must remain the top voice.

### Density per style (thinning / dropping voices)

| Style | Pedal | LH figure | RH fill |
|---|---|---|---|
| Grand chord | grace | full stack | full stack |
| Rolled | grace | arpeggiated over bar | sparse (1 note per beat) |
| Bebop | grace | short stab then rest | moving line (not a stack) |
| Mellow pair | grace | split 12 / 34 | split 23 / 14 |
| Shimmer | grace | spread arpeggio | **drop entirely** |
| Split triad | grace | 123 then 4 | 1 then 234 |

### Voice leading (deferred — Phase 1.5)

Between bar N and N+1, when the vocabulary offers multiple fractions for the same RN, prefer the one that **maximizes common tones** and **minimizes total interval movement** vs. the prior bar's voicing. Layer on top of the per-bar selection, not a replacement. Not yet implemented — skeleton first, voice-leading optimization after styles work.

### Dominance

- **Melody** is the most prominent pitch in every bar. No accompaniment pitch above it except briefly for color.
- **Pedal** is *felt*, not *thumped* — one grace stab per bar, no repeats.
- **LH figure** carries the chord identity; **RH fill** is texture, not harmonic ground truth.
- If RH fill would double a melody pitch in the same octave, drop that fill note.

---

## Ornament palette (phases 2–4)

Applied only to ~20-25% of melody notes, where transit budget allows. Never on fast runs.

| Ornament | Type | Use |
|---|---|---|
| **Ratchet up/down** | entrance | building to a climax / cooling into resolution |
| **Upper / lower neighbor** | entrance | lyrical mid-phrase emphasis |
| **Enclosure** (both-sides) | entrance | phrase-boundary cadences, jazz hallmark |
| **Fall-off** | exit | conversational descent |
| **Lift** | exit | anticipatory rise |
| **Passing run** | exit or bridge | filling the interval to the next melody note |
| **Bridge merge** | exit + entrance combined | exit of note N scalar-runs into approach of note N+1 |

---

## Playability rules (HARD — cannot be violated)

1. **Melody is mandatory** — every S1V1 note plays at its written duration, regardless of anything else.
2. **Transit time is real** — RH moving between melody-string and fraction-string area costs ~100-200 ms. The bar's rhythm must leave that gap.
3. **If transit budget is tight**, fall back to simpler style (grand chord > rolled > full arpeggio). Never pack plucks beyond physical feasibility.
4. **Diatonic only** — all ornaments use current-key scale tones. No chromatic approach.
5. **Ornaments last-priority** — phases 2-4 layer on top of phase-1 skeleton only when surplus time exists.

---

## Phases

### Phase 0 — Foundations ✅ DONE

- [x] 118-chord vocabulary curated (inversion-biased, hex alphabet, all verified playable)
- [x] 294 reharm JSONs built from OpenHymnal.abc via current mapper
- [x] `hymnal_html/review.html` — 294 hymns, alphabet-grouped nav, ID search, typography matched to LaTeX
- [x] `HarpChordSystem.tex/pdf/json` — authoritative handout, 2-page layout
- [x] `HARP_CHORD_SYSTEM.md` pedagogy doc — tonic-centric grammar, cycles, pool, chromatic-bypass substitution

### Phase 1 — Playable skeleton  ✅ Silent Night validated

Deliverable: grand-staff piano scores that are *playable* — correct rhythm, correct pitches, respect transit budgets. No ornaments.

- [x] `tools/build_piano_score.py` — LilyPond emitter (not ABC; better engraving, SVG + PDF + MIDI output)
- [x] Prototype: Silent Night (3/4) — arrangement approved 2026-04-17
- [x] Per-bar style dispatch: `grand_chord` / `strum_pickup` / `cadence_arp`
- [x] LilyPond markup for chord-fraction labels (RN inversions rendered as superscripts, matches LaTeX `\fracA`)
- [x] Phrase-ending enclosure ornaments (upper + lower diatonic neighbor grace pair)
- [x] HarpHymnal.html — left nav + right split score/reharm iframe
- [ ] Transit-budget calculator (deferred — current dispatch is phrase-position only)
- [ ] Play each through at the harp — tag "sounds bad" moments in ISSUES.md

### Current style implementation (2026-04-17)

| Style | When | LH pattern (3/4 / 4/4) |
|---|---|---|
| `grand_chord` | very first bar, very last bar | Block chord full bar, arpeggiated, with pedal grace |
| `strum_pickup` | phrase interior, phrase opener | Beat-1 block chord (quarter) + middle eighths (chord tones) + final-beat quarter = upper diatonic neighbor of next chord root |
| `cadence_arp` | phrase ender (not last bar) | Same skeleton as strum_pickup, but final-beat quarter = current chord root (landing) |

The skeleton is single-voice — the harp's ringing strings deliver the "chord still sounding under the motion" effect naturally. Pedal-unison with LH bottom is accepted (reads as grace-note re-strike of the same string).

### Phase 2 — Entrance ornaments

- [ ] Enclosure on phrase-boundary long melody notes (≥ 1 beat, first or last of phrase)
- [ ] Upper/lower neighbor on mid-phrase long notes (≥ 1 beat, alternate direction)
- [ ] Density cap: ~20-25% of melody notes get any ornament
- [ ] Transit-budget check must still pass after ornament insertion

### Phase 3 — Exit ornaments

- [ ] Fall-off on descending phrase-endings
- [ ] Lift on ascending phrase-endings
- [ ] Passing run when interval to next melody note is a 3rd+
- [ ] Density cap: ornament density incl. phase-2 ornaments still ≤ 25%

### Phase 4 — Bridge merging

- [ ] Detect when an exit from note N can continue into approach of note N+1
- [ ] Merge into single scalar bridge
- [ ] Test for over-decoration — the bridge shouldn't dominate the melody

### Phase 5 — Batch generation  (IN PROGRESS 2026-04-17)

- [ ] Generate all 294 piano scores (.ly + .pdf + .svg + .midi per hymn)
- [ ] Log per-hymn successes/failures → `hymnal_html/batch_report.log`
- [x] HarpHymnal.html nav auto-swaps SVG + MIDI on click (fetch HEAD; falls back silently when file missing)
- [ ] Review batch report; triage meter/parser edge cases into ISSUES.md
- [ ] Print-ready PDF batch (optional)

---

## Decisions log

| Date | Decision | Why |
|---|---|---|
| 2026-04-17 | Palette: grand / rolled / bebop / mellow pair / shimmer / split triad | Covers the stylistic range the user described (bebop → mellow → grand → rolled) |
| 2026-04-17 | RH plays melody + fills fraction in the gaps | User insight: harp strings sustain, so melody and fraction co-exist harmonically |
| 2026-04-17 | Ornaments only when transit budget allows | User insight: RH must physically reach melody and fraction strings in time |
| 2026-04-17 | Diatonic-only ornaments | Harp has no chromatic tones without lever flips |
| 2026-04-17 | Staged as phases 1 → 2 → 3 → 4 → 5 | Each phase is independently testable; ornaments don't matter if skeleton rhythm is wrong |
| 2026-04-17 | Output: ABC + abcjs HTML render, maybe also PDF | Harp-community format; tablet-viewable alongside review sheets |
| 2026-04-17 | V:3 leads each bar with a deep pedal-pluck of the RN root, then LH fraction arpeggiates above it | Low roots ground the harmony; high roots muddy it — classic voicing rule, amplified by ringing strings |
| 2026-04-17 | Hand-crossing is idiomatic and in-scope | Full-register sweeps (LH starts low, RH dips low, hands rendezvous mid-range) are standard harp writing — Tchaikovsky *Sleeping Beauty* is the reference |
| 2026-04-17 | LilyPond, not ABC | Cleaner engraving, better typographic control, built-in SVG/PDF/MIDI output |
| 2026-04-17 | Pedal-grace unison with LH bottom is OK | Reads as grace-note re-strike of the same harp string; never shift LH up an octave (crosses RH) |
| 2026-04-17 | Single-voice LH skeleton (not two-voice held-chord + motion) | Harp strings ring naturally; the beat-1 block chord supplies the "chord still sounding" effect without extra notation |
| 2026-04-17 | Pedal always below bass staff (Bb1–F2) | User observation: "organ pedal notes will probably always be below the bass clef" — consequence of base_octave=1 + G1 floor; visually distinguishes pedal from the LH figure |

---

## Open questions

- [ ] Which letter to use for each finger in the abc score annotation? ABC has limited fingering syntax.
- [ ] How does the ornament density scale per tempo? (Faster hymn = fewer ornaments?)
- [ ] When 6/8 time: beat-unit is dotted quarter. Style rules that worked in 4/4 may need rescaling.
- [ ] Should we export MIDI alongside ABC so the harpist can hear how it sounds before playing?
- [ ] How low can the LH pedal-pluck safely go? Depends on harp size — typical lever-harp floor is A2 or C2. Need to clamp to instrument range.
- [ ] How do we notate hand-crossing in ABC? The current 3-voice layout (V:2 = RH-treble, V:3 = LH-bass) assumes territorial hands. If LH sweeps up into treble range (or RH dips below the melody), do crossed notes stay in their "logical" voice with stem-direction hints, or migrate to the other voice?

---

## Next actions

**Right now**: start phase 1 on Silent Night. Build `tools/build_piano_score.py`, emit ABC, render HTML preview, verify the rhythm feels playable. Iterate until Silent Night sounds right, then extend.

**Session protocol**: when something sounds bad or broken, log it in `ISSUES.md` with hymn + bar + description. When a vocabulary gap surfaces (a chord the 118 can't express well), log under the "HarpChordSystem gaps" heading — don't silently work around it.
