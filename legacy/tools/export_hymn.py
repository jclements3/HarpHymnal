#!/usr/bin/env python3
"""
export_hymn.py — produce a comprehensive machine-consumable JSON for a hymn
that preserves all structural information needed for future phases:
  - Grand staff / SSAATTBB rendering
  - Organ pedal staff (bottom 2 octaves)
  - Syllable-aligned lyrics
  - Harmonic analysis + Harp Chord System mapping
  - Raw ABC source preserved

Usage:
    python3 export_hymn.py "Title" -o output.json
    python3 export_hymn.py --all -o /path/to/dir/  # export every hymn

JSON Schema:
{
  "title": str,
  "abc_source": str,              # raw ABC block, verbatim
  "metadata": {
    "composer": str, "lyricist": str, "tune_name": str, "year": str,
    "copyright": str, "origin": str, "meter_name": str,
    "c_lines": [str],             # raw C: lines for anything we missed
    "z_lines": [str]              # raw Z: lines (attribution)
  },
  "music": {
    "key_header": str,            # as written in K: header
    "key_detected": str,          # after tonic detection
    "key_root": str,
    "mode": "major"|"minor"|"dorian"|...,
    "meter": str,                 # "4/4", "3/4", etc
    "meter_num": int, "meter_den": int,
    "anacrusis_ql": float,        # pickup length in quarter-notes
    "unit_note_length": str,      # L: header, e.g. "1/8"
    "tempo_bpm": int,
    "total_bars": int
  },
  "voices": {
    "S1V1": [  # soprano / melody
      {"offset_ql": float, "bar": int, "beat": float,
       "pitch": "D4"|null, "duration_ql": float,
       "is_rest": bool, "tied_next": bool,
       "fermata": bool}
      ... one object per note/rest
    ],
    "S1V2": [...], "S2V1": [...], "S2V2": [...]
  },
  "beats": [  # sampled at every beat, SATB vertically
    {"offset_ql": float, "bar": int, "beat": int,
     "S": "D4"|null, "A": "A3"|null, "T": "F#3"|null, "B": "D3"|null,
     "rn_raw": str, "rn_clean": str, "is_nct": bool}
  ],
  "regions": {
    "smoothed": [...],      # adjacency-collapsed regions
    "per_bar": [...],       # one chord per bar
    "per_halfbar": [...]
  },
  "phrases": [
    {"label": "A", "bars": [1,2,3,4],
     "ending_marker": "fermata"|"cadence"|"end",
     "start_ql": float, "end_ql": float}
  ],
  "lyrics": {
    "verse_count": int,
    "verses": {
      "1": {
        "raw_text": str,              # cleaned full-verse text
        "syllables": [                # tokenized; aligned to notes
          {"text": "Joy", "note_offset_ql": 0.0, "bar": 1,
           "is_melisma_start": false, "continues_previous": false}
        ]
      },
      "2": {...}
    }
  },
  "harmony": {
    "roman_numerals_per_bar": [  # concise bar → RN listing
      {"bar": 1, "rn": "I", "duration_beats": 3}
    ],
    "harp_chord_assignments": [  # Harp Chord System 118-fraction picks
      {"bar": 1, "rn": "I", "melody": "F4",
       "lh_roman": "I", "lh_figure": "133",
       "rh_roman": "iii", "rh_figure": "743",
       "mood": "Soft", "source": "stacked_chords",
       "method": "stacked"|"2nds-CW"|"3rds-CCW"|"4ths-CW"|...,
       "alternates": [{top 2 other picks}]}
    ]
  }
}
"""
import sys, os, re, json, argparse
sys.path.insert(0, '/home/claude')
from music21 import note as m21note, chord, key, pitch

from hymn_parser import (
    extract_tune, split_voices, build_voice_abc, sample_satb,
    analyze_beats, aggregate_regions, smooth_regions,
    downsample_per_bar, detect_fermata_bars, detect_cadence_bars,
    split_into_phrases, detect_true_tonic, clean_rn
)
from harp_mapper import (
    load_vocab, pick_fraction, pick_transition, infer_contour,
    cycle_of_transition, parse_rn, translate_minor_to_major,
    pick_with_substitution
)
from music21 import converter, note as m21note, chord


