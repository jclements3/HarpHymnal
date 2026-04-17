#!/usr/bin/env python3
"""
hymn_parser.py — parse an OpenHymnal ABC tune into cleaned, bar-level chord regions.

Pipeline:
    1. Extract tune from OpenHymnal.abc by title substring
    2. Split into 4 voices (S1V1, S1V2, S2V1, S2V2)
    3. Parse each voice with music21
    4. Sample all 4 voices at every beat offset → SATB
    5. Detect non-chord tones in melody (passing tones, neighbor tones)
    6. Compute roman numeral from chord tones only
    7. Clean up music21's ugly figures (V752 → V7, ii542 → V, etc.)
    8. Aggregate adjacent identical chords into regions

Usage:
    python hymn_parser.py "Joy to the World"
"""
import re
import sys
import argparse
from fractions import Fraction
from music21 import converter, stream, note, chord, key, roman, pitch, interval

# ═════════════════════════════════════════════════════════════════════════════
#   Tune extraction from multi-hymn ABC file
# ═════════════════════════════════════════════════════════════════════════════
def extract_tune(abc_path, title_query):
    """Return the ABC block for the hymn whose T: line contains title_query."""
    with open(abc_path) as f:
        lines = f.read().split('\n')
    # Find the T: line
    t_line = None
    for i, line in enumerate(lines):
        if line.startswith('T:') and title_query.lower() in line.lower():
            t_line = i
            break
    if t_line is None:
        raise ValueError(f"Hymn not found: {title_query!r}")
    # Walk back to X:
    start = t_line
    for j in range(t_line, -1, -1):
        if lines[j].startswith('X:'):
            start = j
            break
    # Forward to next X:
    end = len(lines)
    for j in range(start+1, len(lines)):
        if lines[j].startswith('X:'):
            end = j
            break
    return lines[start:end]

# ═════════════════════════════════════════════════════════════════════════════
#   Per-voice ABC reconstruction
# ═════════════════════════════════════════════════════════════════════════════
def split_voices(block, return_extras=False):
    """Split ABC block into S1V1/S1V2/S2V1/S2V2 voice lists.

    Handles three voice-labeling conventions found in OpenHymnal.abc:
    (1) Standard 4-voice SATB (S1V1, S1V2, S2V1, S2V2) — direct mapping
    (2) Two-staff piano reduction (S1 + S2) with chords like [Ac] — split
        chords into top/bottom pitches for S1V1/S1V2/S2V1/S2V2
    (3) Three-staff arrangement (S1 + S2V1/S2V2 + S3V1/S3V2 or S3V3) —
        remap solo/alto/tenor/bass into SATB; preserve extra S3 voices
        in the returned `extras` dict if return_extras=True.

    Returns (headers, body) by default, or (headers, body, extras) if
    return_extras=True.
    """
    headers = [l for l in block if re.match(r'^[XTMLKQ]:', l)]

    raw_voices = {}
    current_voice = None   # for multi-line voice blocks where [V:X] starts a section
    for line in block:
        # Voice change marker with possible inline content
        m = re.match(r'^\[V:\s*(\S+)\]\s*(.*)$', line.rstrip())
        if m:
            current_voice = m.group(1)
            inline_content = m.group(2).strip()
            if inline_content:
                # Content on the same line as [V:X]
                raw_voices.setdefault(current_voice, []).append(inline_content)
            continue
        # If we're inside a voice block and this is a content line, attach it
        if current_voice is not None:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('%'):
                # Comment or ABC directive like %%begintext
                # %%begintext / %%endtext signals embedded prose — stop attaching
                if '%%endtext' in stripped or '%%begintext' in stripped:
                    current_voice = None
                continue
            if stripped.startswith('V:'):
                # Voice declaration, not content
                current_voice = None
                continue
            if stripped.startswith('w:'):
                # Lyric line — not part of the note voice
                continue
            if stripped.startswith('"'):
                # Quoted prose (inside %%begintext block for instance)
                continue
            # To be considered ABC music content, the line must contain at least
            # one bar line (|) or a note-producing character. Prose lines that
            # happen to be missed by the other filters won't have these.
            if '|' not in stripped and not re.search(r"[A-Ga-gz][\d,',/]", stripped):
                continue
            raw_voices.setdefault(current_voice, []).append(line.strip())

    body = {'S1V1': [], 'S1V2': [], 'S2V1': [], 'S2V2': []}
    extras = {}

    present = set(raw_voices.keys())
    standard_set = {'S1V1', 'S1V2', 'S2V1', 'S2V2'}
    # Only trust the "standard 4-voice" path when a TOP-staff voice (S1V1 or
    # S1V2) is present. If only S2V1/S2V2 are present along with S1 or S3*,
    # it's a 3-staff arrangement and needs remapping.
    has_top_standard = 'S1V1' in present or 'S1V2' in present

    if has_top_standard:
        # Standard 4-voice — take what's there, leave missing ones empty
        for v in body:
            if v in raw_voices:
                body[v] = raw_voices[v]
        # Pattern 5: 3-voice hymn with S1V1/S1V2 top divisi plus single S2 bass.
        # Happens in shape-note/Sacred-Harp settings where the bass is one line
        # (no tenor/bass divisi). Put S2 into S2V2 so the bass voice isn't lost.
        if 'S2' in present and 'S2V1' not in present and 'S2V2' not in present:
            body['S2V2'] = raw_voices['S2']
    elif {'S1', 'S2'} <= present and not has_top_standard and \
         not any(v.startswith('S3') for v in present):
        # Pattern 2: 2-staff piano reduction (S1 + S2 only). Split chords.
        body['S1V1'] = _split_chord_voice(raw_voices['S1'], which='top')
        body['S1V2'] = _split_chord_voice(raw_voices['S1'], which='bottom')
        body['S2V1'] = _split_chord_voice(raw_voices['S2'], which='top')
        body['S2V2'] = _split_chord_voice(raw_voices['S2'], which='bottom')
    elif 'S1' in present and ('S2V1' in present or 'S2V2' in present or
                               any(v.startswith('S3') for v in present)):
        # Pattern 3: 3-staff arrangement
        body['S1V1'] = raw_voices.get('S1', [])
        body['S1V2'] = raw_voices.get('S2V1', [])
        body['S2V1'] = raw_voices.get('S2V2', [])
        body['S2V2'] = raw_voices.get('S3V1', [])
        for extra in ('S3V2', 'S3V3'):
            if extra in raw_voices:
                extras[extra] = raw_voices[extra]
    else:
        # Fallback
        for v in body:
            if v in raw_voices:
                body[v] = raw_voices[v]

    if return_extras:
        return headers, body, extras
    return headers, body


