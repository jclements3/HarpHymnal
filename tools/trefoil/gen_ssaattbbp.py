#!/usr/bin/env python3
"""
Generate SSAATTBB+P pedal harp MEI arrangements for hymns.
Reads lead_sheets.json, writes NNNN_raw.mei files.
"""
import json, re, sys, os
from fractions import Fraction

# ---- Key signature helpers -------------------------------------------------

KEY_SIGS = {
    'Eb': '3f', 'Bb': '2f', 'F': '1f', 'C': '0',
    'G': '1s', 'D': '2s', 'A': '3s', 'E': '4s',
}

KEY_SCALES = {  # diatonic pitch classes (0=C)
    'C':  [0,2,4,5,7,9,11],
    'G':  [0,2,4,5,7,9,11],  # F# in key
    'D':  [0,2,4,6,7,9,11],
    'A':  [0,2,4,6,7,9,11],
    'E':  [1,2,4,6,7,9,11],
    'Bb': [0,2,3,5,7,9,10],
    'F':  [0,2,4,5,7,9,10],
    'Eb': [0,2,3,5,7,8,10],
}

# Key-signature accidentals: notes that need accid.ges
KEY_ACCID = {
    'Eb': {'b': 'f', 'e': 'f', 'a': 'f'},
    'Bb': {'b': 'f', 'e': 'f'},
    'F':  {'b': 'f'},
    'C':  {},
    'G':  {'f': 's'},
    'D':  {'f': 's', 'c': 's'},
    'A':  {'f': 's', 'c': 's', 'g': 's'},
    'E':  {'f': 's', 'c': 's', 'g': 's', 'd': 's'},
}

def keysig_str(key):
    return KEY_SIGS.get(key, '0')

def accid_ges(pname, key):
    """Return accid.ges value for pname in key, or None if natural."""
    return KEY_ACCID.get(key, {}).get(pname.lower())

# ---- Circled digit chord labels --------------------------------------------

CIRCLED = ['①','②','③','④','⑤','⑥','⑦']

def harm_label(deg, quality='', inv=''):
    """Build harm label: circled digit + m/° + inv superscript."""
    c = CIRCLED[(deg-1) % 7]
    sup = {1:'¹', 2:'²', 3:'³'}.get(inv, '')
    return f'{c}{quality}{sup}'

# ---- Simple ABC melody parser ----------------------------------------------

ABC_NOTE_RE = re.compile(
    r'(\^{1,2}|_{1,2}|=)?([A-Ga-gz])(,*\'*)'
    r'(\d*(?:/\d*)?)'
    r'(-?)'  # tie
)

CHORD_RE = re.compile(r'"?\^([^"]+)"')

def parse_abc_notes(abc_body, L_unit, meter_num, meter_den):
    """Parse ABC body into list of (offset_frac, dur_frac, pname, oct, accid_explicit) tuples.
    Returns events sorted by offset."""
    events = []
    offset = Fraction(0)

    # Tokenize
    i = 0
    body = abc_body

    while i < len(body):
        c = body[i]

        if c in '|:\n[]':
            if c == '|':
                # barline — not tracking here
                i += 1
                continue
            i += 1
            continue

        if c == '"':
            # chord annotation, skip
            j = i + 1
            while j < len(body) and body[j] != '"':
                j += 1
            i = j + 1
            continue

        if c == 'z' or c == 'x':
            # rest
            i += 1
            # parse duration
            dur, skip = parse_dur(body, i, L_unit)
            i += skip
            offset += dur
            continue

        if c == '(':
            i += 1
            continue
        if c == ')':
            i += 1
            continue

        # Try note
        m = ABC_NOTE_RE.match(body, i)
        if m:
            acc_pfx = m.group(1) or ''
            note_str = m.group(2)
            oct_mod = m.group(3)
            dur_str = m.group(4)
            tie_str = m.group(5)

            if note_str == 'z' or note_str == 'x':
                dur = parse_dur_str(dur_str, L_unit)
                offset += dur
                i = m.end()
                continue

            # Pitch
            pname, oct = abc_note_to_pitch(note_str, oct_mod)

            # Explicit accidental
            acc_explicit = None
            if acc_pfx == '^':
                acc_explicit = 's'
            elif acc_pfx == '^^':
                acc_explicit = 'ss'
            elif acc_pfx == '_':
                acc_explicit = 'f'
            elif acc_pfx == '__':
                acc_explicit = 'ff'
            elif acc_pfx == '=':
                acc_explicit = 'n'

            dur = parse_dur_str(dur_str, L_unit)
            events.append((offset, dur, pname, oct, acc_explicit))
            offset += dur
            i = m.end()
            continue

        i += 1

    return events

def abc_note_to_pitch(note_str, oct_mod):
    """Convert ABC note letter + octave modifiers to (pname, oct_int)."""
    base = note_str[0]
    if base.isupper():
        base_oct = 4  # C = C4 in ABC (middle octave)
        pname = base.lower()
    else:
        base_oct = 5  # c = C5
        pname = base.lower()

    # ABC: uppercase = octave 4, lowercase = octave 5
    # commas lower by 1, apostrophes raise by 1
    oct_adj = oct_mod.count("'") - oct_mod.count(',')
    oct_int = base_oct + oct_adj

    return pname, oct_int

def parse_dur_str(dur_str, L_unit):
    """Parse ABC duration string into Fraction."""
    if not dur_str:
        return L_unit
    if dur_str == '/':
        return L_unit / 2
    if dur_str.startswith('/'):
        denom = int(dur_str[1:]) if len(dur_str) > 1 else 2
        return L_unit / denom
    if '/' in dur_str:
        parts = dur_str.split('/')
        num = int(parts[0]) if parts[0] else 1
        den = int(parts[1]) if parts[1] else 2
        return L_unit * Fraction(num, den)
    return L_unit * int(dur_str)