# ═════════════════════════════════════════════════════════════════════════════
#   Metadata extraction
# ═════════════════════════════════════════════════════════════════════════════
def extract_metadata(block):
    """Pull composer, lyricist, tune name, years, and copyright from ABC headers.

    ABC hymn headers use several patterns that this function handles:
      1. Single-purpose C: lines — 'C: Words: Author, 1700.' / 'C: Music: ...'
      2. Combined C: lines — 'C: Words: X, 1700. Music: Y, 1800. Setting: Z.'
      3. Continuation lines — a bare C: line following a prefixed one continues
         that prior field rather than starting a new one.
      4. Copyright boilerplate — lines like 'copyright: Words: Copyright 2009...'
         where the year is a copyright year, not a composition year.

    Returns a dict with: composer, lyricist, tune_name, year (primary),
    words_year, music_year, copyright, origin, meter_name, c_lines, z_lines.
    """
    meta = {
        'composer': None, 'lyricist': None, 'tune_name': None,
        'year': None, 'words_year': None, 'music_year': None,
        'copyright': None, 'origin': None, 'meter_name': None,
        'c_lines': [], 'z_lines': []
    }

    # Accumulators for each field — allow continuation lines to append
    field_chunks = {'lyricist': [], 'composer': [], 'copyright': [], 'setting': []}
    last_field = None   # which field an unprefixed continuation attaches to

    def assign(field, text):
        """Append text to a field accumulator, tracking last_field."""
        nonlocal last_field
        if field == 'setting':
            # Setting counts as composer context
            field_chunks['composer'].append(text)
            last_field = 'composer'
        else:
            field_chunks[field].append(text)
            last_field = field

    def parse_combined(content):
        """Parse a C: line that may contain multiple labeled fields on one line,
        like 'Words: X, 1700. Music: Y, 1800. Setting: Z, 1900.'"""
        # Split by label boundaries. Recognized labels: Words, Text, Lyrics,
        # Music, Tune, Setting, copyright.
        # Use a regex to find label positions in order.
        label_pattern = re.compile(
            r'\b(Words|Text|Lyrics|Music|Tune|Setting|[Cc]opyright)\s*:\s*',
            re.IGNORECASE,
        )
        matches = list(label_pattern.finditer(content))
        if not matches:
            return False  # no labels in this line
        # Slice content by label positions
        for i, m in enumerate(matches):
            label = m.group(1).lower()
            start = m.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(content)
            piece = content[start:end].strip().rstrip(' .')
            if label in ('words', 'text', 'lyrics'):
                assign('lyricist', piece)
            elif label in ('music', 'tune'):
                assign('composer', piece)
            elif label == 'setting':
                assign('setting', piece)
            elif label == 'copyright':
                assign('copyright', piece)
        return True

    for line in block:
        if line.startswith('C:'):
            content = line[2:].strip()
            meta['c_lines'].append(content)
            # Is this line primarily a copyright statement?
            # If it starts with 'copyright:' or contains 'Copyright YYYY' or
            # 'all rights reserved' or 'public domain', treat the whole thing
            # as copyright text and don't extract Words:/Music: from within.
            is_copyright_line = (
                content.lower().startswith('copyright:') or
                content.lower().startswith('words copyright:') or
                content.lower().startswith('music copyright:') or
                re.search(r'\bcopyright\s+\d{4}\b', content, re.IGNORECASE) or
                re.search(r'\ball rights reserved\b', content, re.IGNORECASE) or
                content.lower().startswith('music and setting:') or
                content.lower().startswith('words and setting:') or
                content.lower().startswith('melody,')
            )
            if is_copyright_line:
                # Strip leading 'copyright:' if present, keep the rest as copyright text
                stripped = re.sub(r'^(?:words\s+|music\s+)?copyright\s*:\s*',
                                  '', content, flags=re.IGNORECASE)
                field_chunks['copyright'].append(stripped)
                last_field = 'copyright'
                continue
            # Try to parse as a combined (labeled) line
            had_labels = parse_combined(content)
            if not had_labels:
                # Bare continuation line — attach to whatever field was last set
                if last_field:
                    field_chunks[last_field].append(content)
                # If nothing has been set yet, this is probably a bare composer
                # line (older hymnals sometimes use this). Use it only if no
                # labeled fields ever appeared.
        elif line.startswith('Z:'):
            meta['z_lines'].append(line[2:].strip())
        elif line.startswith('N:'):
            if not meta['origin']:
                meta['origin'] = line[2:].strip()
        elif line.startswith('R:'):
            if not meta['meter_name']:
                meta['meter_name'] = line[2:].strip()
        elif line.startswith('P:'):
            if not meta['tune_name']:
                meta['tune_name'] = line[2:].strip()
        elif line.startswith('O:'):
            if not meta['origin']:
                meta['origin'] = line[2:].strip()

    # Join accumulated chunks per field
    if field_chunks['lyricist']:
        meta['lyricist'] = ' '.join(field_chunks['lyricist'])
    if field_chunks['composer']:
        meta['composer'] = ' '.join(field_chunks['composer'])
    if field_chunks['copyright']:
        meta['copyright'] = ' '.join(field_chunks['copyright'])

    # If no labeled lines found but we have C: lines, use the first as composer
    # (some older hymns just have 'C: Author Name' with no prefix).
    if not meta['composer'] and not meta['lyricist'] and meta['c_lines']:
        # Only use C: lines that don't look like copyright boilerplate
        for c in meta['c_lines']:
            if not re.search(r'copyright|all rights reserved|public domain',
                             c, re.IGNORECASE):
                meta['composer'] = c
                break

    # Extract years separately from each field
    year_pattern = re.compile(r'\b((?:1[0-9]|20)\d{2})\b')
    if meta['lyricist']:
        years = year_pattern.findall(meta['lyricist'])
        if years:
            # Take the first year (typically the original authoring year)
            # Skip 20xx years that look like copyright artifacts
            for y in years:
                if int(y) < 1970:
                    meta['words_year'] = y
                    break
            else:
                # All years are >=1970 — might still be legit (modern lyricist)
                meta['words_year'] = years[0]
    if meta['composer']:
        years = year_pattern.findall(meta['composer'])
        if years:
            for y in years:
                if int(y) < 1970:
                    meta['music_year'] = y
                    break
            else:
                meta['music_year'] = years[0]

    # Primary 'year': prefer music_year (for classical composition-date queries),
    # fall back to words_year if music_year absent
    meta['year'] = meta['music_year'] or meta['words_year']

    return meta