def _split_chord_voice(abc_lines, which='top'):
    """Take lines like '[Ac] [DF]' and return either the top-pitch-only version
    ('Ac]' → 'c', etc.) or the bottom-pitch-only version ('Ac]' → 'A').

    ABC chord syntax:
      [pitch1 pitch2 pitch3 ...]duration
    Pitches are listed low-to-high inside a chord.
    So 'bottom' = first pitch in chord, 'top' = last pitch.
    Duration suffix applies to the whole chord.
    """
    result = []
    for line in abc_lines:
        # Replace each [...] chord with a single pitch
        def replace_chord(m):
            inner = m.group(1)
            duration = m.group(2)
            # Parse pitches inside the chord. Each pitch: [_^=]? [A-Ga-g] [,']*  [duration]?
            # For the purposes of picking top/bottom, we look at letter+octave marks.
            # Split the inside into pitch tokens.
            pitches = re.findall(r"[_^=]?[A-Ga-g][,']*\d*/?\d*", inner)
            if not pitches:
                return inner + duration
            # Pick top or bottom based on pitch height
            # Computing MIDI is overkill — ABC pitches within a chord are usually in
            # order (low to high), and for hymn notation the lowest pitch has more
            # commas or a lowercase letter, the highest has apostrophes or uppercase.
            # Use a simple height heuristic:
            def height(p):
                m = re.match(r"[_^=]?([A-Ga-g])([,']*)", p)
                if not m:
                    return 0
                letter, octave_marks = m.groups()
                # A-G = octave 4, a-g = octave 5
                base = 4 if letter.isupper() else 5
                for c in octave_marks:
                    if c == ',': base -= 1
                    elif c == "'": base += 1
                # Note order: C=0 D=2 E=4 F=5 G=7 A=9 B=11
                note_pc = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11,
                          'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}.get(letter, 0)
                return base * 12 + note_pc
            pitches_sorted = sorted(pitches, key=height)
            pick = pitches_sorted[-1] if which == 'top' else pitches_sorted[0]
            # Strip any internal duration from the picked pitch — we'll add the chord's duration
            pitch_clean = re.sub(r'\d.*$', '', pick)
            return pitch_clean + duration

        # Regex: match [contents]optional_duration, but skip ABC inline directives
        # (which look like [Q:...] [V:...] [M:...] [L:...] [K:...] [T:...] [P:...])
        # A directive has a letter followed by ':' as its first characters.
        new_line = re.sub(
            r'\[(?![A-Z]:)([^\]]+)\](\d*/?\d*)', replace_chord, line
        )
        result.append(new_line)
    return result


def build_voice_abc(headers, body, voice):
    lines = []
    for pfx in ('X:','T:','M:','L:','K:'):
        lines += [h for h in headers if h.startswith(pfx)]
    lines += body[voice]
    return '\n'.join(lines)

# ═════════════════════════════════════════════════════════════════════════════
#   Fermata detection: scan the melody voice's raw ABC text, find which bar
#   each !fermata! falls in, return set of bar numbers ending phrases.
# ═════════════════════════════════════════════════════════════════════════════
def detect_fermata_bars(body, voice='S1V1', total_bars=None):
    """Return set of bar numbers where a !fermata! occurs in the given voice.
    Bar numbering matches the beat analysis (1-indexed from first bar).

    If total_bars is provided, fermata bars are clamped to <= total_bars
    (prevents off-by-one errors from empty trailing bar-split tokens and
    from anacrusis handling differences between our splitter and music21)."""
    if voice not in body or not body[voice]:
        return set()
    joined = ' '.join(body[voice])
    joined = re.sub(r'\|[:\|\]]*', '|', joined)
    bars = joined.split('|')
    fermata_bars = set()
    for i, bar_content in enumerate(bars, start=1):
        # Skip empty trailing entries
        if not bar_content.strip():
            continue
        if '!fermata!' in bar_content:
            fermata_bars.add(i)
    # Clamp to valid range if total_bars supplied
    if total_bars is not None and fermata_bars:
        clamped = set()
        for b in fermata_bars:
            if b <= total_bars:
                clamped.add(b)
            else:
                # Off-by-one or end-of-piece fermata → snap to final bar
                clamped.add(total_bars)
        fermata_bars = clamped
    return fermata_bars