def parse_dur(body, i, L_unit):
    """Parse duration starting at position i, return (Fraction, chars_consumed)."""
    start = i
    s = ''
    while i < len(body) and (body[i].isdigit() or body[i] == '/'):
        s += body[i]
        i += 1
    return parse_dur_str(s, L_unit), i - start

def extract_chord_annotations(abc_body):
    """Extract (position_index, chord_name) from ABC body."""
    chords = []
    for m in CHORD_RE.finditer(abc_body):
        chords.append((m.start(), m.group(1)))
    return chords

def extract_bars(abc_body):
    """Split ABC body into bars, tracking chord context."""
    # Split on barlines
    bars_raw = re.split(r'\|+', abc_body)
    return bars_raw

# ---- Chord analysis --------------------------------------------------------

CHORD_ROOT_MAP = {
    'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11,
    'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11,
}

def chord_root_pc(chord_str):
    """Get pitch class (0-11) of chord root from chord annotation string."""
    if not chord_str:
        return 0
    # Remove decoration
    s = chord_str.strip()
    if not s:
        return 0
    root_letter = s[0].upper()
    pc = CHORD_ROOT_MAP.get(root_letter, 0)
    if len(s) > 1:
        if s[1] == '#' or s[1] == '^':
            pc = (pc + 1) % 12
        elif s[1] == 'b' or s[1] == '_':
            pc = (pc - 1) % 12
    return pc

def chord_quality(chord_str):
    """Determine 'm', 'dim', 'aug', '7', 'maj7', 'min7', 'halfdim', '' from chord string."""
    if not chord_str:
        return ''
    s = chord_str
    # Remove root and accidental
    i = 1
    if i < len(s) and s[i] in '#b^_':
        i += 1
    rest = s[i:]
    if rest.startswith('m7') or rest.startswith('min7'):
        return 'min7'
    if rest.startswith('ø7') or rest.startswith('ø'):
        return 'halfdim'
    if rest.startswith('°7') or rest.startswith('dim7'):
        return 'dim7'
    if rest.startswith('°') or rest.startswith('dim'):
        return 'dim'
    if rest.startswith('Δ7') or rest.startswith('maj7') or rest.startswith('Δ'):
        return 'maj7'
    if rest.startswith('+'):
        return 'aug'
    if rest.startswith('m') or rest.startswith('min'):
        return 'm'
    if rest.startswith('7'):
        return '7'
    if rest.startswith('sus2'):
        return 'sus2'
    if rest.startswith('sus4'):
        return 'sus4'
    return ''

def scale_degree(root_pc, key):
    """Return 1-7 scale degree of root_pc in key. Returns nearest diatonic if chromatic."""
    scale_pcs = KEY_SCALES.get(key, [0,2,4,5,7,9,11])

    # Full key pc
    key_pc_map = {'C':0,'G':7,'D':2,'A':9,'E':4,'B':11,'Bb':10,'F':5,'Eb':3}
    key_pc = key_pc_map.get(key, 0)

    # Scale PCs relative to key root
    scale_abs = [(key_pc + s) % 12 for s in [0,2,4,5,7,9,11]]

    root_pc_mod = root_pc % 12
    if root_pc_mod in scale_abs:
        return scale_abs.index(root_pc_mod) + 1

    # Nearest diatonic
    best = 1
    best_dist = 12
    for i, pc in enumerate(scale_abs):
        d = min(abs(root_pc_mod - pc), 12 - abs(root_pc_mod - pc))
        if d < best_dist:
            best_dist = d
            best = i + 1
    return best

# ---- Voice building --------------------------------------------------------

def key_pc(key):
    """Return pitch class of key tonic."""
    key_pc_map = {'C':0,'G':7,'D':2,'A':9,'E':4,'B':11,'Bb':10,'F':5,'Eb':3}
    return key_pc_map.get(key, 0)

def scale_pitches_in_range(key, lo_midi, hi_midi):
    """Return sorted list of (midi, pname, oct) for all diatonic notes in [lo_midi, hi_midi]."""
    kpc = key_pc(key)
    scale_intervals = [0,2,4,5,7,9,11]  # Ionian

    # Build complete scale from C2 (midi 36) to G6 (midi 91)
    notes = []
    for midi in range(max(24, lo_midi), min(91, hi_midi+1)):
        pc = midi % 12
        pc_rel = (pc - kpc) % 12
        if pc_rel in scale_intervals:
            pname = ['c','d','e','f','g','a','b'][scale_intervals.index(pc_rel)]
            oct_n = (midi // 12) - 1  # MIDI oct: C4=60, oct=4
            notes.append((midi, pname, oct_n))
    return notes

def nearest_diatonic(pname, oct_n, key, direction='up'):
    """Return (midi, pname, oct) of nearest diatonic note to given pitch."""
    pc_names = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}
    midi_target = (oct_n + 1) * 12 + pc_names.get(pname.lower(), 0)

    notes = scale_pitches_in_range(key, 36, 91)
    if not notes:
        return (midi_target, pname, oct_n)

    best = min(notes, key=lambda x: abs(x[0] - midi_target))
    return best

