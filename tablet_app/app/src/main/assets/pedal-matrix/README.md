# pedal harp scale system

Materials for Oliver Prehn's 28-scale system on pedal harp:
4 families of 7 modes each, organized for improvisation and pedal lookup.

## artifacts

`improv_guide.pdf` — 14-page guide
  Cover, 4 family chapters, brightness appendix, and the pedal matrix
  embedded as 2 landscape pages at the end. Each scale entry shows
  sound, use, mark tone, improv tip, chord-scale match, interval pattern,
  notes on a working tonic, and pedal setting in 4-cell braille.

`pedals_matrix.pdf` — standalone 2-page reference
  All 28 scales x 12 tonics in circle-of-fifths order. Pedal setting
  per cell shown as 4 braille glyphs. Footers with mode reference,
  family identity, brightness order, improv tips, and alteration
  cheat-sheet.

`pedals.txt` — single-tonic pedal table (28 scales on tonic C)
`pedals_matrix.txt` — full text matrix (older revision)

## scripts

`build_matrix.py` — generates pedals_matrix.pdf
`build_guide.py`  — generates improv_guide.pdf

Both use reportlab + FreeMono. Adjust the output path inside each
script if running outside this environment.

## braille pedal encoding

Four cells, read left-to-right:

    cell 1: D pedal (left col) + C pedal (right col)
    cell 2: B pedal (left col) + separator (right col, dots 4-5-6)
    cell 3: E pedal (left col) + F pedal (right col)
    cell 4: G pedal (left col) + A pedal (right col)

Within each cell:
    top    (dots 1, 4) = flat
    middle (dots 2, 5) = natural
    bottom (dots 3, 6) = sharp

## family naming

| family | parent       | popular name   |
|--------|--------------|----------------|
| F1     | Ionian       | major scale    |
| F2     | Dorian #7    | melodic minor  |
| F3     | Aeolian #7   | harmonic minor |
| F4     | Ionian b6    | harmonic major |

Within each family, the 7 modes are named systematically:
mode + alteration. F2 alterations follow Ionian-Dorian-Phrygian-
Lydian-Mixolydian-Aeolian-Locrian row order: #1 #7 #6 #5 #4 #3 #2.
F3: #5 #4 #3 #2 #1 #7 #6. F4: b6 b5 b4 b3 b2 b1 b7.