def detect_cadence_bars(bar_regions, key_mode='major', halfbar_regions=None):
    """Return set of bar numbers where a cadence (phrase ending) likely occurs.

    Full (authentic/plagal) cadences are detected first:
      - bar ending with I (or i in minor) preceded by V/V7/IV/ii
      - in minor mode: also VII/bVII/III/v → i (modal cadences)

    If the full-cadence pass finds fewer than ~1 cadence per 4 bars, a
    second pass adds HALF cadences: bars that end on V (the dominant),
    approached by a predominant (ii, IV, vi, i). These are spaced at
    least `min_half_cadence_spacing` bars apart to avoid over-detection.

    Uses halfbar_regions if provided for finer granularity on full cadences.
    Final bar is always marked as a phrase boundary.
    """
    if not bar_regions:
        return set()
    regions_to_use = halfbar_regions if halfbar_regions else bar_regions

    bar_rns = {}
    for r in regions_to_use:
        for b in range(r['start_bar'], r['end_bar'] + 1):
            bar_rns.setdefault(b, []).append((r['start_beat'] if b == r['start_bar'] else 1, r['rn']))

    bars_sorted = sorted(bar_rns.keys())
    if not bars_sorted:
        return set()

    tonic_patterns = ['i', 'I', 'i6', 'I6', 'I64', 'i64']
    leading_to_tonic_major = {'V', 'V7', 'V6', 'V65', 'V43', 'V42',
                              'IV', 'iv', 'ii', 'ii7', 'ii6', 'vii°', 'viiø7'}
    leading_to_tonic_minor = leading_to_tonic_major | {'VII', 'bVII', 'III', 'v'}
    tonic_ok = tonic_patterns
    leading_ok = leading_to_tonic_minor if key_mode == 'minor' else leading_to_tonic_major

    # For half cadences: any → V. Predominants that typically precede V.
    dominant_patterns = ['V', 'V7', 'V6', 'V65', 'V43', 'V42']
    predominant_major = {'I', 'I6', 'ii', 'ii6', 'ii7', 'IV', 'iv', 'vi', 'vi7'}
    predominant_minor = {'i', 'i6', 'ii°', 'iv', 'VI', 'III'}
    predominant_ok = predominant_minor if key_mode == 'minor' else predominant_major

    def rn_base(rn):
        m = re.match(r'^(b?[ivIV]+[°ø]?[\d]*)', rn)
        return m.group(1) if m else rn

    def rn_letters_only(rn):
        """Strip trailing digits from an RN to get the base numeral.
        Used for category matching: 'V4', 'V5', 'V7', 'V' all map to 'V'.
        Keeps one exception: V6/V65 (first inversion) is still dominant-
        function and maps to 'V'. i64/I64 (cadential 6/4) maps to the tonic."""
        m = re.match(r'^(b?[ivIV]+[°ø]?)', rn)
        return m.group(1) if m else rn

    def is_tonic(rn):
        base = rn_letters_only(rn)
        return base in ('i', 'I')

    def is_leading(rn, mode):
        base = rn_letters_only(rn)
        major_set = {'V', 'IV', 'iv', 'ii', 'vii', 'vii°', 'viiø'}
        minor_set = major_set | {'VII', 'bVII', 'III', 'v'}
        return base in (minor_set if mode == 'minor' else major_set)

    cadence_bars = set()
    # --- PASS 1: full cadences (authentic + plagal + modal) ---
    for i, b in enumerate(bars_sorted):
        rns_in_bar = [rn for _, rn in bar_rns[b]]
        # Case 1: cadence WITHIN the bar (e.g., V|I in halfbars)
        for j in range(1, len(rns_in_bar)):
            prev = rns_in_bar[j-1]
            cur = rns_in_bar[j]
            if is_tonic(cur) and is_leading(prev, key_mode):
                cadence_bars.add(b)
                break
        # Case 2: this bar opens with tonic, previous bar ended with leading-tone harmony
        if b in cadence_bars:
            continue
        if rns_in_bar and is_tonic(rns_in_bar[0]):
            if i > 0:
                prev_bar_rns = [rn for _, rn in bar_rns[bars_sorted[i-1]]]
                if prev_bar_rns:
                    prev_last = prev_bar_rns[-1]
                    if is_leading(prev_last, key_mode):
                        cadence_bars.add(b)

    # --- PASS 2: half cadences (always run; spacing constraint prevents over-detection) ---
    # Per-BAR (not halfbar) view for half cadences: use bar_regions
    bar_level_rn = {}
    for r in bar_regions:
        for b in range(r['start_bar'], r['end_bar'] + 1):
            # Take the LAST RN in each bar (half cadence is about how the bar ENDS)
            bar_level_rn[b] = r['rn']

    def is_dominant_letters(rn):
        return rn_letters_only(rn) == 'V'
    def is_predominant(rn, mode):
        base = rn_letters_only(rn)
        major_set = {'I', 'ii', 'IV', 'vi'}
        minor_set = {'i', 'ii°', 'iv', 'VI', 'III'}
        return base in (minor_set if mode == 'minor' else major_set)

    half_cad_candidates = []
    sorted_bars = sorted(bar_level_rn.keys())
    for i, b in enumerate(sorted_bars):
        if i == 0:
            continue  # need a previous bar
        cur = bar_level_rn[b]
        prev = bar_level_rn[sorted_bars[i-1]]
        if is_dominant_letters(cur) and is_predominant(prev, key_mode):
            half_cad_candidates.append(b)

    # Add half-cadence candidates with min spacing of 3 bars from existing cadences
    min_spacing = 3
    for cand in half_cad_candidates:
        too_close = False
        for existing in cadence_bars:
            if abs(cand - existing) < min_spacing:
                too_close = True
                break
        if too_close:
            continue
        cadence_bars.add(cand)

    # Final bar is always a phrase boundary
    cadence_bars.add(bars_sorted[-1])
    return cadence_bars

