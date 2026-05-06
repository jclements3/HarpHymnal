#!/usr/bin/env python3.10
"""
Generate SSAATTBB+P MEI files for pedal harp arrangements.
Reads lead_sheets.json, parses ABC melody+chords, generates 3-staff MEI.

Staff 1: Melody (as written)
Staff 2: RH treble (2-3 fingers, lighter)
Staff 3: LH bass (3-4 fingers, heavier)

Single layer per staff (simplified from prompt's two-layer moving/sustained model,
since the user said ONE layer per staff in the rules).
"""

import json, re, os, sys
from fractions import Fraction

OUT_DIR = "/home/james.clements/projects/trefoil/handout/tch_ssaattbbp_out"

# ─────────────────────────────────────────────────────────────────────────────
# KEY DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

KEY_SIGS = {
    'C':  ('0', []),
    'G':  ('1s', ['f']),
    'D':  ('2s', ['f', 'c']),
    'A':  ('3s', ['f', 'c', 'g']),
    'E':  ('4s', ['f', 'c', 'g', 'd']),
    'F':  ('1f', ['b']),
    'Bb': ('2f', ['b', 'e']),
    'Eb': ('3f', ['b', 'e', 'a']),
}

# Diatonic scale degrees (pitch classes) for each key
# 0=C,1=C#,2=D,3=Eb,4=E,5=F,6=F#,7=G,8=Ab,9=A,10=Bb,11=B
KEY_SCALES = {
    'C':  [0, 2, 4, 5, 7, 9, 11],
    'G':  [7, 9, 11, 0, 2, 4, 6],
    'D':  [2, 4, 6, 7, 9, 11, 1],
    'A':  [9, 11, 1, 2, 4, 6, 8],
    'E':  [4, 6, 8, 9, 11, 1, 3],
    'F':  [5, 7, 9, 10, 0, 2, 4],
    'Bb': [10, 0, 2, 3, 5, 7, 9],
    'Eb': [3, 5, 7, 8, 10, 0, 2],
}

# Sharps/flats in each key (pitch class -> accid.ges value)
KEY_ACCIDENTALS = {
    'C':  {},
    'G':  {6: 's'},        # F#
    'D':  {6: 's', 1: 's'},  # F#, C#
    'A':  {6: 's', 1: 's', 8: 's'},  # F#, C#, G#
    'E':  {6: 's', 1: 's', 8: 's', 3: 's'},  # F#,C#,G#,D#
    'F':  {10: 'f'},       # Bb
    'Bb': {10: 'f', 3: 'f'},  # Bb, Eb
    'Eb': {10: 'f', 3: 'f', 8: 'f'},  # Bb, Eb, Ab
}

# Pitch name to pitch class
PITCH_PC = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}

# Circled digit chord degrees
CIRCLED = ['①', '②', '③', '④', '⑤', '⑥', '⑦']

# ─────────────────────────────────────────────────────────────────────────────
# ABC PARSING
# ─────────────────────────────────────────────────────────────────────────────

def parse_abc_bars(abc_body, L_denom, meter_num, meter_den):
    """
    Parse ABC music body into bars, each bar being a list of (chord_name, notes_list).
    notes_list: list of (pitch_name, octave, duration_fraction, accid)
    chord_name: string like 'G', 'Am', 'D7', etc.
    Returns list of bars, each bar is {'chord': str, 'notes': list, 'beats': Fraction}
    """
    bars = []
    # Split on | barlines but not ||, |], [|
    bar_texts = re.split(r'\|(?!\|)(?!\])', abc_body)

    current_chord = None
    L = Fraction(1, L_denom)  # default note length

    for bar_text in bar_texts:
        bar_text = bar_text.strip().rstrip(']').strip()
        if not bar_text:
            continue

        # Parse notes and chords in this bar
        events = []
        pos = 0
        bar_chord = None

        # Scan through bar text token by token
        i = 0
        t = bar_text
        while i < len(t):
            # Skip whitespace
            if t[i] == ' ':
                i += 1
                continue
            # Chord annotation "^Xxx"
            if t[i] == '"':
                j = t.find('"', i+1)
                if j == -1:
                    break
                ann = t[i+1:j]
                if ann.startswith('^'):
                    chord_str = ann[1:]
                    # Clean chord name (remove special chars for display)
                    current_chord = chord_str
                    if bar_chord is None:
                        bar_chord = chord_str
                i = j + 1
                continue
            # Accidental
            accid = None
            if t[i] in ('^', '_', '='):
                if t[i] == '^':
                    if i+1 < len(t) and t[i+1] == '^':
                        accid = 'ss'
                        i += 2
                    else:
                        accid = 's'
                        i += 1
                elif t[i] == '_':
                    if i+1 < len(t) and t[i+1] == '_':
                        accid = 'ff'
                        i += 2
                    else:
                        accid = 'f'
                        i += 1
                elif t[i] == '=':
                    accid = 'n'
                    i += 1
                if i >= len(t):
                    break
            # Note
            if t[i].lower() in 'cdefgabz':
                pname = t[i].lower()
                # Determine octave: match build_tchaikovsky_mei.py convention
                # Uppercase (no marks): oct=4, e.g. C=C4, D=D4, G=G4
                # Uppercase with ,: oct=4-n, e.g. C, = C3
                # lowercase (no marks): oct=5, e.g. c=C5, d=D5
                # lowercase with ': oct=5+n
                if t[i].isupper():
                    base_oct = 4  # C4 range
                else:
                    base_oct = 5  # C5 range (c = C5)
                i += 1
                # Octave modifiers
                while i < len(t) and t[i] in ("'", ','):
                    if t[i] == "'":
                        base_oct += 1
                    elif t[i] == ',':
                        base_oct -= 1
                    i += 1
                # Duration
                dur_num = 1
                dur_den = 1
                if i < len(t) and t[i].isdigit():
                    dur_num = 0
                    while i < len(t) and t[i].isdigit():
                        dur_num = dur_num * 10 + int(t[i])
                        i += 1
                if i < len(t) and t[i] == '/':
                    i += 1
                    if i < len(t) and t[i].isdigit():
                        dur_den = 0
                        while i < len(t) and t[i].isdigit():
                            dur_den = dur_den * 10 + int(t[i])
                            i += 1
                    else:
                        dur_den = 2
                # Dots
                dots = 0
                while i < len(t) and t[i] == '.':
                    dots += 1
                    i += 1
                # Broken rhythm
                broken = 0
                if i < len(t) and t[i] == '>':
                    broken = 1
                    i += 1
                elif i < len(t) and t[i] == '<':
                    broken = -1
                    i += 1

                dur = L * Fraction(dur_num, dur_den)
                if dots == 1:
                    dur = dur * Fraction(3, 2)
                elif dots == 2:
                    dur = dur * Fraction(7, 4)

                if pname != 'z':  # z = rest
                    events.append({
                        'pname': pname,
                        'oct': base_oct,
                        'dur': dur,
                        'accid': accid,
                        'chord': current_chord,
                    })
                else:
                    events.append({
                        'pname': 'z',
                        'oct': 0,
                        'dur': dur,
                        'accid': None,
                        'chord': current_chord,
                    })
                continue
            # Tie, slur, etc — skip
            if t[i] in '-()~{}\\':
                i += 1
                continue
            # Repeat signs, bar checks
            if t[i] in ':|[!+':
                i += 1
                continue
            i += 1

        if events or bar_chord:
            total_dur = sum(e['dur'] for e in events)
            # Get first chord of bar
            first_chord = bar_chord or current_chord
            bars.append({
                'chord': first_chord,
                'notes': events,
                'beats': total_dur,
                'chord_events': [],  # will fill with (beat_offset, chord_name)
            })
            # Build chord event list
            running = Fraction(0)
            last_chord_beat = Fraction(0)
            last_chord_name = first_chord
            chord_events = []
            for ev in events:
                if ev.get('chord') and ev['chord'] != last_chord_name:
                    chord_events.append((running, ev['chord']))
                    last_chord_name = ev['chord']
                    last_chord_beat = running
                elif running == Fraction(0) and ev.get('chord'):
                    if not chord_events:
                        chord_events.append((Fraction(0), ev['chord']))
                    last_chord_name = ev['chord']
                running += ev['dur']
            bars[-1]['chord_events'] = chord_events

    return bars

