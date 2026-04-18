# HarpHymnal

A machine-consumable dataset of 294 hymns from the Open Hymnal, each exported as a rich JSON record suitable for downstream rendering: grand staff notation, SSAATTBB vocal arrangements, organ-pedal staves (bottom 2 octaves for pedal harp), jazz lead sheets, and any other derivative that needs full structural information rather than a PDF.

## What's in the box

```
HarpHymnal/
├── README.md                    # this file
├── OpenHymnal.abc               # source ABC file (370 hymns, 27k lines)
├── HarpChordSystem.json         # 118-fraction pool (paths + reserve) for the reharm mapper
├── HarpChordSystem.tex          # 2-page handout (LaTeX source)
├── HymnReharmTemplate.tex       # LaTeX template for lead sheets
├── tools/
│   ├── hymn_parser.py           # ABC → SATB beats + chord regions + phrases
│   ├── harp_mapper.py           # RN → 118-fraction picker, cycle-aware
│   ├── export_hymn.py           # produces the comprehensive JSON per hymn
│   └── fill_template.py         # reharm JSON → LaTeX lead sheet
└── hymnal_export/               # 294 hymn JSONs
    ├── A_Mighty_Fortress_Is_Our_God.json
    ├── Amazing_Grace.json
    ├── Silent_Night.json
    └── …
```

## JSON schema per hymn

Each file is self-contained. Relevant top-level keys:

```
{
  "title": str,
  "abc_source": str,              // raw ABC block, verbatim (ground truth)
  "metadata": {
    "composer": str,              // from C:Music: / C:Setting: lines
    "lyricist": str,              // from C:Words: / C:Text: lines
    "year": str,                  // primary year (prefers music_year, falls back to words_year)
    "words_year": str,            // year from the Words: field
    "music_year": str,            // year from the Music: / Setting: field
    "copyright": str,             // copyright statement text (boilerplate filtered from composer/lyricist)
    "c_lines": [str],             // all raw C: lines preserved verbatim
    "z_lines": [str]              // all raw Z: lines (attribution)
  },
  "music": {
    "key_header": str,            // K: header, e.g. "D major"
    "key_detected": str,          // after tonic detection (may differ for modal tunes)
    "key_root": str,              // e.g. "D", "B-", "E"
    "mode": "major"|"minor",
    "modal_name": "ionian"|"dorian"|"phrygian"|"lydian"|"mixolydian"|"aeolian"|"locrian",
    "tonic_override_applied": bool,
    "meter": str,                 // "4/4", "3/4", "6/8", etc
    "meter_num": int,
    "meter_den": int,
    "unit_note_length": str,      // L: header
    "total_bars": int,
    "total_ql": float             // total quarter-note length
  },
  "voices": {                     // full per-note dumps, not just beat samples
    "S1V1": [                     // soprano / melody (top staff, upper voice)
      {
        "offset_ql": float,       // position in quarter-notes from start
        "bar": int, "beat": float,
        "pitch": "D5"|null,       // null if rest
        "midi": 74,
        "duration_ql": float,
        "is_rest": bool,
        "tied_next": bool,        // tied to next note?
        "fermata": bool,
        "is_chord": bool,         // (optional) present if note is actually a chord
        "pitches_all": [str]      // (optional) all pitches if is_chord
      },
      …
    ],
    "S1V2": [...],                // alto (top staff, lower voice)
    "S2V1": [...],                // tenor (bottom staff, upper voice)
    "S2V2": [...]                 // bass (bottom staff, lower voice; the pedal part)
  },
  "extra_voices": {                // additional voices from 3-staff arrangements
    "S3V2": [...]?,                // optional organ pedal line
    "S3V3": [...]?                 // optional pedal line (either S3V2 or S3V3)
  },
  "beats": [                      // SATB sampled vertically at every beat
    {
      "offset_ql": float,
      "bar": int, "beat": int,
      "S": "D5"|null, "A": "A4"|null, "T": "F#4"|null, "B": "D3"|null,
      "rn_raw": str,              // music21's raw roman numeral
      "rn_clean": str,             // cleaned (V752→V7, etc)
      "is_nct": bool               // is the soprano a passing/neighbor tone?
    },
    …
  ],
  "regions": {
    "smoothed": [ …beat-level with single-beat noise absorbed… ],
    "per_bar":  [ …one chord per bar, downbeat weighted… ],
    "per_halfbar": [ …two chords per bar… ]
  },
  "phrases": [
    {
      "label": "A",
      "bars": [1,2,3,4],
      "ending_marker": "fermata"|"cadence"|"end",
      "start_ql": float,
      "end_ql": float
    },
    …
  ],
  "lyrics": {
    "verse_count": int,
    "verses": {
      "1": {
        "raw_text": str,                    // cleaned full-verse prose
        "syllables": [                       // tokenized, aligned to S1V1 notes
          {
            "text": "Joy",
            "note_offset_ql": 0.0,           // offset of the note this syllable sits under
            "note_pitch": "D5",
            "is_melisma_start": bool,
            "continues_previous": bool        // true if this note continues a melisma
          },
          …
        ]
      },
      "2": {...}, "3": {...}, …
    }
  },
  "harmony": {
    "roman_numerals_per_bar": [
      {"bar": 1, "rn": "I", "duration_beats": 2},
      …
    ],
    "harp_chord_assignments": [            // from the 118-fraction pool (paths + reserve)
      {
        "bar": 1,
        "rn": "I",                         // functional roman numeral
        "melody": "D5",
        "contour": "ascending"|"descending"|"static",
        "lh_roman": "I", "lh_figure": "133",      // the harp LH voicing
        "rh_roman": "iii", "rh_figure": "743",    // the harp RH voicing
        "mood": "Soft",                    // label from the handout
        "source": "paths"|"reserve",
        "method": "reserve"|"2nds-CW"|"3rds-CCW"|"4ths-CW"|"4ths-CCW"|…,
        "alternates": [                    // top 2 other candidates
          {...}, {...}
        ]
      },
      …
    ]
  }
}
```

