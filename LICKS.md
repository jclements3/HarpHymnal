# LICKS.md — Somerset LH patterns × Larsen RH licks

A portable, self-contained description of the warm-up "lick mixer" in the HarpHymnal
practice tablet app (`tablet_app/app/src/main/assets/practice/index.html`, the `DATA`
object). Paste this whole file into a fresh claude.ai chat and it has everything it needs:
the harmonic frame in Roman numerals, the ABC-notation reading key, and all 15 right-hand
licks + 19 left-hand patterns verbatim.

---

## 1. The harmonic frame (read this first)

Every lick and every accompaniment pattern is written over **one 3-bar phrase**: a minor
**ii–V–I**, concretely realized in **Eb major**.

| Bar | Roman numeral | Chord (Eb) | Function |
|-----|---------------|------------|----------|
| 1   | **ii7**       | Fm7        | predominant |
| 2   | **V7alt**     | Bb7alt     | dominant, *altered* (♭9 ♯9 ♯11 ♭13) |
| 3   | **Imaj7**     | Ebmaj7     | tonic, held a whole bar |

The licks are a pedal-harp adaptation of **Jens Larsen's "15 altered ii-V-I licks."** The
"altered" color in bar 2 comes from playing **Bb super-locrian = B melodic minor** over the
V (gives the ♭9/♯9/♯11/♭13 tensions). So the pedal story across the phrase is:

```
Eb major  →  (B melodic minor over Bb7)  →  Eb major
ii7          V7alt                           Imaj7
```

**Everything is transposable.** To move to another key, transpose the Roman numerals: ii7
stays a minor-7th on scale degree 2, V7alt a dominant on degree 5, Imaj7 on degree 1. The
LH patterns are diatonic templates — they re-key automatically with the `K:` signature.

---

## 2. How to read the notation (ABC)

The snippets below are **ABC notation**. To render or reason about any one of them, wrap it
in this header (the app does the same concatenation internally):

```abc
X:1
M:4/4
L:1/8
K:Eb
V:RH clef=treble
V:LH clef=bass
[V:RH] <paste an RH lick here>
[V:LH] <paste a LH pattern here>
```

ABC reading key:
- **Pitch:** `C` = middle C. `c` = the octave above. A trailing `'` raises an octave (`c'`),
  a trailing `,` lowers one (`C,`, `C,,`). So `F,,` is two octaves below middle-C's F.
- **Duration:** under `L:1/8`, a bare letter is one eighth note; the digit is a multiple of
  eighths. `B8` = 8 eighths = a whole note. `F,,2` = a quarter. `z` = rest.
- **Accidentals:** `^`=sharp, `_`=flat, `=`=natural — but **the `K:Eb` signature already
  flats B, E, A**, so a plain `B`/`E`/`A` *sounds* Bb/Eb/Ab. The licks add `_`/`=` only for
  the chromatic altered tensions in bar 2.
- **Chords / dyads:** `[F,,C,A,]` = those notes struck together. `"Fm7"` is a chord-symbol
  annotation above the staff, not a sounding note.

The chord symbols embedded in the RH licks (`"Fm7"`, `"Bb7alt"`, `"Ebmaj7"`) mark the three
bars = **ii7 | V7alt | Imaj7**.

---

## 3. Right-hand licks — `DATA.warmup` (15)

Single-line melodic vocabulary, one per phrase. Each name reads `<material over ii7> /
<material over V7alt>`; bar 3 always lands on / sustains a tonic chord tone of Imaj7.