# ─────────────────────────────────────────────────────────────────────────────
# CHORD ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

CHORD_ROOT_RE = re.compile(r'^([A-G][b#]?)(.*)')

def chord_root_pc(chord_str):
    """Return pitch class (0-11) of chord root."""
    m = CHORD_ROOT_RE.match(chord_str)
    if not m:
        return None
    root_str = m.group(1)
    pc = PITCH_PC[root_str[0].lower()]
    if len(root_str) > 1:
        if root_str[1] == '#':
            pc = (pc + 1) % 12
        elif root_str[1] == 'b':
            pc = (pc - 1) % 12
    return pc

def chord_quality(chord_str):
    """Return 'maj', 'min', 'dim', 'aug', 'dom7', 'maj7', 'min7', 'hdim7', 'sus', 'other'."""
    m = CHORD_ROOT_RE.match(chord_str)
    if not m:
        return 'maj'
    suffix = m.group(2)
    if suffix in ('', '+'):
        return 'maj' if suffix == '' else 'aug'
    if suffix.startswith('m') and not suffix.startswith('maj'):
        if '7' in suffix:
            return 'min7'
        return 'min'
    if suffix in ('°', 'dim', '°7'):
        return 'dim'
    if 'ø7' in suffix or 'ø' in suffix:
        return 'hdim7'
    if 'Δ7' in suffix or 'Δ' in suffix:
        return 'maj7'
    if suffix in ('7',):
        return 'dom7'
    if '7' in suffix and suffix[0].isdigit():
        return 'dom7'
    if 's2' in suffix or 'sus2' in suffix:
        return 'sus2'
    if 's4' in suffix or 'sus4' in suffix:
        return 'sus4'
    return 'maj'

def chord_tones_pc(chord_str):
    """Return list of pitch classes (up to 4) for chord."""
    root = chord_root_pc(chord_str)
    if root is None:
        return [0, 4, 7]
    quality = chord_quality(chord_str)
    if quality == 'maj':
        return [root, (root+4)%12, (root+7)%12]
    elif quality == 'min':
        return [root, (root+3)%12, (root+7)%12]
    elif quality == 'dim':
        return [root, (root+3)%12, (root+6)%12]
    elif quality == 'aug':
        return [root, (root+4)%12, (root+8)%12]
    elif quality == 'dom7':
        return [root, (root+4)%12, (root+7)%12, (root+10)%12]
    elif quality == 'maj7':
        return [root, (root+4)%12, (root+7)%12, (root+11)%12]
    elif quality == 'min7':
        return [root, (root+3)%12, (root+7)%12, (root+10)%12]
    elif quality == 'hdim7':
        return [root, (root+3)%12, (root+6)%12, (root+10)%12]
    elif quality == 'sus2':
        return [root, (root+2)%12, (root+7)%12]
    elif quality == 'sus4':
        return [root, (root+5)%12, (root+7)%12]
    return [root, (root+4)%12, (root+7)%12]

def snap_to_diatonic(pc, key):
    """Snap pitch class to nearest diatonic pc in key."""
    scale = KEY_SCALES[key]
    if pc in scale:
        return pc
    # Try up, then down
    for delta in [1, -1, 2, -2]:
        candidate = (pc + delta) % 12
        if candidate in scale:
            return candidate
    return scale[0]

