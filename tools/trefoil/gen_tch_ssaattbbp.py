#!/usr/bin/env python3
"""
Generate pedal-harp SSAATTBB+P arrangements in MEI format.
3 staves: melody (staff 1), RH (staff 2), LH (staff 3).
ONE layer per staff per the caller's rules.
"""

import json, re, os, sys
from fractions import Fraction

# ──────────────────────────────────────────────────────────────────────
#  KEY SIGNATURES
# ──────────────────────────────────────────────────────────────────────
KEY_SIG = {
    'C':  '0',
    'G':  '1s', 'D': '2s', 'A': '3s', 'E': '4s',
    'F':  '1f', 'Bb': '2f', 'Eb': '3f', 'Ab': '4f',
}

# Diatonic scales (pitch classes 0=C, 2=D, 4=E, 5=F, 7=G, 9=A, 11=B)
SCALES = {
    'C':  [0,2,4,5,7,9,11],
    'G':  [0,2,4,7,9,11,6],   # F#
    'D':  [0,2,4,7,9,6,1],    # F# C#
    'A':  [0,2,4,7,6,1,3],    # F# C# G#
    'E':  [0,2,4,6,1,3,8],    # F# C# G# D#
    'F':  [0,2,4,5,7,9,10],   # Bb
    'Bb': [0,2,3,5,7,9,10],   # Bb Eb
    'Eb': [0,2,3,5,7,8,10],   # Bb Eb Ab
}

# Accidentals for each key, keyed by the NATURAL pitch class of the affected note letter.
# e.g. G key: F (natural pc=5) gets sharp -> {5:'s'}
# Bb key: B (natural pc=11) gets flat, E (natural pc=4) gets flat -> {11:'f', 4:'f'}
KEY_ACCID = {
    'C':  {},
    'G':  {5:'s'},          # F#
    'D':  {5:'s', 0:'s'},   # F# C# — wait, C natural pc=0; C# => {5:'s', 0:'s'}
    'A':  {5:'s', 0:'s', 7:'s'},   # F# C# G#
    'E':  {5:'s', 0:'s', 7:'s', 2:'s'},  # F# C# G# D#
    'F':  {11:'f'},          # Bb
    'Bb': {11:'f', 4:'f'},   # Bb Eb
    'Eb': {11:'f', 4:'f', 9:'f'},  # Bb Eb Ab
}

# Scale degree names (1-7) for each root PC in given key
def root_to_deg(root_pc, key):
    scale = SCALES[key]
    # normalize root_pc to 0-11
    root_pc = root_pc % 12
    try:
        idx = scale.index(root_pc)
        return idx + 1  # 1-7
    except ValueError:
        # Non-diatonic: find nearest
        for i, pc in enumerate(scale):
            if (pc - root_pc) % 12 <= 1 or (root_pc - pc) % 12 <= 1:
                return i + 1
        return 1  # fallback

# Circled digit labels
CIRCLED = {1:'①', 2:'②', 3:'③', 4:'④', 5:'⑤', 6:'⑥', 7:'⑦'}

# Chord quality from annotation string
def parse_chord(ann, key):
    """Parse ABC chord annotation (e.g. 'F', 'Bb', 'Gm', 'C7', 'F#°') into (root_pc, quality).
    Returns (deg, quality_str) in key context.
    quality: '' major, 'm' minor, '7' dom7, 'm7' min7, 'Δ' maj7, '°' dim, 'ø7' halfdim
    """
    ann = ann.strip()
    # Root name
    root_map = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    m = re.match(r'^([A-G])(b|#|♭|♯)?(.*)', ann)
    if not m:
        return (1, '')
    rname = m.group(1)
    acc   = m.group(2) or ''
    rest  = m.group(3) or ''

    root_pc = root_map[rname]
    if acc in ('#', '♯'):
        root_pc = (root_pc + 1) % 12
    elif acc in ('b', '♭'):
        root_pc = (root_pc - 1) % 12

    deg = root_to_deg(root_pc, key)

    quality = ''
    if rest in ('m', 'min'):
        quality = 'm'
    elif rest == '7':
        quality = '7'
    elif rest == 'm7':
        quality = 'm7'
    elif rest in ('M7', 'Δ', 'Maj7'):
        quality = 'Δ'
    elif rest in ('°', 'dim'):
        quality = '°'
    elif rest in ('ø7', 'ø', 'dim7'):
        quality = 'ø7'
    elif rest == 'aug':
        quality = '+'
    elif rest in ('sus2', 's2'):
        quality = 's2'
    elif rest in ('sus4', 's4'):
        quality = 's4'

    return (deg, quality)

def harm_label(deg, quality, inv=0):
    """Build circled-digit harm label with quality and inversion."""
    label = CIRCLED.get(deg, '①')
    if quality == 'm':
        label += 'm'
    elif quality == '7':
        label += '7'
    elif quality == 'm7':
        label += 'm7'
    elif quality == 'Δ':
        label += 'Δ'
    elif quality == '°':
        label += '°'
    elif quality == 'ø7':
        label += 'ø7'
    if inv:
        label += ['', '¹', '²', '³'][min(inv, 3)]
    return label

# ──────────────────────────────────────────────────────────────────────
#  ABC PARSING - extract bars with chord annotations
# ──────────────────────────────────────────────────────────────────────

def parse_abc_chords(abc):
    """Extract list of bars, each bar is list of (tstamp, chord_str)."""
    lines = abc.split('\n')
    meter = '4/4'
    lunit_str = '1/4'
    body_lines = []
    past_key = False
    for l in lines:
        if l.startswith('M:'):
            meter = l[2:].strip()
        elif l.startswith('L:'):
            lunit_str = l[2:].strip()
        elif l.startswith('K:'):
            past_key = True
        elif past_key and l.strip() and not l.startswith('%'):
            body_lines.append(l.strip())

    body = ' '.join(body_lines)
    # Remove trailing |]
    body = re.sub(r'\|\]$', '', body.strip())

    # Parse meter
    mn, md = [int(x) for x in meter.split('/')]
    # L unit as fraction of quarter note
    lu_n, lu_d = [int(x) for x in lunit_str.split('/')]
    # 1 L unit = lu_n/lu_d whole note = (lu_n/lu_d)*4 quarter notes
    l_in_quarters = Fraction(lu_n, lu_d) * 4  # quarter note units per L

    beats_per_bar = Fraction(mn, md) * 4  # quarter notes per bar

    bars_raw = [b.strip() for b in re.split(r'\|', body) if b.strip()]

    result = []
    for bar in bars_raw:
        # Find chord annotations and their positions in the bar
        chords_in_bar = []
        beat = Fraction(0)
        i = 0
        s = bar
        # Walk through bar tokens
        tokens = tokenize_abc_bar(s)
        cur_chord = None
        cur_beat = Fraction(0)
        for tok in tokens:
            if tok.startswith('CHORD:'):
                cur_chord = tok[6:]
                chords_in_bar.append((cur_beat + Fraction(1), cur_chord))
                # beats are 1-indexed
            elif tok.startswith('DUR:'):
                dur = Fraction(*[int(x) for x in tok[4:].split('/')])
                cur_beat += dur * l_in_quarters

        result.append({
            'chords': chords_in_bar,
            'beats_per_bar': beats_per_bar,
        })

    return beats_per_bar, result

