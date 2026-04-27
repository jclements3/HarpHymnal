# Quick Reference

How to read one shape token. For everything else, see [README](README.html).

A **shape** is what one hand commits to in the air before it touches the
strings — which fingers go where, in what spread. Spaces separate shapes:
each space means the hand lifts and forms the next configuration.

## Anatomy

```
2L^1 5
│ │ │ │
│ │ │ └─ intervals: gaps between adjacent fingers, bottom-up
│ │ └─── degree (1-7) with the hat: the bottom finger's scale degree
│ └───── hand: L (left) or R (right)
└─────── octave (1-7): bottom-up; octave 4 contains middle C
```

The **hat** (`^`) is the only thing that distinguishes the degree digit
from an interval digit. It renders as a literal hat over the number.

## The four parts

**Octave.** `1` to `7`, indexed bottom-up on the concert pedal harp.
Octave 4 contains middle C. `+1L` / `-2R` are relative. No prefix means
"same octave as the previous shape".

**Hand.** `L` = left, `R` = right. (Drills also use `x` = "either".)

**Degree.** `^1` to `^7`. The pitch the bottom finger lands on, named
relative to the piece's tonic. In C major: `^1` = C, `^3` = E, `^5` = G.

**Intervals.** Each digit after the degree is the gap to the next finger
up, in scale steps. `2` = step, `3` = third, `4` = fourth, … hex `a`-`f`
continue past `9`. Read bottom-up.

## Worked examples (Tonic: C, C-major pedals)

| Token       | Notes        | Reading                            |
|-------------|--------------|------------------------------------|
| `3L^1`      | C3           | one finger on C3                   |
| `3R^1 3`    | C4 E4        | two fingers, a third apart         |
| `3R^1 33`   | C4 E4 G4     | triad: root + third + third = 1·3·5|
| `2L^5 4`    | G2 C3        | bass fifth-to-octave-tonic         |
| `4R^3 5`    | E4 B4        | wide third (a fifth gap) on the 3  |

## Two hands in one bar

LH and RH shapes appear space-separated, low to high:

```
2L^1 5   3R^3 5
LH bass    RH upper
```

## Not covered here

Subscripts `₁-₈`, operators `$ & * ~`, two-hand split notation, the
header block (`Title:` / `Number:` / `Tonic:` / `Pedals:` / braille
pedal cells), inline pedal changes, reach calibration. All in
[README](README.html).
