#!/usr/bin/env python3
"""
harp_mapper.py — given a roman numeral + key + melody note, pick the best
matching fraction from the 118-chord Harp Chord System vocabulary.

Usage (as module):
    from harp_mapper import load_vocab, pick_fraction
    vocab = load_vocab('/mnt/project/HarpChordSystem.json')
    result = pick_fraction(vocab, rn='V7', key='D', melody='G4', mode='major')
    # → {'lh_roman': 'V7', 'lh_figure': '5333',
    #    'rh_roman': 'I', 'rh_figure': 'F33',
    #    'source': 'stacked_chords', 'mood': 'Commanding', 'score': 23.5}

Usage (CLI):
    python3 harp_mapper.py V7 D G4
"""
import json
import re
import sys
import argparse
from music21 import key, pitch, roman

# Scale-degree mapping for major keys
MAJOR_SCALE = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
MINOR_SCALE = ['i', 'ii', 'III', 'iv', 'V', 'VI', 'VII']   # natural minor (Aeolian)

# ═════════════════════════════════════════════════════════════════════════════
#   Load vocabulary
# ═════════════════════════════════════════════════════════════════════════════
def load_vocab(path='/mnt/project/HarpChordSystem.json'):
    with open(path) as f:
        return json.load(f)

# ═════════════════════════════════════════════════════════════════════════════
#   Roman numeral → scale-degree
# ═════════════════════════════════════════════════════════════════════════════
ROMAN_TO_DEG = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7,
}

def parse_rn(rn_str):
    """Return (root_degree_1to7, quality, inversion).
    quality ∈ {'maj', 'min', 'dim', 'halfdim', 'dom7', 'min7', 'maj7', ...}
    inversion ∈ {0, 1, 2, 3} — 0=root, 1=first inv (6), 2=second inv (64), 3=third inv (42)"""
    s = rn_str.strip()
    # Strip leading accidentals (b, #) — treat bVII same as VII for degree purposes
    m = re.match(r'^[#b]?([ivIV]+)([oø°Δ]?)(\d*)([+b#]*\d*)?', s)
    if not m:
        return None, None, 0
    numerals, qual_char, digits, extras = m.groups()
    deg = ROMAN_TO_DEG.get(numerals)
    if deg is None:
        return None, None, 0

    is_upper = numerals[0].isupper()

    # Quality
    if qual_char == '°':
        quality = 'dim'
    elif qual_char == 'ø':
        quality = 'halfdim'
    elif qual_char == 'Δ':
        quality = 'maj7'
    else:
        quality = 'maj' if is_upper else 'min'

    # Inversion/extensions from digits
    inversion = 0
    if digits == '6':
        inversion = 1
    elif digits == '64':
        inversion = 2
    elif digits == '7':
        quality = 'dom7' if is_upper else 'min7'
        inversion = 0
    elif digits == '65':
        quality = 'dom7' if is_upper else 'min7'
        inversion = 1
    elif digits == '43':
        quality = 'dom7' if is_upper else 'min7'
        inversion = 2
    elif digits == '42' or digits == '2':
        quality = 'dom7' if is_upper else 'min7'
        inversion = 3
    return deg, quality, inversion

# ═════════════════════════════════════════════════════════════════════════════
#   Harp-system LH roman → scale degree (reverse lookup)
# ═════════════════════════════════════════════════════════════════════════════
def harp_rn_to_degree(harp_rn):
    """Convert a vocabulary LH/RH roman like 'V7', 'IVΔ', 'iii¹', 'viiø7' to degree."""
    s = harp_rn
    # Strip superscripts and modifiers to get base numerals
    m = re.match(r'^([#b]?)([ivIV]+)', s)
    if not m:
        return None
    return ROMAN_TO_DEG.get(m.group(2))

def harp_rn_quality(harp_rn):
    """Return the quality tag of a harp-vocabulary roman."""
    s = harp_rn
    if '°' in s:
        return 'dim'
    if 'ø7' in s:
        return 'halfdim'
    if 'Δ' in s:
        return 'maj7'
    m = re.match(r'^[#b]?([ivIV]+)(.*)$', s)
    if not m:
        return 'unknown'
    numerals, rest = m.groups()
    is_upper = numerals[0].isupper()
    if '7' in rest:
        return 'dom7' if is_upper else 'min7'
    if 's4' in rest or 's2' in rest:
        return 'sus'
    if 'q' in rest:
        return 'quartal'
    return 'maj' if is_upper else 'min'