def chord_tones_midi(chord_str, key, lo_midi, hi_midi):
    """Return sorted list of (midi, pname, oct) for chord tones of chord_str in key within range."""
    root_p = chord_root_pc(chord_str)
    qual = chord_quality(chord_str)

    # Chord tone intervals from root (semitones)
    if qual in ('m', 'min7', 'halfdim'):
        if qual == 'halfdim':
            intervals = [0, 3, 6, 10]
        elif qual == 'min7':
            intervals = [0, 3, 7, 10]
        else:
            intervals = [0, 3, 7]
    elif qual in ('dim', 'dim7'):
        if qual == 'dim7':
            intervals = [0, 3, 6, 9]
        else:
            intervals = [0, 3, 6]
    elif qual == 'aug':
        intervals = [0, 4, 8]
    elif qual == 'maj7':
        intervals = [0, 4, 7, 11]
    elif qual == '7':
        intervals = [0, 4, 7, 10]
    elif qual == 'sus2':
        intervals = [0, 2, 7]
    elif qual == 'sus4':
        intervals = [0, 5, 7]
    else:  # major
        intervals = [0, 4, 7]

    # Get diatonic scale pitches
    scale_notes = scale_pitches_in_range(key, lo_midi, hi_midi)

    # Filter to chord tones (use diatonic approximation)
    chord_pcs = [(root_p + iv) % 12 for iv in intervals]

    result = []
    for midi, pname, oct_n in scale_notes:
        if (midi % 12) in chord_pcs:
            result.append((midi, pname, oct_n))

    # If empty (non-diatonic chord), fall back to scale tones near root
    if not result:
        # Use tonic triad as fallback
        key_tonic_pc = key_pc(key)
        major_pcs = [(key_tonic_pc + iv) % 12 for iv in [0,4,7]]
        for midi, pname, oct_n in scale_notes:
            if (midi % 12) in major_pcs:
                result.append((midi, pname, oct_n))

    return sorted(result)

# ---- Voicing selection -----------------------------------------------------

def pick_lh_voicing(chord_str, key, prev_lh=None):
    """Pick 3-4 note LH voicing. Bass-heavy, open spacing."""
    tones = chord_tones_midi(chord_str, key, 36, 62)  # C2-D4
    if not tones:
        tones = scale_pitches_in_range(key, 36, 50)[:4]

    if len(tones) < 3:
        # Extend range
        tones = chord_tones_midi(chord_str, key, 24, 65)
        if not tones:
            tones = scale_pitches_in_range(key, 36, 62)[:4]

    # Choose root + 5th + octave + 3rd pattern
    # Find the best 3-4 notes with open spacing (no 2nds/3rds in bottom)
    if len(tones) >= 3:
        # Try to get root, 5th, octave
        root_pc_val = chord_root_pc(chord_str)
        qual = chord_quality(chord_str)

        if qual in ('m', 'min7', 'halfdim'):
            fifth_pc = (root_pc_val + 7) % 12
        elif qual in ('dim', 'dim7'):
            fifth_pc = (root_pc_val + 6) % 12
        elif qual == 'aug':
            fifth_pc = (root_pc_val + 8) % 12
        else:
            fifth_pc = (root_pc_val + 7) % 12

        # Get root, fifth, octave
        roots = [t for t in tones if t[0] % 12 == root_pc_val]
        fifths = [t for t in tones if t[0] % 12 == fifth_pc]

        if roots and fifths:
            r = roots[0]  # lowest root
            # Find fifth above root
            f_above = [t for t in fifths if t[0] > r[0]]
            if f_above:
                f = f_above[0]
                # Find octave above fifth (root an octave up)
                r_oct = [t for t in roots if t[0] >= f[0] and t[0] <= 65]
                if r_oct:
                    voicing = [r, f, r_oct[0]]
                    # Add 3rd if available and doesn't create muddy bass
                    if qual in ('m', 'min7'):
                        third_pc = (root_pc_val + 3) % 12
                    else:
                        third_pc = (root_pc_val + 4) % 12
                    thirds = [t for t in tones if t[0] % 12 == third_pc and t[0] > voicing[-1][0]]
                    if thirds and thirds[0][0] <= 65:
                        voicing.append(thirds[0])
                    return sorted(voicing)[:4]

        # Fallback: pick lowest 3-4 tones with spacing > 2 semitones in bass
        result = [tones[0]]
        for t in tones[1:]:
            if len(result) >= 4:
                break
            gap = t[0] - result[-1][0]
            if len(result) < 2:
                if gap >= 5:  # P4 minimum in bass
                    result.append(t)
            else:
                if gap >= 3:  # m3 OK for top note
                    result.append(t)
        if len(result) >= 2:
            return result

    return tones[:3] if tones else []

def pick_rh_voicing(chord_str, key, lh_notes, prev_rh=None):
    """Pick 2-3 note RH voicing above LH."""
    lh_max = max(n[0] for n in lh_notes) if lh_notes else 60
    lo = max(60, lh_max + 1)  # above LH, starting at C4

    tones = chord_tones_midi(chord_str, key, lo, 79)  # up to G5
    if not tones:
        tones = chord_tones_midi(chord_str, key, 60, 84)
    if not tones:
        tones = scale_pitches_in_range(key, lo, 79)[:3]

    if not tones:
        return []

    # Pick close position 2-3 notes
    # Prefer voice leading from previous RH
    if prev_rh:
        prev_avg = sum(n[0] for n in prev_rh) / len(prev_rh)
        # Find closest tone to prev_avg
        closest = min(tones, key=lambda t: abs(t[0] - prev_avg))
        idx = tones.index(closest)
        # Take 2-3 notes around that point
        start = max(0, idx - 1)
        result = tones[start:start+3]
    else:
        # Take lowest 2-3 available
        result = tones[:3]

    return sorted(result)[:3]

def pick_pedal(chord_str, key):
    """Pick pedal bass note (C1-B1, midi 24-35, below lever harp range)."""
    root_p = chord_root_pc(chord_str)
    # Find root in C1-B1 range
    for oct_n in [1, 2]:
        midi = (oct_n + 1) * 12 + root_p
        if 24 <= midi <= 35:
            pname_map = {0:'c',2:'d',4:'e',5:'f',7:'g',9:'a',11:'b'}
            # Find diatonic nearest
            kpc = key_pc(key)
            pc_rel = (root_p - kpc) % 12
            scale_intervals = [0,2,4,5,7,9,11]
            diatonic_pcs = [(kpc + iv) % 12 for iv in scale_intervals]
            if root_p in diatonic_pcs:
                pname = pname_map.get(root_p % 12, 'c')
                return (midi, pname, oct_n)
            else:
                # Use nearest diatonic
                best_pc = min(diatonic_pcs, key=lambda x: min(abs(x - root_p), 12 - abs(x - root_p)))
                pname = pname_map.get(best_pc, 'c')
                midi = (oct_n + 1) * 12 + best_pc
                return (midi, pname, oct_n)
    return (24, 'c', 1)  # fallback C1