def pc_to_note(pc, key, preferred_oct):
    """Convert pitch class to (pname, oct, accid_ges) in preferred octave."""
    # Note names for PCs
    PC_NAMES = {0:'c', 1:'c', 2:'d', 3:'e', 4:'e', 5:'f', 6:'f', 7:'g', 8:'a', 9:'a', 10:'b', 11:'b'}
    # Actually use sharps/flats based on key
    # Key accidentals
    key_acc = KEY_ACCIDENTALS.get(key, {})

    # Find the pitch name
    # Natural names: C=0,D=2,E=4,F=5,G=7,A=9,B=11
    naturals = {0:'c', 2:'d', 4:'e', 5:'f', 7:'g', 9:'a', 11:'b'}

    if pc in naturals:
        pname = naturals[pc]
        accid_ges = key_acc.get(pc)
        return pname, preferred_oct, accid_ges

    # Sharp or flat
    # Try sharp first if key has sharps, flat if key has flats
    if key in ('G','D','A','E'):
        # sharp keys
        sharp_pc = (pc - 1) % 12
        if sharp_pc in naturals:
            pname = naturals[sharp_pc]
            accid_ges = 's'
            return pname, preferred_oct, accid_ges
        flat_pc = (pc + 1) % 12
        if flat_pc in naturals:
            pname = naturals[flat_pc]
            accid_ges = 'f'
            return pname, preferred_oct, accid_ges
    else:
        # flat keys or C
        flat_pc = (pc + 1) % 12
        if flat_pc in naturals:
            pname = naturals[flat_pc]
            accid_ges = 'f'
            return pname, preferred_oct, accid_ges
        sharp_pc = (pc - 1) % 12
        if sharp_pc in naturals:
            pname = naturals[sharp_pc]
            accid_ges = 's'
            return pname, preferred_oct, accid_ges

    return 'c', preferred_oct, None

def midi_pitch(pname, oct, accid=None):
    """Return MIDI pitch number."""
    base = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}[pname]
    midi = (oct + 1) * 12 + base
    if accid == 's':
        midi += 1
    elif accid == 'f':
        midi -= 1
    elif accid == 'ss':
        midi += 2
    elif accid == 'ff':
        midi -= 2
    return midi

def note_from_midi(midi, key, key_acc):
    """Convert MIDI pitch to (pname, oct, accid_ges)."""
    oct = midi // 12 - 1
    pc = midi % 12

    naturals = {0:'c', 2:'d', 4:'e', 5:'f', 7:'g', 9:'a', 11:'b'}

    if pc in naturals:
        pname = naturals[pc]
        accid_ges = key_acc.get(pc)
        return pname, oct, accid_ges

    if key in ('G','D','A','E'):
        sharp_pc = (pc - 1) % 12
        if sharp_pc in naturals:
            return naturals[sharp_pc], oct, 's'
        flat_pc = (pc + 1) % 12
        if flat_pc in naturals:
            return naturals[flat_pc], oct, 'f'
    else:
        flat_pc = (pc + 1) % 12
        if flat_pc in naturals:
            return naturals[flat_pc], oct, 'f'
        sharp_pc = (pc - 1) % 12
        if sharp_pc in naturals:
            return naturals[sharp_pc], oct, 's'
    return 'c', oct, None

def diatonic_scale_midi(key, low_midi, high_midi):
    """Return sorted list of MIDI pitches in key between low and high."""
    scale_pcs = set(KEY_SCALES[key])
    notes = []
    for m in range(low_midi, high_midi+1):
        if m % 12 in scale_pcs:
            notes.append(m)
    return notes

def build_lh_voicing(chord_str, key, prev_lh=None, measure_num=0):
    """
    Build LH voicing: 3-4 notes in bass clef (C2=36 to B3=59).
    Open spacing: root, 5th, octave, 3rd.
    No 2nds or minor 3rds between bottom notes.
    """
    tones_pc = chord_tones_pc(chord_str)
    root_pc = chord_root_pc(chord_str)
    key_acc = KEY_ACCIDENTALS.get(key, {})

    # Snap chord tones to diatonic
    diatonic_tones = [snap_to_diatonic(pc, key) for pc in tones_pc]
    diatonic_tones = list(dict.fromkeys(diatonic_tones))  # dedupe

    # Find root in bass range (C2=36 to B3=59)
    # Try to put root at C2-B2 (36-47) first, then C3-B3 (48-59)
    root_midi_candidates = []
    for oct in [2, 3]:
        m = (oct + 1) * 12 + root_pc
        if 36 <= m <= 59:
            root_midi_candidates.append(m)

    if not root_midi_candidates:
        root_midi_candidates = [36 + root_pc % 12]  # fallback

    # Use lower octave for root for open spacing
    root_midi = root_midi_candidates[0]

    # Build open voicing: root, 5th above, octave above root
    # Find all diatonic pitches from root to root+12
    notes = [root_midi]

    # Add fifth (7 semitones up from root, snapped to diatonic)
    fifth_pc = (root_pc + 7) % 12
    fifth_pc_diatonic = snap_to_diatonic(fifth_pc, key)

    # Find fifth in range above root
    for oct in [2, 3]:
        m = (oct + 1) * 12 + fifth_pc_diatonic
        if m > root_midi and m <= root_midi + 12 and m <= 59:
            if m - notes[-1] >= 5:  # at least a 4th above
                notes.append(m)
                break

    # Add octave above root
    octave_midi = root_midi + 12
    if octave_midi <= 59 and len(notes) < 4:
        notes.append(octave_midi)

    # Add third/seventh near top of LH range (near C4)
    if len(notes) < 4:
        third_pc = diatonic_tones[1] if len(diatonic_tones) > 1 else (root_pc + 4) % 12
        third_pc = snap_to_diatonic(third_pc, key)
        # Find third just below C4 (48-59 range)
        for oct in [3, 2]:
            m = (oct + 1) * 12 + third_pc
            if m > (notes[-1] if notes else root_midi) and m <= 59:
                if m - notes[-1] >= 3:  # at least a minor 3rd (OK near top)
                    notes.append(m)
                    break

    # Sort and remove duplicates
    notes = sorted(set(notes))

    # Smooth voice leading from previous
    if prev_lh:
        # Keep notes that are common tones, move others by step
        pass  # simplified for now

    # Convert to note tuples
    result = []
    for m in notes:
        pname, oct, accid_ges = note_from_midi(m, key, key_acc)
        result.append({'pname': pname, 'oct': oct, 'accid_ges': accid_ges, 'midi': m})

    return result