def split_into_phrases(bar_regions, fermata_bars, cadence_bars, min_phrase_length=2):
    """Return a list of phrase dicts: {label, bars, ending_marker}.
    Uses the UNION of fermatas and cadences as phrase boundaries. Fermatas
    take priority as the `ending_marker` label when both apply at a bar.
    Phrases are labeled A, B, C, ... in order."""
    if not bar_regions:
        return []
    all_bars = sorted({b for r in bar_regions
                       for b in range(r['start_bar'], r['end_bar'] + 1)})
    if not all_bars:
        return []

    # Combine fermatas and cadences as boundaries.
    # If both are empty, fall back to every-4-bars.
    boundaries = set(fermata_bars or set()) | set(cadence_bars or set())
    if not boundaries:
        boundaries = set(all_bars[3::4]) | {all_bars[-1]}
    # Ensure last bar is always a boundary
    boundaries = boundaries | {all_bars[-1]}

    phrases = []
    cur_bars = []
    label_idx = 0
    for b in all_bars:
        cur_bars.append(b)
        if b in boundaries and len(cur_bars) >= min_phrase_length:
            label = chr(ord('A') + label_idx)
            marker = 'fermata' if b in fermata_bars else ('cadence' if b in cadence_bars else 'auto')
            phrases.append({
                'label': label,
                'bars': list(cur_bars),
                'ending_marker': marker,
            })
            cur_bars = []
            label_idx += 1
    # Tail phrase (no boundary at end) — merge into previous if tiny
    if cur_bars:
        if phrases and len(cur_bars) < min_phrase_length:
            # Merge into previous phrase
            phrases[-1]['bars'] += cur_bars
        else:
            label = chr(ord('A') + label_idx)
            phrases.append({
                'label': label,
                'bars': list(cur_bars),
                'ending_marker': 'end',
            })
    return phrases

# ═════════════════════════════════════════════════════════════════════════════
#   Beat-by-beat SATB sampling
# ═════════════════════════════════════════════════════════════════════════════
def sample_satb(voices_parsed, beat_unit_ql=1.0):
    """Return a list of (offset, M, A, T, B) tuples, one per beat.
    Each voice entry is either a music21 Note object or None (rest)."""
    # Get total length from melody
    mel = voices_parsed['S1V1']
    total_ql = float(mel[-1].offset) + float(mel[-1].duration.quarterLength)

    def pitch_at(voice, t):
        for n in voices_parsed[voice]:
            start = float(n.offset)
            end = start + float(n.duration.quarterLength)
            if start <= t < end:
                if isinstance(n, note.Rest): return None
                return n
        return None

    samples = []
    n_beats = int(total_ql / beat_unit_ql)
    for i in range(n_beats):
        t = i * beat_unit_ql
        samples.append((
            t,
            pitch_at('S1V1', t),
            pitch_at('S1V2', t),
            pitch_at('S2V1', t),
            pitch_at('S2V2', t),
        ))
    return samples, total_ql

# ═════════════════════════════════════════════════════════════════════════════
#   Non-chord-tone detection (specifically passing tones in the melody)
# ═════════════════════════════════════════════════════════════════════════════
def is_passing_tone(prev_pitch, curr_pitch, next_pitch):
    """Stepwise motion prev → curr → next, same direction on both steps."""
    if prev_pitch is None or curr_pitch is None or next_pitch is None:
        return False
    # Semitone distances
    i1 = interval.Interval(prev_pitch, curr_pitch).semitones
    i2 = interval.Interval(curr_pitch, next_pitch).semitones
    # Passing tone = both intervals 1 or 2 semitones in same direction
    return abs(i1) in (1,2) and abs(i2) in (1,2) and (i1 > 0) == (i2 > 0)

def is_neighbor_tone(prev_pitch, curr_pitch, next_pitch):
    """prev → curr → prev, curr a step away."""
    if prev_pitch is None or curr_pitch is None or next_pitch is None:
        return False
    if prev_pitch.nameWithOctave != next_pitch.nameWithOctave:
        return False
    i = abs(interval.Interval(prev_pitch, curr_pitch).semitones)
    return i in (1,2)