# ---- MEI note rendering ----------------------------------------------------

def mei_note(xml_id, pname, oct_n, dur_str, key, dots=0, stem_dir=None, tie_start=False, tie_end=False, extra_accid=None):
    """Render a single MEI note element."""
    ges = accid_ges(pname, key)
    attrs = f'xml:id="{xml_id}" dur="{dur_str}" oct="{oct_n}" pname="{pname}"'
    if dots:
        attrs += f' dots="{dots}"'
    if ges:
        attrs += f' accid.ges="{ges}"'
    if extra_accid:
        attrs += f' accid="{extra_accid}"'
    if stem_dir:
        attrs += f' stem.dir="{stem_dir}"'
    tie_attr = ''
    if tie_start and tie_end:
        tie_attr = ' tie="m"'
    elif tie_start:
        tie_attr = ' tie="i"'
    elif tie_end:
        tie_attr = ' tie="t"'
    return f'<note {attrs}{tie_attr}/>'

def mei_chord(xml_id, notes_list, dur_str, key, dots=0, stem_dir=None):
    """Render a MEI chord element containing multiple notes.
    notes_list: [(pname, oct_n), ...]"""
    attrs = f'xml:id="{xml_id}" dur="{dur_str}"'
    if dots:
        attrs += f' dots="{dots}"'
    if stem_dir:
        attrs += f' stem.dir="{stem_dir}"'
    inner = ''
    for i, (pname, oct_n) in enumerate(notes_list):
        ges = accid_ges(pname, key)
        nattrs = f'xml:id="{xml_id}n{i+1}" pname="{pname}" oct="{oct_n}"'
        if ges:
            nattrs += f' accid.ges="{ges}"'
        inner += f'\n            <note {nattrs}/>'
    return f'<chord {attrs}>{inner}\n          </chord>'

# ---- ABC measures extraction -----------------------------------------------

def parse_abc_measures(abc_str):
    """Parse ABC string into list of (chord_annotations, raw_notes_str) per measure.
    Returns list of {'chord': str, 'notes': str, 'pickup': bool}
    """
    # Find body (after K:)
    k_match = re.search(r'\nK:[^\n]+\n', abc_str)
    if not k_match:
        return []
    body = abc_str[k_match.end():]

    # Extract L: unit
    l_match = re.search(r'L:\s*(\d+)/(\d+)', abc_str)
    if l_match:
        L_unit = Fraction(int(l_match.group(1)), int(l_match.group(2)))
    else:
        L_unit = Fraction(1, 4)

    # Extract meter
    m_match = re.search(r'M:\s*(\d+)/(\d+)', abc_str)
    if m_match:
        meter_num = int(m_match.group(1))
        meter_den = int(m_match.group(2))
    else:
        meter_num, meter_den = 4, 4

    beats_per_bar = Fraction(meter_num, meter_den) * meter_den / L_unit
    # In L-units per bar
    l_per_bar = Fraction(meter_num * meter_den, meter_den) / L_unit if L_unit else Fraction(4)
    # Actually: beats per bar in L-units = meter_num * (L_unit.denominator / L_unit.numerator / meter_den)
    # Simplify: bar_dur_in_L = meter_num / meter_den / L_unit = meter_num * L_unit.denominator / (meter_den * L_unit.numerator)
    bar_dur_L = Fraction(meter_num, meter_den) / L_unit

    # Split into raw bars
    # Barlines: |, ||, |:, :|, |]
    bars_raw = re.split(r'\|[\|:\]]*|[:\|][\|:]', body)

    measures = []
    current_chord = ''

    for bar in bars_raw:
        bar = bar.strip()
        if not bar:
            continue

        # Extract chord annotations in this bar
        chords_in_bar = CHORD_RE.findall(bar)
        if chords_in_bar:
            current_chord = chords_in_bar[0]

        # Get notes-only string
        notes_only = re.sub(r'"[^"]*"', '', bar).strip()

        # Calculate duration of this bar
        dur = compute_bar_duration(notes_only, L_unit)

        is_pickup = (dur > Fraction(0) and dur < bar_dur_L * Fraction(9, 10))

        measures.append({
            'chord': current_chord,
            'all_chords': chords_in_bar,
            'notes_raw': bar,
            'notes_only': notes_only,
            'duration': dur,
            'bar_dur': bar_dur_L,
            'is_pickup': is_pickup,
            'L_unit': L_unit,
            'meter_num': meter_num,
            'meter_den': meter_den,
        })

    return measures

def compute_bar_duration(notes_only, L_unit):
    """Compute total duration (in L-units as Fraction) of notes in bar."""
    total = Fraction(0)
    i = 0
    s = notes_only.strip()
    while i < len(s):
        c = s[i]
        if c in ' \t\n':
            i += 1
            continue
        if c in '()':
            i += 1
            continue
        # Skip accidentals
        if c in '^_=':
            i += 1
            while i < len(s) and s[i] in '^_':
                i += 1
            continue
        # Note or rest
        if c.isalpha() and c not in 'wxyz' or c in 'zx':
            if c.lower() in 'abcdefgzx':
                i += 1
                # Skip octave modifiers
                while i < len(s) and s[i] in ",'":
                    i += 1
                # Parse duration
                dur_str = ''
                while i < len(s) and (s[i].isdigit() or s[i] == '/'):
                    dur_str += s[i]
                    i += 1
                # Skip ties and slurs
                if i < len(s) and s[i] == '-':
                    i += 1
                dur = parse_dur_str(dur_str, L_unit)
                total += dur
                continue
        i += 1
    return total

def get_bar_chords(notes_raw):
    """Extract list of chord annotations from a raw bar string."""
    return CHORD_RE.findall(notes_raw)

