# Pretty Fraction Recipe

Algorithm for generating good-sounding chord voicings ("pretty fractions") on a
diatonic harp in the jazz-hymnal range (C2–C6, 29 strings in C major).

A **fraction** = LH shape + inter-hand gap + RH shape. Each fraction produces
a specific 3–5 note chord voicing with clear bass, singing top, and enough
color in between.

Implementation: [`trefoil/pretty_fraction.py`](trefoil/pretty_fraction.py)

---

## Principles (why this algorithm exists)

Teacher's guidance distilled into rules:

1. **Audiences hear the extremes** — bass defines function, top carries melody,
   middle notes are texture. A good voicing has a clear bass and a singing top.
2. **Less is more** — 3–5 notes per chord is plenty. Dense 6+ note stacks smear
   on a resonant harp.
3. **Spacing matters** — LH stays low and sparse; RH carries the color tones
   up top; gap between hands creates breathing room.
4. **No clusters in the bass** — adjacent-string intervals below middle C smear
   into mud. Keep the lower register open.
5. **Diatonic by construction** — lever harp has no accidentals; every fraction
   uses only C-major scale tones.

---

## Range and constraints

```
Instrument: 47-string pedal harp, but hymnal voicings use C2–C6
Strings:    29 (positions 1–29 in C-major scale)
C2 = string 1, C3 = 8, C4 = 15 (middle C), C5 = 22, C6 = 29

Per hand:   ≤ 10 strings span
Total:      LH + gap + RH ≤ 29 strings
Max gap:    ~9 strings (when both hands use full 10-string reach)
```

---

## Scoring function (lower = prettier)

A fraction's penalty is the sum of:

| criterion | penalty | rationale |
|---|---|---|
| missing root | +3 | rootless is jazz-piano; hymn wants a clear bass |
| missing 3rd (unless sus/quartal) | +4 | 3rd defines major/minor quality |
| missing 5th (unless quartal) | +1 | 5th is the easiest to drop, mildly preferred |
| missing 7th (on 7-chord) | +4 | 7th is what makes the chord a 7-chord |
| missing named addition | +2 each | add9, add11, add13 must actually sound |
| >5 total notes | +2 per extra | density penalty |
| >3 notes in LH | +2 per extra | LH mud |
| >4 notes in RH | +2 per extra | RH saturation |
| bass isn't root/3rd/5th | +3 | bass should anchor the chord |
| top isn't a chord tone | +2 | top should reinforce, not clash |
| adjacent 2nds below C4 | +3 | low-register clusters |
| gap < 2 | +1 per missing string | hands too close = no breathing room |
| gap > 15 | +1 per extra | too wide = broken halves (unless intentional) |

**Hard constraints (reject = 9999):**

- Any note outside C2–C6
- LH span > 10 strings
- RH span > 10 strings

---

## Generator strategy

For each target chord:

1. **Compute pitch classes.** Essentials = root + 3rd + 5th (+ 7th if 7-chord).
   Modifications from sus/quartal/additions/omissions adjust the set.
2. **Bass choices.** Root, 3rd, or 5th; in octaves 2 or 3. Placed low and solo.
3. **Top choices.** Any chord tone in octaves 4–6. Prefer high for brilliance.
4. **LH fill.** Bass alone, or bass + one more chord tone within 10 strings.
5. **RH fill.** Top + 1–2 middle chord tones, all within 10 strings ending at top.
6. **Enumerate, score, rank.** Return the lowest-scoring candidate.

Candidate space per chord is ~500–1000 combinations; pruning at the span-check
and de-duplication step trims to ~200 realistic candidates.

---

## Usage

```python
from trefoil.pretty_fraction import pretty, format_fraction

# Generate a pretty voicing for V7
frac = pretty({"numeral": "V", "quality": "7"})
print(format_fraction(frac))
# → LH[G,,] gap=5 RH[F·B·d]

# Specify quality and additions
frac = pretty({"numeral": "I", "additions": [9]})
# → I add9 chord (C-E-G-D' spread)

# Verbose: show top 5 candidates
frac = pretty({"numeral": "ii", "quality": "7"}, verbose=True)
```

The output is a dict:

```python
{
  "lh": [(5, 2)],              # (scale-degree, octave) — G2
  "rh": [(4, 4), (7, 4), (2, 5)]  # F4, B4, D5
}
```

Convert to ABC or display via `format_fraction()`.

---

## Example outputs (current best pass)

```
chord          best fraction
----------------------------------------
I              LH[C,,] gap=8 RH[E·G·c]
IΔ             LH[C,,·B,,] gap=2 RH[E·G·c]
ii7            LH[D,,] gap=8 RH[F·A·c]
iii7           LH[E,,] gap=8 RH[G·B·d]
IVΔ            LH[F,,] gap=5 RH[E·A·c]
V7             LH[G,,] gap=5 RH[F·B·d]
vi7            LH[A,,] gap=3 RH[E·G·c]
vii°h7         LH[B,,] gap=3 RH[F·A·d]
Is9 (Iadd9)    LH[C,,·E,,] gap=5 RH[D·G·c]
Vs4            LH[G,,] gap=3 RH[D·c]
```

Each:
- **Bass**: root in bass clef (single note)
- **Top**: clear melodic note in treble (octave 4–5)
- **Middle**: 1–2 more chord tones filling the RH
- **Gap**: 3–8 strings, open enough to breathe
- **Total**: 3–5 notes

---

## Extensions (not yet implemented)

- **Voice leading** across a progression — prefer candidates where the top
  voice moves by step from the previous chord's top. Enabled via the
  `context` arg to `pretty()`.
- **Inversion-aware** — score bonuses for specific inversions requested by
  the composer ("V7 in 3rd inversion").
- **Substitution-aware** — accept jazz substitutions (tritone sub, diatonic
  substitution) when the context allows.
- **Automatic pool rework** — run over all 118 pool fractions, rescore them,
  flag the worst-sounding, propose replacements.

---

## Relationship to the grammar

A fraction is the **realized** form of a `bishape` (two `shape`s plus gap).
The scoring / generation module sits between the **chord** layer (what harmony
is being named) and the **renderer** (what gets drawn / played):

```
chord (Ⅴ7, ⅠΔ, ⅱ7) → pretty_fraction → bishape realization → renderer (LilyPond/ABC/audio)
```

The algorithm is the bridge that turns "name this chord prettily" into "here
are the exact strings to pluck."