# ═════════════════════════════════════════════════════════════════════════════
#   Compute actual pitches produced by a (key, figure) pair
# ═════════════════════════════════════════════════════════════════════════════
def figure_pitches(figure, K):
    """Return list of music21 Pitch objects produced by `figure` in key K.
    Figure format: first char = start scale degree (1-9,A,B,C,D,E,F,G,H);
    subsequent chars = inclusive intervals to next note."""
    # Convert figure characters to integer degrees
    vals = []
    for c in figure:
        if c.isdigit():
            vals.append(int(c))
        else:
            vals.append(ord(c) - ord('A') + 10)
    if not vals:
        return []
    start = vals[0]
    degrees = [start]
    cur = start
    for iv in vals[1:]:
        cur = cur + iv - 1
        degrees.append(cur)
    # Map each scale degree to a concrete pitch in K
    # Scale degree 1 = K.tonic; degree 8 = octave up; degree 9 = ninth; etc.
    tonic = K.tonic
    scale_pitches = K.getPitches(tonic.name + '2', tonic.name + '7')  # spans enough octaves
    # Build scale: degree n → nth pitch starting from tonic in the key's scale
    # Simpler approach: compute using interval-based arithmetic
    result = []
    for d in degrees:
        # d=1 means tonic; d=8 means octave up; d=9 means 2nd up octave
        octave_shift = (d - 1) // 7
        scale_deg = ((d - 1) % 7) + 1
        # Get the pitch at scale_deg in the key (1-indexed)
        base_pitch_name = K.pitchFromDegree(scale_deg).name
        # Start from octave 3 as the reference for 'tonic = degree 1'
        p = pitch.Pitch(f"{base_pitch_name}{3 + octave_shift}")
        result.append(p)
    return result

# ═════════════════════════════════════════════════════════════════════════════
#   Scoring: how well does a vocab entry match (rn, key, melody)?
# ═════════════════════════════════════════════════════════════════════════════
def score_entry(entry, target_deg, target_quality, target_inv,
                melody_pitch, K, prefer_color=True):
    """Return a numeric score for this vocab entry matching the target."""
    lh_deg = harp_rn_to_degree(entry['lh_roman'])
    rh_deg = harp_rn_to_degree(entry['rh_roman'])
    lh_qual = harp_rn_quality(entry['lh_roman'])

    score = 0.0

    # 1. LH root match with target — CRITICAL (must match on degree)
    if lh_deg == target_deg:
        score += 10
    elif rh_deg == target_deg:
        score += 5   # chord-root in RH is also acceptable (the LH is a pedal or pivot)
    else:
        return -100  # degree mismatch — skip

    # 2. Quality match on the LH chord
    if lh_qual == target_quality:
        score += 8
    elif target_quality == 'dom7' and lh_qual in ('maj', 'dom7'):
        score += 5  # V triad acceptable for V7 if no dom7 available
    elif target_quality == 'min7' and lh_qual in ('min', 'min7'):
        score += 5

    # 3. Melody compatibility — RH top note covers melody pitch
    if melody_pitch:
        try:
            rh_pitches = figure_pitches(entry['rh_figure'], K)
            lh_pitches = figure_pitches(entry['lh_figure'], K)
            all_pcs = {p.pitchClass for p in (rh_pitches + lh_pitches)}
            if melody_pitch.pitchClass in all_pcs:
                score += 6
                # Extra bonus if melody is the top note of RH
                if rh_pitches and melody_pitch.pitchClass == rh_pitches[-1].pitchClass:
                    score += 3
            else:
                score -= 4   # melody clashes with voicing
        except Exception:
            pass

    # 4. Color preference — stacked_chords usually richer than jazz_progressions triads
    if prefer_color:
        if entry.get('mood'):  # it's a stacked chord
            # Favor moods that suggest jazz richness
            rich_moods = {'Radiant', 'Commanding', 'Sultry', 'Pealing', 'Urgent',
                         'Chiming', 'Soulful', 'Poised', 'Lush', 'Shimmer',
                         'Ethereal', 'Velvety', 'Layered', 'Anchored'}
            if entry['mood'] in rich_moods:
                score += 2
            else:
                score += 1

    # 5. Inversion preference
    if target_inv > 0:
        # User asked for an inversion — try to pick an entry with an inverted RH
        if '¹' in entry['rh_roman'] or '²' in entry['rh_roman'] or '³' in entry['rh_roman']:
            score += 2

    return score