def tokenize_abc_bar(bar):
    """Walk ABC bar and yield CHORD: and DUR: tokens."""
    tokens = []
    i = 0
    while i < len(bar):
        c = bar[i]
        if c == '"':
            # Find end of string
            j = bar.index('"', i+1)
            s = bar[i+1:j]
            if s.startswith('^'):
                tokens.append('CHORD:' + s[1:])
            i = j + 1
        elif c in 'abcdefgABCDEFGz':
            # Note: parse duration
            i, dur = parse_note_dur(bar, i)
            tokens.append(f'DUR:{dur.numerator}/{dur.denominator}')
        elif c == '[':
            # chord cluster
            j = bar.index(']', i)
            inner = bar[i+1:j]
            # get duration of first note
            k = 0
            while k < len(inner) and inner[k] not in 'abcdefgABCDEFG':
                k += 1
            if k < len(inner):
                _, dur = parse_note_dur(inner, k)
                tokens.append(f'DUR:{dur.numerator}/{dur.denominator}')
            i = j + 1
        elif c == '(':
            # tuplet marker - skip
            # (3 or (3:2:3 etc
            j = i + 1
            while j < len(bar) and (bar[j].isdigit() or bar[j] in ':'):
                j += 1
            i = j
        else:
            i += 1
    return tokens

def parse_note_dur(bar, i):
    """Parse duration starting at note character at position i. Returns (new_i, Fraction)."""
    i += 1  # skip note name
    # optional octave markers
    while i < len(bar) and bar[i] in "',":
        i += 1
    # duration
    num = ''
    while i < len(bar) and bar[i].isdigit():
        num += bar[i]
        i += 1
    has_slash = False
    if i < len(bar) and bar[i] == '/':
        has_slash = True
        i += 1
    den = ''
    while i < len(bar) and bar[i].isdigit():
        den += bar[i]
        i += 1
    # dots
    dots = 0
    while i < len(bar) and bar[i] == '.':
        dots += 1
        i += 1

    # Build fraction
    if num and not has_slash:
        f = Fraction(int(num), 1)
    elif has_slash and den:
        f = Fraction(int(num) if num else 1, int(den))
    elif has_slash and not den:
        f = Fraction(1, 2)  # just "/"
    else:
        f = Fraction(1, 1)  # no modifier = 1 L

    # Apply dots
    for d in range(dots):
        f = f * Fraction(3, 2) if d == 0 else f * Fraction(7, 4) if d == 1 else f

    return i, f

# ──────────────────────────────────────────────────────────────────────
#  PITCH UTILITIES
# ──────────────────────────────────────────────────────────────────────

# MIDI note from pname+oct
PNAME_PC = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}

def midi(pname, oct, acc=0):
    return (oct+1)*12 + PNAME_PC[pname.lower()] + acc

