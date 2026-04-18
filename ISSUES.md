# Issues, Bugs, Bad-Sounding Moments, Vocabulary Gaps

Living issue log. Add new entries at the top of each section. Mark fixed items with the fix date and move to the "Fixed / addressed" section at the bottom.

**Log format per entry:**
```
### Short title (hymn, bar, date)
Description of what's wrong. Audio reference if possible.
Proposed fix or diagnosis.
```

---

## Bugs (code or data problems)

*(none logged yet)*

---

## Bad-sounding moments

Moments in specific hymns where the output doesn't sound musical. Grouped by likely cause.

### RH chord-fraction fill sits too high (Silent Night, all bars, 2026-04-17)
Phase 1 v0.1 piano-score: fraction figures starting at strings 8+ render with triple ledger-lines above the treble staff — well above the melody. Likely fix: drop RH fill `base_octave` from 4 to 3, or only octave-down when the starting string is ≥ 8. Visually and harmonically the fill should sit *between* melody and bass, not above the melody.

### Bar 2 silent in Silent Night piano score (Silent Night, bar 2, 2026-04-17)
The reharm JSON for Silent Night has 11 chord assignments for a 12-bar melody — bar 2 is skipped. In the piano score this renders as an empty harmony bar (melody alone). Likely cause: export_to_reharm.py's downbeat-weighted collapse rejected bar 2 (probably because the music21 RN analysis for that bar was ambiguous or labeled as a passing chord). Diagnose in the reharm pipeline, not the piano-score builder.

---

## HarpChordSystem vocabulary gaps

Songs or passages where the 118-chord vocabulary can't provide a good voicing for what the music wants. These are candidates for the vocabulary to **grow** (via replacement of a weaker entry) or for the mapper to **substitute** more aggressively.

*(none logged yet)*

**Adjustment process** when a gap is confirmed:
1. Describe the musical need (chord, context, why current options fail).
2. Propose a replacement fraction from the un-selected universe (there are ~2,200 unused playable fingerings — see `ChordAnalysis.md`).
3. Verify replacement meets rules: diatonic, gap ≥ 1, hex alphabet, fits the 14 patterns.
4. Update `HarpChordSystem.tex`, rebuild JSON, regenerate the affected hymns.

---

## Deferred / won't-fix (with rationale)

Items the user has decided not to change, with reasoning preserved so they don't get re-raised.

- **Harmonic-minor V can't live in the 118** — strictly diatonic by design. Minor-key hymns use substitution strategies (`bVII_backdoor`, `III_deceptive`, `pedal_i`, `modal_v`). This is the point, not a limitation.
- **~10 hymns mis-label as phrygian** due to tonic-detection ambiguity. Won't fix — documented in README as known.
- **Come Thou Long-Expected Jesus over-segments to 12 phrases** — modal i↔III oscillation trips the cadence detector; rhythm-weighted phrase detection tried and failed empirically.
- **In The Bleak MidWinter final bar labeled vii°7** — music21 analysis artifact, would require RN analyzer changes.
- **Amazing Grace composer metadata merges two names** — source ABC lacks delimiter, not worth heuristics.

---

## Fixed / addressed

*(items move here from above with fix date + brief note on the resolution)*