## How the data was produced

1. `hymn_parser.py` reads the ABC source, splits into 4 voices (S1V1, S1V2, S2V1, S2V2), parses each with music21, samples beat-by-beat SATB, extracts cleaned roman numerals, and detects phrase boundaries from fermatas (preferred) or cadences (fallback: V/IV/ii → I, including modal cadences VII/bVII/III/v → i for minor hymns).

2. `harp_mapper.py` takes a roman numeral plus the optional melody note and returns the top-scoring fractions from the 118-fraction pool (paths + reserve). It handles minor keys by translating RNs to the relative major (the pool entries are Ionian-labeled). Cycle-aware: detects whether an RN-to-RN transition is a 2nds / 3rds / 4ths cycle edge and picks path entries accordingly, with CW/CCW direction inferred from melodic contour.

3. `export_hymn.py` combines both into a single JSON per hymn, preserving the original ABC source and adding structural/analytical layers on top.

## Harp Chord System constraints

The 118-fraction pool is **strictly diatonic** — no tritone substitutions, no ♭II7, no modal interchange, no altered dominants with real ♭9 pitches. The mapper will correctly return low scores for out-of-vocabulary progressions (e.g., harmonic-minor V with chromatic leading tone). For minor-key hymns, the natural-minor `v` or `III` is used instead of the chromaticized `V`.

Melodic contour drives cycle direction:
- Ascending melody → CW edges (Resolving, Lifting, Exploring, Triumphing)
- Descending melody → CCW edges (Landing, Lofting, Dreaming, Brooding)

## Known limitations

- **Harmonic-minor V** cannot be expressed in the 118 (it needs a chromatic pitch). Minor-key hymns fall back to modal dominants or `III` substitutes. This is intentional — the system is diatonic by design.

- **Voice-layout recognition**: the parser handles three ABC conventions found in OpenHymnal.abc:
  1. Standard 4-voice SATB using explicit `[V: S1V1]`, `[V: S1V2]`, `[V: S2V1]`, `[V: S2V2]` labels
  2. Two-staff piano reduction with `[V: S1]` and `[V: S2]`, where multi-note chords like `[Ac]` are automatically split into top (soprano/tenor) and bottom (alto/bass) pitches
  3. Three-staff arrangement with `[V: S1]` (solo/melody) + `[V: S2V1]` (alto) + `[V: S2V2]` (tenor) + `[V: S3V1]` (bass) + optional `[V: S3V2]`/`[V: S3V3]` (organ pedal or extra divisi). The extra S3* voices are preserved in the output JSON's `extra_voices` field for future pedal-staff rendering.