# ═════════════════════════════════════════════════════════════════════════════
#   Minor-key translation: vocabulary is Ionian-labeled, but we often want
#   to reharmonize minor-key hymns. Translate the minor-mode RN to its
#   relative-major equivalent so the lookup finds the right pitches.
# ═════════════════════════════════════════════════════════════════════════════
MINOR_TO_RELATIVE_MAJOR_DEG = {
    1: 6,   # i(minor) = vi(relative major)
    2: 7,   # ii° = vii°
    3: 1,   # III = I
    4: 2,   # iv = ii
    5: 3,   # V = iii (but often chromaticized — watch out)
    6: 4,   # VI = IV
    7: 5,   # VII = V
}

def translate_minor_to_major(rn_str):
    """Translate a minor-mode RN to its relative-major equivalent.
    E.g. 'i' → 'vi', 'iv' → 'ii', 'V' → 'iii' (harmonic minor V = major III).
    Returns a new RN string."""
    target_deg, target_quality, target_inv = parse_rn(rn_str)
    if target_deg is None:
        return rn_str
    new_deg = MINOR_TO_RELATIVE_MAJOR_DEG.get(target_deg, target_deg)
    # Reconstruct: use uppercase if the relative-major chord is major
    # In a major key: I IV V are major; ii iii vi are minor; vii° is diminished
    if new_deg in (1, 4, 5):
        numerals = {1:'I', 4:'IV', 5:'V'}[new_deg]
    elif new_deg in (2, 3, 6):
        numerals = {2:'ii', 3:'iii', 6:'vi'}[new_deg]
    elif new_deg == 7:
        numerals = 'vii'
    else:
        return rn_str
    # Preserve quality suffixes from the original
    suffix = ''
    if target_quality in ('dom7', 'min7'):
        suffix = '7'
    elif target_quality == 'maj7':
        suffix = 'Δ'
    elif target_quality == 'dim':
        suffix = '°'
    elif target_quality == 'halfdim':
        suffix = 'ø7'
    inv_suffix = {0:'', 1:'6', 2:'64', 3:'42'}.get(target_inv, '')
    return f"{numerals}{suffix}{inv_suffix}"


# ═════════════════════════════════════════════════════════════════════════════
#   Harmonic-minor V substitution strategies
# ═════════════════════════════════════════════════════════════════════════════
# The 118-chord vocabulary is strictly diatonic, so a V chord in minor mode
# (which classically wants a chromatic leading tone) cannot be directly
# represented. Instead, we substitute one of four diatonic strategies:
#
#   'modal_v'       — minor v (v7/i). Soft, unresolved, Renaissance/Aeolian.
#                     Default for unmarked mid-phrase passages.
#   'bVII_backdoor' — bVII → i. Plagal approach from below. Folk/modal feel.
#                     Preferred when the previous chord was IV (continues plagal pull).
#   'III_deceptive' — III → i. Relative-major substitute. Dramatic ambiguity.
#                     Preferred at fermata-ending final cadences.
#   'pedal_i'       — skip the V; hold tonic under the melody. Suspended feel.
#                     Preferred for brief V passages where melody already fits tonic.
# ═════════════════════════════════════════════════════════════════════════════