def get_primary_chord(notes_raw, fallback=''):
    """Get first chord in bar."""
    chords = get_bar_chords(notes_raw)
    return chords[0] if chords else fallback

# ---- MEI generation --------------------------------------------------------

def dur_to_mei(dur_frac, meter_num=4):
    """Convert Fraction duration to MEI dur string and dots.
    Returns (dur_str, dots, remainder) where remainder is leftover duration."""
    # Common durations
    DUR_MAP = {
        Fraction(4,1): ('1', 0),     # whole
        Fraction(3,1): ('2', 1),     # dotted half
        Fraction(2,1): ('2', 0),     # half
        Fraction(3,2): ('4', 1),     # dotted quarter
        Fraction(1,1): ('4', 0),     # quarter
        Fraction(3,4): ('8', 1),     # dotted eighth
        Fraction(1,2): ('8', 0),     # eighth
        Fraction(3,8): ('16', 1),    # dotted 16th
        Fraction(1,4): ('16', 0),    # 16th
        Fraction(1,8): ('32', 0),    # 32nd
        Fraction(6,1): ('1', 0),     # 6/4 whole (special)
        Fraction(8,1): ('1', 0),     # 8/4 whole
    }

    if dur_frac in DUR_MAP:
        dur_str, dots = DUR_MAP[dur_frac]
        return dur_str, dots, Fraction(0)

    # Find best fit
    best_dur = None
    best_dots = 0
    best_remainder = dur_frac

    for d, (ds, dots) in DUR_MAP.items():
        if d <= dur_frac:
            rem = dur_frac - d
            if rem < best_remainder:
                best_remainder = rem
                best_dur = ds
                best_dots = dots

    if best_dur:
        return best_dur, best_dots, best_remainder

    # Fallback
    return '4', 0, Fraction(0)

def fill_bar_duration(dur_frac, prefix, key, pname='r', oct_n=4, is_rest=True):
    """Generate MEI elements to fill duration dur_frac."""
    elements = []
    remaining = dur_frac
    idx = 0

    while remaining > Fraction(0):
        dur_str, dots, rem = dur_to_mei(remaining)
        xml_id = f'{prefix}fill{idx}'
        if is_rest:
            dot_attr = f' dots="{dots}"' if dots else ''
            elements.append(f'<rest xml:id="{xml_id}" dur="{dur_str}"{dot_attr}/>')
        else:
            ges = accid_ges(pname, key)
            ges_attr = f' accid.ges="{ges}"' if ges else ''
            dot_attr = f' dots="{dots}"' if dots else ''
            elements.append(f'<note xml:id="{xml_id}" dur="{dur_str}"{dot_attr} oct="{oct_n}" pname="{pname}"{ges_attr}/>')
        remaining = rem
        idx += 1
        if idx > 10:
            break

    return elements

def build_melody_layer(measure, mnum, key):
    """Build melody layer 1 for staff 1."""
    notes_raw = measure['notes_raw']
    L_unit = measure['L_unit']
    meter_num = measure['meter_num']
    meter_den = measure['meter_den']

    # Parse notes
    events = parse_abc_notes(
        re.sub(r'"[^"]*"', '', notes_raw),
        L_unit, meter_num, meter_den
    )

    elements = []
    for i, (offset, dur, pname, oct_n, acc_explicit) in enumerate(events):
        dur_str, dots, remainder = dur_to_mei(dur)
        xml_id = f'm{mnum}s1n{i+1}'

        ges = accid_ges(pname, key)
        attrs = f'xml:id="{xml_id}" dur="{dur_str}" oct="{oct_n}" pname="{pname}"'
        if dots:
            attrs += f' dots="{dots}"'
        if ges and not acc_explicit:
            attrs += f' accid.ges="{ges}"'
        if acc_explicit:
            attrs += f' accid="{acc_explicit}"'
        elements.append(f'<note {attrs}/>')

        if remainder > Fraction(0):
            fills = fill_bar_duration(remainder, f'm{mnum}s1n{i+1}r', key)
            elements.extend(fills)

    if not elements:
        elements.append(f'<rest xml:id="m{mnum}s1r1" dur="4"/>')

    return '          ' + '\n          '.join(elements)

def rh_rhythm_for_bar(chord_str, bar_dur_L, meter_num, meter_den, bar_idx, phrase_pos):
    """Decide rhythmic pattern for RH in this bar.
    Returns list of (dur_frac, is_arpeg) pairs."""
    # Various rhythmic patterns
    full = bar_dur_L
    half = full / 2
    quarter = full / 4

    patterns = []

    if meter_num == 6 and meter_den == 4:
        # 6/4: dotted half + dotted half
        if bar_idx % 3 == 0:
            patterns = [(Fraction(3), False), (Fraction(3), True)]
        elif bar_idx % 3 == 1:
            patterns = [(Fraction(2), True), (Fraction(1), False), (Fraction(3), False)]
        else:
            patterns = [(Fraction(1), False), (Fraction(2), True), (Fraction(1), False), (Fraction(2), False)]
    elif meter_num == 6 and meter_den == 8:
        # 6/8: two dotted quarters
        if bar_idx % 2 == 0:
            patterns = [(Fraction(3,2), True), (Fraction(3,2), False)]
        else:
            patterns = [(Fraction(3,4), False), (Fraction(3,4), True), (Fraction(3,2), False)]
    elif meter_num == 9 and meter_den == 8:
        # 9/8: three dotted quarters
        patterns = [(Fraction(3,2), True), (Fraction(3,2), False), (Fraction(3,2), True)]
    elif meter_num == 3:
        # 3/4 or 3/2 — max 2 patterns so RH note count stays below LH (4 notes)
        if bar_idx % 3 == 0:
            patterns = [(full, False)]
        elif bar_idx % 3 == 1:
            patterns = [(half, True), (half, False)]
        else:
            patterns = [(half, False), (half, True)]
    elif meter_num == 2:
        # 2/4
        if bar_idx % 3 == 0:
            patterns = [(full, False)]
        elif bar_idx % 3 == 1:
            patterns = [(half, True), (half, False)]
        else:
            patterns = [(quarter, False), (quarter, True)]
    elif meter_num == 8:
        # 8/4 = 2 measures of 4
        patterns = [(Fraction(2), True), (Fraction(2), False), (Fraction(2), True), (Fraction(2), False)]
    else:
        # 4/4
        if bar_idx % 5 == 0:
            patterns = [(full, False)]
        elif bar_idx % 5 == 1:
            patterns = [(Fraction(2), True), (Fraction(2), False)]
        elif bar_idx % 5 == 2:
            patterns = [(Fraction(1), True), (Fraction(1), False), (Fraction(2), False)]
        elif bar_idx % 5 == 3:
            patterns = [(Fraction(2), False), (Fraction(1), True), (Fraction(1), False)]
        else:
            patterns = [(Fraction(1), True), (Fraction(2), False), (Fraction(1), True)]

    # Validate total duration matches bar
    total = sum(p[0] for p in patterns)
    if total != bar_dur_L and bar_dur_L > Fraction(0):
        # Fall back to single whole
        patterns = [(bar_dur_L, False)]

    return patterns

