# 15 Altered-Dominant ii-V-I Licks - Pedal-Harp Version

Pedal-harp adaptation of **Jens Larsen, "15 II V I licks - Altered Dominants"**
(jazz-guitar e-book, 2017). Original source PDF in `src/`.

Every lick runs over **Dm7 | G7alt | Cmaj7** (a ii-V-I in C major). The guitar
TAB was transcribed to concert pitch and re-spelled for the harp; the guitar
fingering/TAB is dropped (irrelevant to harp).

## Files
- `abc/lick_01.abc` .. `lick_15.abc` - one ABC tune per lick, chord symbols + notes.
- `HARP_NOTES.md` - per-lick device, concert pitches, **pedal setup per bar**,
  within-bar pedal-change flags, and range.
- `src/15-II-V-I-licks-Altered-Dominants.pdf` - the original guitar e-book.
- `build_altered_licks.py` - regenerates everything from the transcription data.

## Harp adaptation in one line
Pedal-wise each lick is **C major -> Ab melodic minor -> C major** (two foot
changes). The G-altered scale equals Ab melodic minor, so it covers every
altered note in bar 2. See `HARP_NOTES.md` for per-lick pedal rows.

## Relationship to the rest of the repo
These are **chromatic** jazz licks and live OUTSIDE the diatonic Trefoil system
(which deliberately excludes altered dominants). They are a standalone practice
resource, not part of the reharm engine.

## Caveats
Transcribed from the guitar TAB by automated readers. Licks 3, 5 and 6 were
re-verified by hand against high-zoom crops of the TAB: lick 3's G bar really
does use a natural-5 (D) -> a within-bar D pedal change (flagged in
`HARP_NOTES.md`); lick 6's G bar is a descending Eb/Db triad pair (re-read to 8
notes). The other 12 came back high-confidence and fit Ab melodic minor cleanly.
Still a faithful-but-verify first pass -- spot-check against `src/` if a note
sounds off.

## Render
```
abcm2ps abc/lick_01.abc -O out.ps && ps2pdf out.ps lick_01.pdf
```