def choose_minor_V_substitution(prev_rn=None, is_final_cadence=False,
                                 ending_marker=None, v_duration_beats=None,
                                 melody=None, key_root=None):
    """Decide which substitution strategy to use when V appears in minor mode.

    Parameters
    ----------
    prev_rn : str or None
        Roman numeral of the chord preceding this V, e.g. 'iv', 'i', 'VI'.
    is_final_cadence : bool
        True if this V is the penultimate chord of the hymn / phrase.
    ending_marker : str or None
        The phrase's ending_marker: 'fermata', 'cadence', 'end', or None.
    v_duration_beats : int or None
        How many beats this V occupies (short V → pedal strategy preferred).
    melody : str or None
        The melody note at this V (e.g. 'A4'); used to check tonic compatibility
        for the pedal strategy.
    key_root : str or None
        The tonic pitch name (e.g. 'E' for E minor); used with melody to check
        tonic compatibility.

    Returns
    -------
    str — one of 'modal_v', 'bVII_backdoor', 'III_deceptive', 'pedal_i'
    """
    # Rule 1: IV → V in minor → continue plagal feel with bVII backdoor
    if prev_rn:
        prev_base_m = re.match(r'^([ivIV]+)', prev_rn)
        prev_base = prev_base_m.group(1).lower() if prev_base_m else ''
        if prev_base == 'iv':
            return 'bVII_backdoor'

    # Rule 2: fermata-marked final cadence → III deceptive (dramatic)
    if is_final_cadence and ending_marker == 'fermata':
        return 'III_deceptive'

    # Rule 3: brief V (1 beat or less) with tonic-compatible melody → pedal i
    if v_duration_beats is not None and v_duration_beats <= 1 and melody and key_root:
        try:
            mel_pc = pitch.Pitch(melody).pitchClass
            tonic_pc = pitch.Pitch(key_root).pitchClass
            # Tonic triad pitch-classes: tonic, minor-3rd above, perfect-5th above
            tonic_triad_pcs = {tonic_pc, (tonic_pc + 3) % 12, (tonic_pc + 7) % 12}
            if mel_pc in tonic_triad_pcs:
                return 'pedal_i'
        except Exception:
            pass

    # Default: modal v (natural-minor v with no chromatic alteration)
    return 'modal_v'


def translate_minor_V_with_strategy(strategy):
    """Given a substitution strategy, return the relative-major RN to look up
    in the 118 vocabulary.

    E minor → G major relative-major lookup:
      modal_v        → 'iii7'  (E minor's v7 = G major's iii7, a minor-7 chord)
      bVII_backdoor  → 'V'     (E minor's bVII = D major = G major's V, a major triad)
      III_deceptive  → 'I'     (E minor's III = G major = G major's I)
      pedal_i        → 'vi'    (E minor's i = G major's vi; tonic voicing)
    """
    return {
        'modal_v':       'iii7',
        'bVII_backdoor': 'V',
        'III_deceptive': 'I',
        'pedal_i':       'vi',
    }.get(strategy, 'iii')   # fallback to old default





def pick_fraction(vocab, rn, key_name, melody=None, mode='major', top_n=3,
                  prefer_color=True):
    """Given RN + key + optional melody pitch, return top-N matching entries."""
    # For minor-mode queries, translate to relative-major lookup so the 118
    # vocabulary (Ionian-labeled) finds the right pitches. The LH/RH labels
    # in the result will read relative-major but the pitches are correct.
    original_rn = rn
    if mode == 'minor':
        rn = translate_minor_to_major(rn)
    target_deg, target_quality, target_inv = parse_rn(rn)
    if target_deg is None:
        return []
    # Build music21 Key — always use relative major for pitch arithmetic
    # when mode is minor
    if mode == 'minor':
        # Compute relative major: minor tonic + 3 semitones
        minor_tonic = pitch.Pitch(key_name)
        rel_maj_tonic = minor_tonic.transpose(3)
        K = key.Key(rel_maj_tonic.name, 'major')
    else:
        K = key.Key(key_name, 'major')
    # Parse melody pitch
    melody_pitch = None
    if melody:
        try:
            melody_pitch = pitch.Pitch(melody)
        except Exception:
            pass
    # Score all 118 entries
    all_entries = []
    for e in vocab['jazz_progressions']['entries']:
        all_entries.append(dict(e, source='jazz_progressions'))
    for e in vocab['stacked_chords']['entries']:
        all_entries.append(dict(e, source='stacked_chords'))

    scored = []
    for e in all_entries:
        s = score_entry(e, target_deg, target_quality, target_inv,
                       melody_pitch, K, prefer_color)
        if s > 0:
            scored.append((s, e))
    scored.sort(key=lambda x: -x[0])
    return [dict(e, score=s) for s, e in scored[:top_n]]