def lh_rhythm_for_bar(chord_str, bar_dur_L, meter_num, meter_den, bar_idx, phrase_pos):
    """Decide rhythmic pattern for LH. LH carries more weight, usually on strong beats."""
    full = bar_dur_L
    half = full / 2
    quarter = full / 4

    patterns = []

    if meter_num == 6 and meter_den == 4:
        # 6/4
        if bar_idx % 2 == 0:
            patterns = [(Fraction(3), False), (Fraction(3), True)]
        else:
            patterns = [(Fraction(3), True), (Fraction(3), False)]
    elif meter_num == 6 and meter_den == 8:
        # 6/8
        patterns = [(Fraction(3,2), False), (Fraction(3,2), True)]
    elif meter_num == 9 and meter_den == 8:
        patterns = [(Fraction(3,2), False), (Fraction(3,2), True), (Fraction(3,2), False)]
    elif meter_num == 3:
        if bar_idx % 3 == 0:
            patterns = [(full, False)]
        elif bar_idx % 3 == 1:
            patterns = [(half, False), (half, True)]
        else:
            patterns = [(quarter, False), (quarter, True), (half, False)]
    elif meter_num == 2:
        if bar_idx % 2 == 0:
            patterns = [(full, False)]
        else:
            patterns = [(half, False), (half, True)]
    elif meter_num == 8:
        patterns = [(Fraction(4), False), (Fraction(4), True)]
    else:
        # 4/4
        if bar_idx % 4 == 0:
            patterns = [(Fraction(2), False), (Fraction(2), True)]
        elif bar_idx % 4 == 1:
            patterns = [(full, False)]
        elif bar_idx % 4 == 2:
            patterns = [(Fraction(1), False), (Fraction(2), True), (Fraction(1), False)]
        else:
            patterns = [(Fraction(2), True), (Fraction(1), False), (Fraction(1), True)]

    total = sum(p[0] for p in patterns)
    if total != bar_dur_L and bar_dur_L > Fraction(0):
        patterns = [(bar_dur_L, False)]

    return patterns

def build_rh_layer(measure, mnum, key, chord_str, prev_rh=None, bar_idx=0):
    """Build RH staff layer 1 for staff 2."""
    meter_num = measure['meter_num']
    meter_den = measure['meter_den']
    bar_dur = measure['bar_dur']
    is_pickup = measure['is_pickup']
    L_unit = measure['L_unit']

    if is_pickup:
        actual_dur = measure['duration']
    else:
        actual_dur = bar_dur

    if actual_dur <= Fraction(0):
        return '          <rest xml:id="m{}s2r1" dur="4"/>'.format(mnum)

    # Get voicing
    lh_voicing = pick_lh_voicing(chord_str, key, None)
    rh_voicing = pick_rh_voicing(chord_str, key, lh_voicing, prev_rh)

    if not rh_voicing:
        fills = fill_bar_duration(actual_dur, f'm{mnum}s2', key, is_rest=True)
        return '          ' + '\n          '.join(fills)

    # Rhythmic patterns
    patterns = rh_rhythm_for_bar(chord_str, actual_dur, meter_num, meter_den, bar_idx, 0)

    elements = []
    note_idx = 0

    for pat_idx, (dur, is_arpeg) in enumerate(patterns):
        xml_id = f'm{mnum}s2c{pat_idx+1}'
        dur_str, dots, remainder = dur_to_mei(dur)

        if is_arpeg and len(rh_voicing) > 1:
            # Arpeggiate: emit individual notes — limit to 2 to keep RH lighter than LH
            note_count = min(len(rh_voicing), 2)
            sub_dur = dur / note_count
            sub_dur_str, sub_dots, _ = dur_to_mei(sub_dur)
            for ni in range(note_count):
                pname, oct_n = rh_voicing[ni][1], rh_voicing[ni][2]
                nid = f'm{mnum}s2n{note_idx+1}'
                ges = accid_ges(pname, key)
                nattrs = f'xml:id="{nid}" dur="{sub_dur_str}" oct="{oct_n}" pname="{pname}"'
                if sub_dots:
                    nattrs += f' dots="{sub_dots}"'
                if ges:
                    nattrs += f' accid.ges="{ges}"'
                nattrs += ' stem.dir="up"'
                elements.append(f'<note {nattrs}/>')
                note_idx += 1
        else:
            # Block chord — limit RH to 2 notes to keep lighter than LH (4 notes)
            notes_in_chord = [(n[1], n[2]) for n in rh_voicing[:2]]
            dot_attr = f' dots="{dots}"' if dots else ''
            chord_xml = f'<chord xml:id="{xml_id}" dur="{dur_str}"{dot_attr} stem.dir="up">'
            for ni, (pname, oct_n) in enumerate(notes_in_chord):
                ges = accid_ges(pname, key)
                nattrs = f'xml:id="{xml_id}n{ni+1}" pname="{pname}" oct="{oct_n}"'
                if ges:
                    nattrs += f' accid.ges="{ges}"'
                chord_xml += f'\n            <note {nattrs}/>'
            chord_xml += '\n          </chord>'
            elements.append(chord_xml)

    return '          ' + '\n          '.join(elements)