# ═════════════════════════════════════════════════════════════════════════════
#   Clean music21's roman numeral notation
# ═════════════════════════════════════════════════════════════════════════════
CLEAN_RN = {
    # music21 figured-bass noise → jazz-readable
    'V752':   'V7',
    'V542':   'V7',    # 4-2 sus variants all = V7 functionally
    'V432':   'V7',
    'ii542':  'V',     # typically a cadential sus over V bass
    'ii752':  'V7',
    'I753':   'I7',
    'I64':    'I64',   # keep cadential 6/4 — it's a real thing
    'IV64':   'IV64',  # keep pedal 6/4
    'iii6':   'V7',    # common misread: A C# E over A bass = V, not iii6
}

# Diatonic quality for each scale degree in major / minor keys.
# Maps bare numeral (case determines quality) to the correct case for the key.
MAJOR_DIATONIC = {'I':'I', 'II':'ii', 'III':'iii', 'IV':'IV', 'V':'V', 'VI':'vi', 'VII':'vii°'}
MINOR_DIATONIC = {'I':'i', 'II':'ii°', 'III':'III', 'IV':'iv', 'V':'V', 'VI':'VI', 'VII':'VII'}

def enforce_diatonic_quality(rn_figure, key_mode='major'):
    """Normalize case and quality to the diatonic chord for the key.
    E.g. in D major, 'i7' from a passing C# becomes 'I7' (D major 7 / dominant)."""
    m = re.match(r'^([#b]?)([ivIV]+)([oø°Δ]?)(\d*)(.*)$', rn_figure)
    if not m:
        return rn_figure
    acc, numerals, quality, ext, rest = m.groups()
    # Uppercase the numerals to look up
    upper = numerals.upper()
    diatonic = MAJOR_DIATONIC if key_mode == 'major' else MINOR_DIATONIC
    if upper not in diatonic:
        return rn_figure
    correct = diatonic[upper]
    # Re-extract correct case and inherent quality from the diatonic mapping
    cm = re.match(r'^([ivIV]+)([oø°Δ]?)$', correct)
    if cm:
        correct_num, correct_qual = cm.groups()
        # Keep user-provided quality (°, ø7, Δ) if it matches or is absent; otherwise use diatonic
        final_qual = quality if quality else correct_qual
        return f"{acc}{correct_num}{final_qual}{ext}"
    return rn_figure

def clean_rn(rn_figure, key_mode='major', bass_pitch_name=None):
    """Normalize music21's RN string. Returns cleaned figure."""
    if rn_figure in CLEAN_RN:
        result = CLEAN_RN[rn_figure]
    else:
        # Strip trailing extensions longer than 2 chars (usually noise)
        m = re.match(r'^([#b]?[ivIV]+[oø°Δ]?)(\d*)(.*)$', rn_figure)
        if m:
            base, ext, rest = m.groups()
            if len(ext) > 2:
                ext = ext[:1]
            result = base + ext
        else:
            result = rn_figure
    # Enforce diatonic quality (fixes i7 → I7 in major keys etc.)
    return enforce_diatonic_quality(result, key_mode)

# ═════════════════════════════════════════════════════════════════════════════
#   Modal detection: when tonic differs from header tonic, identify the
#   specific church mode (Dorian, Phrygian, Mixolydian, Aeolian, etc.)
# ═════════════════════════════════════════════════════════════════════════════
def detect_mode(new_tonic_pc, header_scale_pcs):
    """Return the specific mode name given a tonic pitch-class and the set of
    pitch-classes the header key signature implies. All modes use the same
    7-note scale as the header; they differ only in which note is 'home'.

    Modes by scale degree (semitones from tonic):
      ionian     [0, 2, 4, 5, 7, 9, 11]  (major)
      dorian     [0, 2, 3, 5, 7, 9, 10]
      phrygian   [0, 1, 3, 5, 7, 8, 10]
      lydian     [0, 2, 4, 6, 7, 9, 11]
      mixolydian [0, 2, 4, 5, 7, 9, 10]
      aeolian    [0, 2, 3, 5, 7, 8, 10]  (natural minor)
      locrian    [0, 1, 3, 5, 6, 8, 10]
    """
    # Compute the interval pattern (semitones above new tonic)
    intervals = sorted((p - new_tonic_pc) % 12 for p in header_scale_pcs)
    patterns = {
        (0, 2, 4, 5, 7, 9, 11):  'ionian',
        (0, 2, 3, 5, 7, 9, 10):  'dorian',
        (0, 1, 3, 5, 7, 8, 10):  'phrygian',
        (0, 2, 4, 6, 7, 9, 11):  'lydian',
        (0, 2, 4, 5, 7, 9, 10):  'mixolydian',
        (0, 2, 3, 5, 7, 8, 10):  'aeolian',
        (0, 1, 3, 5, 6, 8, 10):  'locrian',
    }
    return patterns.get(tuple(intervals), 'unknown')



