# CLAUDE.md

## Project Overview

**Boddie Hymnal** — hymn arrangement style modeled on Brook Boddie's
*Brook Boddie Hymnal Vol. 1* (Seraphim Music, 2020). Companion to Retab
and Reharm but **single-output, no levels** — one Boddie render per
hymn, no L1/L2/L3 ladder.

Where Retab tabulates SATB into harp texture and Reharm substitutes
diatonic jazz chords, Boddie does **figuration + phrasing** on
otherwise-diatonic chords. The harmonic vocabulary is the same 14-chord
diatonic pool Reharm uses (7 triads + 7 diatonic 7ths); the novelty is
in the LH arpeggio pattern, RH octave doubling on cadences, rolled-chord
notation, breath marks, and the wide-spread rolled final chord.

## Source

`/home/james.clements/projects/HarpHymnal/The-Brook-Boddie-Hymnal-Vol-1-E-flat-version-j6brq2.pdf`
(44 pages, 16 pieces, lever harp tuned in E-flat). Style summary in
`BODDIE.md`.

## The instrument

Target is a **47-string pedal harp** (not the lever harp Brook used).
Range policy:

- **C1-C2** (lowest octave): LH octave-pluck drones only, sparingly.
  Used at opening + cadence as a structural anchor. Striking these
  often makes the sound muddy.
- **C2-G7**: regular playing range.
- **>G7**: never played as melody; reserved for occasional glissando
  flourishes at intros / closings.

Same harp-idiom rules as Retab/Reharm:
- No piano stomping (no consecutive identical strikes)
- Zero lever flips (every note diatonic to the hymn's key)

## Project layout

```
boddie/
  CLAUDE.md            this file
  BODDIE.md            style fingerprint (synthesized from the PDF)
  hymnal/
    boddie_hymnal.py     emitter (single output, no level argument)
    build_hymnal.py      bulk builder (all 279 hymns)
  drills/
    build_drills.py      generates Boddie figuration drill cards
```

## Build

Single hymn:

```bash
python3 boddie/hymnal/boddie_hymnal.py data/hymns/amazing_grace.json -o /tmp/ag.abc
abcm2ps /tmp/ag.abc -g -O /tmp/ag
```

Bulk build (all 279 hymns):

```bash
cd boddie/hymnal && python3 build_hymnal.py
```

Drills:

```bash
python3 boddie/drills/build_drills.py
```

Outputs land in `tablet_app/app/src/main/assets/boddie/`:
- `hymns/<slug>.svg` — one per hymn
- `boddie_hymns.js` — `window.BODDIE_HYMNS` catalog
- `drills/<n>.svg` — one per drill card
- `boddie_drills.js` — `window.BODDIE_DRILLS` catalog

## Why no levels?

Retab's L1-L7 are texture sophistication; Reharm's L1-L7 are harmonic
sophistication. Boddie style is a **single voice** (Brook's
arrangement idiom). Multiple levels would dilute the brand and add no
pedagogical value. One shot, one style.

## 7-bit ASCII

Source files stay 7-bit ASCII. Generated ABC may contain Unicode
(superscripts, fermata, breath marks) because abcm2ps renders them.