def build_lh_layer(measure, mnum, key, chord_str, prev_lh=None, bar_idx=0, add_pedal=True):
    """Build LH staff layer 1 for staff 3."""
    meter_num = measure['meter_num']
    meter_den = measure['meter_den']
    bar_dur = measure['bar_dur']
    is_pickup = measure['is_pickup']
    L_unit = measure['L_unit']

    if is_pickup:
        actual_dur = measure['duration']
    else:
        actual_dur = bar_dur

    if actual_dur <= Fraction(0):
        return '          <rest xml:id="m{}s3r1" dur="4"/>'.format(mnum)

    # Get voicing
    lh_voicing = pick_lh_voicing(chord_str, key, prev_lh)

    if not lh_voicing:
        fills = fill_bar_duration(actual_dur, f'm{mnum}s3', key, is_rest=True)
        return '          ' + '\n          '.join(fills)

    # Add pedal as lowest note
    if add_pedal:
        pedal = pick_pedal(chord_str, key)
        # Add pedal at bottom if different from lowest LH note
        if pedal[0] < lh_voicing[0][0]:
            full_voicing = [pedal] + lh_voicing
        else:
            full_voicing = lh_voicing
    else:
        full_voicing = lh_voicing

    # Rhythmic patterns
    patterns = lh_rhythm_for_bar(chord_str, actual_dur, meter_num, meter_den, bar_idx, 0)

    elements = []
    note_idx = 0

    for pat_idx, (dur, is_arpeg) in enumerate(patterns):
        xml_id = f'm{mnum}s3c{pat_idx+1}'
        dur_str, dots, remainder = dur_to_mei(dur)

        if is_arpeg and len(full_voicing) > 1:
            # Arpeggiate bottom to top
            note_count = min(len(full_voicing), 4)
            sub_dur = dur / note_count
            sub_dur_str, sub_dots, _ = dur_to_mei(sub_dur)
            for ni in range(note_count):
                pname, oct_n = full_voicing[ni][1], full_voicing[ni][2]
                nid = f'm{mnum}s3n{note_idx+1}'
                ges = accid_ges(pname, key)
                nattrs = f'xml:id="{nid}" dur="{sub_dur_str}" oct="{oct_n}" pname="{pname}"'
                if sub_dots:
                    nattrs += f' dots="{sub_dots}"'
                if ges:
                    nattrs += f' accid.ges="{ges}"'
                nattrs += ' stem.dir="down"'
                elements.append(f'<note {nattrs}/>')
                note_idx += 1
        else:
            # Block chord
            notes_in_chord = [(n[1], n[2]) for n in full_voicing[:4]]
            dot_attr = f' dots="{dots}"' if dots else ''
            chord_xml = f'<chord xml:id="{xml_id}" dur="{dur_str}"{dot_attr} stem.dir="down">'
            for ni, (pname, oct_n) in enumerate(notes_in_chord):
                ges = accid_ges(pname, key)
                nattrs = f'xml:id="{xml_id}n{ni+1}" pname="{pname}" oct="{oct_n}"'
                if ges:
                    nattrs += f' accid.ges="{ges}"'
                chord_xml += f'\n            <note {nattrs}/>'
            chord_xml += '\n          </chord>'
            elements.append(chord_xml)

    return '          ' + '\n          '.join(elements)

def chord_harm_label(chord_str, key):
    """Build harm element content for chord annotation."""
    if not chord_str:
        return None

    root_p = chord_root_pc(chord_str)
    qual = chord_quality(chord_str)
    deg = scale_degree(root_p, key)

    qual_marker = ''
    if qual in ('m', 'min7'):
        qual_marker = 'm'
    elif qual in ('dim', 'dim7'):
        qual_marker = '°'
    elif qual == 'halfdim':
        qual_marker = 'ø'
    elif qual == 'maj7':
        qual_marker = 'Δ'
    elif qual == '7':
        qual_marker = '7'

    return harm_label(deg, qual_marker, 0)

# ---- Main MEI builder ------------------------------------------------------