# ═════════════════════════════════════════════════════════════════════════════
#   Fermata offset extraction from raw ABC (music21 drops these markers)
# ═════════════════════════════════════════════════════════════════════════════
def extract_fermata_offsets(voice_body_lines, parsed_events):
    """Walk raw ABC voice text; return list of booleans aligned 1:1 with
    parsed_events (where parsed_events includes Notes AND Chords, not rests).

    music21's ABC parser silently drops !fermata! decorations. This function
    re-derives them from the raw ABC by tokenizing note-producing events and
    attaching any preceding !fermata! marker."""
    raw = ' '.join(voice_body_lines)
    # Strip comments, chord-symbol quotes, and inline directives
    raw = re.sub(r'%.*', '', raw)
    raw = re.sub(r'"[^"]*"', '', raw)
    raw = re.sub(r'\[[VQMLK]:[^\]]+\]', '', raw)
    # Remove non-fermata decorations, keep !fermata!
    def _dec_repl(m):
        name = m.group(1)
        return m.group(0) if name == 'fermata' else ''
    raw = re.sub(r'!([a-z][a-z0-9]*)!', _dec_repl, raw)
    # Remove parens, ties, dashes, tildes
    raw = re.sub(r'[()\\~-]', ' ', raw)
    txt = raw

    fermata_list = [False] * len(parsed_events)
    pending_fermata = False
    pos = 0
    ev_idx = 0
    while pos < len(txt):
        c = txt[pos]
        if c in ' \t\n':
            pos += 1; continue
        if c == '|':
            pos += 1
            while pos < len(txt) and txt[pos] in ':]|[':
                pos += 1
            continue
        if c in '.-_*':
            pos += 1; continue
        if txt.startswith('!fermata!', pos):
            pending_fermata = True
            pos += 9; continue
        if c == '!':
            # Unknown decoration remnant — skip to next !
            end = txt.find('!', pos + 1)
            pos = end + 1 if end > 0 else pos + 1
            continue
        if c in 'zx':
            # Rest — not in parsed_events (we only aligned Notes+Chords)
            pos += 1
            while pos < len(txt) and (txt[pos].isdigit() or txt[pos] == '/'):
                pos += 1
            continue
        if c == '[':
            # Chord — one event
            end = txt.find(']', pos)
            if end < 0:
                pos += 1; continue
            if ev_idx < len(fermata_list):
                fermata_list[ev_idx] = pending_fermata
            ev_idx += 1
            pending_fermata = False
            pos = end + 1
            while pos < len(txt) and (txt[pos].isdigit() or txt[pos] == '/'):
                pos += 1
            continue
        if c in '_^=':
            pos += 1; continue
        if c in 'abcdefgABCDEFG':
            if ev_idx < len(fermata_list):
                fermata_list[ev_idx] = pending_fermata
            ev_idx += 1
            pending_fermata = False
            pos += 1
            while pos < len(txt) and txt[pos] in ",'":
                pos += 1
            while pos < len(txt) and (txt[pos].isdigit() or txt[pos] == '/'):
                pos += 1
            continue
        pos += 1
    return fermata_list