def build_rh_voicing(chord_str, key, lh_notes, prev_rh=None, measure_num=0):
    """
    Build RH voicing: 2-3 notes in treble (C4=48 to G5=79, above LH).
    Close voicing, lighter than LH.
    """
    tones_pc = chord_tones_pc(chord_str)
    root_pc = chord_root_pc(chord_str)
    key_acc = KEY_ACCIDENTALS.get(key, {})

    # Snap chord tones to diatonic
    diatonic_tones = [snap_to_diatonic(pc, key) for pc in tones_pc]
    diatonic_tones = list(dict.fromkeys(diatonic_tones))

    # LH top note
    lh_top = max(n['midi'] for n in lh_notes) if lh_notes else 48
    rh_low = max(lh_top + 2, 60)  # Start at least above LH, min C4 (midi 60)

    # Vary voicing by measure
    voicing_style = measure_num % 4  # 0=close, 1=spread, 2=first_inv, 3=close

    notes = []

    if voicing_style == 0:
        # Close position: third + fifth above some root in RH range
        root_candidates = []
        for pc in diatonic_tones[:2]:
            for oct in [4, 5]:
                m = (oct + 1) * 12 + pc
                if rh_low <= m <= 79:
                    root_candidates.append(m)

        if root_candidates:
            rh_root = root_candidates[0]
            notes.append(rh_root)
            # Add third above
            for pc in diatonic_tones[1:]:
                m_third = None
                for delta in range(3, 6):
                    candidate = rh_root + delta
                    if candidate % 12 in set(KEY_SCALES[key]) and candidate <= 79:
                        m_third = candidate
                        break
                if m_third:
                    notes.append(m_third)
                    break
            # Add fifth above (optional for 3-note voicing)
            if len(notes) < 3:
                for delta in range(6, 9):
                    candidate = notes[0] + delta
                    if candidate % 12 in set(KEY_SCALES[key]) and candidate <= 79:
                        notes.append(candidate)
                        break
    else:
        # Spread: find diatonic chord tones in RH range
        scale_set = set(KEY_SCALES[key])
        chord_pc_set = set(diatonic_tones)

        rh_notes_pool = []
        for m in range(rh_low, 80):
            if m % 12 in chord_pc_set:
                rh_notes_pool.append(m)

        if voicing_style == 1:
            # Start from 3rd above bass
            third_pc = diatonic_tones[1] if len(diatonic_tones) > 1 else diatonic_tones[0]
            for m in rh_notes_pool:
                if m % 12 == third_pc:
                    notes.append(m)
                    break
        elif voicing_style == 2:
            # Start from 5th
            fifth_pc = diatonic_tones[2] if len(diatonic_tones) > 2 else diatonic_tones[0]
            for m in rh_notes_pool:
                if m % 12 == fifth_pc:
                    notes.append(m)
                    break
        else:
            # Start from root in treble
            for m in rh_notes_pool:
                if m % 12 == diatonic_tones[0]:
                    notes.append(m)
                    break

        if not notes and rh_notes_pool:
            notes.append(rh_notes_pool[0])

        # Add 1-2 more
        for m in rh_notes_pool:
            if m not in notes and m > (notes[-1] if notes else rh_low) and len(notes) < 3:
                if m - notes[-1] >= 3:
                    notes.append(m)

    if not notes:
        # Fallback: root in treble range
        for oct in [4, 5]:
            m = (oct + 1) * 12 + diatonic_tones[0]
            if 60 <= m <= 79:
                notes = [m]
                break

    notes = sorted(set(notes))[:3]

    # Smooth voice leading
    if prev_rh and notes:
        pass  # simplified

    result = []
    for m in notes:
        pname, oct, accid_ges = note_from_midi(m, key, key_acc)
        result.append({'pname': pname, 'oct': oct, 'accid_ges': accid_ges, 'midi': m})

    return result

# ─────────────────────────────────────────────────────────────────────────────
# ROMAN NUMERAL LABELS
# ─────────────────────────────────────────────────────────────────────────────

def chord_to_roman(chord_str, key):
    """Return circled-digit roman numeral label for chord in key."""
    root_pc = chord_root_pc(chord_str)
    if root_pc is None:
        return chord_str

    scale = KEY_SCALES[key]
    quality = chord_quality(chord_str)

    # Find scale degree (1-7)
    if root_pc in scale:
        deg = scale.index(root_pc)  # 0-based
    else:
        # Try snapping
        snapped = snap_to_diatonic(root_pc, key)
        if snapped in scale:
            deg = scale.index(snapped)
        else:
            # Non-diatonic: return letter name
            return chord_str

    circ = CIRCLED[deg]

    if quality == 'min':
        return circ + 'm'
    elif quality == 'dim':
        return circ + '°'
    elif quality == 'aug':
        return circ + '+'
    elif quality == 'dom7':
        return circ + '7'
    elif quality == 'maj7':
        return circ + 'Δ'
    elif quality == 'min7':
        return circ + 'm7'
    elif quality == 'hdim7':
        return circ + 'ø7'
    elif quality == 'sus2':
        return circ + 's2'
    elif quality == 'sus4':
        return circ + 's4'
    else:
        return circ

# ─────────────────────────────────────────────────────────────────────────────
# DURATION FORMATTING
# ─────────────────────────────────────────────────────────────────────────────

