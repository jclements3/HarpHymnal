# Next session pickup

## Where we left off (2026-04-27)

Created `SAMPLES.md` — 21 acoustically-motivated shape combinations
across 7 categories, written in the same style as `DRILLS.md`. Each
sample is labeled with the physical mechanism it exploits (overtone
alignment, sympathetic resonance, harmonic-series stacking,
decay-envelope chorusing, top-octave beating-as-brightness).

## Categories in SAMPLES.md

1. Wide-open low + stacked fifths above (samples 1-3)
2. Octave-doubled bass with triad above (samples 4-6)
3. Stacked fourths through the middle register (samples 7-9)
4. Drone bass + sparse high pings (samples 10-12)
5. Top-octave bell clusters (samples 13-15)
6. Overtone-series voicing (samples 16-18)
7. Octave-doubled with chorusing (samples 19-21)

## Conventions used

- Header: `Tonic: C` + `Pedals: ⠩⠹⠡⠒` (C major all-naturals)
- Every shape kept inside published reach ceilings:
  ring-middle ≤ 4, middle-index ≤ 5, index-thumb ≤ 6
- Thumb-ring dyads use the wider 13th ceiling — that's where the
  overtone-stack shapes (`1x^18`, `1x^1c5`, `1L^18`) live
- Two-hand textures use separate-shapes form (`1L^1 3R^1333`) not the
  comma form (`1x^1333,3333`), matching DRILLS §5

## Open questions for the user

- The C-major pedal cell `⠩⠹⠡⠒` was inferred from README example
  (B♭ major was `⠒⠹⠑⠒`) — verify this is correct C-major notation
  before committing
- Sample 17 (`1x^1888,55`) uses comma form for a sustained bloom
  texture — check this is the right choice vs separate shapes
- Top-octave cluster shapes (§5) violate the published aesthetic
  scoring penalties (stepwise clash, three adjacent stepwise) by
  design — the rationale in the file explains why this reverses in
  octave 7, but consider whether to add a note in the README's
  scoring table acknowledging the register exception

## Files in this archive

- `README.md` — encoding spec (current shape-setup grammar)
- `HANDOUT.md` — beautiful patterns reference
- `DRILLS.md` — practice sequences (the style template SAMPLES follows)
- `VERIFY.md` — reach calibration drills (not yet run)
- `HANDOFF.md` — repo state ledger
- `SAMPLES.md` — this session's output
- `NEXTSESSION.md` — this file

## Memory note

The userMemories block at session start described the OLD system
(118-chord roman-numeral jazz reharmonization, `harp_mapper.py`,
`fill_template.py` pipeline). The CURRENT system in `/mnt/project` is
the rewritten shape-setup encoding — completely different vocabulary,
no roman numerals, no chord names. Trust the project files over the
memory block; HANDOFF.md confirms the rewrite is the active system as
of 2026-04-25.