def detect_true_tonic(voices_parsed, K_header):
    """Return a music21 Key object for the true tonic of the hymn.

    Algorithm:
      1. Collect tonic candidates from multiple evidence sources, weighted:
           - bass first note (weight 2)
           - bass last note (weight 2)
           - melody first note (weight 1)
           - melody last note (weight 2)
           - most-common bass pitch-class (weight 1)
           - header tonic (weight 1)
      2. The pitch-class with the highest vote wins. Ties favor the header.
      3. Mode is determined by the scale-third rule.
    """
    # Pick the voice with the lowest average pitch as the true bass
    bass_voice = None
    bass_lowest = 999
    for v_name, notes_list in voices_parsed.items():
        nn = [n for n in notes_list if isinstance(n, note.Note)]
        if not nn:
            continue
        avg_pc = sum(n.pitch.midi for n in nn) / len(nn)
        if avg_pc < bass_lowest:
            bass_lowest = avg_pc
            bass_voice = v_name
    if not bass_voice:
        return K_header

    bass_notes = [n for n in voices_parsed[bass_voice] if isinstance(n, note.Note)]
    if not bass_notes:
        return K_header

    # Collect melody notes (S1V1 preferred)
    mel_voice = 'S1V1' if 'S1V1' in voices_parsed else None
    mel_notes = []
    if mel_voice:
        mel_notes = [n for n in voices_parsed[mel_voice] if isinstance(n, note.Note)]

    # Weighted vote. The ending of a hymn is the strongest tonic signal:
    # where bass-last and melody-last agree, that's nearly always the true tonic.
    # So final pitches weigh more than opening pitches.
    votes = {}
    def vote(pc, weight):
        if pc is not None:
            votes[pc] = votes.get(pc, 0) + weight

    vote(bass_notes[0].pitch.pitchClass, 1)         # bass first (opening; can be on 5th/3rd)
    vote(bass_notes[-1].pitch.pitchClass, 3)        # bass last (strong — final cadence lands here)
    if mel_notes:
        vote(mel_notes[0].pitch.pitchClass, 1)     # melody first
        vote(mel_notes[-1].pitch.pitchClass, 3)    # melody last (strong — melody ends on tonic)
    # Most common bass pc
    pc_count = {}
    for n in bass_notes:
        pc = n.pitch.pitchClass
        pc_count[pc] = pc_count.get(pc, 0) + 1
    most_common = max(pc_count, key=pc_count.get)
    vote(most_common, 1)
    # Header gets a baseline vote so it wins pure ties
    header_pc = K_header.tonic.pitchClass
    vote(header_pc, 1)

    # Pick the winner
    winner_pc = max(votes, key=votes.get)
    # If the header wins (or ties and breaks to it), keep the header unchanged
    if winner_pc == header_pc:
        return K_header

    # Find a pitch object matching winner_pc (prefer bass, then melody)
    new_tonic_pitch = None
    for n in bass_notes + mel_notes:
        if n.pitch.pitchClass == winner_pc:
            new_tonic_pitch = n.pitch
            break
    if new_tonic_pitch is None:
        return K_header

    # Determine major/minor by scale-third test
    header_scale_pcs = {p.pitchClass for p in K_header.pitches}
    major_third_pc = (winner_pc + 4) % 12
    minor_third_pc = (winner_pc + 3) % 12
    has_M3 = major_third_pc in header_scale_pcs
    has_m3 = minor_third_pc in header_scale_pcs
    new_name = new_tonic_pitch.name
    if has_M3 and not has_m3:
        return key.Key(new_name, 'major')
    elif has_m3 and not has_M3:
        return key.Key(new_name, 'minor')
    elif has_m3 and has_M3:
        return key.Key(new_name, 'minor')
    else:
        return K_header


def analyze_beats(samples, K, key_mode='major', beats_per_bar=2):
    """Return a list of dicts: {bar, beat, offset, M, A, T, B, rn_raw, rn_clean, nct}"""
    results = []
    for i, (t, m, a, tn, b) in enumerate(samples):
        bar = i // beats_per_bar + 1
        beat = i % beats_per_bar + 1
        pitches = [p for p in (b, tn, a, m) if p is not None]
        # Detect melodic passing tone: use neighbors in the melody voice
        mel_pitches = [s[1].pitch if s[1] else None for s in samples]
        nct = False
        if 0 < i < len(samples)-1 and mel_pitches[i]:
            if is_passing_tone(mel_pitches[i-1], mel_pitches[i], mel_pitches[i+1]):
                nct = True
            elif is_neighbor_tone(mel_pitches[i-1], mel_pitches[i], mel_pitches[i+1]):
                nct = True
        # If melody is NCT, exclude it from the chord
        chord_pitches = [p for p in (b, tn, a) if p is not None]
        if not nct and m is not None:
            chord_pitches.append(m)
        rn_raw = '—'
        rn_clean = '—'
        if chord_pitches:
            c = chord.Chord([p.pitch for p in chord_pitches])
            try:
                rn = roman.romanNumeralFromChord(c, K)
                rn_raw = rn.figure
                rn_clean = clean_rn(rn_raw, key_mode)
            except Exception:
                pass
        results.append({
            'bar': bar, 'beat': beat, 'offset': t,
            'M': m.nameWithOctave if m else None,
            'A': a.nameWithOctave if a else None,
            'T': tn.nameWithOctave if tn else None,
            'B': b.nameWithOctave if b else None,
            'rn_raw': rn_raw, 'rn_clean': rn_clean, 'nct': nct,
        })
    return results