def pname_from_midi(m, key):
    """Return (pname, oct, accid_ges) for midi note in given key."""
    oct = (m // 12) - 1
    pc = m % 12
    scale = SCALES[key]
    key_accid = KEY_ACCID[key]
    if pc in scale:
        # Find pname
        for pname, bpc in PNAME_PC.items():
            adj = key_accid.get(bpc, None)
            actual = (bpc + (1 if adj == 's' else -1 if adj == 'f' else 0)) % 12
            if actual == pc:
                return pname, oct, None  # key sig handles it
        # fallback: find nearest natural
    # Try to find nearest diatonic pitch
    # search up and down
    for delta in [0,1,-1,2,-2,3,-3,4,-4,5,-5,6]:
        cpc = (pc + delta) % 12
        for pname, bpc in PNAME_PC.items():
            adj = key_accid.get(bpc, None)
            actual = (bpc + (1 if adj == 's' else -1 if adj == 'f' else 0)) % 12
            if actual == cpc:
                o = oct + (1 if pc + delta > 11 else (-1 if pc + delta < 0 else 0))
                return pname, o, None
    # absolute fallback
    for pname, bpc in PNAME_PC.items():
        if bpc == pc:
            return pname, oct, None
    return 'c', oct, None

def diatonic_notes_in_range(key, low_midi, high_midi):
    """Return sorted list of MIDI values of diatonic notes in [low_midi, high_midi]."""
    scale = SCALES[key]
    key_accid = KEY_ACCID[key]
    result = []
    for m_val in range(low_midi, high_midi+1):
        pc = m_val % 12
        if pc in scale:
            result.append(m_val)
    return result

# Scale degrees of diatonic notes
def scale_degree_of_midi(m_val, key):
    scale = SCALES[key]
    pc = m_val % 12
    if pc in scale:
        return scale.index(pc) + 1
    return None

# ──────────────────────────────────────────────────────────────────────
#  CHORD VOICING ENGINE
# ──────────────────────────────────────────────────────────────────────

# Chord tones by degree and quality (as scale degrees relative to key)
def chord_tones(deg, quality, key):
    """Return list of diatonic scale degrees (1-7) in the chord."""
    scale = SCALES[key]
    # degree indices (0-based)
    idx = deg - 1

    def scale_deg(steps_up):
        return ((idx + steps_up) % 7) + 1

    root = scale_deg(0)
    third = scale_deg(2)
    fifth = scale_deg(4)
    seventh = scale_deg(6)

    if quality in ('', 'major', '°', '+', 's2', 's4'):
        if quality == 's2':
            return [root, scale_deg(1), fifth]
        if quality == 's4':
            return [root, scale_deg(3), fifth]
        return [root, third, fifth]
    elif quality == 'm':
        return [root, third, fifth]  # diatonic minor
    elif quality == '7':
        return [root, third, fifth, seventh]
    elif quality == 'm7':
        return [root, third, fifth, seventh]
    elif quality == 'Δ':
        return [root, third, fifth, seventh]
    elif quality == 'ø7':
        return [root, third, fifth, seventh]
    elif quality == '°':
        return [root, third, fifth]
    else:
        return [root, third, fifth]

def midi_notes_for_chord(deg, quality, key, rh_range=(60, 84), lh_range=(36, 60)):
    """Return (rh_notes_midi, lh_notes_midi) for a chord voicing.
    RH: 2-3 notes in treble (C4-C6), LH: 3-4 notes in bass (C2-B3).
    """
    tones = chord_tones(deg, quality, key)  # list of scale degrees
    scale = SCALES[key]

    def deg_to_pc(d):
        return scale[(d-1) % 7]

    tone_pcs = [deg_to_pc(t) for t in tones]

    # Get all diatonic notes in range that match chord tones
    rh_diatonic = diatonic_notes_in_range(key, rh_range[0], rh_range[1])
    lh_diatonic = diatonic_notes_in_range(key, lh_range[0], lh_range[1])

    rh_chord = [m for m in rh_diatonic if m % 12 in tone_pcs]
    lh_chord = [m for m in lh_diatonic if m % 12 in tone_pcs]

    return rh_chord, lh_chord

# ──────────────────────────────────────────────────────────────────────
#  VOICING SELECTOR — picks best notes for each hand
# ──────────────────────────────────────────────────────────────────────

def pick_rh_notes(chord_midis, prev_rh=None, n_notes=2):
    """Pick 2-3 RH notes from available chord midis, with voice leading from prev."""
    if not chord_midis:
        return []

    # Sort ascending
    available = sorted(chord_midis)

    if len(available) <= n_notes:
        return available

    if prev_rh:
        # Pick notes closest to previous position
        target = sum(prev_rh) / len(prev_rh)
        # Find n_notes consecutive notes closest to target
        best = None
        best_dist = float('inf')
        for i in range(len(available) - n_notes + 1):
            grp = available[i:i+n_notes]
            center = sum(grp) / len(grp)
            dist = abs(center - target)
            if dist < best_dist:
                best_dist = dist
                best = grp
        return best if best else available[:n_notes]
    else:
        # Default: middle of range
        mid_idx = len(available) // 2
        start = max(0, mid_idx - n_notes // 2)
        return available[start:start+n_notes]

def pick_lh_notes(chord_midis, prev_lh=None, n_notes=3):
    """Pick 3-4 LH notes with open bass voicing (P4/P5 at bottom)."""
    if not chord_midis:
        return []

    available = sorted(chord_midis)

    if len(available) <= n_notes:
        return available

    if prev_lh:
        target = sum(prev_lh) / len(prev_lh)
        best = None
        best_dist = float('inf')
        for i in range(len(available) - n_notes + 1):
            grp = available[i:i+n_notes]
            center = sum(grp) / len(grp)
            dist = abs(center - target)
            if dist < best_dist:
                best_dist = dist
                best = grp
        # Verify open bass voicing (at least a 4th between bottom notes)
        if best and len(best) >= 2:
            if best[1] - best[0] < 4:
                # Try to get a wider voicing
                for grp in [available[i:i+n_notes] for i in range(len(available)-n_notes+1)]:
                    if grp[1] - grp[0] >= 4:
                        return grp
        return best if best else available[:n_notes]
    else:
        # Default: bottom notes widely spaced (open voicing)
        # Try to get root + 5th + octave type spacing
        if len(available) >= 3:
            # Pick with wide bass
            for i in range(len(available)):
                for j in range(i+1, len(available)):
                    interval = available[j] - available[i]
                    if 5 <= interval <= 8:  # P4 to P5
                        # Found a good bass pair, now pick top note
                        if j + 1 < len(available):
                            return [available[i], available[j], available[j+1]]
                        elif j > 0:
                            return [available[i], available[j], available[j]]
        return available[:n_notes]

# ──────────────────────────────────────────────────────────────────────
#  MEI NOTE RENDERING
# ──────────────────────────────────────────────────────────────────────

def dur_to_mei(beats):
    """Convert beat count (quarter notes) to MEI dur + dots."""
    # Common durations
    dur_map = {
        Fraction(4,1): ('1', 0),
        Fraction(3,1): ('2', 1),
        Fraction(2,1): ('2', 0),
        Fraction(3,2): ('4', 1),
        Fraction(1,1): ('4', 0),
        Fraction(3,4): ('8', 1),
        Fraction(1,2): ('8', 0),
        Fraction(1,4): ('16', 0),
        Fraction(1,8): ('32', 0),
        Fraction(6,1): ('1', 1),
        Fraction(8,1): ('breve', 0),
    }
    beats_f = Fraction(beats).limit_denominator(16)
    if beats_f in dur_map:
        return dur_map[beats_f]
    # Try closest
    closest = min(dur_map.keys(), key=lambda k: abs(k - beats_f))
    return dur_map[closest]

def render_note_xml(mid_id, m, key, dur_beats, stem_dir=None, tie_start=False, tie_end=False):
    """Render a single MEI <note> element."""
    pname, oct, _ = pname_from_midi(m, key)
    dur, dots = dur_to_mei(dur_beats)

    pc = m % 12
    key_accid = KEY_ACCID[key]
    # accid.ges needed if key has accidental at this pc
    pname_pc = PNAME_PC[pname.lower()]
    accid_ges = key_accid.get(pname_pc, None)

    attrs = f'xml:id="{mid_id}" dur="{dur}"'
    if dots:
        attrs += f' dots="{dots}"'
    attrs += f' oct="{oct}" pname="{pname}"'
    if accid_ges:
        attrs += f' accid.ges="{accid_ges}"'
    if stem_dir:
        attrs += f' stem.dir="{stem_dir}"'
    if tie_start and tie_end:
        attrs += ' tie="m"'
    elif tie_start:
        attrs += ' tie="i"'
    elif tie_end:
        attrs += ' tie="t"'

    return f'<note {attrs}/>'

def render_chord_xml(mid_id, notes_midi, key, dur_beats, stem_dir=None):
    """Render a MEI <chord> with multiple notes."""
    if not notes_midi:
        return ''
    if len(notes_midi) == 1:
        return render_note_xml(mid_id + 'n0', notes_midi[0], key, dur_beats, stem_dir)

    dur, dots = dur_to_mei(dur_beats)
    attrs = f'xml:id="{mid_id}" dur="{dur}"'
    if dots:
        attrs += f' dots="{dots}"'
    if stem_dir:
        attrs += f' stem.dir="{stem_dir}"'

    inner = ''
    for i, m in enumerate(sorted(notes_midi)):
        pname, oct, _ = pname_from_midi(m, key)
        pc = m % 12
        key_accid = KEY_ACCID[key]
        pname_pc = PNAME_PC[pname.lower()]
        accid_ges = key_accid.get(pname_pc, None)
        note_attrs = f'xml:id="{mid_id}n{i}" pname="{pname}" oct="{oct}"'
        if accid_ges:
            note_attrs += f' accid.ges="{accid_ges}"'
        inner += f'<note {note_attrs}/>'

    return f'<chord {attrs}>{inner}</chord>'

def render_rest_xml(mid_id, dur_beats):
    """Render a MEI <rest>."""
    dur, dots = dur_to_mei(dur_beats)
    attrs = f'xml:id="{mid_id}" dur="{dur}"'
    if dots:
        attrs += f' dots="{dots}"'
    return f'<rest {attrs}/>'

# ──────────────────────────────────────────────────────────────────────
#  ABC MELODY PARSER — convert ABC notes to MEI
# ──────────────────────────────────────────────────────────────────────

# ABC note to MIDI
ABC_NOTE_PC = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11,
               'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}
# Octave: uppercase = oct 4 (C4=60), lowercase = oct 5 in ABC (c'=C5)
# In ABC: C,=C3 C=C4 c=C5 c'=C6
ABC_BASE_OCT = {'C':4,'D':4,'E':4,'F':4,'G':4,'A':4,'B':4,
                'c':5,'d':5,'e':5,'f':5,'g':5,'a':5,'b':5}

def abc_note_to_midi_dur(token, key, prev_accid={}):
    """Parse an ABC note token like 'A', 'A3/2', '^F', '_B,' etc.
    Returns (midi, duration_in_L_units, accid_type).
    accid_type: None, 's', 'f', 'n'
    """
    i = 0
    accid = None
    if i < len(token) and token[i] in '^_=':
        if token[i] == '^':
            accid = 's'
        elif token[i] == '_':
            accid = 'f'
        elif token[i] == '=':
            accid = 'n'
        i += 1
        if i < len(token) and token[i] in '^_':
            # double sharp/flat
            if token[i] == '^':
                accid = 'ss'
            elif token[i] == '_':
                accid = 'ff'
            i += 1

    if i >= len(token) or token[i] not in 'ABCDEFGabcdefgz':
        return None, Fraction(1), None

    note_char = token[i]
    i += 1

    # Octave modifiers
    oct_adj = 0
    while i < len(token) and token[i] == "'":
        oct_adj += 1
        i += 1
    while i < len(token) and token[i] == ',':
        oct_adj -= 1
        i += 1

    # Duration
    num = ''
    while i < len(token) and token[i].isdigit():
        num += token[i]
        i += 1
    has_slash = False
    if i < len(token) and token[i] == '/':
        has_slash = True
        i += 1
    den = ''
    while i < len(token) and token[i].isdigit():
        den += token[i]
        i += 1
    # dots (broken rhythm markers < > )
    # We ignore broken rhythm for now

    if note_char == 'z':
        return None, Fraction(int(num) if num else 1, int(den) if den else (2 if has_slash else 1)), None

    pc = ABC_NOTE_PC[note_char]
    base_oct = ABC_BASE_OCT[note_char]
    oct = base_oct + oct_adj

    # Apply accidental
    if accid == 's':
        pc_adj = 1
    elif accid == 'f':
        pc_adj = -1
    elif accid == 'n':
        pc_adj = 0  # natural - cancel key sig
    else:
        # Apply key sig
        key_accid = KEY_ACCID[key]
        pname_base = PNAME_PC.get(note_char.lower(), 0)
        if pname_base in key_accid:
            if key_accid[pname_base] == 's':
                pc_adj = 1
            elif key_accid[pname_base] == 'f':
                pc_adj = -1
            else:
                pc_adj = 0
        else:
            pc_adj = 0

    midi_val = (oct + 1) * 12 + pc + pc_adj

    # Duration fraction (in L units)
    if num and not has_slash:
        dur = Fraction(int(num))
    elif has_slash and den:
        dur = Fraction(int(num) if num else 1, int(den))
    elif has_slash and not den:
        dur = Fraction(1, 2)
    else:
        dur = Fraction(1)

    return midi_val, dur, accid

def parse_abc_bar_notes(bar_str, key, l_in_q):
    """Parse ABC bar into list of (midi_or_None, dur_in_quarters, is_rest, accid)."""
    notes = []
    i = 0
    s = bar_str
    n = len(s)

    # Remove chord annotations
    s_clean = re.sub(r'"[^"]*"', '', s)

    i = 0
    while i < len(s_clean):
        c = s_clean[i]
        if c in '^\\_=':
            # accidental + note
            j = i
            while j < len(s_clean) and s_clean[j] in '^\\_=':
                j += 1
            if j < len(s_clean) and s_clean[j] in 'ABCDEFGabcdefg':
                tok = s_clean[i:j+10]  # grab note + duration
                midi_v, dur, accid = abc_note_to_midi_dur(tok, key)
                dur_q = dur * l_in_q
                notes.append((midi_v, dur_q, False, accid))
                # Advance i past note
                i = j + 1
                while i < len(s_clean) and s_clean[i] in "',":
                    i += 1
                while i < len(s_clean) and s_clean[i].isdigit():
                    i += 1
                if i < len(s_clean) and s_clean[i] == '/':
                    i += 1
                    while i < len(s_clean) and s_clean[i].isdigit():
                        i += 1
            else:
                i += 1
        elif c in 'ABCDEFGabcdefg':
            tok = s_clean[i:]
            midi_v, dur, accid = abc_note_to_midi_dur(tok, key)
            dur_q = dur * l_in_q
            notes.append((midi_v, dur_q, False, accid))
            i += 1
            while i < len(s_clean) and s_clean[i] in "',":
                i += 1
            while i < len(s_clean) and s_clean[i].isdigit():
                i += 1
            if i < len(s_clean) and s_clean[i] == '/':
                i += 1
                while i < len(s_clean) and s_clean[i].isdigit():
                    i += 1
        elif c == 'z' or c == 'x':
            tok = s_clean[i:]
            _, dur, _ = abc_note_to_midi_dur(tok, key)
            dur_q = dur * l_in_q
            notes.append((None, dur_q, True, None))
            i += 1
            while i < len(s_clean) and s_clean[i].isdigit():
                i += 1
            if i < len(s_clean) and s_clean[i] == '/':
                i += 1
                while i < len(s_clean) and s_clean[i].isdigit():
                    i += 1
        elif c == '[':
            # chord cluster - take first note pitch, sum of durations
            j = s_clean.index(']', i) if ']' in s_clean[i:] else len(s_clean)
            inner = s_clean[i+1:j]
            # First note
            first_midi = None
            total_dur = None
            for m in re.finditer(r'([A-Ga-gz])([0-9]*)(/?)([0-9]*)', inner):
                nc = m.group(1)
                if nc in 'ABCDEFGabcdefg':
                    tok = inner[m.start():]
                    midi_v, dur, accid = abc_note_to_midi_dur(tok, key)
                    if first_midi is None:
                        first_midi = midi_v
                        total_dur = dur
                    break
            if total_dur:
                dur_q = total_dur * l_in_q
                notes.append((first_midi, dur_q, False, None))
            i = j + 1
        elif c == '(':
            # tuplet
            j = i + 1
            while j < len(s_clean) and (s_clean[j].isdigit() or s_clean[j] in ':'):
                j += 1
            i = j
        elif c in '-':
            # tie marker - skip
            i += 1
        else:
            i += 1

    return notes

def abc_note_midi_from_bar(bar_str, key):
    """Quick parse - just get first melody note's midi for pitch reference."""
    clean = re.sub(r'"[^"]*"', '', bar_str)
    for m in re.finditer(r'([=^_]?)([A-Ga-g])([,\']*)', clean):
        acc, nc, oct_mods = m.groups()
        if nc not in 'ABCDEFGabcdefg':
            continue
        pc = ABC_NOTE_PC[nc]
        base_oct = ABC_BASE_OCT[nc]
        oct = base_oct
        for ch in oct_mods:
            if ch == "'": oct += 1
            elif ch == ',': oct -= 1
        key_accid = KEY_ACCID[key]
        pname_pc_val = PNAME_PC.get(nc.lower(), 0)
        pc_adj = 0
        if acc == '^': pc_adj = 1
        elif acc == '_': pc_adj = -1
        elif acc == '=': pc_adj = 0
        elif pname_pc_val in key_accid:
            pc_adj = 1 if key_accid[pname_pc_val] == 's' else -1
        midi_v = (oct + 1)*12 + pc + pc_adj
        return midi_v
    return 60

# ──────────────────────────────────────────────────────────────────────
#  MELODY PARSER — convert ABC body to MEI staff 1 notes
# ──────────────────────────────────────────────────────────────────────

def abc_to_mei_melody(abc_body, key, l_in_q, measure_num, beats_per_bar):
    """Convert a single ABC bar to MEI <layer n="1"> content for melody staff."""
    xml_id_prefix = f'm{measure_num}s1'

    # Clean: remove chord annotations
    clean = re.sub(r'"[^"]*"', '', abc_body).strip()

    # Parse tokens manually
    result_notes = []
    i = 0
    note_idx = 0

    def advance_dur(s, i):
        """From position i (past note name), parse octave/duration modifiers. Returns (new_i, dur_frac)."""
        # Octave
        while i < len(s) and s[i] in "',":
            i += 1
        # Duration
        num = ''
        while i < len(s) and s[i].isdigit():
            num += s[i]
            i += 1
        slash = False
        if i < len(s) and s[i] == '/':
            slash = True
            i += 1
        den = ''
        while i < len(s) and s[i].isdigit():
            den += s[i]
            i += 1
        # Dots (broken rhythm)
        while i < len(s) and s[i] in '<>':
            i += 1

        if num and not slash:
            dur = Fraction(int(num))
        elif slash and den:
            dur = Fraction(int(num) if num else 1, int(den))
        elif slash:
            dur = Fraction(1, 2)
        else:
            dur = Fraction(1)
        return i, dur

    while i < len(clean):
        c = clean[i]

        if c in '([':
            if c == '(':
                # tuplet: (3 or (3:2:3
                i += 1
                while i < len(clean) and (clean[i].isdigit() or clean[i] in ':'):
                    i += 1
                continue
            else:
                # Chord cluster
                j = clean.find(']', i)
                if j < 0: j = len(clean)
                inner = clean[i+1:j]
                # Take first note
                first = None
                first_dur = Fraction(1)
                ii = 0
                while ii < len(inner):
                    ic = inner[ii]
                    if ic in '^_=':
                        ii += 1
                        continue
                    if ic in 'ABCDEFGabcdefgz':
                        midi_v, dur, accid = abc_note_to_midi_dur(inner[ii:], key)
                        first = midi_v
                        first_dur = dur
                        break
                    ii += 1
                # external duration after ]
                i = j + 1
                ext_num = ''
                while i < len(clean) and clean[i].isdigit():
                    ext_num += clean[i]
                    i += 1
                ext_slash = False
                if i < len(clean) and clean[i] == '/':
                    ext_slash = True
                    i += 1
                ext_den = ''
                while i < len(clean) and clean[i].isdigit():
                    ext_den += clean[i]
                    i += 1
                if ext_num and not ext_slash:
                    first_dur = Fraction(int(ext_num))
                elif ext_slash and ext_den:
                    first_dur = Fraction(int(ext_num) if ext_num else 1, int(ext_den))
                elif ext_slash:
                    first_dur = Fraction(1, 2)

                dur_q = first_dur * l_in_q
                if first is not None:
                    result_notes.append(('note', first, dur_q, None))
                else:
                    result_notes.append(('rest', None, dur_q, None))
                note_idx += 1
                continue

        if c in '^_=':
            acc_str = ''
            while i < len(clean) and clean[i] in '^_=':
                acc_str += clean[i]
                i += 1
            if i < len(clean) and clean[i] in 'ABCDEFGabcdefg':
                accid_char = acc_str[-1]
                midi_v, dur, accid = abc_note_to_midi_dur(acc_str + clean[i:], key)
                i2, dur2 = advance_dur(clean, i+1)
                dur_q = dur2 * l_in_q
                # Determine explicit accid for MEI
                key_acc = KEY_ACCID[key]
                pn = PNAME_PC.get(clean[i].lower(), 0)
                explicit_accid = None
                if accid_char == '^':
                    if key_acc.get(pn) != 's':
                        explicit_accid = 's'
                elif accid_char == '_':
                    if key_acc.get(pn) != 'f':
                        explicit_accid = 'f'
                elif accid_char == '=':
                    if pn in key_acc:
                        explicit_accid = 'n'
                result_notes.append(('note', midi_v, dur_q, explicit_accid))
                i = i2
                note_idx += 1
            else:
                i += 1
            continue

        if c in 'ABCDEFGabcdefg':
            midi_v, dur, accid = abc_note_to_midi_dur(clean[i:], key)
            i2, dur2 = advance_dur(clean, i+1)
            dur_q = dur2 * l_in_q
            result_notes.append(('note', midi_v, dur_q, None))
            i = i2
            note_idx += 1
            continue

        if c in 'zx':
            _, dur, _ = abc_note_to_midi_dur(clean[i:], key)
            i2, dur2 = advance_dur(clean, i+1)
            dur_q = dur2 * l_in_q
            result_notes.append(('rest', None, dur_q, None))
            i = i2
            note_idx += 1
            continue

        if c == '-':
            # tie - skip
            i += 1
            continue

        i += 1

    # Now render to MEI
    xml_parts = []
    for idx, (ntype, midi_v, dur_q, explicit_accid) in enumerate(result_notes):
        nid = f'{xml_id_prefix}n{idx+1}'
        if ntype == 'rest' or midi_v is None:
            xml_parts.append('          ' + render_rest_xml(nid, dur_q))
        else:
            pname, oct, _ = pname_from_midi(midi_v, key)
            dur, dots = dur_to_mei(dur_q)
            pc = midi_v % 12
            key_accid = KEY_ACCID[key]
            pname_pc_val = PNAME_PC.get(pname.lower(), 0)
            accid_ges = key_accid.get(pname_pc_val, None)

            attrs = f'xml:id="{nid}" dur="{dur}"'
            if dots:
                attrs += f' dots="{dots}"'
            attrs += f' oct="{oct}" pname="{pname}"'
            if accid_ges:
                attrs += f' accid.ges="{accid_ges}"'
            if explicit_accid:
                attrs += f' accid="{explicit_accid}"'
                if explicit_accid == 'n':
                    # natural overrides key sig
                    pass
                else:
                    # explicit accidental overrides accid.ges
                    attrs = attrs.replace(f' accid.ges="{accid_ges}"', '')
                    attrs += f' accid.ges="{explicit_accid}"'

            xml_parts.append(f'          <note {attrs}/>')

    return '\n'.join(xml_parts)

# ──────────────────────────────────────────────────────────────────────
#  HARM LABEL EXTRACTION FROM ABC
# ──────────────────────────────────────────────────────────────────────

def extract_harms(bar_str, key, l_in_q, beats_per_bar):
    """Extract chord annotations with tstamp from ABC bar.
    Returns list of (tstamp_float, deg, quality).
    """
    harms = []
    beat = Fraction(0)

    # Walk through bar tokens in order
    i = 0
    while i < len(bar_str):
        c = bar_str[i]
        if c == '"':
            j = bar_str.index('"', i+1)
            ann = bar_str[i+1:j]
            if ann.startswith('^'):
                chord_ann = ann[1:]
                tstamp = float(beat + 1)  # 1-indexed
                deg, quality = parse_chord(chord_ann, key)
                harms.append((tstamp, deg, quality))
            i = j + 1
        elif c in '^_=':
            # accidental + note
            while i < len(bar_str) and bar_str[i] in '^_=':
                i += 1
            if i < len(bar_str) and bar_str[i] in 'ABCDEFGabcdefgz':
                tok = bar_str[i:]
                _, dur, _ = abc_note_to_midi_dur(tok, key)
                beat += dur * l_in_q
                i += 1
                while i < len(bar_str) and bar_str[i] in "',":
                    i += 1
                while i < len(bar_str) and bar_str[i].isdigit():
                    i += 1
                if i < len(bar_str) and bar_str[i] == '/':
                    i += 1
                    while i < len(bar_str) and bar_str[i].isdigit():
                        i += 1
        elif c in 'ABCDEFGabcdefgz':
            tok = bar_str[i:]
            _, dur, _ = abc_note_to_midi_dur(tok, key)
            beat += dur * l_in_q
            i += 1
            while i < len(bar_str) and bar_str[i] in "',":
                i += 1
            while i < len(bar_str) and bar_str[i].isdigit():
                i += 1
            if i < len(bar_str) and bar_str[i] == '/':
                i += 1
                while i < len(bar_str) and bar_str[i].isdigit():
                    i += 1
        elif c == '[':
            j = bar_str.find(']', i)
            if j < 0: j = len(bar_str)
            inner = bar_str[i+1:j]
            dur = Fraction(1)
            for m in re.finditer(r'([A-Ga-gz])', inner):
                tok = inner[m.start():]
                _, dur, _ = abc_note_to_midi_dur(tok, key)
                break
            beat += dur * l_in_q
            i = j + 1
        elif c == '(':
            i += 1
            while i < len(bar_str) and (bar_str[i].isdigit() or bar_str[i] in ':'):
                i += 1
        else:
            i += 1

    return harms

# ──────────────────────────────────────────────────────────────────────
#  FULL ARRANGEMENT GENERATOR
# ──────────────────────────────────────────────────────────────────────

def generate_arrangement(hymn):
    """Generate full MEI arrangement for one hymn."""
    n = hymn['n']
    title = hymn['t']
    key = hymn['key']
    abc = hymn['abc']

    # Parse ABC header
    lines = abc.split('\n')
    meter = '4/4'
    lunit_str = '1/4'
    body_lines = []
    past_key = False
    for l in lines:
        if l.startswith('M:'):
            meter = l[2:].strip()
        elif l.startswith('L:'):
            lunit_str = l[2:].strip()
        elif l.startswith('K:'):
            past_key = True
        elif past_key and l.strip() and not l.startswith('%'):
            body_lines.append(l.strip())

    body = ' '.join(body_lines).strip()
    body = re.sub(r'\|\]$', '', body).strip()
    body = re.sub(r'\|$', '', body).strip()

    lu_n, lu_d = [int(x) for x in lunit_str.split('/')]
    l_in_q = Fraction(lu_n, lu_d) * 4  # L units to quarter notes

    mn, md = [int(x) for x in meter.split('/')]
    beats_per_bar = Fraction(mn, md) * 4  # quarter notes per bar

    # Split into bars
    bars_raw = [b.strip() for b in re.split(r'\|', body) if b.strip()]

    # Key sig
    key_sig = KEY_SIG.get(key, '0')

    # Build MEI header
    mei_header = f'''<?xml version='1.0' encoding='utf-8'?>
<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.0">
  <meiHead>
    <fileDesc>
      <titleStmt>
        <title>{title}</title>
        <title type="subtitle">Pedal Harp — SSAATTBB+P</title>
      </titleStmt>
      <pubStmt><date isodate="2026-04-12"/></pubStmt>
    </fileDesc>
  </meiHead>
  <music>
    <body>
      <mdiv>
        <score>
          <scoreDef meter.count="{mn}" meter.unit="{md}" key.sig="{key_sig}">
            <staffGrp symbol="bracket" barthru="true">
              <staffDef n="1" lines="5" clef.shape="G" clef.line="2" label="Melody">
                <keySig sig="{key_sig}"/>
              </staffDef>
              <staffGrp symbol="brace">
                <staffDef n="2" lines="5" clef.shape="G" clef.line="2" label="RH">
                  <keySig sig="{key_sig}"/>
                </staffDef>
                <staffDef n="3" lines="5" clef.shape="F" clef.line="4" label="LH">
                  <keySig sig="{key_sig}"/>
                </staffDef>
              </staffGrp>
            </staffGrp>
          </scoreDef>
          <section>'''

    mei_footer = '''
          </section>
        </score>
      </mdiv>
    </body>
  </music>
</mei>'''

    measures_xml = []

    # State for voice leading
    prev_rh = None
    prev_lh = None
    prev_deg = None
    bar_count = 0
    total_bars = len(bars_raw)

    # Texture arc: opening (0-25%), building (25-50%), climax (50-75%), cadence (75-100%)

    for bar_idx, bar_str in enumerate(bars_raw):
        bar_count += 1
        progress = bar_idx / max(total_bars - 1, 1)

        # Extract chords from this bar
        harms = extract_harms(bar_str, key, l_in_q, beats_per_bar)

        # Determine primary chord for this bar
        if harms:
            _, primary_deg, primary_quality = harms[0]
        elif prev_deg:
            primary_deg, primary_quality = prev_deg
        else:
            primary_deg, primary_quality = 1, ''

        # Determine RH note count based on texture arc
        if progress < 0.15:
            rh_n = 2  # light opening
        elif progress < 0.5:
            rh_n = 2
        elif progress < 0.75:
            rh_n = 3  # fuller middle
        else:
            rh_n = 2  # taper at end

        # LH is always 1 more than RH
        lh_n = rh_n + 1

        # Get chord tones in range
        rh_avail, lh_avail = midi_notes_for_chord(primary_deg, primary_quality, key,
                                                    rh_range=(60, 81),   # C4 to A5
                                                    lh_range=(36, 59))   # C2 to B3

        # Pick notes with voice leading
        rh_notes = pick_rh_notes(rh_avail, prev_rh, rh_n)
        lh_notes = pick_lh_notes(lh_avail, prev_lh, lh_n)

        # Make sure LH has at least as many notes as RH
        if len(lh_notes) < len(rh_notes):
            # Try to get more LH notes
            extra_lh = pick_lh_notes(lh_avail, prev_lh, len(rh_notes) + 1)
            if extra_lh:
                lh_notes = extra_lh

        prev_rh = rh_notes
        prev_lh = lh_notes
        prev_deg = (primary_deg, primary_quality)

        # Generate MEI for this bar
        m_num = bar_count

        # Determine bar type
        bar_dur = sum(
            Fraction(dur_q)
            for (_, _, dur_q, _) in []  # will recalc below
        )

        # Parse melody notes to get actual bar duration
        mel_notes_parsed = parse_abc_bar_notes(bar_str, key, l_in_q)
        actual_dur = sum(d for (_, d, _, _) in mel_notes_parsed)

        # Is this a pickup bar?
        is_pickup = (bar_idx == 0 and actual_dur < beats_per_bar)

        # Use actual_dur for harp parts to match melody
        harp_dur = actual_dur if actual_dur > 0 else beats_per_bar

        # Rhythmic variety: split into sub-events based on chords in bar
        # If multiple chords, split the bar
        harp_events = build_harp_events(harms, harp_dur, beats_per_bar, rh_notes, lh_notes,
                                         primary_deg, primary_quality, key, progress, bar_idx)

        # Render melody
        mel_xml = abc_to_mei_melody(bar_str, key, l_in_q, m_num, beats_per_bar)

        # Render harp RH
        rh_xml = render_harp_staff(harp_events, 'rh', m_num, key)

        # Render harp LH
        lh_xml = render_harp_staff(harp_events, 'lh', m_num, key)

        # Render harm labels
        harm_xml = render_harms(harms, m_num)

        # Assemble measure
        right = 'end' if bar_idx == len(bars_raw) - 1 else 'single'
        pickup_attr = ' type="pickup"' if is_pickup else ''

        measure_xml = f'''
            <measure n="{m_num}"{pickup_attr} right="{right}">
              <staff n="1">
                <layer n="1">
{mel_xml}
                </layer>
              </staff>
              <staff n="2">
                <layer n="1">
{rh_xml}
                </layer>
              </staff>
              <staff n="3">
                <layer n="1">
{lh_xml}
                </layer>
              </staff>
{harm_xml}            </measure>'''

        measures_xml.append(measure_xml)

    full_mei = mei_header + ''.join(measures_xml) + mei_footer
    return full_mei

def build_harp_events(harms, harp_dur, beats_per_bar, rh_notes, lh_notes,
                       primary_deg, primary_quality, key, progress, bar_idx):
    """Build list of harp chord events for a bar.
    Returns list of {beat_start, dur, rh_notes, lh_notes, deg, quality}.
    Durations are guaranteed to sum to harp_dur.
    """
    harp_dur = Fraction(harp_dur)
    events = []

    def get_voicing(deg, quality, prev_rh_v, prev_lh_v):
        rh_avail, lh_avail = midi_notes_for_chord(deg, quality, key,
                                                    rh_range=(60, 81),
                                                    lh_range=(36, 59))
        rh_n = 2 if progress < 0.5 else 3
        lh_n = rh_n + 1
        rh_v = pick_rh_notes(rh_avail, prev_rh_v, rh_n)
        lh_v = pick_lh_notes(lh_avail, prev_lh_v, lh_n)
        if len(lh_v) < len(rh_v):
            extra = pick_lh_notes(lh_avail, prev_lh_v, len(rh_v) + 1)
            if extra:
                lh_v = extra
        return rh_v, lh_v

    if not harms:
        events.append({
            'beat_start': Fraction(0),
            'dur': harp_dur,
            'rh': rh_notes,
            'lh': lh_notes,
            'deg': primary_deg,
            'quality': primary_quality,
        })
        return events

    n_chords = len(harms)
    if n_chords == 1:
        rh_v, lh_v = get_voicing(harms[0][1], harms[0][2], rh_notes, lh_notes)
        events.append({
            'beat_start': Fraction(0),
            'dur': harp_dur,
            'rh': rh_v,
            'lh': lh_v,
            'deg': harms[0][1],
            'quality': harms[0][2],
        })
        return events

    # Valid MEI note durations in quarter notes
    VALID_DURS = {
        Fraction(4,1), Fraction(3,1), Fraction(2,1), Fraction(3,2), Fraction(1,1),
        Fraction(3,4), Fraction(1,2), Fraction(1,4), Fraction(1,8), Fraction(6,1), Fraction(8,1),
    }

    def snap_to_grid(bp, harp_dur):
        """Snap beat position to nearest clean grid point expressible in MEI."""
        # Grid points: every eighth note (1/2 quarter note)
        grid = Fraction(1, 2)
        snapped = Fraction(round(bp / grid)) * grid
        return max(Fraction(0), min(snapped, harp_dur))

    def is_expressible(dur):
        return dur in VALID_DURS

    # Convert tstamps to Fraction beat positions (1-indexed → 0-indexed)
    def ts_to_frac(ts):
        return Fraction(ts).limit_denominator(32) - 1  # 0-indexed

    chord_positions = []
    for (tstamp, deg, quality) in harms:
        bp = ts_to_frac(tstamp)
        if bp < 0:
            bp = Fraction(0)
        # Snap to clean grid
        bp = snap_to_grid(bp, harp_dur)
        chord_positions.append((bp, deg, quality))

    # Sort by beat position
    chord_positions.sort(key=lambda x: x[0])

    # Deduplicate by beat position (keep last)
    deduped = []
    for (bp, deg, quality) in chord_positions:
        if deduped and deduped[-1][0] == bp:
            deduped[-1] = [bp, deg, quality]
        else:
            deduped.append([bp, deg, quality])

    # If the first annotated chord doesn't start at beat 0, prepend a "gap" entry
    # using the primary chord to cover beats 0..first_annotation
    if deduped and deduped[0][0] > 0:
        deduped.insert(0, [Fraction(0), primary_deg, primary_quality])

    # Build durations: each chord runs from its beat_pos to next chord's beat_pos (or harp_dur)
    chord_beats = []
    for idx, (bp, deg, quality) in enumerate(deduped):
        if idx + 1 < len(deduped):
            next_bp = deduped[idx+1][0]
            dur = next_bp - bp
        else:
            dur = harp_dur - bp
        if dur <= 0:
            continue  # skip zero-duration events (duplicate after snap)
        # If duration is not expressible, merge into next event
        chord_beats.append([bp, dur, deg, quality])

    # Merge adjacent events whose duration is not expressible in MEI
    # by combining short events with the next one
    merged = []
    i = 0
    while i < len(chord_beats):
        bp, dur, deg, quality = chord_beats[i]
        # Merge forward while dur not expressible
        j = i + 1
        while j < len(chord_beats) and not is_expressible(dur):
            # Extend this event to absorb the next
            dur += chord_beats[j][1]
            j += 1
        merged.append([bp, dur, deg, quality])
        i = j if j > i + 1 else i + 1

    chord_beats = merged

    # Final pass: ensure total equals harp_dur
    if chord_beats:
        total = sum(x[1] for x in chord_beats)
        if total != harp_dur:
            # Adjust last event
            diff = harp_dur - total
            chord_beats[-1][1] += diff
            if chord_beats[-1][1] <= 0:
                chord_beats.pop()
        # If still not clean, just use one event
        if not chord_beats or any(not is_expressible(x[1]) for x in chord_beats):
            chord_beats = [[Fraction(0), harp_dur, primary_deg, primary_quality]]

    prev_rh_v = rh_notes
    prev_lh_v = lh_notes

    for (beat_pos, dur, deg, quality) in chord_beats:
        rh_v, lh_v = get_voicing(deg, quality, prev_rh_v, prev_lh_v)
        events.append({
            'beat_start': beat_pos,
            'dur': dur,
            'rh': rh_v,
            'lh': lh_v,
            'deg': deg,
            'quality': quality,
        })
        prev_rh_v = rh_v
        prev_lh_v = lh_v

    return events

def render_harp_staff(events, hand, m_num, key):
    """Render harp staff (RH or LH) events to MEI layer XML."""
    lines = []
    note_idx = 0
    staff_n = 2 if hand == 'rh' else 3

    for ev_idx, ev in enumerate(events):
        notes = ev['rh'] if hand == 'rh' else ev['lh']
        dur = ev['dur']

        if not notes:
            # Rest
            nid = f'm{m_num}s{staff_n}ev{ev_idx}r'
            lines.append('          ' + render_rest_xml(nid, dur))
            continue

        # Remove duplicates, sort
        notes = sorted(set(notes))

        if len(notes) == 1:
            nid = f'm{m_num}s{staff_n}ev{ev_idx}n0'
            lines.append('          ' + render_note_xml(nid, notes[0], key, dur))
        else:
            cid = f'm{m_num}s{staff_n}ev{ev_idx}c'
            lines.append('          ' + render_chord_xml(cid, notes, key, dur))

        note_idx += 1

    return '\n'.join(lines)

def render_harms(harms, m_num):
    """Render <harm> elements for a bar."""
    if not harms:
        return ''
    lines = []
    for (tstamp, deg, quality) in harms:
        label = harm_label(deg, quality)
        # Format tstamp: integer if whole, else decimal
        ts = Fraction(tstamp)
        if ts.denominator == 1:
            ts_str = str(ts.numerator)
        elif ts.denominator == 2:
            ts_str = f'{ts.numerator // 2 + (ts.numerator % 2) / 2:.1f}'.rstrip('0').rstrip('.')
            # Better: use fraction notation
            ts_str = f'{float(ts):.4f}'.rstrip('0').rstrip('.')
        else:
            ts_str = str(float(ts))[:6]
        lines.append(f'              <harm staff="1" tstamp="{ts_str}">{label}</harm>')
    return '\n'.join(lines) + '\n'

# ──────────────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with open('/home/james.clements/projects/trefoil/app/lead_sheets.json') as f:
        data = json.load(f)

    target_ids = {4244,4245,4246,4247,4248,4249,4250,4251,4252,4254,4255,4256,4257,4259,4260,
                  4261,4262,4263,4264,4266,4267,4268,4270,4271,4272,4273,4274,4275,4276,4277,
                  4278,4279,4280,4281,4282}

    hymns = sorted([h for h in data if int(h['n']) in target_ids], key=lambda h: int(h['n']))

    out_dir = '/home/james.clements/projects/trefoil/handout/tch_ssaattbbp_out'
    os.makedirs(out_dir, exist_ok=True)

    for hymn in hymns:
        n = hymn['n']
        print(f'Generating {n} {hymn["t"]} ({hymn["key"]})...')
        try:
            mei = generate_arrangement(hymn)
            out_path = os.path.join(out_dir, f'{n}_raw.mei')
            with open(out_path, 'w') as f:
                f.write(mei)
            print(f'  -> {out_path}')
        except Exception as e:
            print(f'  ERROR: {e}')
            import traceback
            traceback.print_exc()

    print('Done.')