def fraction_to_dur(f, meter_den=4):
    """
    Convert duration fraction (in units of quarter note = 1) to MEI dur/dots.
    Returns (dur_str, dots, tie_split) where tie_split is list if needed.
    """
    # f is in quarter-note units (Fraction)
    # MEI dur values: 1=whole, 2=half, 4=quarter, 8=eighth, 16=sixteenth, 32=32nd

    # Normalize: assume L is already in quarter units
    dur_map = {
        Fraction(4): (1, 0),
        Fraction(3): (2, 1),
        Fraction(2): (2, 0),
        Fraction(3,2): (4, 1),
        Fraction(1): (4, 0),
        Fraction(3,4): (8, 1),
        Fraction(1,2): (8, 0),
        Fraction(3,8): (16, 1),
        Fraction(1,4): (16, 0),
        Fraction(1,8): (32, 0),
        Fraction(6): (2, 0),  # dotted whole? use 2+2 tie
    }

    if f in dur_map:
        return dur_map[f][0], dur_map[f][1], False

    # Handle ties: split into two note values
    # Try whole + something
    for d1 in [Fraction(4), Fraction(2), Fraction(1), Fraction(1,2)]:
        if f > d1 and (f - d1) in dur_map:
            return None, None, (d1, f - d1)

    # Fallback to quarter
    return 4, 0, False

def dur_to_mei_attrs(quarter_dur, L_frac, meter_den=4):
    """
    Convert duration in quarter-note units to MEI dur/dots attributes string.
    L_frac is the ABC L: value as Fraction.
    """
    # quarter_dur is already in quarter-note units (since we convert L to quarters)
    d, dots, tie = fraction_to_dur(quarter_dur, meter_den)
    if tie:
        return None  # caller handles tie
    attrs = f'dur="{d}"'
    if dots:
        attrs += f' dots="{dots}"'
    return attrs

# ─────────────────────────────────────────────────────────────────────────────
# MEI NOTE GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def note_xml(xml_id, pname, oct, dur, dots, accid_ges=None, stem_dir=None, tie_to=None):
    """Generate <note> XML element."""
    attrs = f'xml:id="{xml_id}" dur="{dur}" oct="{oct}" pname="{pname}"'
    if dots:
        attrs += f' dots="{dots}"'
    if accid_ges:
        attrs += f' accid.ges="{accid_ges}"'
    if stem_dir:
        attrs += f' stem.dir="{stem_dir}"'
    return f'<note {attrs}/>'

def chord_xml(xml_id, notes_list, dur, dots, stem_dir=None):
    """Generate <chord> XML element with notes."""
    attrs = f'xml:id="{xml_id}" dur="{dur}"'
    if dots:
        attrs += f' dots="{dots}"'
    if stem_dir:
        attrs += f' stem.dir="{stem_dir}"'
    inner = ''
    for i, n in enumerate(notes_list):
        nid = xml_id.replace('c', 'n') + f'_{i}'
        nattrs = f'xml:id="{nid}" pname="{n["pname"]}" oct="{n["oct"]}"'
        if n.get('accid_ges'):
            nattrs += f' accid.ges="{n["accid_ges"]}"'
        inner += f'\n                    <note {nattrs}/>'
    return f'<chord {attrs}>{inner}\n                  </chord>'

# ─────────────────────────────────────────────────────────────────────────────
# MELODIC NOTE CONVERSION
# ─────────────────────────────────────────────────────────────────────────────

def melody_note_xml(xml_id, event, L_frac, key_acc, meter_den=4):
    """Convert ABC melody event to MEI note XML."""
    if event['pname'] == 'z':
        # Rest
        dur_q = event['dur'] / L_frac  # normalize to quarter units...
        # Actually dur is already in Fraction of whole note value
        # We need it in quarter note units
        dur_q_val = event['dur'] * 4  # since L is fraction of whole note, *4 = quarter units
        d, dots, tie = fraction_to_dur(dur_q_val, meter_den)
        if d is None:
            d, dots = 4, 0
        rattrs = f'xml:id="{xml_id}" dur="{d}"'
        if dots:
            rattrs += f' dots="{dots}"'
        return f'<rest {rattrs}/>'

    pname = event['pname']
    oct = event['oct']
    dur_q_val = event['dur'] * 4  # quarter units
    d, dots, tie = fraction_to_dur(dur_q_val, meter_den)
    if d is None:
        d, dots = 4, 0

    natural_pc = PITCH_PC.get(pname, 0)
    pc = natural_pc
    accid_ges = None

    # Key signature accidentals
    if event['accid']:
        # Explicit accidental in ABC overrides key sig
        abc_acc = event['accid']
        if abc_acc == 's':
            accid_ges = 's'
            pc = (natural_pc + 1) % 12
        elif abc_acc == 'f':
            accid_ges = 'f'
            pc = (natural_pc - 1) % 12
        elif abc_acc == 'n':
            accid_ges = 'n'
            pc = natural_pc
    else:
        # Check if key signature modifies this natural note
        # Key accidentals store the resulting PC after modification
        # e.g. KEY_ACCIDENTALS['Eb'] = {Bb=10:'f', Eb=3:'f', Ab=8:'f'}
        # For note 'e' (natural pc=4), flatted pc = 3 -> check if 3 in key_acc with 'f'
        flatted_pc = (natural_pc - 1) % 12
        sharped_pc = (natural_pc + 1) % 12
        if flatted_pc in key_acc and key_acc[flatted_pc] == 'f':
            accid_ges = 'f'
            pc = flatted_pc
        elif sharped_pc in key_acc and key_acc[sharped_pc] == 's':
            accid_ges = 's'
            pc = sharped_pc

    nattrs = f'xml:id="{xml_id}" dur="{d}" oct="{oct}" pname="{pname}"'
    if dots:
        nattrs += f' dots="{dots}"'
    if accid_ges:
        nattrs += f' accid.ges="{accid_ges}"'
    return f'<note {nattrs}/>'

# ─────────────────────────────────────────────────────────────────────────────
# RHYTHMIC VARIETY FOR HARP STAVES
# ─────────────────────────────────────────────────────────────────────────────