def dump_voice(voice_notes, beats_per_bar, voice_name='S1V1'):
    """Return list of per-note dicts for a single voice.

    voice_name is used to decide which pitch to surface when a chord appears
    in the voice: upper voices (S1V1, S1V2) surface the TOP pitch; lower
    voices (S2V1, S2V2) surface the BOTTOM pitch. `pitches_all` always
    contains all pitches so future renderers can split chords if needed.
    """
    is_upper_voice = voice_name in ('S1V1', 'S1V2')
    result = []
    for n in voice_notes:
        offset = float(n.offset)
        bar = int(offset // beats_per_bar) + 1
        beat = offset - (bar - 1) * beats_per_bar + 1
        if isinstance(n, m21note.Note):
            has_fermata = any(
                type(e).__name__ == 'Fermata' for e in n.expressions
            )
            result.append({
                'offset_ql': offset,
                'bar': bar,
                'beat': round(beat, 3),
                'pitch': n.pitch.nameWithOctave,
                'midi': n.pitch.midi,
                'duration_ql': float(n.duration.quarterLength),
                'is_rest': False,
                'tied_next': (n.tie is not None and n.tie.type in ('start', 'continue')),
                'fermata': has_fermata,
            })
        elif isinstance(n, chord.Chord):
            # Pick the voice-appropriate pitch as the "representative" pitch.
            # Upper voices: top pitch (the soprano/alto melodic contour).
            # Lower voices: bottom pitch (the tenor/bass line — especially
            # important for bass where the lowest note IS the pedal part).
            if is_upper_voice:
                rep = max(n.pitches, key=lambda p: p.midi)
            else:
                rep = min(n.pitches, key=lambda p: p.midi)
            has_fermata = any(
                type(e).__name__ == 'Fermata' for e in n.expressions
            )
            result.append({
                'offset_ql': offset,
                'bar': bar,
                'beat': round(beat, 3),
                'pitch': rep.nameWithOctave,
                'midi': rep.midi,
                'pitches_all': [p.nameWithOctave for p in n.pitches],
                'duration_ql': float(n.duration.quarterLength),
                'is_rest': False,
                'tied_next': (n.tie is not None and n.tie.type in ('start', 'continue')),
                'fermata': has_fermata,
                'is_chord': True,
            })
        elif isinstance(n, m21note.Rest):
            result.append({
                'offset_ql': offset,
                'bar': bar,
                'beat': round(beat, 3),
                'pitch': None,
                'midi': None,
                'duration_ql': float(n.duration.quarterLength),
                'is_rest': True,
                'tied_next': False,
                'fermata': False,
            })
    return result


# ═════════════════════════════════════════════════════════════════════════════
#   Syllable-aligned lyrics
# ═════════════════════════════════════════════════════════════════════════════
def _detect_melody_voice_label(block):
    """Figure out which ABC voice label carries the w: lyric lines.

    Strategy: walk the block, track which [V: X] marker each w: line
    follows. Whichever voice label has the most w: lines attached is the
    melody voice. Fall back to S1V1 / S1 / first-voice if no w: lines.
    """
    current_voice = None
    w_counts = {}
    for line in block:
        m = re.match(r'^\[V:\s*(\S+)\]', line)
        if m:
            current_voice = m.group(1)
            continue
        if line.startswith('w:') and current_voice:
            w_counts[current_voice] = w_counts.get(current_voice, 0) + 1
    if w_counts:
        # Return the voice with most w: lines
        return max(w_counts, key=w_counts.get)

    # Fallback: look at declarations
    seen = []
    for line in block:
        m = re.match(r'^\[V:\s*(\S+)\]', line)
        if m and m.group(1) not in seen:
            seen.append(m.group(1))
    if 'S1V1' in seen:
        return 'S1V1'
    if 'S1' in seen:
        return 'S1'
    return seen[0] if seen else 'S1V1'


def extract_lyrics_aligned(block, voice_notes, melody_label='S1V1'):
    """Extract lyrics and align each syllable to a note offset.

    Parameters
    ----------
    block : list of str
        The raw ABC block for this hymn.
    voice_notes : list
        The parsed S1V1 melody notes (already post-remap).
    melody_label : str
        Which ABC voice label carries the melody's w: lyric lines. Defaults
        to 'S1V1' (standard 4-voice hymns). For 2-staff piano reductions and
        3-staff arrangements, the melody lyrics live under 'S1'.

    Returns: dict[verse_num] -> {
        'raw_text': str,         # cleaned full-verse prose
        'syllables': [           # one entry per note-syllable pair
            {'text': str,
             'note_offset_ql': float,
             'note_pitch': str,
             'is_melisma_start': bool,
             'continues_previous': bool}
        ]
    }
    """
    # Collect raw w: lines per melody-line-group.
    # A "melody line-group" begins at each [V: melody_label] marker and
    # accumulates w: lines until a different [V:...] or a section comment
    # appears.
    melody_marker = f'[V: {melody_label}]'
    line_groups = []
    cur_mel_idx = -1
    collecting = False
    cur_wlines = []

    for line in block:
        if line.startswith(melody_marker) or line.rstrip() == f'[V:{melody_label}]':
            # Starting a new melody-voice line (inline or bare)
            if cur_wlines:
                line_groups.append((cur_mel_idx, cur_wlines))
            cur_mel_idx += 1
            cur_wlines = []
            collecting = True
        elif line.startswith('[V:'):
            # Starting a non-melody voice — stop collecting
            if cur_wlines:
                line_groups.append((cur_mel_idx, cur_wlines))
                cur_wlines = []
            collecting = False
        elif line.startswith('w:') and collecting:
            cur_wlines.append(line[2:].strip())
        elif line.startswith('%') and cur_wlines:
            # New section marker — save and reset
            line_groups.append((cur_mel_idx, cur_wlines))
            cur_wlines = []
            collecting = False
    if cur_wlines:
        line_groups.append((cur_mel_idx, cur_wlines))

    # Determine verse count (max w: lines in any group)
    max_verses = max((len(wl) for _, wl in line_groups), default=0)
    verses = {}
    for v in range(1, max_verses + 1):
        verses[v] = {'raw_chunks': [], 'syllable_lists': []}

    # For each line-group, distribute w: lines across verses.
    # If a line-group has FEWER w: lines than max_verses, this usually means
    # the text is a shared refrain sung by every verse — so we duplicate the
    # single w: line across all verses rather than leaving later verses empty.
    for mel_idx, wlines in line_groups:
        if not wlines:
            continue
        # Detect refrain pattern: exactly 1 w: line in a group where other
        # groups have max_verses lines.
        if len(wlines) == 1 and max_verses > 1:
            # Shared refrain — broadcast to every verse
            raw = wlines[0]
            # Strip leading "1.~" if present (unlikely on a refrain line but safe)
            stripped = re.sub(r'^\d+\.?[~\s]+', '', raw)
            syllables = tokenize_syllables(stripped)
            for v in range(1, max_verses + 1):
                verses.setdefault(v, {'raw_chunks': [], 'syllable_lists': []})
                verses[v]['raw_chunks'].append(stripped)
                verses[v]['syllable_lists'].append(syllables)
        else:
            # Standard case: one w: line per verse, in order
            for v_idx, raw in enumerate(wlines):
                v = v_idx + 1
                stripped = re.sub(r'^\d+\.?[~\s]+', '', raw)
                verses.setdefault(v, {'raw_chunks': [], 'syllable_lists': []})
                verses[v]['raw_chunks'].append(stripped)
                syllables = tokenize_syllables(stripped)
                verses[v]['syllable_lists'].append(syllables)

    # Align syllables to note offsets
    # Get only pitched objects (Notes or Chords — not rests) from S1V1
    melody_notes = [n for n in voice_notes
                   if isinstance(n, (m21note.Note, chord.Chord))]

    # Pre-compute which notes are tied-continuations (second half of a tie pair).
    # These notes share the previous note's syllable, so they consume a note
    # slot but NOT a syllable token.
    is_tie_continuation = [False] * len(melody_notes)
    for i, n in enumerate(melody_notes):
        t = n.tie
        if t is not None and getattr(t, 'type', None) in ('continue', 'stop'):
            is_tie_continuation[i] = True

    # Flatten syllables in order and align.
    # For each note in order:
    #   - if it's a tie continuation, emit an empty-text entry with
    #     continues_previous=True (does NOT consume a syllable token)
    #   - otherwise, consume one syllable token
    aligned_verses = {}
    for v, data in verses.items():
        all_syllables = []
        for syl_list in data['syllable_lists']:
            all_syllables.extend(syl_list)
        aligned = []
        syl_idx = 0
        for note_idx, n in enumerate(melody_notes):
            offset = float(n.offset)
            if isinstance(n, chord.Chord):
                pitch_name = max(n.pitches, key=lambda p: p.midi).nameWithOctave
            else:
                pitch_name = n.pitch.nameWithOctave

            if is_tie_continuation[note_idx]:
                # Tied continuation — same syllable, emit empty-text entry
                aligned.append({
                    'text': '',
                    'note_offset_ql': offset,
                    'note_pitch': pitch_name,
                    'is_melisma_start': False,
                    'continues_previous': True,
                })
                continue

            # Regular note — consume a syllable token
            if syl_idx >= len(all_syllables):
                # Out of syllables; emit empty-text entry
                aligned.append({
                    'text': '',
                    'note_offset_ql': offset,
                    'note_pitch': pitch_name,
                    'is_melisma_start': False,
                    'continues_previous': False,
                })
                continue

            syl = all_syllables[syl_idx]
            aligned.append({
                'text': syl['text'],
                'note_offset_ql': offset,
                'note_pitch': pitch_name,
                'is_melisma_start': syl.get('is_melisma_start', False),
                'continues_previous': syl.get('continues_previous', False),
                'joins_next': syl.get('joins_next', False),
            })
            syl_idx += 1

        aligned_verses[v] = {
            'raw_text': clean_lyric_prose(' '.join(data['raw_chunks'])),
            'syllables': aligned,
        }
    return aligned_verses


def tokenize_syllables(raw):
    """Split an ABC w: line into individual syllable tokens with alignment flags.

    ABC conventions:
      - space separates tokens (each token = one note)
      - '-' at end of token: next token is same word (syllable break)
      - '*' standalone: continuation/melisma (previous syllable held)
      - '_' : extend previous syllable (also melisma)
      - '~' : non-breaking space (part of syllable text)
      - '|' : bar line (ignore for alignment)
    """
    tokens = []
    # Replace ~ with a non-breaking marker we handle in the token
    raw = raw.replace('~', '\u00a0')
    # Split by whitespace but preserve structure
    parts = raw.split()
    i = 0
    while i < len(parts):
        p = parts[i]
        if p in ('*', '_'):
            # Melisma continuation
            tokens.append({
                'text': '',
                'is_melisma_start': False,
                'continues_previous': True,
            })
        elif p == '|':
            # Bar line — skip (alignment doesn't need this)
            pass
        else:
            # Regular syllable; may end with '-' meaning more syllables follow
            has_trailing_hyphen = p.endswith('-')
            text = p.rstrip('-')
            # Restore non-breaking space back to regular space
            text = text.replace('\u00a0', ' ')
            tokens.append({
                'text': text,
                'is_melisma_start': False,   # set below if needed
                'continues_previous': False,
                'joins_next': has_trailing_hyphen,   # true if this syllable joins the next into one word
            })
        i += 1
    return tokens


def clean_lyric_prose(raw):
    """Convert raw ABC lyric to readable prose (for raw_text field)."""
    s = raw
    s = s.replace('~', ' ')
    s = re.sub(r'\s*\*\s*', ' ', s)      # remove melisma markers
    s = re.sub(r'\s*_\s*', ' ', s)       # remove continuation markers
    # Join hyphen-broken syllables (handles apostrophes between)
    s = re.sub(r"(\w)-\s*([\'\"]?)(\w)", r'\1\2\3', s)
    s = re.sub(r'(\w)-(\w)', r'\1\2', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# ═════════════════════════════════════════════════════════════════════════════
#   Main export
# ═════════════════════════════════════════════════════════════════════════════
def export_hymn(title_query, hymnal_path='/mnt/project/OpenHymnal.abc',
                vocab_path='/mnt/project/HarpChordSystem.json'):
    """Build the comprehensive JSON for one hymn."""
    block = extract_tune(hymnal_path, title_query)
    headers, body, extras = split_voices(block, return_extras=True)

    # Raw ABC source preserved
    abc_source = '\n'.join(block)

    # Find title
    title = title_query
    for h in headers:
        if h.startswith('T:'):
            title = h[2:].strip()
            break

    # Metadata
    meta = extract_metadata(block)

    # Key and meter
    key_line = next((h for h in headers if h.startswith('K:')), 'K: C')
    meter_line = next((h for h in headers if h.startswith('M:')), 'M: 4/4')
    unit_line = next((h for h in headers if h.startswith('L:')), 'L: 1/8')

    key_match = re.match(r'K:\s*([A-G][b#]?m?(?:aj|in)?)', key_line)
    key_str = key_match.group(1) if key_match else 'C'
    K_header = key.Key(key_str.rstrip('maj').rstrip('in'))
    meter_match = re.search(r'M:\s*(\d+)/(\d+)', meter_line)
    meter_num = int(meter_match.group(1)) if meter_match else 4
    meter_den = int(meter_match.group(2)) if meter_match else 4

    # Parse all 4 voices
    voices_raw = {}   # original, may contain Chord objects
    for v in ['S1V1', 'S1V2', 'S2V1', 'S2V2']:
        abc = build_voice_abc(headers, body, v)
        s = converter.parseData(abc, format='abc')
        voices_raw[v] = list(s.flatten().notesAndRests)

    # Normalize: some voices have Chord objects (2-note divisi).
    # Convert them to Notes so the parser pipeline works. Pick the pitch
    # matching the voice's direction: upper voices → top pitch (melodic
    # contour), lower voices → bottom pitch (bass line).
    # The original chord info is preserved in voice_dumps via dump_voice.
    voices_parsed = {}
    for v_name, notes_list in voices_raw.items():
        is_upper = v_name in ('S1V1', 'S1V2')
        fixed = []
        for n in notes_list:
            if isinstance(n, chord.Chord):
                if is_upper:
                    rep = max(n.pitches, key=lambda p: p.midi)
                else:
                    rep = min(n.pitches, key=lambda p: p.midi)
                replacement = m21note.Note(rep)
                replacement.offset = n.offset
                replacement.duration = n.duration
                replacement.tie = n.tie
                replacement.expressions = n.expressions
                fixed.append(replacement)
            else:
                fixed.append(n)
        voices_parsed[v_name] = fixed

    # Sanity: if S1V1 is empty, we can't do beat-level analysis. Skip that
    # portion and emit a partial record.
    if not voices_parsed.get('S1V1'):
        return {
            'title': title,
            'abc_source': abc_source,
            'metadata': meta,
            'music': {
                'key_header': str(K_header), 'key_detected': str(K_header),
                'key_root': K_header.tonic.name, 'mode': K_header.mode,
                'tonic_override_applied': False,
                'meter': f'{meter_num}/{meter_den}',
                'meter_num': meter_num, 'meter_den': meter_den,
                'unit_note_length': unit_line[2:].strip(),
                'total_bars': 0, 'total_ql': 0,
            },
            'voices': {'S1V1': [], 'S1V2': [], 'S2V1': [], 'S2V2': []},
            'beats': [], 'regions': {'smoothed': [], 'per_bar': [], 'per_halfbar': []},
            'phrases': [],
            'lyrics': {'verse_count': 0, 'verses': {}},
            'harmony': {'roman_numerals_per_bar': [], 'harp_chord_assignments': []},
            'export_note': 'S1V1 voice was empty; partial record only',
        }

    # Detect true tonic
    K = detect_true_tonic(voices_parsed, K_header)
    key_mode = 'minor' if K.mode == 'minor' else 'major'
    override = (K.tonic.name != K_header.tonic.name or K.mode != K_header.mode)

    # Detect specific church mode when tonic was overridden (Dorian, Mixolydian, etc.)
    from hymn_parser import detect_mode
    header_scale_pcs = {p.pitchClass for p in K_header.pitches}
    modal_name = detect_mode(K.tonic.pitchClass, header_scale_pcs)

    # Beat-level SATB
    samples, total_ql = sample_satb(voices_parsed)
    beats = analyze_beats(samples, K, key_mode, meter_num)
    regions_raw = aggregate_regions(beats)
    regions_smoothed = smooth_regions(regions_raw)
    bar_regions = downsample_per_bar(beats, meter_num, slots_per_bar=1)
    halfbar_regions = downsample_per_bar(beats, meter_num, slots_per_bar=2)

    # Phrases
    total_bars_for_fermata = max((b['bar'] for b in beats), default=0)
    fermata_bars = detect_fermata_bars(body, total_bars=total_bars_for_fermata)
    cadence_bars = detect_cadence_bars(bar_regions, key_mode, halfbar_regions)
    phrases = split_into_phrases(bar_regions, fermata_bars, cadence_bars)
    # Enrich phrases with ql offsets
    for p in phrases:
        first_bar = min(p['bars'])
        last_bar = max(p['bars'])
        p['start_ql'] = (first_bar - 1) * meter_num
        p['end_ql'] = last_bar * meter_num

    # Voice dumps (preserve original chord info)
    voice_dumps = {}
    for v in ['S1V1', 'S1V2', 'S2V1', 'S2V2']:
        voice_dumps[v] = dump_voice(voices_raw[v], meter_num, voice_name=v)

    # Parse and dump extra voices (organ pedal, S3V3 etc.) if present
    extra_voice_dumps = {}
    for ev_name, ev_lines in extras.items():
        try:
            abc = build_voice_abc(headers, {ev_name: ev_lines}, ev_name)
            s = converter.parseData(abc, format='abc')
            ev_notes = list(s.flatten().notesAndRests)
            # Same Chord-handling as main voices: classify based on label
            # (S3V3 is a pedal → lower voice)
            is_upper = ev_name.startswith('S1') or ev_name == 'S2V1'
            fixed = []
            for n in ev_notes:
                if isinstance(n, chord.Chord):
                    rep = (max if is_upper else min)(n.pitches, key=lambda p: p.midi)
                    replacement = m21note.Note(rep)
                    replacement.offset = n.offset
                    replacement.duration = n.duration
                    replacement.tie = n.tie
                    replacement.expressions = n.expressions
                    fixed.append(replacement)
                else:
                    fixed.append(n)
            extra_voice_dumps[ev_name] = dump_voice(ev_notes, meter_num, voice_name=ev_name)
        except Exception:
            extra_voice_dumps[ev_name] = []

    # Overlay fermata flags re-derived from raw ABC (music21 drops them).
    # For each voice, filter to Note+Chord events (not rests) and align.
    for v in ['S1V1', 'S1V2', 'S2V1', 'S2V2']:
        if v not in body:
            continue
        non_rest_events = [n for n in voices_raw[v]
                           if isinstance(n, (m21note.Note, chord.Chord))]
        fermata_flags = extract_fermata_offsets(body[v], non_rest_events)
        # Walk voice_dumps[v] and set fermata=True where applicable
        ev_idx = 0
        for entry in voice_dumps[v]:
            if entry['is_rest']:
                continue
            if ev_idx < len(fermata_flags) and fermata_flags[ev_idx]:
                entry['fermata'] = True
            ev_idx += 1

    # Syllable-aligned lyrics (use raw melody with chord info)
    melody_label = _detect_melody_voice_label(block)
    lyrics = extract_lyrics_aligned(block, voices_raw['S1V1'], melody_label=melody_label)

    # Harmonic analysis + Harp Chord System mapping
    vocab = load_vocab(vocab_path)
    key_root = K.tonic.name.replace('-', 'b') if False else K.tonic.name  # keep music21 style
    # For harp_mapper, key_root should be music21-style name (e.g. 'B-' for B flat)
    key_root_m21 = K.tonic.name

    bar_to_melody = {}
    for r in bar_regions:
        target = next((b for b in beats
                       if b['bar'] == r['start_bar'] and b['beat'] == r['start_beat']),
                      None)
        bar_to_melody[r['start_bar']] = target['M'] if target else None
    bar_to_rn = {r['start_bar']: r['rn'] for r in bar_regions}
    bar_list = sorted(bar_to_rn.keys())

    # Build bar → phrase-context lookup (for minor-V substitution dispatch)
    bar_to_phrase = {}
    for phrase in phrases:
        for b in phrase['bars']:
            bar_to_phrase[b] = phrase
    last_bar_in_hymn = max(bar_list) if bar_list else 0

    rn_per_bar = []
    harp_assignments = []
    for i, bn in enumerate(bar_list):
        rn = bar_to_rn[bn]
        mel = bar_to_melody[bn]
        prev_mel = bar_to_melody[bar_list[i-1]] if i > 0 else None
        next_mel = bar_to_melody[bar_list[i+1]] if i < len(bar_list)-1 else None
        contour = infer_contour(prev_mel, mel, next_mel)
        next_rn = bar_to_rn[bar_list[i+1]] if i < len(bar_list)-1 else None
        prev_rn = bar_to_rn[bar_list[i-1]] if i > 0 else None

        # Find the region this bar belongs to (for duration_beats)
        matching_region = next((r for r in bar_regions if r['start_bar'] == bn), None)
        duration_beats = matching_region['length'] if matching_region else 0
        rn_per_bar.append({'bar': bn, 'rn': rn, 'duration_beats': duration_beats})

        # Phrase context: is this the last bar of its phrase? what's the ending_marker?
        cur_phrase = bar_to_phrase.get(bn)
        is_phrase_end = cur_phrase and bn == max(cur_phrase['bars'])
        is_final_cadence = (bn == last_bar_in_hymn) or is_phrase_end
        ending_marker = cur_phrase['ending_marker'] if cur_phrase else None

        # Use the high-level picker with minor-V substitution logic
        picks = pick_with_substitution(
            vocab, rn=rn, key_root=key_root_m21,
            next_rn=next_rn, prev_rn=prev_rn,
            melody=mel, mode=key_mode, contour=contour,
            is_final_cadence=is_final_cadence,
            ending_marker=ending_marker,
            v_duration_beats=duration_beats,
            top_n=3,
        )

        # Determine method label (cycle or stacked), looking at the picks
        method = 'stacked'
        if next_rn and picks:
            # Re-determine cycle for labeling purposes
            # (substitution may have altered the effective RN, but we label by original)
            try:
                from_t = translate_minor_to_major(rn) if key_mode == 'minor' else rn
                to_t = translate_minor_to_major(next_rn) if key_mode == 'minor' else next_rn
                d_from, _, _ = parse_rn(from_t)
                d_to, _, _ = parse_rn(to_t)
                cyc, dir_ = cycle_of_transition(d_from, d_to)
                if cyc:
                    method = f"{cyc}-{dir_}"
            except Exception:
                pass

        if picks:
            p = picks[0]
            harp_assignments.append({
                'bar': bn,
                'rn': rn,
                'melody': mel,
                'contour': contour,
                'lh_roman': p['lh_roman'],
                'lh_figure': p['lh_figure'],
                'rh_roman': p['rh_roman'],
                'rh_figure': p['rh_figure'],
                'mood': p.get('mood', p.get('cw_label', '')),
                'source': p['source'],
                'method': method,
                'harmonic_substitution': p.get('harmonic_substitution'),
                'requested_rn': p.get('requested_rn', rn),
                'alternates': [
                    {
                        'lh_roman': alt['lh_roman'], 'lh_figure': alt['lh_figure'],
                        'rh_roman': alt['rh_roman'], 'rh_figure': alt['rh_figure'],
                        'mood': alt.get('mood', alt.get('cw_label', '')),
                        'source': alt['source'],
                    }
                    for alt in picks[1:3]
                ],
            })

    # Assemble
    return {
        'title': title,
        'abc_source': abc_source,
        'metadata': meta,
        'music': {
            'key_header': str(K_header),
            'key_detected': str(K),
            'key_root': K.tonic.name,
            'mode': K.mode,
            'modal_name': modal_name,
            'tonic_override_applied': override,
            'meter': f'{meter_num}/{meter_den}',
            'meter_num': meter_num,
            'meter_den': meter_den,
            'unit_note_length': unit_line[2:].strip(),
            'total_bars': max((b['bar'] for b in beats), default=0),
            'total_ql': total_ql,
        },
        'voices': voice_dumps,
        'extra_voices': extra_voice_dumps,
        'beats': [
            {'offset_ql': b['offset'], 'bar': b['bar'], 'beat': b['beat'],
             'S': b['M'], 'A': b['A'], 'T': b['T'], 'B': b['B'],
             'rn_raw': b['rn_raw'], 'rn_clean': b['rn_clean'], 'is_nct': b['nct']}
            for b in beats
        ],
        'regions': {
            'smoothed': [
                {'start_bar': r['start_bar'], 'start_beat': r['start_beat'],
                 'end_bar': r['end_bar'], 'end_beat': r['end_beat'],
                 'rn': r['rn'], 'length_beats': r['length']}
                for r in regions_smoothed
            ],
            'per_bar': [
                {'start_bar': r['start_bar'], 'start_beat': r['start_beat'],
                 'end_bar': r['end_bar'], 'end_beat': r['end_beat'],
                 'rn': r['rn'], 'length_beats': r['length']}
                for r in bar_regions
            ],
            'per_halfbar': [
                {'start_bar': r['start_bar'], 'start_beat': r['start_beat'],
                 'end_bar': r['end_bar'], 'end_beat': r['end_beat'],
                 'rn': r['rn'], 'length_beats': r['length']}
                for r in halfbar_regions
            ],
        },
        'phrases': phrases,
        'lyrics': {
            'verse_count': len(lyrics),
            'verses': {str(v): data for v, data in lyrics.items()},
        },
        'harmony': {
            'roman_numerals_per_bar': rn_per_bar,
            'harp_chord_assignments': harp_assignments,
        },
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('title', nargs='?', help='Hymn title substring')
    ap.add_argument('--all', action='store_true',
                    help='Export every hymn in the hymnal')
    ap.add_argument('-o', '--output',
                    help='Output .json file (single hymn) or directory (--all)')
    ap.add_argument('--hymnal', default='/mnt/project/OpenHymnal.abc')
    ap.add_argument('--vocab', default='/mnt/project/HarpChordSystem.json')
    args = ap.parse_args()

    if args.all:
        outdir = args.output or '/mnt/user-data/outputs/hymnal_export'
        os.makedirs(outdir, exist_ok=True)
        # Enumerate all titles
        with open(args.hymnal) as f:
            all_lines = f.read().split('\n')
        titles = []
        for line in all_lines:
            if line.startswith('T:'):
                t = line[2:].strip()
                if t and not t.startswith('(also'):
                    titles.append(t)
        print(f"Exporting {len(titles)} hymns to {outdir}")
        ok = 0; fail = 0
        for t in titles:
            safe = re.sub(r'[^A-Za-z0-9]', '_', t)[:60]
            out_path = os.path.join(outdir, f'{safe}.json')
            try:
                data = export_hymn(t, args.hymnal, args.vocab)
                with open(out_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                ok += 1
                if ok % 20 == 0:
                    print(f"  {ok}/{len(titles)} done")
            except Exception as e:
                fail += 1
                print(f"  ✗ {t}: {e}")
        print(f"Done. {ok} succeeded, {fail} failed.")
    else:
        if not args.title:
            print("Provide a title or use --all")
            sys.exit(1)
        data = export_hymn(args.title, args.hymnal, args.vocab)
        out_path = args.output or f'/home/claude/{args.title.replace(" ","_")}.json'
        with open(out_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Wrote {out_path}")