```
 1. 4ths / Bb-pent            "Fm7"FAce fcfb | "Bb7alt"=ba=e_g eB_dB | "Ebmaj7"B8
 2. Fmaj7(13) / quartal+Abm   "Fm7"Acef gfec | "Bb7alt"da_d'b =b_g'=d'b | "Ebmaj7"f'8
 3. arp / AbMaj7+Db nat-5     "Fm7"e'c'af c'_d'e'c' | "Bb7alt"e'=b_g=e af_eB | "Ebmaj7"G8
 4. dorian+Fmaj7 / Bmaj7b5    "Fm7"FGAB Acgf | "Bb7alt"_d=d_ga =b_bd'g' | "Ebmaj7"f'8
 5. Am7+Fmaj7 / Abm+run       "Fm7"cebg ac'e'g' | "Bb7alt"_g'd'=b_d' =d'=e'_d'b | "Ebmaj7"b8
 6. Fmaj7+Dm11 / Eb+Db pair   "Fm7"Aceg fbe'c' | "Bb7alt"b_g_da =e=BAB | "Ebmaj7"B8
 7. scalar / Abm+Db tritone   "Fm7"FGAB cedc | "Bb7alt"=Bd_g=e ab_ba | "Ebmaj7"g8
 8. Dm11 sweep / Eb+Db pair   "Fm7"FAce gbag | "Bb7alt"b_g_da =e=BAB | "Ebmaj7"B8
 9. pentatonic / 4ths from B  "Fm7"c'bfa fcec | "Bb7alt"AB=B_d =da_d'b | "Ebmaj7"b8
10. 5-encircle-3 / Bmaj7#5    "Fm7"cegb agfe | "Bb7alt"d_gb_d' =d'=e'_d'=b | "Ebmaj7"b8
11. Fmaj7 drop2 / run+3rds    "Fm7"A,EGc efgb | "Bb7alt"=bd'_d'b a=e_g=d | "Ebmaj7"f8
12. quartal Dm7(11) / Eb arp  "Fm7"aBea fgaf | "Bb7alt"=e_G=Be db_ba | "Ebmaj7"g8
13. pent triads / Bb-min      "Fm7"fbe'e ac'fb | "Bb7alt"=ba_b=b a=e_dB | "Ebmaj7"B8
14. open F triad / Baug+Db    "Fm7"cae'c' afga | "Bb7alt"b_gda =e=B_BA | "Ebmaj7"G8
15. quartal arps / Ab-sus4    "Fm7"FBea fgab | "Bb7alt"=b=e'_g'b' a'_b'a'g' | "Ebmaj7"g'8
```

---

## 4. Left-hand patterns — `DATA.somerset` (19)

"Somerset"-style accompaniment grooves (named after the Somerset Folk Harp School comping
idiom). Each is a **diatonic template** voiced from each bar's chord root, so the three bars
land on roots **F (ii) → Bb (V) → Eb (I)**. Degrees below are relative to the bar's root;
under `K:Eb` the diatonic 3rd/10th comes out as the correct chord third (Ab over Fm, D over
Bb7, G over Eb).