def build_harp_rhythm_pattern(bar_beats, meter_num, meter_den, voicing_notes, xml_id_prefix, staff_num, measure_num, is_lh=False):
    """
    Generate rhythmically varied MEI for one harp staff for one measure.
    Returns list of XML element strings.

    bar_beats: total beats in bar (Fraction in quarter units)
    voicing_notes: list of dicts with pname/oct/accid_ges/midi
    """
    elements = []

    if not voicing_notes:
        # Empty bar: whole rest
        d = 1 if bar_beats >= 4 else (2 if bar_beats >= 2 else 4)
        elements.append(f'<rest xml:id="{xml_id_prefix}_r" dur="{d}"/>')
        return elements

    # Choose rhythm pattern based on measure_num and meter
    pattern_idx = (measure_num + (1 if is_lh else 0)) % 6

    # For 4/4: 4 beats
    # For 3/4: 3 beats
    # For 6/4: 6 beats
    # For 3/2: 6 quarter beats

    beats = float(bar_beats)  # in quarter note units

    # Sort notes low to high
    notes = sorted(voicing_notes, key=lambda n: n['midi'])

    def chord_elem(cid, note_list, dur_val, dots_val=0):
        """Make chord element."""
        if len(note_list) == 1:
            n = note_list[0]
            nattrs = f'xml:id="{cid}" dur="{dur_val}" oct="{n["oct"]}" pname="{n["pname"]}"'
            if dots_val:
                nattrs += f' dots="{dots_val}"'
            if n.get('accid_ges'):
                nattrs += f' accid.ges="{n["accid_ges"]}"'
            return f'<note {nattrs}/>'
        else:
            cattrs = f'xml:id="{cid}" dur="{dur_val}"'
            if dots_val:
                cattrs += f' dots="{dots_val}"'
            inner = ''
            for i, n in enumerate(note_list):
                nid = cid.replace('c', 'n') + f'_{i}'
                nattrs = f'xml:id="{nid}" pname="{n["pname"]}" oct="{n["oct"]}"'
                if n.get('accid_ges'):
                    nattrs += f' accid.ges="{n["accid_ges"]}"'
                inner += f'\n                    <note {nattrs}/>'
            return f'<chord {cattrs}>{inner}\n                  </chord>'

    if beats == 4.0:  # 4/4
        if pattern_idx == 0:
            # Half note + half note (block)
            lower = notes[:len(notes)//2+1] if len(notes) >= 2 else notes
            upper = notes[len(notes)//2:] if len(notes) >= 2 else notes
            if len(notes) >= 3:
                lower = notes[:2]
                upper = notes[1:]
            elements.append(chord_elem(f'{xml_id_prefix}_c1', lower if is_lh else upper, 2))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes, 2))
        elif pattern_idx == 1:
            # Quarter + dotted half (arrive early)
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes[:2] if len(notes)>=2 else notes, 4))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes, 2, 1))
        elif pattern_idx == 2:
            # Arpeggio: 4 quarters ascending
            if len(notes) >= 2:
                for i, n in enumerate(notes):
                    elements.append(chord_elem(f'{xml_id_prefix}_c{i+1}', [n], 4))
                    if i >= 3:
                        break
                # Fill remaining beats
                used = min(len(notes), 4)
                if used < 4:
                    elements.append(chord_elem(f'{xml_id_prefix}_cfill', notes, 4 if 4-used==1 else 2))
            else:
                elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 1))
        elif pattern_idx == 3:
            # Whole note block
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 1))
        elif pattern_idx == 4:
            # Dotted quarter + eighth + half
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes[:2] if len(notes)>=2 else notes, 4, 1))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes[-1:] if len(notes)>=1 else notes, 8))
            elements.append(chord_elem(f'{xml_id_prefix}_c3', notes, 2))
        else:  # pattern 5
            # Half + quarter + quarter
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 2))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes[:2] if len(notes)>=2 else notes, 4))
            elements.append(chord_elem(f'{xml_id_prefix}_c3', notes[-2:] if len(notes)>=2 else notes, 4))

    elif beats == 3.0:  # 3/4
        if pattern_idx == 0:
            # Dotted half (whole bar)
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 2, 1))
        elif pattern_idx == 1:
            # Quarter + half
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes[:2] if len(notes)>=2 else notes, 4))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes, 2))
        elif pattern_idx == 2:
            # Half + quarter
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 2))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes[:2] if len(notes)>=2 else notes, 4))
        elif pattern_idx == 3:
            # Arpeggio: 3 quarters
            for i, n in enumerate(notes[:3]):
                elements.append(chord_elem(f'{xml_id_prefix}_c{i+1}', [n], 4))
            if len(notes) < 3:
                elements.append(chord_elem(f'{xml_id_prefix}_cfill', notes, 4 if len(notes)==2 else 2))
        elif pattern_idx == 4:
            # Quarter + quarter + quarter (all chords)
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes[:2] if len(notes)>=2 else notes, 4))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes[1:3] if len(notes)>=3 else notes, 4))
            elements.append(chord_elem(f'{xml_id_prefix}_c3', notes, 4))
        else:  # 5
            # Dotted half
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 2, 1))

    elif beats == 6.0:  # 6/4
        if pattern_idx == 0:
            # Dotted half + dotted half
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes[:2] if len(notes)>=2 else notes, 2, 1))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes, 2, 1))
        elif pattern_idx == 1:
            # Half note x3
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes[:2] if len(notes)>=2 else notes, 2))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes, 2))
            elements.append(chord_elem(f'{xml_id_prefix}_c3', notes[-2:] if len(notes)>=2 else notes, 2))
        else:
            # Whole note + half
            elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 1))
            elements.append(chord_elem(f'{xml_id_prefix}_c2', notes[:2] if len(notes)>=2 else notes, 2))

    elif beats == 2.0:  # 2/4 or pickup
        elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 2))

    elif beats == 1.0:  # pickup
        elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 4))

    elif beats == 1.5:  # dotted quarter pickup
        elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, 4, 1))

    else:
        # Generic: whole note
        d_val = 1
        if beats <= 1.5:
            d_val = 4 if beats <= 1.0 else 4
        elif beats <= 3:
            d_val = 2
        elements.append(chord_elem(f'{xml_id_prefix}_c1', notes, d_val))

    return elements

# ─────────────────────────────────────────────────────────────────────────────
# MEI GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def get_key_sig_str(key):
    return KEY_SIGS[key][0]

