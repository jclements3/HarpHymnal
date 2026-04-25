# Retab — seven levels of SATB-to-harp tabulation

**Retab** (from *tabulation* — the historical term for arranging vocal
polyphony into keyboard notation, as in Renaissance keyboard tablatures) is
the counterpart to reharm. Where reharm changes the chords under a melody,
**retab changes the texture** — taking a four-part SATB hymn and rendering
it as an idiomatic composition for 47-string lever harp.

The axis of difficulty isn't "distance from the original harmony" — it's
**distance from the vocal texture toward idiomatic harp composition**.

## Level 1 — Close-score keyboard reduction

Take SATB as-is. Soprano + alto go in the RH, tenor + bass in the LH. Four
attacks per beat in a compact two-octave range. Sounds like a pianist
sight-reading a hymnal. No harp idiom yet — strings can't damp between
attacks, so on harp this turns to mud. Useful only as a starting point.

## Level 2 — Lead-sheet reduction (melody + chord)

Drop the inner voices. Keep the soprano as-is in the RH. In the LH, replace
the literal bass note with the chord symbol's root. Grand staff, two attacks
per bar in LH. Much cleaner than L1 on harp, but under-uses the instrument.

## Level 3 — Trefoil block-135

Replace the LH root with a diatonic **block 135** triad (root + 3rd + 5th,
all diatonic, all stacked) drawn from the trefoil vocabulary. The
voicing is stated once; how often it's re-struck depends on the pattern.

**Harp-idiomatic rule:** never re-strike the same triad on consecutive
beats — that re-attacks the strings and kills the ring, which is why it
reads as "stomp stomp" piano texture. Instead, either strike once and let
the strings ring, or walk through different chord tones so each beat hits
a fresh string. By the end of the bar all three tones are sounding
together anyway from the prior strikes' sympathetic ring.

## Level 4 — Phrase-role articulation

Stop striking the same block on every beat. Vary the rhythm by
**phrase role**:

| Phrase role      | Articulation                          |
|---               |---                                    |
| opening          | single block, full bar                |
| middle           | two half-bar blocks                   |
| cadence_approach | arpeggio 1–3–5, 5th sustained         |
| cadence          | single block, full bar                |

The tune starts *breathing* — arrivals feel different from motion.

## Level 5 — Structural low-bass anchors

Exploit the bottom of the 47-string range. On opening and cadence bars, add
the root an octave below the triad (octave 1) — struck once on beat 1, then
ring. This turns C1–B1 strings from "drumming range" into structural pedal
tones. Used sparsely; if every bar gets one, it becomes a pulse and kills
the effect.

## Level 6 — Trefoil-path contour matching

Look at the direction of harmonic motion from chord to chord and pick the
trefoil voicing that matches:

- Motion by **4ths clockwise** (I→IV, V→I — most common in hymns) →
  ascending arpeggio or rising open voicing
- Motion by **4ths counter-clockwise** (I→V, ii→vi) → descending figure
- Motion by **3rds** (I→iii, vi→I) → common-tone pivot; only the non-common
  notes move
- Motion by **2nds** (iii→IV, V→vi) → stepwise inner-voice motion, outer
  notes held

The LH now *responds* to the chord progression's shape instead of being a
static template. This is where a retab starts sounding composed.

## Level 7 — Full harp texture

All of the above plus genuine harp idiom:

- **Rolled chords** (⌇) on arrivals — the attack itself becomes expressive
- **Glissando** between phrases over the diatonic collection, filling rests
  and breath points
- **Counter-melody** in the LH's top voice when the soprano sustains a long
  note — borrow the tenor/alto line dropped in L2 and re-introduce it only
  where the melody rests
- **Octave doubling** of the melody in the RH on the final cadence (climax)
- **Bisbigliando** (two fingers alternating on the same string) for held
  tonic pedals
- **String damping** (⊕) explicitly marked only where consecutive stepwise
  notes would clash — the rest rings freely

At L7 the arrangement is no longer a reduction — it's an idiomatic harp
composition whose skeleton happens to be a hymn.

---

## Status of the Retab Hymnal

`hymnal/retab_hymnal.py` now ships **all seven levels** as independently
selectable passes. The emitter accepts `--level 1..7`; `RETAB_LEVELS`
dispatches to per-level functions, and `build_hymnal.py --levels 1..7`
bulk-builds every level for every hymn into
`tablet_app/assets/retab/hymns/L<n>/`. The tablet's Retab Hymnal tile
has an L1–L7 selector in the banner; the user picks the level per hymn.

L1 and L2 are new code paths that bypass the trefoil pipeline. L3–L7
are feature-gated inside the existing `lh_pattern()` — each level turns
on the next feature:

| Level | Feature added on top of L-1                          |
|---    |---                                                   |
| L3    | Block-135 trefoil triads + no-piano-stomp walk       |
| L4    | Phrase-role articulation (opening / middle / cadence)|
| L5    | Low-bass octave-1 anchors on opening + cadence       |
| L6    | Contour matching: arpeggio direction follows motion  |
| L7    | Rolled chords, final-cadence octave doubling,        |
|       | counter-motion under held melody, bisbigliando       |

`build_abc(hymn)` with no `level=` kwarg is byte-identical to the
pre-refactor L6+partial-L7 output, so legacy calls keep working.

Deferred: inter-phrase glissandos (few hymns have phrase-end rest space
to support a gliss cleanly).
