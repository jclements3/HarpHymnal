# pedal matrix

Pedal-harp reference for Oliver Prehn's 28 scales (4 families x 7 modes)
across 12 tonics in circle-of-fifths order.

## files

- `pedals_matrix.pdf` — 2-page Letter-landscape reference
- `build_pdf.py`     — generator script (reportlab, FreeMono)
- `pedals_matrix.txt` — plain-text matrix (single-tonic spelling)
- `pedals.txt`       — 28 scales on tonic C only

## braille pedal encoding

Four cells, read left-to-right:

    cell 1: D (left col) + C (right col)
    cell 2: B (left col) + separator (right col, dots 4-5-6 always on)
    cell 3: E (left col) + F (right col)
    cell 4: G (left col) + A (right col)

Within each cell, dot row encodes pedal position:

    top    (dots 1, 4) = flat
    middle (dots 2, 5) = natural
    bottom (dots 3, 6) = sharp

## naming

Family | parent          | popular name
-------|-----------------|-----------------
F1     | Ionian          | major scale
F2     | Dorian #7       | melodic minor
F3     | Aeolian #7      | harmonic minor
F4     | Ionian b6       | harmonic major

Each row is a mode of the family parent. Row labels follow Prehn's
systematic naming (mode + alteration), e.g. F3 Lydian #2 = Lydian
with the 2nd degree raised (popularly Lydian #2 of harmonic minor).

## rebuild

    python3 build_pdf.py

Output: `/mnt/user-data/outputs/pedals_matrix.pdf`. Adjust the path
in the script if running locally.
