# Harp idiom — what makes this different from piano

Both Retab and Reharm target a **47-string lever harp**. That instrument
has four constraints that dominate every voicing, rhythm, and chord
choice in the app. Internalise these four and the 7-level ladders stop
feeling arbitrary — each level is climbing *away* from piano habits and
*toward* the harp's strengths.

## 1. Strings ring; they don't damp

On piano a key release stops the note. On a harp a plucked string keeps
ringing until it's physically damped by a finger or palm (or until
another finger plucks the same string). This inverts the default
rhythmic approach.

**Piano default:** strike the chord on every beat, release on the next.

**Harp default:** strike once, let it ring, strike a *different* string on
the next beat.

Re-striking the same triad on consecutive beats is the cardinal sin —
it re-attacks the strings and kills the ring, producing the
"stomp-stomp-stomp" texture that reads as a pianist reducing a score
rather than a harpist arranging one. The LH either **holds** or **walks
through chord tones** so each beat hits a fresh string. By the end of
the bar all three tones are sounding together anyway from the prior
strikes' sympathetic ring.

Retab L3 and above enforce this. Reharm inherits it unchanged.

## 2. C1–B1 is the drumming octave

The lowest seven strings on a 47-string harp (roughly C1 through B1)
have a distinctive booming, drum-like sustain that's useful as a
**structural anchor** — a low pedal tone struck on beat 1 and left to
resonate under the phrase — but **disruptive** if used on every chord
change.

**Rule of thumb:** low-bass C1–B1 anchors only on phrase *openings* and
*cadences*. Everywhere else the LH triad base lives in octave 2.

Retab L5 is the level where this becomes explicit; Reharm applies the
same rule whenever the LH renders a bass pitch.

## 3. Lever flips are expensive

Each string has a lever that raises its pitch by a semitone. To change
a B♭ to a B♮ (or vice versa) mid-piece, the harpist has to reach up and
flip that lever — a physical action that breaks the flow of playing,
especially mid-phrase.

This is why **both** projects commit to strict diatonic content:

- **Retab**: every level of the ladder stays within the hymn's key
  signature. No chromatic passing tones in the LH voicings.
- **Reharm**: the entire point of Reharm's 7-level ladder is that it
  never demands a flip. Textbook jazz reharmonisation leans on
  secondary dominants (flip), modal interchange (flip), tritone subs
  (flip), and distant-key modulation (many flips). Reharm swaps all of
  that for 7 levels of *technique sophistication inside the diatonic
  collection*. The chord pool is 14 symbols total (7 diatonic triads +
  7 diatonic sevenths). Anything outside the pool is a bug, not a
  feature.

A harp arrangement that demands even *one* mid-piece flip is already a
compromise. Target: **zero flips**, full piece.

## 4. Four fingers per hand, not five

Harpists play with fingers 1–4 (thumb through ring); the pinky is too
short to reach the strings reliably. This caps a single LH strike at
**four simultaneous pitches**. A full diatonic 7th chord fits (root +
3rd + 5th + 7th = 4 tones). Adding a diatonic 9th or an octave
doubling pushes past the hand and requires splitting the strike across
beats.

This is why Reharm's voicings peak at **diatonic 7ths** — not because
richer chords wouldn't sound good, but because the fourth voice already
fills the hand. Extensions (9/11/13) could in principle be added when
the melody supplies the tension; the current emitter ships chord
*symbols* at 7ths and leaves upper-structure colour to the player.

---

## The 7-level ladders, seen through these constraints

Both ladders are climbing *away* from piano habits and *toward* each
of the four rules above.

**Retab** climbs the **texture** axis. Each rung turns off a piano habit
(L1: SATB block-strikes every beat — peak pianistic mud) or turns on a
harp-idiomatic feature (L3: block-135 with no re-strike; L5: low-bass
anchors; L6: contour-matched LH motion; L7: rolled chords, octave
doubling at final cadence, bisbigliando on tonic holds).

**Reharm** climbs the **harmonic-technique** axis, entirely inside the
diatonic collection. L1–L3 progressively enrich the same-root chord
(triad → 7th → functional substitution). L4–L5 shift tonal gravity
without changing the key signature (relative minor, then modes). L6–L7
abandon functional root motion for chromatic mediants and voice-leading-
first construction — still diatonic, just not cadential-major.

The two ladders are orthogonal. The app surfaces each axis separately
so you can study one dimension at a time. The **Retab Hymnal** tile
lets you see how the same written harmony re-textures from L1 through
L7; the **Reharm Hymnal** tile lets you hear what happens when the
chords under the *same* melody shift from basic triads all the way to
voice-leading-first reharm. Both tiles read from the same 279-hymn
corpus, so you can compare like-for-like.