# ═════════════════════════════════════════════════════════════════════════════
#   Bar-level aggregation: collapse adjacent identical RNs into regions
# ═════════════════════════════════════════════════════════════════════════════
def aggregate_regions(beats):
    """Collapse runs of identical rn_clean into (start_bar, start_beat, end_bar, end_beat, rn)."""
    if not beats: return []
    regions = []
    cur = {'start_bar': beats[0]['bar'], 'start_beat': beats[0]['beat'],
           'end_bar': beats[0]['bar'], 'end_beat': beats[0]['beat'],
           'rn': beats[0]['rn_clean'], 'length': 1}
    for b in beats[1:]:
        if b['rn_clean'] == cur['rn']:
            cur['end_bar'] = b['bar']
            cur['end_beat'] = b['beat']
            cur['length'] += 1
        else:
            regions.append(cur)
            cur = {'start_bar': b['bar'], 'start_beat': b['beat'],
                   'end_bar': b['bar'], 'end_beat': b['beat'],
                   'rn': b['rn_clean'], 'length': 1}
    regions.append(cur)
    return regions

# ═════════════════════════════════════════════════════════════════════════════
#   Smooth out single-beat noise regions flanked by the same chord
# ═════════════════════════════════════════════════════════════════════════════
SIMPLE_FUNCS = {'I', 'IV', 'V', 'V7', 'vi', 'ii', 'iii', 'I6', 'IV6',
                'V6', 'vi6', 'ii6', 'I64', 'IV64', 'V65', 'V43', 'V42',
                'i', 'iv', 'v', 'III', 'VI', 'VII'}
NOISE_PATTERNS = (r'#', r'^b(?!vii°$)', r'\d{2,}(?!$)', r'42$', r'54$',
                  r'65$', r'5$', r'\(no', r'incomplete')

def is_noise(rn):
    """Heuristic: is this RN likely music21 figured-bass noise?"""
    if rn in SIMPLE_FUNCS:
        return False
    for pat in NOISE_PATTERNS:
        if re.search(pat, rn):
            return True
    return False

def smooth_regions(regions, min_kept_length=2):
    """Collapse single-beat noise regions that are flanked by the same neighbor.
    E.g. [I (2b), #IVø7 (1b), I (2b)] → [I (5b)].
    Also collapse [X (1b), Y (nb)] → [Y (n+1b)] when X is noise."""
    if len(regions) < 3:
        return regions
    # First pass: noise flanked by same chord → absorb into neighbors
    result = [regions[0]]
    i = 1
    while i < len(regions) - 1:
        prev, cur, nxt = result[-1], regions[i], regions[i+1]
        if (cur['length'] == 1 and is_noise(cur['rn'])
                and prev['rn'] == nxt['rn']):
            # Absorb cur into prev, extend to nxt's end
            prev['end_bar'] = nxt['end_bar']
            prev['end_beat'] = nxt['end_beat']
            prev['length'] += cur['length'] + nxt['length']
            i += 2  # skip cur and nxt
            continue
        result.append(cur)
        i += 1
    if i == len(regions) - 1:
        result.append(regions[-1])
    # Second pass: drop single-beat noise regions at boundaries
    # (append to previous non-noise region)
    result2 = []
    for r in result:
        if (r['length'] == 1 and is_noise(r['rn']) and result2
                and not is_noise(result2[-1]['rn'])):
            # absorb into previous
            result2[-1]['end_bar'] = r['end_bar']
            result2[-1]['end_beat'] = r['end_beat']
            result2[-1]['length'] += 1
        else:
            result2.append(r)
    return result2

# ═════════════════════════════════════════════════════════════════════════════
#   Bar-level downsampling: one chord per bar (or per half-bar)
# ═════════════════════════════════════════════════════════════════════════════
def downsample_per_bar(beats, beats_per_bar, slots_per_bar=1):
    """Emit exactly `slots_per_bar` regions per bar.
    slots_per_bar=1: one chord per bar (the one with most beats; downbeat wins ties)
    slots_per_bar=2: two chords per bar (first half / second half)
    Returns list of region dicts, one per slot.
    """
    if not beats:
        return []
    # Group beats by bar
    bars = {}
    for b in beats:
        bars.setdefault(b['bar'], []).append(b)

    regions = []
    slot_size = beats_per_bar // slots_per_bar  # beats per slot
    if slot_size < 1:
        slot_size = 1

    for bar_num in sorted(bars.keys()):
        bar_beats = bars[bar_num]
        for slot_idx in range(slots_per_bar):
            slot_start_beat = slot_idx * slot_size + 1
            slot_end_beat = min((slot_idx + 1) * slot_size, beats_per_bar)
            slot_beats = [b for b in bar_beats
                         if slot_start_beat <= b['beat'] <= slot_end_beat]
            if not slot_beats:
                continue
            # Vote: which RN occupies the most beats in this slot?
            vote = {}
            for b in slot_beats:
                # Downbeat gets 2x weight; first-beat-of-slot gets +1
                weight = 2 if b['beat'] == slot_start_beat else 1
                # Penalty for noise labels
                if is_noise(b['rn_clean']):
                    weight = 0.3
                vote[b['rn_clean']] = vote.get(b['rn_clean'], 0) + weight
            if not vote:
                continue
            winner = max(vote, key=vote.get)
            regions.append({
                'start_bar': bar_num,
                'start_beat': slot_start_beat,
                'end_bar': bar_num,
                'end_beat': slot_end_beat,
                'rn': winner,
                'length': len(slot_beats),
            })
    # Optional: collapse adjacent identical regions across bar lines
    collapsed = [regions[0]] if regions else []
    for r in regions[1:]:
        if r['rn'] == collapsed[-1]['rn']:
            collapsed[-1]['end_bar'] = r['end_bar']
            collapsed[-1]['end_beat'] = r['end_beat']
            collapsed[-1]['length'] += r['length']
        else:
            collapsed.append(r)
    return collapsed