# ═════════════════════════════════════════════════════════════════════════════
#   Transition-aware picker: pick a jazz_progression entry for a specific
#   chord-to-chord move, with contour influencing CW vs CCW direction
# ═════════════════════════════════════════════════════════════════════════════

# Which cycle does a scale-degree transition belong to?
# Distance in diatonic steps: 1 step = 2nds, 2 steps = 3rds, 3 steps = 4ths.
# Note: 4ths down = 5ths up and vice versa — we normalize to smallest direction.
def cycle_of_transition(deg_from, deg_to):
    """Return ('2nds'|'3rds'|'4ths', 'CW'|'CCW') or None if not a cycle edge.
    CW/CCW is determined by the cycle's traversal order.
    cycle_4ths_cw: I IV vii° iii vi ii V I  (step = +3 in degree)
    cycle_3rds_cw: I iii V vii° ii IV vi I  (step = +2)
    cycle_2nds_cw: I ii iii IV V vi vii° I  (step = +1)
    """
    if deg_from is None or deg_to is None or deg_from == deg_to:
        return None, None
    # Distance in diatonic degrees (1-7 wraps)
    forward = (deg_to - deg_from) % 7
    backward = (deg_from - deg_to) % 7
    # CW traversals
    cw_traversals = {
        '2nds': [1, 2, 3, 4, 5, 6, 7],    # step forward by 1
        '3rds': [1, 3, 5, 7, 2, 4, 6],    # step forward by 2
        '4ths': [1, 4, 7, 3, 6, 2, 5],    # step forward by 3
    }
    for cyc, order in cw_traversals.items():
        # If deg_to comes right after deg_from in CW order, it's CW
        try:
            idx_from = order.index(deg_from)
            idx_to = order.index(deg_to)
            # CW: +1 step in order
            if (idx_to - idx_from) % 7 == 1:
                return cyc, 'CW'
            # CCW: -1 step in order
            if (idx_from - idx_to) % 7 == 1:
                return cyc, 'CCW'
        except ValueError:
            continue
    return None, None