Multi-line voice blocks (where `[V: X]` is on its own line and notes follow on subsequent lines) are also supported. This recovered 9 hymns that were previously unparseable, including "Away In A Manger," "I Bind Unto Myself Today," "Jesus Loves Me," "Now Thank We All Our God," and others.

- **Voice layout conventions**: the parser recognizes three ABC voice layouts: (a) standard 4-voice SATB using S1V1/S1V2/S2V1/S2V2 labels, (b) 2-staff piano reduction with S1+S2 labels and packed chords like `[Ac]` that get split into top/bottom pitches, and (c) 3-staff arrangements with S1+S2V1/V2+S3V1/V3 where the S3V3 (or S3V2) voice is preserved in the `extra_voices` field for future organ-pedal rendering.

- **Tonic detection** uses weighted voting across bass-first, bass-last, melody-first, melody-last, most-common-bass-pc, and header-tonic. The winner is the pitch class with highest total weight. Header wins on ties. This handles most ambiguous cases but may occasionally disagree with traditional analyses of specific modal hymns (e.g., Slane tune in "Be Thou My Vision" is labeled phrygian per the scale intervals produced, though some sources call it dorian or mixolydian).

- **Modal name**: for any hymn where the scale pitches produce a recognized church mode (Dorian, Phrygian, Mixolydian, Aeolian, etc.), `music.modal_name` carries that specific label regardless of whether `mode` is "major" or "minor". Consumers doing mode-aware rendering (e.g., correct accidentals in key signatures) should prefer `modal_name` over `mode`.

- **Regions can be noisy** on dense chorales (music21 sometimes labels passing chords as `#IVø7` or `V42`). The per_bar downsampling collapses these with a downbeat-weighted vote, but some residue remains.

- **Phrase detection** covers both fermata-marked hymns (~16% of the corpus) and cadence-based fallback (~84%). In hymns without V→I cadences AND without fermatas, phrase boundaries may be less musical (worst case: one phrase per 4 bars).

- **Lyric alignment** is one-token-per-non-rest-S1V1-event. Each `*` melisma marker produces an entry with empty text and `continues_previous=true`, positioned on its own note. The `syllables` array length equals the count of Note+Chord events in S1V1 (rests are excluded).

- **Shared refrains**: when an ABC melody line-group has only 1 `w:` line in a hymn where other groups have multiple verses, the single line is treated as a shared refrain and broadcast to every verse. This handles the common pattern where the chorus text is written once in the source.

- **Harmonic-minor V substitution**: The 118-fraction pool is strictly diatonic, so a classical harmonic-minor V (with chromatic leading tone) cannot be represented. When a V chord appears in a minor-mode hymn, the mapper selects one of four substitution strategies based on context:
  - `bVII_backdoor` — when preceded by IV (continues plagal pull)
  - `III_deceptive` — at fermata-marked final cadences (dramatic, Aeolian)
  - `pedal_i` — for brief V with tonic-compatible melody
  - `modal_v` — default for mid-phrase V (natural-minor v7, modal feel)
  
  Each `harp_chord_assignments` entry includes a `harmonic_substitution` field (one of the above strategy names, or `null`) and a `requested_rn` field preserving the original roman numeral. This lets future rendering phases know when a substitution occurred and optionally annotate the score.

- **Fermata recovery**: music21's ABC parser silently drops `!fermata!` decorations. This exporter re-derives fermata positions by tokenizing the raw ABC text and matching note positions, so each Note entry in `voices.*` carries the correct `fermata: bool` flag. Note that fermatas are typically marked only on the top voice (S1V1) in the ABC source — other voices in the same chord position should be rendered with fermatas from the S1V1 reference.

- **Chord-in-voice handling**: upper voices (S1V1, S1V2) surface the TOP pitch of any chord in the `pitch` field; lower voices (S2V1, S2V2) surface the BOTTOM pitch. `pitches_all` always contains all pitches of the chord so future renderers (e.g., SSAATTBB splitters) can redistribute them.

## Reproducing the export

```bash
pip install music21 --break-system-packages
python3 tools/export_hymn.py --all -o hymnal_export/
```

Takes roughly 5 minutes on a reasonable machine.

## Licensing

The Open Hymnal source material is public domain. The analytical overlays (SATB sampling, roman numeral extraction, Harp Chord System mapping) are derivative works generated algorithmically and released under the same terms.

The Harp Chord System vocabulary (`HarpChordSystem.json`, `HarpChordSystem.tex`) is a custom pedagogical system for lever harp — separate attribution.
