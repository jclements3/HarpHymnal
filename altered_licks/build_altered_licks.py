#!/usr/bin/env python3
"""
Build the pedal-harp version of Jens Larsen's "15 II V I licks - Altered
Dominants" (jazz-guitar e-book, 2017).

Source progression for every lick:  Dm7 | G7alt | Cmaj7   (a ii-V-I in C major).

Transcription: the guitar TAB was read note-by-note (concert pitch) by 15
parallel agents and cross-checked against Jens's stated device for each lick
and against the G-altered scale (= Ab melodic minor).  This script:

  * spells each note for the HARP  (Dm7/Cmaj7 bars in C major; the G7alt bar
    in flats, i.e. Ab-melodic-minor spelling, so the pedal setup is coherent),
  * emits a renderable ABC file per lick with chord symbols + a pedal header,
  * computes the harp PEDAL SETUP per bar (D C B | E F G A) and the foot-moves
    between bars, flagging any within-bar pedal conflict,
  * checks every note against the 47-string range,
  * writes HARP_NOTES.md (per-lick pedagogy) and README.md.

The whole harp insight: pedal-wise each lick is just
        C major  ->  Ab melodic minor  ->  C major
two foot changes, at the two bar lines.  Some G bars don't pluck every altered
string, but dialing the full Ab-melodic-minor tuning is always safe because
every G-bar note lives in that scale.
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ABC_DIR = os.path.join(HERE, "abc")
os.makedirs(ABC_DIR, exist_ok=True)

# ---- transcriptions: per lick, three bars, each a list of (midi, dur) -------
# dur codes: "16","8","4","2","1" (sixteenth..whole).  Bars are 4/4.
LICKS = {
 1:{"dev":"Dm7: Dm7 + stack of 4ths.  G7: Bb-minor-pentatonic line.",
    "D":[(50,"8"),(53,"8"),(57,"8"),(60,"8"),(62,"8"),(57,"8"),(62,"8"),(67,"8")],
    "G":[(68,"8"),(65,"8"),(61,"8"),(63,"8"),(61,"8"),(56,"8"),(58,"8"),(56,"8")],
    "C":[(55,"1")]},
 2:{"dev":"Dm7: Fmaj7(13) arpeggio.  G7: quartal stack from B (aug4) + Ab-minor triad.",
    "D":[(53,"8"),(57,"8"),(60,"8"),(62,"8"),(64,"8"),(62,"8"),(60,"8"),(57,"8")],
    "G":[(59,"8"),(65,"8"),(70,"8"),(67,"8"),(68,"8"),(75,"8"),(71,"8"),(68,"8")],
    "C":[(74,"1")]},
 3:{"dev":"Dm7: descending Dm7 arpeggio + scale fragment.  G7: AbMaj7 + Db-major over a natural-5 (D).",
    # Re-verified from the TAB at high zoom: G-bar note 6 really is fret3/str2 = D natural
    # (the natural 5th of G, a chord tone) -- NOT a misread. Keep it.
    "D":[(72,"8"),(69,"8"),(65,"8"),(62,"8"),(69,"8"),(70,"8"),(72,"8"),(69,"8")],
    "G":[(72,"8"),(68,"8"),(63,"8"),(61,"8"),(65,"8"),(62,"8"),(60,"8"),(56,"8")],
    "C":[(52,"1")],
    "flag":"Dm7 bar uses Bb (D natural minor) -> B pedal flat for bar 1. G7 bar has BOTH Db and D-natural -> a within-bar D pedal change (set Db, then snap to D-natural for note 6). C-natural here (AbMaj7 3rd), not Cb."},
 4:{"dev":"Dm7: D-dorian run + Fmaj7 shell.  G7: Bmaj7(b5) arpeggio + B-aug triad.",
    "D":[(50,"8"),(52,"8"),(53,"8"),(55,"8"),(53,"8"),(57,"8"),(64,"8"),(62,"8")],
    "G":[(58,"8"),(59,"8"),(63,"8"),(65,"8"),(68,"8"),(67,"8"),(71,"8"),(75,"8")],
    "C":[(74,"1")]},
 5:{"dev":"Dm7: Am7 shell + Fmaj7 arpeggio.  G7: Ab-minor triad + scale run.",
    "D":[(57,"8"),(60,"8"),(67,"8"),(64,"8"),(65,"8"),(69,"8"),(72,"8"),(76,"8")],
    "G":[(75,"8"),(71,"8"),(68,"8"),(70,"8"),(71,"8"),(73,"8"),(70,"8"),(68,"8")],
    "C":[(67,"1")]},
 6:{"dev":"Dm7: Fmaj7 arpeggio (Dm9) then 4ths-from-D (Dm11).  G7: descending triad pair Eb-major + Db-major.",
    # G bar re-read from the TAB at high zoom (the first pass missed 2 notes):
    # frets 8,8,8 / 6,6,6 / 8,6 on strings 2,3,4 / 2,3,4 / 5,4 = two descending major triads.
    "D":[(53,"8"),(57,"8"),(60,"8"),(64,"8"),(62,"8"),(67,"8"),(72,"8"),(69,"8")],
    "G":[(67,"8"),(63,"8"),(58,"8"),(65,"8"),(61,"8"),(56,"8"),(53,"8"),(56,"8")],
    "C":[(55,"1")]},
 7:{"dev":"Dm7: scalar, Dm7 triad on strong beats.  G7: tritone triads Ab-minor + Db-major.",
    "D":[(50,"8"),(52,"8"),(53,"8"),(55,"8"),(57,"8"),(60,"8"),(59,"8"),(57,"8")],
    "G":[(56,"8"),(59,"8"),(63,"8"),(61,"8"),(65,"8"),(68,"8"),(67,"8"),(65,"8")],
    "C":[(64,"1")]},
 8:{"dev":"Dm7: Dm11 extended arpeggio (Wes sweep).  G7: triad pair Eb-major + Db-major.",
    "D":[(50,"8"),(53,"8"),(57,"8"),(60,"8"),(64,"8"),(67,"8"),(65,"8"),(64,"8")],
    "G":[(67,"8"),(63,"8"),(58,"8"),(65,"8"),(61,"8"),(56,"8"),(53,"8"),(56,"8")],
    "C":[(55,"1")]},
 9:{"dev":"Dm7: pentatonic exercise.  G7: scale run + stack of 4ths from B.",
    "D":[(69,"8"),(67,"8"),(62,"8"),(65,"8"),(62,"8"),(57,"8"),(60,"8"),(57,"8")],
    "G":[(53,"8"),(55,"8"),(56,"8"),(58,"8"),(59,"8"),(65,"8"),(70,"8"),(68,"8")],
    "C":[(67,"1")]},
 10:{"dev":"Dm7: 5th-arpeggio encircling the 3rd + descending run.  G7: Bmaj7(#5) arpeggio + scale.",
    "D":[(57,"8"),(60,"8"),(64,"8"),(67,"8"),(65,"8"),(64,"8"),(62,"8"),(60,"8")],
    "G":[(59,"8"),(63,"8"),(67,"8"),(70,"8"),(71,"8"),(73,"8"),(70,"8"),(68,"8")],
    "C":[(67,"1")]},
 11:{"dev":"Dm7: Fmaj7 drop2 arpeggio (>2 octaves).  G7: scale run + diatonic 3rds.",
    "D":[(41,"8"),(48,"8"),(52,"8"),(57,"8"),(60,"8"),(62,"8"),(64,"8"),(67,"8")],
    "G":[(68,"8"),(71,"8"),(70,"8"),(68,"8"),(65,"8"),(61,"8"),(63,"8"),(59,"8")],
    "C":[(62,"1")]},
 12:{"dev":"Whole line quartal.  Dm7: 4ths from G (Dm7(11)).  G7: arpeggio from Eb (b13 b9 b5).",
    "D":[(65,"8"),(55,"8"),(60,"8"),(65,"8"),(62,"8"),(64,"8"),(65,"8"),(62,"8")],
    "G":[(61,"8"),(51,"8"),(56,"8"),(61,"8"),(59,"8"),(68,"8"),(67,"8"),(65,"8")],
    "C":[(64,"1")]},
 13:{"dev":"Dm7: D-pentatonic as diatonic triads.  G7: Bb-minor connection.",
    "D":[(62,"8"),(67,"8"),(72,"8"),(60,"8"),(65,"8"),(69,"8"),(62,"8"),(67,"8")],
    "G":[(68,"8"),(65,"8"),(67,"8"),(68,"8"),(65,"8"),(61,"8"),(58,"8"),(56,"8")],
    "C":[(55,"1")]},
 14:{"dev":"Dm7: open F-major triad.  G7: triad pair B-augmented + Db-major.",
    "D":[(57,"8"),(65,"8"),(72,"8"),(69,"8"),(65,"8"),(62,"8"),(64,"8"),(65,"8")],
    "G":[(67,"8"),(63,"8"),(59,"8"),(65,"8"),(61,"8"),(56,"8"),(55,"8"),(53,"8")],
    "C":[(52,"1")]},
 15:{"dev":"Dm7: quartal arpeggios.  G7: Ab-sus4 (Ab Db Eb) upper-structure triad.",
    "D":[(50,"8"),(55,"8"),(60,"8"),(65,"8"),(62,"8"),(64,"8"),(65,"8"),(67,"8")],
    "G":[(68,"8"),(73,"8"),(75,"8"),(80,"8"),(77,"8"),(79,"8"),(77,"8"),(75,"8")],
    "C":[(76,"1")]},
}

# ---- spelling ---------------------------------------------------------------
LETTER_PC = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
# C-major spelling: pc -> (letter, accidental in -1/0/+1)
SPELL_CMAJ = {0:('C',0),1:('C',1),2:('D',0),3:('E',-1),4:('E',0),5:('F',0),
              6:('F',1),7:('G',0),8:('A',-1),9:('A',0),10:('B',-1),11:('B',0)}
# Ab-melodic-minor (flat) spelling for the G7alt bar: Ab Bb Cb Db Eb F G
SPELL_ABMM = {8:('A',-1),10:('B',-1),11:('C',-1),1:('D',-1),3:('E',-1),
              5:('F',0),7:('G',0),0:('C',0),9:('A',0)}  # 0,9 as fallbacks if they occur

ACC_SYM = {-1:'_',0:'=',1:'^'}        # ABC accidental prefixes
ACC_NAME = {-1:'b',0:'♮',1:'#'}   # display: flat / natural / sharp

def spell(midi, bar):
    pc = midi % 12
    table = SPELL_ABMM if bar == 'G' else SPELL_CMAJ
    letter, acc = table.get(pc, SPELL_CMAJ[pc])
    # octave of the spelled LETTER (not the pitch class): find o so that the
    # natural letter pitch is within 1 semitone of (midi-acc).
    target = midi - acc
    o = round((target - LETTER_PC[letter]) / 12) - 1
    return letter, acc, o

def abc_note(midi, dur, bar, state):
    letter, acc, o = spell(midi, bar)
    # accidental: emit only when it changes the running bar state for this letter
    out = ''
    if state.get(letter) != acc:
        out += ACC_SYM[acc]
        state[letter] = acc
    # octave marks
    if o >= 5:
        out += letter.lower() + "'" * (o - 5)
    elif o == 4:
        out += letter
    else:
        out += letter + "," * (4 - o)
    # duration relative to L:1/8
    out += {"16":"/2","8":"","4":"2","2":"4","1":"8"}[dur]
    return out

# ---- pedal setup ------------------------------------------------------------
PEDAL_ORDER = ['D','C','B','E','F','G','A']   # left foot D C B | right foot E F G A

def bar_pedals(notes, bar):
    """Return {letter: set(accidentals)} actually used in this bar."""
    used = {}
    for midi, _ in notes:
        letter, acc, _o = spell(midi, bar)
        used.setdefault(letter, set()).add(acc)
    return used

def pedal_row(used):
    """Render the 7-pedal row; '.' = not plucked this bar (free)."""
    cells = []
    for L in PEDAL_ORDER:
        if L in used:
            accs = used[L]
            cells.append(L + "/".join(ACC_NAME[a] for a in sorted(accs)))
        else:
            cells.append(L + ".")
        if L == 'B':
            cells.append("|")
    return " ".join(cells)

def conflicts(used):
    return [L for L, accs in used.items() if len(accs) > 1]

# ---- range check ------------------------------------------------------------
HARP_LOW, HARP_HIGH = 24, 104    # ~C1 .. G#7 on a 47-string pedal harp (concert)

def midi_name(m):
    # flat spellings so note lists match the pedal language (Db/Eb/Ab/Bb)
    names=['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
    return f"{names[m%12]}{m//12-1}"

# ---- emit -------------------------------------------------------------------
def build_abc(n, L):
    lines = []
    lines.append(f"X:{n}")
    lines.append(f"T:Altered ii-V-I Lick {n} (after Jens Larsen)")
    lines.append("C:Jens Larsen (guitar original) - harp adaptation")
    lines.append("M:4/4")
    lines.append("L:1/8")
    lines.append("Q:1/4=120")
    lines.append("K:C")
    # pedal header as a comment-ish info line
    body = []
    for bar in ('D','G','C'):
        chord = {'D':'Dm7','G':'G7alt','C':'Cmaj7'}[bar]
        state = {L:0 for L in LETTER_PC} # K:C -> every letter natural at bar start
        toks = [f'"{chord}"']
        for i,(midi,dur) in enumerate(L[bar]):
            tok = abc_note(midi, dur, bar, state)
            if i == 0:
                toks[-1] = f'"{chord}"' + tok
            else:
                toks.append(tok)
        seg = " ".join(toks)
        # pad short bars (e.g. lick 6 G) to a full 4/4 with a rest
        total = sum({"16":0.5,"8":1,"4":2,"2":4,"1":8}[d] for _,d in L[bar])
        if total < 8 and bar != 'C':
            seg += f" z{int(8-total)}"
        body.append(seg)
    lines.append(" | ".join(body) + " |]")
    return "\n".join(lines) + "\n"

def main():
    notes_md = ["# Harp Notes - 15 Altered-Dominant ii-V-I Licks",
        "",
        "Pedal-harp adaptation of Jens Larsen's jazz-guitar e-book. Every lick is",
        "**Dm7 | G7alt | Cmaj7** (ii-V-I in C). Pitches are concert pitch, transcribed",
        "from the guitar TAB.",
        "",
        "## The one big idea",
        "",
        "Pedal-wise each lick is just **C major -> Ab melodic minor -> C major** -- two",
        "foot changes, at the two bar lines. The whole G-altered scale",
        "(`G Ab Bb Cb Db Eb F`) IS Ab melodic minor, so setting that tuning for bar 2",
        "covers every altered note. Reset to C major for the Cmaj7 resolution.",
        "",
        "Pedal rows below are written `D C B | E F G A` (left foot | right foot).",
        "`b`=flat `♮`=natural `#`=sharp; `.` = string not plucked in that bar (pedal free).",
        "",
        "**The hard part on harp:** the Dm7->G7alt change can need up to five pedals",
        "(flat C D E A B). With continuous eighth-notes there's little time, so pre-set",
        "the pedals you can during bar 1 and dial the rest right at the bar line. Practise",
        "the V-I (bars 2-3) alone first.",
        "",
    ]
    range_issues = []
    for n in range(1,16):
        L = LICKS[n]
        abc = build_abc(n, L)
        path = os.path.join(ABC_DIR, f"lick_{n:02d}.abc")
        open(path,"w").write(abc)
        # per-lick notes
        notes_md.append(f"## Lick {n}")
        notes_md.append("")
        notes_md.append(f"*{L['dev']}*")
        notes_md.append("")
        for bar in ('D','G','C'):
            chord = {'D':'Dm7','G':'G7alt','C':'Cmaj7'}[bar]
            pcs = bar_pedals(L[bar], bar)
            names = " ".join(midi_name(m) for m,_ in L[bar])
            notes_md.append(f"- **{chord}**: {names}")
            notes_md.append(f"  - pedals: `{pedal_row(pcs)}`")
            cf = conflicts(pcs)
            if cf:
                notes_md.append(f"  - WITHIN-BAR PEDAL CHANGE on: {', '.join(cf)} (re-set mid-bar)")
        if L.get("flag"):
            notes_md.append(f"- FLAG: {L['flag']}")
        # range
        for bar in ('D','G','C'):
            for m,_ in L[bar]:
                if not (HARP_LOW <= m <= HARP_HIGH):
                    range_issues.append((n,m))
        lo = min(m for bar in 'DGC' for m,_ in L[bar])
        hi = max(m for bar in 'DGC' for m,_ in L[bar])
        notes_md.append(f"- range: {midi_name(lo)}..{midi_name(hi)}")
        notes_md.append("")
    notes_md.append("## Range")
    notes_md.append("")
    if range_issues:
        notes_md.append("Out-of-range notes (47-string harp ~C1..G#7):")
        for n,m in range_issues:
            notes_md.append(f"- lick {n}: {midi_name(m)}")
    else:
        notes_md.append("All notes fall within the 47-string pedal-harp range (~C1..G#7). No transposition needed.")
    notes_md.append("")
    open(os.path.join(HERE,"HARP_NOTES.md"),"w").write("\n".join(notes_md))

    readme = f"""# 15 Altered-Dominant ii-V-I Licks - Pedal-Harp Version

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
"""
    open(os.path.join(HERE,"README.md"),"w").write(readme)
    print("wrote 15 ABC files + HARP_NOTES.md + README.md")
    print("range issues:", range_issues or "none")

if __name__ == "__main__":
    main()