def generate_mei(hymn_n, title, key, meter_num, meter_den, L_frac, bars):
    """Generate complete MEI document for a hymn."""
    key_sig = get_key_sig_str(key)
    key_acc = KEY_ACCIDENTALS.get(key, {})

    lines = []
    lines.append("<?xml version='1.0' encoding='utf-8'?>")
    lines.append('<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.0">')
    lines.append('  <meiHead>')
    lines.append('    <fileDesc>')
    lines.append('      <titleStmt>')
    lines.append(f'        <title>{title}</title>')
    lines.append(f'        <title type="subtitle">Harp Arrangement -- SSAATTBB + Pedal</title>')
    lines.append('      </titleStmt>')
    lines.append('      <pubStmt>')
    lines.append('        <date isodate="2026-04-12" />')
    lines.append('      </pubStmt>')
    lines.append('    </fileDesc>')
    lines.append('  </meiHead>')
    lines.append('  <music>')
    lines.append('    <body>')
    lines.append('      <mdiv>')
    lines.append('        <score>')
    lines.append(f'          <scoreDef meter.count="{meter_num}" meter.unit="{meter_den}" key.sig="{key_sig}">')
    lines.append('            <staffGrp symbol="bracket" barthru="true">')
    lines.append('              <staffDef n="1" lines="5" clef.shape="G" clef.line="2" label="Melody">')
    lines.append(f'                <keySig sig="{key_sig}" />')
    lines.append('              </staffDef>')
    lines.append('              <staffGrp symbol="brace">')
    lines.append('                <staffDef n="2" lines="5" clef.shape="G" clef.line="2" label="RH">')
    lines.append(f'                  <keySig sig="{key_sig}" />')
    lines.append('                </staffDef>')
    lines.append('                <staffDef n="3" lines="5" clef.shape="F" clef.line="4" label="LH">')
    lines.append(f'                  <keySig sig="{key_sig}" />')
    lines.append('                </staffDef>')
    lines.append('              </staffGrp>')
    lines.append('            </staffGrp>')
    lines.append('          </scoreDef>')
    lines.append('          <section>')

    prev_lh = None
    prev_rh = None
    prev_chord = None
    bar_beat_total = Fraction(meter_num, 1)  # total beats per bar in quarter units
    # If meter_den != 4, adjust
    # e.g. 6/4: 6 quarter beats, 3/2: 6 quarter beats, 3/4: 3 quarter beats
    bar_beat_total = Fraction(meter_num * 4, meter_den)  # in quarter units

    # Track LH/RH voicings per chord for smooth voice leading
    chord_to_lh_voicing = {}
    chord_to_rh_voicing = {}

    for bar_idx, bar in enumerate(bars):
        measure_n = bar_idx + 1
        chord_str = bar.get('chord') or prev_chord or 'C'
        notes = bar.get('notes', [])

        if not notes:
            continue

        # Calculate actual bar duration in quarter units
        bar_dur_q = sum(ev['dur'] * 4 for ev in notes)  # L was already in whole-note fractions

        # Is this a pickup bar?
        is_pickup = bar_dur_q < bar_beat_total and measure_n == 1

        right_attr = '"single"'
        if bar_idx == len(bars) - 1:
            right_attr = '"final"'

        measure_attrs = f'n="{measure_n}"'
        if is_pickup:
            measure_attrs += ' type="pickup"'

        lines.append(f'')
        lines.append(f'            <!-- Measure {measure_n}: {chord_str} -->')
        lines.append(f'            <measure {measure_attrs} right={right_attr}>')

        # Staff 1: Melody
        lines.append(f'              <staff n="1">')
        lines.append(f'                <layer n="1">')
        for ev_idx, ev in enumerate(notes):
            xml_id = f'm{measure_n}s1n{ev_idx+1}'
            mel_xml = melody_note_xml(xml_id, ev, L_frac, key_acc, meter_den)
            lines.append(f'                  {mel_xml}')
        lines.append(f'                </layer>')
        lines.append(f'              </staff>')

        # Build harp voicings
        # Use chord from bar, with variety
        lh_notes = build_lh_voicing(chord_str, key, prev_lh, measure_n)
        rh_notes = build_rh_voicing(chord_str, key, lh_notes, prev_rh, measure_n)

        # Build rhythmic patterns
        # For pickup bar: use simpler rhythm
        effective_beats = bar_dur_q if is_pickup else bar_beat_total

        rh_elems = build_harp_rhythm_pattern(
            effective_beats, meter_num, meter_den, rh_notes,
            f'm{measure_n}s2', 2, measure_n, is_lh=False
        )
        lh_elems = build_harp_rhythm_pattern(
            effective_beats, meter_num, meter_den, lh_notes,
            f'm{measure_n}s3', 3, measure_n, is_lh=True
        )

        # Staff 2: RH
        lines.append(f'              <staff n="2">')
        lines.append(f'                <layer n="1">')
        for elem in rh_elems:
            lines.append(f'                  {elem}')
        lines.append(f'                </layer>')
        lines.append(f'              </staff>')

        # Staff 3: LH
        lines.append(f'              <staff n="3">')
        lines.append(f'                <layer n="1">')
        for elem in lh_elems:
            lines.append(f'                  {elem}')
        lines.append(f'                </layer>')
        lines.append(f'              </staff>')

        # Harm labels for chord changes in this bar
        # Get distinct chord events
        chord_events = bar.get('chord_events', [])
        if chord_events:
            for beat_offset, c_str in chord_events:
                # beat_offset is in L units (Fraction of whole note)
                # tstamp is in meter.unit units, 1-based
                # Convert: beat_offset * 4 / (meter_den/4) = beat_offset * 16 / meter_den
                # Actually tstamp = 1 + (beat_offset_in_quarter_units) / (4/meter_den)
                # = 1 + beat_offset * 4 * meter_den / 4 = 1 + beat_offset * meter_den
                # For meter_den=4: tstamp = 1 + beat_offset * 4 (quarter units)
                # beat_offset is in Fraction whole notes, so in quarters = beat_offset * 4
                tstamp = float(beat_offset * 4) + 1
                label = chord_to_roman(c_str, key)
                ts_str = f'{tstamp:.4g}' if tstamp != int(tstamp) else str(int(tstamp))
                lines.append(f'              <harm staff="1" tstamp="{ts_str}">{label}</harm>')
        else:
            # Just use bar chord at beat 1
            label = chord_to_roman(chord_str, key)
            lines.append(f'              <harm staff="1" tstamp="1">{label}</harm>')

        lines.append(f'            </measure>')

        prev_lh = lh_notes
        prev_rh = rh_notes
        prev_chord = chord_str

    lines.append('          </section>')
    lines.append('        </score>')
    lines.append('      </mdiv>')
    lines.append('    </body>')
    lines.append('  </music>')
    lines.append('</mei>')

    return '\n'.join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def split_bar_into_submeasures(bar, beats_per_submeasure_q):
    """
    Split a long bar (M:none) into sub-measures of beats_per_submeasure_q quarter beats.
    Returns list of bar dicts.
    """
    notes = bar['notes']
    if not notes:
        return [bar]

    submeasures = []
    running = Fraction(0)
    current_notes = []
    current_chord = bar['chord']
    bps = beats_per_submeasure_q  # in quarter units

    for ev in notes:
        dur_q = ev['dur'] * 4  # convert to quarter units

        # Does this note fit in current submeasure?
        space_left = bps - running
        if dur_q <= space_left + Fraction(1, 32):  # small tolerance
            current_notes.append(ev)
            running += dur_q
        else:
            # Flush current submeasure
            if current_notes:
                ce = [(Fraction(0), current_chord)] if current_chord else []
                submeasures.append({
                    'chord': current_chord,
                    'notes': current_notes,
                    'beats': running,
                    'chord_events': ce,
                })
            current_notes = [ev]
            running = dur_q
            if ev.get('chord'):
                current_chord = ev['chord']

        # Check if submeasure is complete
        if abs(running - bps) < Fraction(1, 32):
            ce = [(Fraction(0), current_chord)] if current_chord else []
            submeasures.append({
                'chord': current_chord,
                'notes': current_notes,
                'beats': running,
                'chord_events': ce,
            })
            current_notes = []
            running = Fraction(0)

    # Remaining notes
    if current_notes:
        ce = [(Fraction(0), current_chord)] if current_chord else []
        submeasures.append({
            'chord': current_chord,
            'notes': current_notes,
            'beats': running,
            'chord_events': ce,
        })

    return submeasures if submeasures else [bar]


