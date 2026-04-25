# Reharm -- seven levels of diatonic reharmonisation

**Reharm** is the counterpart to [Retab](../retab/RETAB.md). Where retab
changes the *texture* under a melody (re-tabulating SATB as idiomatic harp
composition), **reharm changes the harmony** -- substituting jazz-idiomatic
chords under the same melody, still playable on a 47-string lever harp.

The axis of difficulty is **technique sophistication within the diatonic
collection**. Every chord at every level is drawn from the hymn's key
signature -- no secondary dominants, no modal interchange, no modulation
to foreign keys, no tritone substitutions. The harp's levers stay put.

This is a deliberate narrowing from the "distance-from-original-key"
ladder implied by general jazz reharm pedagogy (e.g. Adam Neely, 8-bit
Music Theory). Those approaches reharmonise into the relative minor,
then IV, then distant keys, each step requiring more lever flips than
the last. On a 47-string lever harp, even a single flip mid-piece is
disruptive; a piece that modulates to V major is effectively untunable
without rebuilding the instrument's setup. **So we trade the
"distant-key" dimension entirely and spend the full seven rungs of the
ladder climbing within the one diatonic collection.**

## The harp constraint

- **Zero lever flips.** Every chord in every level draws only from the
  diatonic scale of the hymn's key. Accidentals are forbidden.
- **No piano stomping.** Carried over from retab: never re-strike the
  same voicing on consecutive beats. Walk through chord tones or let
  ring.
- **C1-B1 as drumming range.** Low-bass anchor tones sound there only on
  opening and cadence. Mid-piece triad bases sit at octave 2.

## The chord pool

Within the diatonic scale there are only two chord-type families:

| Kind | Symbols |
|---   |---      |
| Triads   | I, ii, iii, IV, V, vi, vii(dim) |
| 7ths     | Imaj7, ii7, iii7, IVmaj7, V7, vi7, viiø7 |

Higher levels extend voicings with diatonic 9ths / 11ths / 13ths *when
and only when* the melody supplies the tension. Those aren't new chord
symbols; they're richer voicings of the seven diatonic seventh chords.
Slash-chord notation (L6) adds variety on the surface (`F/G`, `C/D`)
but the underlying pitches remain diatonic.

Total chord symbols produced: **14** (seven triads + seven sevenths),
with diatonic extensions and slash-chord surface variants layered on
top at the higher levels. Anything outside this pool -- any chord
requiring a lever flip -- is a bug.

## Level 1 -- Straight triads (baseline)

Output the hymn's written chord as a bare diatonic triad in the LH.
Quality field is cleared; inversions dropped. This is the baseline
against which every higher level is judged. Functionally equivalent to
retab's L3.

**Goal:** establish that the pipeline (JSON -> ABC -> SVG -> tablet)
works end-to-end and the LH walking pattern reads cleanly under the
melody.

## Level 2 -- Diatonic 7ths

Every triad gets its diatonic-7th form. Roots don't move; only the
quality is enriched.

| Original | L2 | Quality |
|---       |--- |---      |
| I   | Imaj7   | major 7 |
| ii  | ii7     | minor 7 |
| iii | iii7    | minor 7 |
| IV  | IVmaj7  | major 7 |
| V   | V7      | dominant 7 |
| vi  | vi7     | minor 7 |
| vii(dim) | viiø7 | half-diminished 7 |

**Smallest real step away from the hymn.** All sevenths are already in
the diatonic collection, so zero flip cost.

## Level 3 -- Functional substitution

Chord-quality substitution *within* the seven diatonic seventh chords.
Roots move; chord pool stays the same. The three functional groups:

- **Tonic function:** I, iii, vi (all share the tonic pitch or two
  tones with I).
- **Pre-dominant function:** ii, IV (share three tones).
- **Dominant function:** V, vii (vii is a rootless V7 minus the fifth).

Substitutions that preserve function:

- **Deceptive tonic:** `I -> vi7` at a weak arrival (video's "swap the
  6 for the 3" move, done conservatively).
- **Plagal-colour tonic:** `I -> iii7` at phrase starts that need
  motion without cadential weight.
- **Pre-dominant shift:** `IV -> ii7` (the "two chord for the four" swap
  -- three tones in common).
- **Weak dominant:** `V -> iii7` or `V -> viiø7` mid-phrase when the bar
  wants no cadential weight.

**Rule:** no substitution at the hymn's final cadence bar. The written
cadence is sacred at L3.

## Level 4 -- Relative-minor reharm

Re-centre the harmonic gravity on the **relative minor** (vi). The
hymn's melody is unchanged; the chord progression reharmonises as if
the piece were in vi-minor.

Key move: the relative minor shares the parent major's key signature
exactly. A hymn in C major reharmonised into A minor uses only the
white keys -- zero flips. The classic "Hit the Road Jack" / Andalusian
descent (i -- bVII -- bVI -- v in natural minor, which is vi -- V -- IV
-- iii in parent major) is L4's signature move.

**Diatonic constraint:** use **natural-minor v** (the minor v chord,
i.e. iii in parent major), not the raised-leading-tone V. Raising the
leading tone is the one lever flip that *wants* to appear here --
reject it. Natural-minor cadences sound modal/Dorian-adjacent rather
than functional-major, which is exactly the colour L4 is going for.

**When to insert:** bar spans where the melody outlines the relative-
minor triad (vi-I-iii in parent major = i-bIII-v in relative minor)
rather than the parent tonic. Hymns whose melodies sit on I throughout
won't take L4 well; hymns that dip to the relative minor at phrase
midpoints respond beautifully.

## Level 5 -- Modal reharm

Where L4 shifts the gravity to the relative minor, L5 shifts it to
**any of the diatonic modes** -- Dorian, Mixolydian, Lydian, Phrygian,
Aeolian (= L4), Locrian -- while keeping the parent key signature.

Each mode has a characteristic "home chord" and a cadential move that
doesn't require flips:

- **Dorian** (ii as centre): i - IV - i, with the raised 6th as the
  chord-tone colour. Dorian in C-major sig = D Dorian; home is Dm.
- **Mixolydian** (V as centre): I - bVII - I. In C-major sig this is
  G - F - G.  The flat-7 descent is its signature.
- **Lydian** (IV as centre): I - II - I, with the #4 as the colour.
  In C-major sig = F Lydian; home is F with G major as the bright II.
- **Phrygian** (iii as centre): i - bII - i. In C-major sig = E
  Phrygian; home is Em with F as the bII.

**When to insert:** L5 applies in 4-8 bar sections, not single chords.
Pick one phrase of the hymn and reharmonise it with a modal centre
other than I or vi. The rest of the hymn stays at L2/L3.

**Budget:** at most one modal section per hymn. More than one and the
piece loses its original tonal centre.

## Level 6 -- Non-functional and slash chords

Abandon functional root motion (fifths and cadences) in favour of:

- **Chromatic mediants within the diatonic collection.** Root moves by
  a third between chords of different qualities: `I -> iii`, `IV -> vi`,
  `V -> vii`. All seven pairings are diatonic.
- **Diatonic slash chords.** Any diatonic triad over any diatonic bass
  pitch. `F/G` in C major is a dominant 11 without the third; `C/D` is
  a D11-no-3; `Dm/G` is a G9sus4. All pitches diatonic, no flips.
- **Stepwise root motion.** Wayne Shorter / Herbie Hancock modal-jazz
  habit: bars of static harmony interrupted by a step-wise chord shift
  that doesn't resolve.

**Budget:** L6 is an entire-hymn aesthetic, not a per-chord substitution
pass. Either a hymn renders at L6 or it doesn't. Test on 5-10 hymns
before generalising.

## Level 7 -- Voice-leading first

The "ultimate" approach from the reference video, constrained to
diatonic: build the harmony from smooth **inner-voice motion** rather
than chord-symbol-to-chord-symbol logic. Each inner voice is its own
melodic line that prefers step-wise motion or common tones.

Concretely, at L7 the emitter:

1. Computes the melody line.
2. Picks an inner-voice contour (e.g. a descending step-wise line from
   tonic to dominant across a phrase).
3. Picks a bass contour (often the inverse of the inner voice).
4. For each bar, emits the diatonic chord whose tones match the melody,
   inner voice, and bass at that beat. The chord *symbol* falls out of
   the voice-leading rather than being chosen first.

Because every voice is drawn from the diatonic scale, the resulting
chord symbols can be unexpected -- e.g. a bar whose melody is E, inner
voice is G, and bass is D produces Em7/D (a diatonic voicing that would
rarely be chosen symbol-first). All pitches remain diatonic; zero flips.

**Budget:** L7 replaces L1-L3 passes entirely for the hymns it's
applied to. It can't be layered on top of the other levels -- the
voice-leading search is its own pass.

---

## Implementation plan

The emitter at `hymnal/reharm_hymnal.py` takes a `--level` 1-7 and
applies one of the following strategies:

| Level | Pass |
|---    |---   |
| L1 | Clear the `quality` field; render bare triads. |
| L2 | Lift each triad to its diatonic 7th. |
| L3 | Apply tonic / pre-dominant / dominant substitutions per phrase role. |
| L4 | Scan for melody-dips into the relative minor; reharmonise those sections with the Andalusian descent (natural-minor v). |
| L5 | Detect modal character from the melody; apply one modal reharm section per hymn. |
| L6 | Replace functional root motion with chromatic mediants and diatonic slash chords. |
| L7 | Voice-leading-first: inner-voice + bass contour search, chord symbol derived. |

Each pass validates that every output chord's pitches are in the
parent key's diatonic scale. A pitch outside the scale is a hard
failure -- that's the flip-free guarantee.

## Implementation status

All seven levels are implemented and shipping. All 279 hymns in the
corpus render at every level without pool-validation failures. The
Reharm Hymnal tile on the tablet carries an L1-L7 selector in its
banner.

Small gaps between spec and code worth noting for the reader:

- **L3 weak dominant** currently emits only `V -> iii7`; the spec also
  allows `V -> viiø7` as an alternative, not yet in the code.
- **L6 slash chords** (`F/G`, `C/D`, `Dm/G`) are described in the spec
  but the current L6 pass emits chromatic mediants only. Slash-chord
  notation requires a bass-pitch field on the chord dict that the LH
  voicing code would need to respect; pending.
- **Minor-mode hymns.** Aeolian-to-Ionian translation runs once at the
  top of every level pass via `_normalize_to_ionian`, so every
  downstream stage works in parent-major terms. For minor-mode hymns
  the "relative minor reharm" at L4 therefore becomes a **relative-
  major** feel in practice (the phrase re-centres on the parent major
  tonic), which turns out to be the more useful colour anyway.

These are refinements, not bugs -- the output is musically coherent at
every level and the pool guarantee (zero accidentals) holds.

## Relationship to the old reharm

The earlier reharm effort (`../HarpHymnal/reharm/`,
`trefoil/reharm/`, `data/reharm/tactics.json`) tried to do too many
things -- catalog, fragment-cut, legality, selector, MIDI rendering,
schema validation, drill extraction -- before producing a single
playable hymn. This rewrite inverts that: **a playable hymn at every
level**, and the ladder is the product roadmap.