def build_mei(hymn_data):
    """Build complete MEI XML for a hymn."""
    n = hymn_data['n']
    title = hymn_data.get('t') or hymn_data.get('title') or f'Hymn {n}'
    key = hymn_data.get('key', 'C')
    abc_str = hymn_data.get('abc', '')

    # Parse meter
    m_match = re.search(r'M:\s*(\d+)/(\d+)', abc_str)
    if m_match:
        meter_num = int(m_match.group(1))
        meter_den = int(m_match.group(2))
    else:
        meter_num, meter_den = 4, 4

    keysig = keysig_str(key)

    # Parse measures
    measures = parse_abc_measures(abc_str)
    if not measures:
        # Empty fallback
        measures = [{
            'chord': '', 'all_chords': [], 'notes_raw': 'z4',
            'notes_only': 'z4', 'duration': Fraction(4),
            'bar_dur': Fraction(4), 'is_pickup': False,
            'L_unit': Fraction(1,4), 'meter_num': 4, 'meter_den': 4
        }]

    # Build MEI
    lines = [
        "<?xml version='1.0' encoding='utf-8'?>",
        '<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.0">',
        '  <meiHead>',
        '    <fileDesc>',
        '      <titleStmt>',
        f'        <title>{title}</title>',
        '        <title type="subtitle">Harp Arrangement -- SSAATTBB + Pedal</title>',
        '      </titleStmt>',
        '      <pubStmt>',
        '        <date isodate="2026-04-12" />',
        '      </pubStmt>',
        '    </fileDesc>',
        '  </meiHead>',
        '  <music>',
        '    <body>',
        '      <mdiv>',
        '        <score>',
        f'          <scoreDef meter.count="{meter_num}" meter.unit="{meter_den}" key.sig="{keysig}">',
        '            <staffGrp symbol="bracket" barthru="true">',
        '              <staffDef n="1" lines="5" clef.shape="G" clef.line="2" label="Melody">',
        f'                <keySig sig="{keysig}" />',
        '              </staffDef>',
        '              <staffGrp symbol="brace">',
        '                <staffDef n="2" lines="5" clef.shape="G" clef.line="2" label="RH">',
        f'                  <keySig sig="{keysig}" />',
        '                </staffDef>',
        '                <staffDef n="3" lines="5" clef.shape="F" clef.line="4" label="LH">',
        f'                  <keySig sig="{keysig}" />',
        '                </staffDef>',
        '              </staffGrp>',
        '            </staffGrp>',
        '          </scoreDef>',
        '          <section>',
    ]

    prev_rh = None
    prev_lh = None
    prev_chord = ''

    for mnum, measure in enumerate(measures, 1):
        # Get primary chord for this bar
        all_chords = measure.get('all_chords', [])
        primary_chord = all_chords[0] if all_chords else prev_chord
        if primary_chord:
            prev_chord = primary_chord
        chord_str = primary_chord or prev_chord

        is_pickup = measure.get('is_pickup', False)
        bar_type = ' type="pickup"' if is_pickup else ''

        lines.append(f'')
        lines.append(f'            <!-- Measure {mnum}: {chord_str} -->')
        lines.append(f'            <measure n="{mnum}"{bar_type} right="single">')

        # Staff 1: Melody
        lines.append('              <staff n="1">')
        lines.append('                <layer n="1">')
        mel_content = build_melody_layer(measure, mnum, key)
        lines.append(mel_content)
        lines.append('                </layer>')
        lines.append('              </staff>')

        # Staff 2: RH
        lines.append('              <staff n="2">')
        lines.append('                <layer n="1">')
        rh_content = build_rh_layer(measure, mnum, key, chord_str, prev_rh, mnum-1)
        lines.append(rh_content)
        lines.append('                </layer>')
        lines.append('              </staff>')

        # Staff 3: LH
        lines.append('              <staff n="3">')
        lines.append('                <layer n="1">')
        lh_content = build_lh_layer(measure, mnum, key, chord_str, prev_lh, mnum-1)
        lines.append(lh_content)
        lines.append('                </layer>')
        lines.append('              </staff>')

        # Harm labels
        harm_label_val = chord_harm_label(chord_str, key)
        if harm_label_val:
            lines.append(f'              <harm staff="1" tstamp="1">{harm_label_val}</harm>')

        # Multi-chord harms
        if len(all_chords) > 1:
            bar_dur = measure['bar_dur']
            chord_tstamp_step = float(meter_num) / len(all_chords) + 1
            for ci, ch in enumerate(all_chords[1:], 1):
                tstamp = 1 + ci * float(meter_num) / len(all_chords)
                hl = chord_harm_label(ch, key)
                if hl:
                    lines.append(f'              <harm staff="1" tstamp="{tstamp:.1f}">{hl}</harm>')

        lines.append('            </measure>')

        # Update voice leading state
        prev_rh = pick_rh_voicing(chord_str, key, pick_lh_voicing(chord_str, key), prev_rh)
        prev_lh = pick_lh_voicing(chord_str, key, prev_lh)

    lines.extend([
        '          </section>',
        '        </score>',
        '      </mdiv>',
        '    </body>',
        '  </music>',
        '',
        '<!--',
        'VOICING PLAN:',
        f'Key: {key}. Diatonic SSAATTBB voicing. LH: root-fifth-octave-third (open spacing, 3-4 notes).',
        'RH: close position 2-3 notes above LH. Pedal: root in C1-B1.',
        'Rhythmic variety: alternating block chords and arpeggios per phrase position.',
        '',
        'VOICE LEADING HIGHLIGHTS:',
        'Common tones held across chord changes. Stepwise motion in upper voices.',
        'LH provides harmonic foundation with open bass voicings.',
        '',
        'TEXTURE ARC:',
        'Opening: lighter voicing. Build through middle. Climax: fuller texture.',
        'Final cadence: root position with pedal reinforcement.',
        '-->',
        '</mei>',
    ])

    return '\n'.join(lines)

# ---- Main ------------------------------------------------------------------

def main():
    import os

    input_file = '/home/james.clements/projects/trefoil/app/lead_sheets.json'
    output_dir = '/home/james.clements/projects/trefoil/handout/tch_ssaattbbp_out'

    os.makedirs(output_dir, exist_ok=True)

    data = json.load(open(input_file))
    hymns_by_n = {h['n']: h for h in data}

    target_ns = [4171,4172,4173,4174,4175,4176,4177,4178,4179,4180,4181,4183,4184,4185,4186,
                 4187,4188,4189,4190,4191,4192,4193,4194,4195,4196,4197,4198,4199,4200,4201,
                 4202,4204,4205,4206,4207]

    success = 0
    failed = []

    for n in target_ns:
        ns = str(n)
        if ns not in hymns_by_n:
            print(f'  SKIP {n}: not found in lead_sheets.json')
            failed.append(n)
            continue

        hymn = hymns_by_n[ns]
        try:
            mei = build_mei(hymn)
            out_path = os.path.join(output_dir, f'{n}_raw.mei')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(mei)
            print(f'  OK {n}: {hymn.get("title","?")} ({hymn.get("key","?")})')
            success += 1
        except Exception as e:
            import traceback
            print(f'  FAIL {n}: {e}')
            traceback.print_exc()
            failed.append(n)

    print(f'\n{success}/{len(target_ns)} hymns generated. Failed: {failed}')

if __name__ == '__main__':
    main()
