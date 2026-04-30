# Boddie style fingerprint

Distilled from a read of *The Brook Boddie Hymnal Vol. 1* (Seraphim
Music, 2020) — 16 pieces, all on lever harp tuned E-flat, transcribed by
Bill Ooms, edited by Rhett Barnwell. The style markers below are
applied to every Boddie-styled hymn render in this project.

## Tempo & character

- Default tempo `Q:1/4=72` (Brook used 66-84; 72 is the modal value, 9
  of 16 pieces). Use 72 unless the source hymn JSON specifies another.
- Header annotation: "Slowly, with great expression" placed above the
  first bar.
- `rit. ... a tempo` arcs once per phrase (not just once per piece).
- `molto rit.` + fermata + L.V. on the final bar.

## LH (V2 — bass clef)

The signature pattern: **bass note on beat 1, ascending arpeggio of
chord tones in eighths spanning ~1.5-2 octaves through the rest of the
bar**. Includes walking passing tones — not pure chord-tone-only.

Three contextual variants:

1. **Opening bar of hymn** — drone-octave bass (C1-C2 range octave
   pluck) on beat 1, then arpeggio rises through C2-C4 chord tones.
2. **Middle phrase bars** — bass at C2-C3, arpeggio rises through
   C3-C4 chord tones, no drone octave.
3. **Cadence bar (last of each phrase)** — wide-spread chord (root
   octave + chord triad above), rolled, held a full bar.
4. **Final bar of hymn** — wide-spread rolled chord with C1-C2 drone
   octave below the LH staff, fermata, L.V.

## RH (V1 — treble clef)

Carries the melody. Modifications from the source melody:

- **Octave doubling on the cadence bar of every phrase** — the top
  note of every melody event in those bars is also struck one octave
  up.
- **Rolled chord on the final melody note** — the last melody note is
  decorated `!arpeggio!` (rolled).
- **Breath mark `!breath!`** at the last melody event of every
  non-final phrase.

## Harmony

Same diatonic 14-chord pool as Reharm L2 (7 triads + 7 diatonic 7ths).
Boddie does NOT add jazz substitutions. Triads in the source JSON are
lifted to their diatonic 7th forms (V -> V7, I -> Imaj7, etc.) which is
all the harmonic enrichment the style does.

## Notation conventions

abcm2ps decorations used:

- `!arpeggio!` — rolled chord (matches Brook's curved roll mark)
- `!breath!` — phrase-end comma
- `!fermata!` — fermata at cadences
- `!ppp!` / `!pp!` — dynamic markings on the final bar
- Annotations: `"^Slowly, with great expression"` in italic

## Range policy (47-string pedal harp)

- C1-C2: drone-only LH octave plucks at openings + cadences.
- C2-G7: regular range.
- Above G7: not emitted (reserved for glissando flourishes that the
  current emitter does not generate).