def pick_transition(vocab, rn_from, rn_to, key_name, melody_to=None,
                    mode='major', contour=None, top_n=3):
    """Pick a jazz_progression entry for the chord-to-chord move rn_from → rn_to.

    Parameters
    ----------
    rn_from, rn_to : roman-numeral strings (e.g. 'V', 'I')
    contour : 'ascending' | 'descending' | 'static' | None
        - ascending  → prefer CW edges (forward motion: Resolving, Lifting, Exploring)
        - descending → prefer CCW edges (receding motion: Landing, Lofting, Dreaming)
        - static/None → no direction preference

    Returns top_n matching jazz_progression entries, scored.
    """
    if mode == 'minor':
        # Translate both RNs to relative major for vocabulary lookup
        rn_from_t = translate_minor_to_major(rn_from)
        rn_to_t = translate_minor_to_major(rn_to)
        minor_tonic = pitch.Pitch(key_name)
        rel_maj_tonic = minor_tonic.transpose(3)
        K = key.Key(rel_maj_tonic.name, 'major')
    else:
        rn_from_t, rn_to_t = rn_from, rn_to
        K = key.Key(key_name, 'major')

    deg_from, qual_from, _ = parse_rn(rn_from_t)
    deg_to, qual_to, _ = parse_rn(rn_to_t)
    if deg_from is None or deg_to is None:
        return []

    cycle, direction = cycle_of_transition(deg_from, deg_to)
    # If this transition isn't a cycle edge, fall back to pick_fraction on rn_to
    if cycle is None:
        return pick_fraction(vocab, rn_to, key_name, melody_to, mode, top_n)

    # Score jazz_progressions entries only (they encode the transitions)
    melody_pitch = None
    if melody_to:
        try:
            melody_pitch = pitch.Pitch(melody_to)
        except Exception:
            pass

    scored = []
    for e in vocab['jazz_progressions']['entries']:
        # Must match the cycle
        if e.get('cycle') != cycle:
            continue
        # Must involve both chords (one is LH, other is RH, either orientation)
        lh_deg = harp_rn_to_degree(e['lh_roman'])
        rh_deg = harp_rn_to_degree(e['rh_roman'])
        if {lh_deg, rh_deg} != {deg_from, deg_to}:
            continue

        score = 0.0
        # Base score: matched the transition at all
        score += 15

        # Direction bonus: CW-labeled entries align with ascending contour
        if contour == 'ascending' and direction == 'CW':
            score += 6
        elif contour == 'descending' and direction == 'CCW':
            score += 6
        elif contour in ('ascending', 'descending') and direction != contour[:2].upper():
            # Opposite direction — mild penalty
            score -= 2

        # Melody fit on RH (same logic as pick_fraction)
        if melody_pitch:
            try:
                rh_pitches = figure_pitches(e['rh_figure'], K)
                lh_pitches = figure_pitches(e['lh_figure'], K)
                all_pcs = {p.pitchClass for p in (rh_pitches + lh_pitches)}
                if melody_pitch.pitchClass in all_pcs:
                    score += 5
                    if rh_pitches and melody_pitch.pitchClass == rh_pitches[-1].pitchClass:
                        score += 3
                else:
                    score -= 3
            except Exception:
                pass

        # Verse 2 entries have richer voicings (7ths, sus, +8) — slight bonus
        if e.get('verse') == 2:
            score += 2

        entry = dict(e, source='jazz_progressions', score=score,
                    cycle_inferred=cycle, direction=direction)
        # Label gets the matching direction's mood
        entry['mood'] = e.get('cw_label' if direction == 'CW' else 'ccw_label', '')
        scored.append((score, entry))

    scored.sort(key=lambda x: -x[0])
    return [e for _, e in scored[:top_n]]


def infer_contour(melody_prev, melody_cur, melody_next):
    """Return 'ascending' | 'descending' | 'static' based on melody movement.
    `melody_cur` is the note at the current region. Compares to neighbors.
    Expects music21-style pitch strings or None."""
    def pc_midi(p):
        try:
            return pitch.Pitch(p).midi if p else None
        except Exception:
            return None
    p0, p1, p2 = pc_midi(melody_prev), pc_midi(melody_cur), pc_midi(melody_next)
    if p1 is None:
        return 'static'
    # If we have next note, prioritize forward motion
    if p2 is not None:
        if p2 > p1:
            return 'ascending'
        elif p2 < p1:
            return 'descending'
    if p0 is not None:
        if p1 > p0:
            return 'ascending'
        elif p1 < p0:
            return 'descending'
    return 'static'