def main():
    data = json.load(open('/home/james.clements/projects/trefoil/app/lead_sheets.json'))
    target = {str(n) for n in range(4208, 4244)}
    hymns = {str(h['n']): h for h in data if str(h.get('n','')) in target}

    os.makedirs(OUT_DIR, exist_ok=True)

    # Process each hymn
    for n_str in sorted(target, key=int):
        if n_str not in hymns:
            print(f'SKIP {n_str}: not found')
            continue

        h = hymns[n_str]
        abc = h['abc']
        key = h['key']

        # Parse ABC headers
        title_m = re.search(r'^T:\s*(.+)', abc, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else 'Untitled'

        meter_m = re.search(r'^M:\s*(.+)', abc, re.MULTILINE)
        meter_str = meter_m.group(1).strip() if meter_m else '4/4'

        L_m = re.search(r'^L:\s*(.+)', abc, re.MULTILINE)
        L_str = L_m.group(1).strip() if L_m else '1/8'

        # Parse meter
        is_free_meter = (meter_str == 'none')
        if is_free_meter:
            meter_num, meter_den = 4, 4  # render as 4/4
        elif '/' in meter_str:
            mn, md = meter_str.split('/')
            meter_num, meter_den = int(mn), int(md)
        else:
            meter_num, meter_den = 4, 4

        # Parse L (default note length)
        if '/' in L_str:
            ln, ld = L_str.split('/')
            L_frac = Fraction(int(ln), int(ld))
        else:
            L_frac = Fraction(1, 8)
        L_denom = L_frac.denominator // L_frac.numerator if L_frac.numerator != 1 else L_frac.denominator

        # Extract ABC music body (after K: line)
        k_pos = abc.find('\nK:')
        if k_pos == -1:
            k_pos = abc.find('K:')
        body_start = abc.find('\n', k_pos) + 1 if k_pos != -1 else 0
        body = abc[body_start:].strip()
        body_lines = []
        for line in body.split('\n'):
            if re.match(r'^[A-Z]:', line) or line.startswith('%%'):
                continue
            body_lines.append(line)
        body = ' '.join(body_lines)

        # Parse bars
        bars = parse_abc_bars(body, L_denom if L_frac.numerator == 1 else 1, meter_num, meter_den)

        if not bars:
            print(f'WARN {n_str}: no bars parsed')
            bars = [{'chord': 'C', 'notes': [], 'beats': Fraction(meter_num), 'chord_events': []}]

        # For M:none, split long bars into 4/4 sub-measures
        if is_free_meter:
            beats_per_measure_q = Fraction(4)  # 4 quarter beats
            new_bars = []
            for bar in bars:
                bar_dur_q = sum(ev['dur'] * 4 for ev in bar['notes'])
                if bar_dur_q > beats_per_measure_q * Fraction(3, 2):
                    # Long bar: split it
                    subs = split_bar_into_submeasures(bar, beats_per_measure_q)
                    new_bars.extend(subs)
                else:
                    new_bars.append(bar)
            bars = new_bars

        # Generate MEI
        mei = generate_mei(n_str, title, key, meter_num, meter_den, L_frac, bars)

        out_path = os.path.join(OUT_DIR, f'{n_str}_raw.mei')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(mei)

        print(f'OK {n_str}: {title[:40]} [{key} {meter_str}] {len(bars)} bars')

    print('Done.')

if __name__ == '__main__':
    main()