```
 1. Octaves        [F,,F,]8 | [B,,B,]8 | [E,,E,]8
                   → root octave (1+8), held a whole bar.
 2. 1-5-8 Arp      F,,2 C,2 F,4 | B,,2 F,2 B,4 | E,,2 B,,2 E,4
                   → ascending arpeggio root–5th–octave.
 3. 1-5-10 Block   [F,,C,A,]8 | [B,,F,D]8 | [E,,B,,G,]8
                   → block voicing root–5th–10th(=3rd up an 8ve), whole bar.
 4. 1-5-10 Arp     F,,2 C,2 A,4 | B,,2 F,2 D4 | E,,2 B,,2 G,4
                   → same as #3, arpeggiated.
 5. 1-5-10 Arp 3/4 F,,2 C,2 A,2 z2 | B,,2 F,2 D2 z2 | E,,2 B,,2 G,2 z2
                   → #4 with a waltz-y rest on beat 4.
 6. Alberti        F,,C, A,C, F,,C, A,C, | B,,F, DF, B,,F, DF, | E,,B,, G,B,, E,,B,, G,B,,
                   → classic Alberti: root–5th–10th–5th broken eighths.
 7. Calypso        F,,2 z [F,,A,,C,][F,,A,,C,] z [F,,A,,C,]2 | (…transposed)
                   → bass downbeat + syncopated upper-triad stabs.
 8. Latin 1-8-5-5  F,,3 F, C,2 C,2 | B,,3 B, F,2 F,2 | E,,3 E, B,,2 B,,2
                   → root(dotted)–octave–5th–5th.
 9. Latin 1-5-10-5 F,,3 C, A,2 C,2 | B,,3 F, D2 F,2 | E,,3 B,, G,2 B,,2
                   → root(dotted)–5th–10th–5th.
10. Latin 1-10-5-5 F,,3 A, C,2 C,2 | B,,3 D F,2 F,2 | E,,3 G, B,,2 B,,2
                   → root(dotted)–10th–5th–5th.
11. Pretty Waltz w/9
                   F,,2 [F,,A,,C,G,]2 [F,,A,,C,G,]2 z2 | (…)
                   → oom-pah-pah; upper chord adds the 9th (root–♭3–5–9).
12. Slap          F,,2 C,2 F,,2 C,2 | B,,2 F,2 B,,2 F,2 | E,,2 B,,2 E,,2 B,,2
                   → root/5th two-beat ostinato.
13. Samba         F,,C, F,,C, F,,C, F,,C, | (…)
                   → root–5th eighth-note ostinato across the bar.
14. Mexican       F,,3 [F,,A,,C,][F,,A,,C,] [F,,A,,C,]3 | (…)
                   → bass + dotted triad stabs (ranchera feel).
15. Stride        F,,2 [F,,A,,C,]2 F,,2 [F,,A,,C,]2 | (…)
                   → bass–chord–bass–chord (classic stride).
16. Broken Stride F,,3 [F,,A,,C,] F,,3 [F,,A,,C,] | (…)
                   → dotted stride variant.
17. Waltz         F,,2 [F,,A,,C,]2 [F,,A,,C,]2 z2 | (…)
                   → oom-pah-pah with a plain triad.
18. Jazz Waltz    F,,2 [F,,A,,C,G,]2 [F,,A,,C,G,]2 z2 | (…)
                   → waltz with an add9 voicing (root–♭3–5–9).
19. Jazz Waltz Var F,,2 [F,,A,,C,E,]2 [F,,A,,C,E,]2 z2 | (…)
                   → waltz with the FULL seventh chord (root–♭3–5–♭7 = ii7 / V7 / Imaj7).
```

(Patterns 7, 11, 13–19 are abbreviated to bar 1 for readability; bars 2 and 3 transpose the
same shape to the Bb and Eb roots exactly as bars do in 1–6. Full verbatim text is in the
`DATA.somerset` array in `index.html`.)

---

## 5. How they combine

The app pairs **one RH lick × one LH pattern** into a single 3-bar étude (`regenWarm()` in
`index.html`): same key, same `ii7 | V7alt | Imaj7` bars, RH on the treble voice, LH on the
bass voice. "Shuffle" re-rolls the pairing. So the practice unit is always:

> **a Larsen altered-ii–V–I line over a Somerset comp groove, in Eb.**

Example — **Lick 1 × Stride**, ready to render:

```abc
X:1
M:4/4
L:1/8
K:Eb
V:RH clef=treble
V:LH clef=bass
[V:RH] "Fm7"FAce fcfb | "Bb7alt"=ba=e_g eB_dB | "Ebmaj7"B8
[V:LH] F,,2 [F,,A,,C,]2 F,,2 [F,,A,,C,]2 | B,,2 [B,,D,F,]2 B,,2 [B,,D,F,]2 | E,,2 [E,,G,,B,,]2 E,,2 [E,,G,,B,,]2
```

---

## 6. Pedal-harp constraints worth flagging to the other chat

If the receiving chat is going to *compose* with these (not just read them), it needs the
harp rules this app obeys:

- **47-string pedal harp, diatonic per bar.** Chromatic notes require pedal changes between
  bars; you can't get arbitrary accidentals within a fast run. The altered tensions in bar 2
  are reachable because the whole bar sits in one altered-scale pedal setting (B melodic
  minor over Bb7), not note-by-note chromaticism.
- **Bass register:** the LH roots `F,,`/`B,,`/`E,,` sit low; C1–C2 is drone-only territory,
  so keep dense LH voicings at `,`/`,,` (≈ C2 and up), not lower.
- **Hand span ≤ a 10th.** The `[F,,C,A,]`-style LH chords are a root-to-10th grab — already
  at the comfortable limit; don't widen them.
- **Sustain rings** — vary the LH figure every chord (the Somerset patterns do this) rather
  than re-striking a static voicing.

Source of truth for these rules: `HARP_RULES.md` in the HarpHymnal repo.