# ═════════════════════════════════════════════════════════════════════════════
#   High-level picker: handles minor-V substitution, cycle detection, and
#   stacked fallback in one call. Returns the best fraction plus metadata
#   about any harmonic substitution that was applied.
# ═════════════════════════════════════════════════════════════════════════════
def pick_with_substitution(vocab, rn, key_root, *,
                            next_rn=None, prev_rn=None,
                            melody=None, mode='major', contour=None,
                            is_final_cadence=False, ending_marker=None,
                            v_duration_beats=None, top_n=3):
    """Main entry point for choosing a fraction. Handles:
      - Cycle-edge transitions (when next_rn forms a cycle with rn)
      - Stacked fallback (single-chord selection)
      - Minor-mode V substitution (bVII_backdoor / III_deceptive /
        modal_v / pedal_i chosen by context)

    Returns a list of up to top_n picks (dicts), each annotated with:
      - 'harmonic_substitution': None, or one of the strategy names, explaining
        when the original RN was replaced
      - 'requested_rn': the original RN before substitution
    """
    requested_rn = rn
    substitution = None

    # Minor-mode V → requires substitution since the 118 is strictly diatonic
    if mode == 'minor':
        rn_base_m = re.match(r'^(b?[ivIV]+)', rn)
        rn_base = rn_base_m.group(1) if rn_base_m else ''
        if rn_base in ('V', 'V7'):
            substitution = choose_minor_V_substitution(
                prev_rn=prev_rn,
                is_final_cadence=is_final_cadence,
                ending_marker=ending_marker,
                v_duration_beats=v_duration_beats,
                melody=melody,
                key_root=key_root,
            )
            # Replace rn with the substituted RN (already in relative-major terms
            # for 118 lookup). Switch mode to major for the lookup path so we
            # don't re-translate.
            substituted_rn = translate_minor_V_with_strategy(substitution)
            # For bVII_backdoor, we want to find V → I (backdoor) in the relative
            # major; this is exactly a cycle-edge transition if next_rn is 'i'.
            # For III_deceptive, we want I → vi (relative-major terms when next
            # is 'i' = 'vi' in relative major) which is also a cycle edge.
            # For modal_v, we want iii7 (stacked).
            # For pedal_i, we want vi (stacked, as tonic).
            rn = substituted_rn
            # Also translate next_rn if it's 'i' (minor tonic → relative-major 'vi')
            if next_rn:
                nb_m = re.match(r'^(b?[ivIV]+)', next_rn)
                nb = nb_m.group(1) if nb_m else ''
                if nb in ('i', 'i6', 'i64'):
                    next_rn = 'vi'
            # Compute the look-up key_root (relative major root, +3 semitones)
            minor_tonic_p = pitch.Pitch(key_root)
            rel_maj_tonic = minor_tonic_p.transpose(3)
            lookup_key_root = rel_maj_tonic.name
            lookup_mode = 'major'
        else:
            lookup_key_root = key_root
            lookup_mode = mode
    else:
        lookup_key_root = key_root
        lookup_mode = mode

    # Try cycle transition first if we have a next_rn
    picks = None
    if next_rn:
        # Translate both for cycle-degree math
        from_t = translate_minor_to_major(rn) if lookup_mode == 'minor' else rn
        to_t = translate_minor_to_major(next_rn) if lookup_mode == 'minor' else next_rn
        d_from, _, _ = parse_rn(from_t)
        d_to, _, _ = parse_rn(to_t)
        cyc, dir_ = cycle_of_transition(d_from, d_to)
        if cyc:
            picks = pick_transition(vocab, rn, next_rn, lookup_key_root,
                                    melody, lookup_mode, contour, top_n=top_n)

    if not picks:
        picks = pick_fraction(vocab, rn, lookup_key_root, melody,
                              lookup_mode, top_n=top_n)

    # Annotate each pick with the substitution info
    for p in picks:
        p['harmonic_substitution'] = substitution
        p['requested_rn'] = requested_rn

    return picks


# ═════════════════════════════════════════════════════════════════════════════
#   CLI
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('rn', help='Roman numeral, e.g. V7, I64, iii6')
    ap.add_argument('key', help='Key root, e.g. D, F, Bb, A')
    ap.add_argument('melody', nargs='?', default=None,
                    help='Optional melody pitch, e.g. G4, C#5')
    ap.add_argument('--mode', default='major', choices=('major', 'minor'))
    ap.add_argument('--top', type=int, default=3)
    ap.add_argument('--vocab', default='/mnt/project/HarpChordSystem.json')
    args = ap.parse_args()

    vocab = load_vocab(args.vocab)
    results = pick_fraction(vocab, args.rn, args.key, args.melody,
                           args.mode, args.top)
    if not results:
        print(f"No matches for RN={args.rn} in key {args.key} {args.mode}")
        sys.exit(1)
    print(f"\nTop {len(results)} matches for {args.rn} in {args.key} {args.mode}"
          + (f", melody={args.melody}" if args.melody else ""))
    print("─" * 80)
    for r in results:
        label = f"{r['lh_roman']:>6} / {r['rh_roman']:<6}   "
        fig = f"lh={r['lh_figure']:<6} rh={r['rh_figure']:<6}"
        src = r['source']
        mood = r.get('mood', r.get('cw_label', ''))
        print(f"  {r['score']:>5.1f}  {label}{fig}   [{src}: {mood}]")