# ═════════════════════════════════════════════════════════════════════════════
#   Main
# ═════════════════════════════════════════════════════════════════════════════
def analyze_hymn(hymnal_path, title_query, verbose=True):
    block = extract_tune(hymnal_path, title_query)
    headers, body = split_voices(block)

    # Detect key
    key_line = next((h for h in headers if h.startswith('K:')), 'K: C')
    key_str = re.match(r'K:\s*([A-G][b#]?m?(?:aj|in)?)', key_line).group(1)
    K = key.Key(key_str.rstrip('maj').rstrip('in'))  # simplify 'Dmaj' → 'D', 'Amin' → 'Am'
    meter_line = next((h for h in headers if h.startswith('M:')), 'M: 4/4')
    title = next((h for h in headers if h.startswith('T:')), 'T: Unknown').split(':',1)[1].strip()

    if verbose:
        print(f"═══ {title} ═══")
        print(f"  Key: {K}   Meter: {meter_line.split(':')[1].strip()}")

    # Parse voices
    voices_parsed = {}
    for v in ['S1V1','S1V2','S2V1','S2V2']:
        if not body[v]:
            continue
        abc = build_voice_abc(headers, body, v)
        s = converter.parseData(abc, format='abc')
        voices_parsed[v] = list(s.flatten().notesAndRests)
    if len(voices_parsed) < 4:
        print(f"  ⚠ only {len(voices_parsed)} voices present: {list(voices_parsed.keys())}")
        return None

    samples, total_ql = sample_satb(voices_parsed)
    # Parse time sig to determine beats per bar
    m = re.search(r'M:\s*(\d+)/(\d+)', meter_line)
    beats_per_bar = int(m.group(1)) if m else 4
    # TONIC DETECTION: final bass note reveals the true tonic
    K_true = detect_true_tonic(voices_parsed, K)
    if K_true.tonic.name != K.tonic.name or K_true.mode != K.mode:
        if verbose:
            print(f"  ⚠ Tonic override: header said {K}, but final bass says {K_true}")
        K = K_true
    key_mode = 'minor' if K.mode == 'minor' else 'major'
    beats = analyze_beats(samples, K, key_mode, beats_per_bar)
    regions_raw = aggregate_regions(beats)
    regions = smooth_regions(regions_raw)
    bar_regions = downsample_per_bar(beats, beats_per_bar, slots_per_bar=1)
    halfbar_regions = downsample_per_bar(beats, beats_per_bar, slots_per_bar=2)

    if verbose:
        print(f"\n  Beat-level (with NCT flagged):")
        print(f"  {'bar':>3} {'bt':>2}  {'M':>5} {'A':>5} {'T':>5} {'B':>5}   {'raw':<8} {'clean':<8} nct")
        print("  " + "─" * 65)
        for b in beats:
            mark = '*' if b['nct'] else ' '
            cell = lambda v: (str(v) if v else '—')
            print(f"  {b['bar']:>3} {b['beat']:>2}   {cell(b['M']):>5} {cell(b['A']):>5} {cell(b['T']):>5} {cell(b['B']):>5}   {b['rn_raw']:<8} {b['rn_clean']:<8} {mark}")

        print(f"\n  Aggregated regions: ({len(regions_raw)} raw → {len(regions)} smoothed)")
        for r in regions:
            span = f"bar {r['start_bar']}.{r['start_beat']} → bar {r['end_bar']}.{r['end_beat']}"
            print(f"    {span:<30}  ({r['length']} beats)   {r['rn']}")

        print(f"\n  Per-bar downsample ({len(bar_regions)} chords):")
        for r in bar_regions:
            span = f"bar {r['start_bar']}.{r['start_beat']} → bar {r['end_bar']}.{r['end_beat']}"
            print(f"    {span:<30}  ({r['length']} beats)   {r['rn']}")

        print(f"\n  Half-bar downsample ({len(halfbar_regions)} chords):")
        for r in halfbar_regions:
            span = f"bar {r['start_bar']}.{r['start_beat']} → bar {r['end_bar']}.{r['end_beat']}"
            print(f"    {span:<30}  ({r['length']} beats)   {r['rn']}")

    # ───── Phrase detection: fermatas (preferred) or cadences (fallback) ─────
    fermata_bars = detect_fermata_bars(body)
    cadence_bars = detect_cadence_bars(bar_regions, key_mode, halfbar_regions)
    phrases = split_into_phrases(bar_regions, fermata_bars, cadence_bars)

    if verbose:
        print(f"\n  Phrases ({len(phrases)}): "
              f"{len(fermata_bars)} fermatas, {len(cadence_bars)} cadences detected")
        for p in phrases:
            print(f"    {p['label']}: bars {p['bars']}  [{p['ending_marker']}]")

    return {'title': title, 'key': str(K), 'beats': beats,
            'regions': regions, 'bar_regions': bar_regions,
            'halfbar_regions': halfbar_regions,
            'fermata_bars': sorted(fermata_bars),
            'cadence_bars': sorted(cadence_bars),
            'phrases': phrases}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('query', help='Title substring to find')
    ap.add_argument('--hymnal', default='/mnt/project/OpenHymnal.abc')
    args = ap.parse_args()
    analyze_hymn(args.hymnal, args.query)
