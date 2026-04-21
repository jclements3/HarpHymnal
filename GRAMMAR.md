# HarpHymnal Grammar v4

Authoritative EBNF for the HarpHymnal ecosystem. Every script parses into and emits from these productions. See `SDD.md` for the architectural narrative; this file is the grammar alone.

```ebnf
(* ═════════════════════════════════════════════════════════════════
   HarpHymnal Grammar v4
   ═════════════════════════════════════════════════════════════════ *)

(* ------- Atoms ------- *)
interval   = "2" | "3" | "4" ;
degree     = "1" | "2" | "3" | "4" | "5" | "6" | "7" ;
digit      = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
number     = digit, { digit } ;
text       = ? free string ? ;
letter     = "A" | "B" | "C" | "D" | "E" | "F" | "G" ;
accidental = "♭" | "♯" ;

(* ------- Roman numerals ------- *)
numeral    = "I"  | "ii"  | "iii" | "IV" | "V"  | "vi"  | "vii○"
           | "i"  | "ii○" | "III" | "iv" | "v"  | "VI"  | "VII" ;
quality    = "Δ" | "Δ7" | "7" | "ø7" | "○7"
           | "6" | "9" | "s2" | "s4" | "q" | "q7" | "+8" ;
inversion  = "¹" | "²" | "³" ;

(* ------- Chord naming ------- *)
legacy     = numeral, [ quality ] ;               (* traditional pitch-class name; no inversion; ambiguous — `ii7` tells you Dm7 somewhere, nothing about bass or voicing *)
(* Note: the handout.tex uses legacy + inversion (e.g. `ii7³`); this form can collide across different shapes with the same pitch classes (rows 233 and 434 both reduce to `ii7³`). *)

(* ------- Voicings ------- *)
intervals  = interval, interval, { interval } ;
shape      = degree, intervals ;
bishape    = shape, shape ;                             (* constraint: gap(lh, rh) >= 0; pool prefers gap < 4 *)
gap        = number ;                                   (* derived: min(positions(rh)) - max(positions(lh)) - 1;
                                                           gap=0 = adjacent strings (tightest); gap<0 = same-string
                                                           collision (unplayable); gap<4 = preferred harmonic range *)

(* ------- Chord names ------- *)
chord      = ??? ;                                (* pattern-unique: each distinct shape gets a distinct name; design TBD *)
bichord    = chord, chord ;

(* ------- Pool ------- *)
ipool      = degree, digit, digit ;                     (* {degree}{rank:02d} — first digit = LH degree 1..7, last two = rank inside that degree; paths are the low ranks, reserve the high ranks, 118 entries total *)

(* ------- Drill algebra ------- *)
brace      = ipool, { ipool } | chord ;
step       = brace, { brace } ;
drill      = technique, path, step, { step } ;
instance   = (shape | bishape), { shape | bishape } ;

(* ------- Techniques ------- *)
technique    = substitution | approach | voicing | placement ;
substitution = "Third sub" | "Quality sub" | "Modal reframing"
             | "Deceptive sub" | "Common-tone pivot" ;
approach     = "Step approach" | "Third approach" | "Dominant approach"
             | "Suspension approach" | "Double approach" ;
voicing      = "Inversion" | "Density" | "Stacking" | "Pedal"
             | "Voice leading" | "Open/closed spread" ;
placement    = "Anticipation" | "Delay" ;

(* ------- Paths ------- *)
path       = ("2nds" | "3rds" | "4ths"), ("CW" | "CCW") ;

(* ═════════ Music side ═════════ *)

music      = song | piece ;
song       = metadata, bars, lyrics ;
piece      = metadata, bars ;

metadata   = title, key, meter, tempo, [ pedals ],
             [ phrases ], [ form ] ;
title      = text ;
key        = root, mode ;
root       = letter, [ accidental ] ;
mode       = "major" | "minor"
           | "dorian" | "phrygian" | "lydian"
           | "mixolydian" | "aeolian" | "locrian" ;
meter      = beats, unit ;
beats      = number ;
unit       = "1" | "2" | "4" | "8" | "16" | "32" ;
tempo      = number, unit ;

(* ------- Bars ------- *)
bars       = bar, { bar } ;
bar        = melody, (chord | bichord), [ shape | bishape ],
             { ornament }, { pedal_change }, [ technique ] ;
melody     = { note | rest } ;
note       = pitch, duration, { ornament } ;
rest       = duration ;
pitch      = letter, [ accidental ], number ;
duration   = ? quarter-length, e.g. 0.5, 1, 1.5 ? ;

(* ------- Ornaments (lever-harp idiom) ------- *)
ornament     = arpeggio | grace | enclosure | neighbor
             | glissando | damping | harmonic | bisbigliando ;
arpeggio     = "arp" ;
grace        = "grace", pitch ;
enclosure    = "enc", pitch, pitch ;
neighbor     = ("upper" | "lower"), pitch ;
glissando    = "gliss", pitch, pitch ;
damping      = "damp", ("LH" | "RH") ;
harmonic     = "harm" ;
bisbigliando = "bisb", pitch ;

(* ------- Pedal harp (7 pedals, 3 positions) ------- *)
pedals       = pedal_pos, pedal_pos, pedal_pos,        (* D C B — left foot  *)
               pedal_pos, pedal_pos, pedal_pos, pedal_pos ;  (* E F G A — right  *)
pedal_pos    = "flat" | "natural" | "sharp" ;
pedal_change = pedal_letter, pedal_pos ;
pedal_letter = letter ;

(* ------- Lyrics ------- *)
lyrics     = verse, { verse } ;
verse      = syllable, { syllable } ;
syllable   = ibar, inote, text, [ melisma ] ;
melisma    = "continues" ;

(* ------- Phrases ------- *)
phrases    = phrase, { phrase } ;
phrase     = ibar, { ibar }, [ path ] ;

(* ------- Form ------- *)
form       = section, { section } ;
section    = label, ibar, ibar ;
label      = "intro" | "verse" | "chorus" | "bridge" | "refrain" | "outro" ;

(* ------- Refs ------- *)
ibar       = number ;    (* 1-based position in `bars` *)
inote      = number ;    (* 0-based position inside a bar's melody *)
```

## Rendering vs structure

The grammar is pure structure. Rendering choices live in `renderers/`:

| Concept | Structure | Typical rendering |
|---|---|---|
| `bichord` | two chords | `I/V`, space, hrule |
| `meter` | two numbers | `3/4`, `C`, `𝄵` |
| `brace` | list of ipools | `{101\|102\|103}`, `{101,102,103}` |
| `pedal_pos` | abstract state | `♭/♮/♯`, `↑/—/↓`, `up/mid/down` |
| phrase's cycle color | derived from `path` | `leafblue`, `leafgreen`, via stylesheet |

Parsers emit structure; renderers choose glyphs.
