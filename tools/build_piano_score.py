#!/usr/bin/env python3
"""
build_piano_score.py — render a hymn as a grand-staff piano score for a
4-finger harpist.  Jazz-style arrangement of chord fractions, not SATB blocks.

Phase 1 v0.3 — LilyPond backend.

Pipeline:
  hymnal_export JSON + reharm JSON  →  LilyPond source (.ly)
      →  lilypond CLI  →  PDF + SVG + MIDI

LilyPond gives us professional-grade typography, native MIDI generation from
the same source, proper dynamics handling, and a path to LaTeX-rendered chord
fractions via lilypond-book.

Input:
  - hymnal_export/<slug>.json  (voices.S1V1, music.key_root, etc.)
  - hymnal_html/reharms/<slug>.json  (per-bar chord-fraction assignments)

Output (when -o specifies a .ly path):
  - <name>.ly     — LilyPond source
  - <name>.pdf    — engraved score
  - <name>.svg    — SVG of the score (when --svg)
  - <name>.midi   — MIDI audio

Usage:
    python3 tools/build_piano_score.py --title "Silent_Night" \\
        -o hymnal_html/silent_night.ly --svg
    python3 tools/build_piano_score.py <export.json> <reharm.json> -o out.ly
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

# ─────────────────────────────────────────────────────────────────────────────
# Figure parsing
# ─────────────────────────────────────────────────────────────────────────────
STRING_ALPHABET = {str(n): n for n in range(1, 10)}
STRING_ALPHABET.update({'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15})

HARP_LOW_MIDI = 31   # ~G1; bump pedal up an octave if we'd go below this
                     # (user's harp reaches this register — keeps pedal
                     # deep and out of the LH figure's bass-clef range)


def rn_to_root_degree(rn):
    """'V7' → 5. 'bVII' → 7. 'iiø7' → 2. Returns 1-7 or None."""
    if not rn:
        return None
    m = re.match(r'^[b#\u266d\u266f]?([ivIV]+)', rn)
    if not m:
        return None
    roman = m.group(1)
    mapping = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
               'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7}
    return mapping.get(roman)


def figure_to_strings(fig):
    """'1333' -> [1, 3, 5, 7]  (string positions/scale-degrees the fingers hit)."""
    start = STRING_ALPHABET[fig[0]]
    positions = [start]
    for ch in fig[1:]:
        positions.append(positions[-1] + int(ch) - 1)
    return positions


# ─────────────────────────────────────────────────────────────────────────────
# Pitch math
# ─────────────────────────────────────────────────────────────────────────────
MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
MINOR_STEPS = [0, 2, 3, 5, 7, 8, 10]
PITCH_CLASS = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def parse_key_root(key_root_str):
    """'B-' → pitch class 10 (Bb). 'F#' → 6. 'G' → 7."""
    s = key_root_str.strip() if key_root_str else ''
    if not s:
        return 0
    base = PITCH_CLASS[s[0].upper()]
    for ch in s[1:]:
        if ch == '#':
            base = (base + 1) % 12
        elif ch in ('-', 'b'):
            base = (base - 1) % 12
    return base


def string_to_midi(string_num, key_root, mode='major', base_octave=4):
    """String N in key K → MIDI pitch."""
    steps = MAJOR_STEPS if mode == 'major' else MINOR_STEPS
    tonic_pc = parse_key_root(key_root)
    zero_based = string_num - 1
    octave_offset = zero_based // 7
    degree_idx = zero_based % 7
    semitones_above_tonic = steps[degree_idx] + 12 * octave_offset
    return 12 * (base_octave + 1) + tonic_pc + semitones_above_tonic


def pitch_to_midi(pitch_str):
    """music21-style 'B-4' or 'F#5' → MIDI number."""
    if not pitch_str:
        return None
    m = re.match(r'^([A-G])([#b\-]*)(-?\d+)$', pitch_str)
    if not m:
        return None
    letter, accid, octave = m.group(1), m.group(2), int(m.group(3))
    pc = PITCH_CLASS[letter]
    for ch in accid:
        if ch == '#':
            pc = (pc + 1) % 12
        elif ch in ('-', 'b'):
            pc = (pc - 1) % 12
    return 12 * (octave + 1) + pc


# ─────────────────────────────────────────────────────────────────────────────
# LilyPond pitch + duration
# ─────────────────────────────────────────────────────────────────────────────
LY_LETTER_ORDER = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
LY_LETTER_NATURAL_PC = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}


def music21_key_to_ly(key_root_str, mode):
    """'B-' → 'bes \\major', 'F#' → 'fis \\minor'. Defaults to c \\major."""
    if not key_root_str:
        return 'c \\major'
    letter = key_root_str[0].lower()
    accid = ''
    for ch in key_root_str[1:]:
        if ch == '#':
            accid = 'is'
        elif ch in ('-', 'b'):
            accid = 'es'
    mode_str = '\\major' if mode == 'major' else '\\minor'
    return f'{letter}{accid} {mode_str}'


def key_pc_to_ly_spelling(key_root_str, mode):
    """For a diatonic scale in this key, map pc → LilyPond spelling (e.g. 'bes', 'ees').

    LilyPond is smart about courtesy accidentals — if the key sig already
    says a pitch is flat/sharp, writing it with the matching Dutch name
    doesn't print a redundant accidental.
    """
    if not key_root_str:
        return {}
    tonic_letter = key_root_str[0].lower()
    if tonic_letter not in LY_LETTER_ORDER:
        return {}
    tonic_pc = parse_key_root(key_root_str)
    steps = MAJOR_STEPS if mode == 'major' else MINOR_STEPS
    start = LY_LETTER_ORDER.index(tonic_letter)
    result = {}
    for i in range(7):
        letter = LY_LETTER_ORDER[(start + i) % 7]
        natural_pc = LY_LETTER_NATURAL_PC[letter]
        target_pc = (tonic_pc + steps[i]) % 12
        diff = (target_pc - natural_pc) % 12
        if diff == 0:
            spelling = letter
        elif diff == 1:
            spelling = letter + 'is'
        elif diff == 2:
            spelling = letter + 'isis'
        elif diff == 11:
            spelling = letter + 'es'
        elif diff == 10:
            spelling = letter + 'eses'
        else:
            spelling = letter
        result[target_pc] = spelling
    return result


_CHROMATIC_DEFAULTS = {
    0: 'c', 1: 'cis', 2: 'd', 3: 'ees', 4: 'e', 5: 'f',
    6: 'fis', 7: 'g', 8: 'aes', 9: 'a', 10: 'bes', 11: 'b',
}


def midi_to_lilypond(midi, pc_spelling=None):
    """MIDI → LilyPond absolute pitch notation (e.g. 'bes', 'c'', 'f,,').

    Uses key-aware spelling when pc_spelling is supplied, else falls back
    to a chromatic default map.
    """
    pc = midi % 12
    spelling = (pc_spelling or {}).get(pc) or _CHROMATIC_DEFAULTS[pc]
    letter = spelling[0]
    natural_pc = LY_LETTER_NATURAL_PC[letter]
    if 'isis' in spelling:
        accid_offset = 2
    elif 'eses' in spelling:
        accid_offset = -2
    elif 'is' in spelling:
        accid_offset = 1
    elif 'es' in spelling:
        accid_offset = -1
    else:
        accid_offset = 0
    # Bare letter (e.g. 'c') in LilyPond absolute = MIDI 48 (C3).
    spelled_at_nat_oct = natural_pc + 48 + accid_offset
    octave_diff = (midi - spelled_at_nat_oct) // 12
    if octave_diff > 0:
        return spelling + "'" * octave_diff
    elif octave_diff < 0:
        return spelling + ',' * (-octave_diff)
    return spelling


# Quarter-length → LilyPond duration string.  Covers standard note values
# with up to one dot; add tied pairs if we ever hit anything weird.
_DUR_MAP = {
    0.0625: '32',  0.09375: '32.',
    0.125: '32',   0.1875: '32.',    # treat 0.125 as 32 (unlikely in hymns)
    0.25: '16',    0.375: '16.',
    0.5: '8',      0.75: '8.',
    1.0: '4',      1.5: '4.',
    2.0: '2',      3.0: '2.',
    4.0: '1',      6.0: '1.',
    8.0: '\\breve',
}


def ql_to_lilypond_duration(ql):
    """Quarter-length → LilyPond duration string ('4', '2.', '8', etc.)."""
    # Round to 1/32 grid to avoid float drift
    key = round(ql * 32) / 32
    if key in _DUR_MAP:
        return _DUR_MAP[key]
    # Fallback: pick the nearest standard duration
    for v, s in _DUR_MAP.items():
        if abs(ql - v) < 1e-3:
            return s
    return '4'


def midis_to_lilypond_chord(midis, pc_spelling=None):
    """[60, 64, 67] → "<c' e' g'>" (or a single pitch if only one MIDI)."""
    if not midis:
        return 'r'
    if len(midis) == 1:
        return midi_to_lilypond(midis[0], pc_spelling)
    return '<' + ' '.join(midi_to_lilypond(m, pc_spelling) for m in midis) + '>'


def chord_label_markup(assignment):
    """Build a LilyPond \\markup block for the bar's chord fraction.

    Approximates the reharm-sheet \\fracA styling:
      RH roman on top (blue), LH roman below (red), figures underneath (grey).
    Returned string is the *content* of a \\markup { ... } block.
    """
    if not assignment:
        return None
    lh_rom = (assignment.get('lh_rom') or assignment.get('rn') or '').strip()
    rh_rom = (assignment.get('rh_rom') or assignment.get('rn') or '').strip()
    # Colors from HymnReharmTemplate.tex: rhcol=#1F4E79, lhcol=#7B2B2B
    rh_color = '#(rgb-color 0.122 0.306 0.475)'
    lh_color = '#(rgb-color 0.482 0.169 0.169)'
    parts = [
        render_rn_markup(rh_rom, rh_color),
        render_rn_markup(lh_rom, lh_color),
    ]
    # Tighten baseline-skip so RH and LH chord fractions sit close together.
    return "\\override #'(baseline-skip . 1.8) \\center-column { " + ' '.join(parts) + ' }'


def render_rn_markup(rn_str, color):
    """Render 'V7iii' → LilyPond markup: V bold, 7 plain, 3 superscript.

    The chord system spells inversions as trailing 'i'/'ii'/'iii' on the
    roman numeral (e.g. V7iii = V7 third-inversion). The \\fracA macro in
    HymnReharmTemplate.tex renders the inversion digit as a superscript
    via \\inv{...}; we do the same with LilyPond's \\raise + \\smaller.
    """
    if not rn_str:
        return f'\\with-color {color} ""'
    m = re.match(r'^([b#]?[ivIV]+)(.*)$', rn_str)
    base, tail = (m.group(1), m.group(2)) if m else (rn_str, '')
    inv_num = ''
    for suffix, digit in (('iii', '3'), ('ii', '2'), ('i', '1')):
        if tail.endswith(suffix):
            inv_num = digit
            tail = tail[:-len(suffix)]
            break
    pieces = [f'\\bold "{base}"']
    if tail:
        pieces.append(f'"{tail}"')
    if inv_num:
        pieces.append(f'\\raise #0.6 \\smaller "{inv_num}"')
    return f'\\with-color {color} \\concat {{ ' + ' '.join(pieces) + ' }'


def events_to_lilypond_bar(events, full_bar_ql, pc_spelling=None,
                            arpeggiate=False, dynamic=None, label=None):
    """Convert one voice's events in a bar to LilyPond notation.

    Returns something like "f'4. g'8 f'4 d'2." for melody.
    If `label` is a markup string, attaches `^\\markup { label }` to the first
    note — renders as a chord-fraction annotation above the bar.
    """
    events = sorted(events, key=lambda e: e['offset_ql'])
    if not events:
        return f'r{ql_to_lilypond_duration(full_bar_ql)}'

    out = []
    dyn_applied = False
    label_applied = False
    for e in events:
        pieces = []
        if e.get('ornament_midis'):
            # Sequence of grace notes (e.g. enclosure: upper + lower neighbor).
            seq = ' '.join(
                midi_to_lilypond(m, pc_spelling) + '16'
                for m in e['ornament_midis']
            )
            pieces.append('\\acciaccatura { ' + seq + ' }')
        if e.get('grace_midis'):
            grace_chord = midis_to_lilypond_chord(e['grace_midis'], pc_spelling)
            pieces.append('\\acciaccatura { ' + grace_chord + '8 }')
        chord = midis_to_lilypond_chord(e['midis'], pc_spelling)
        dur = ql_to_lilypond_duration(e['duration_ql'])
        note = chord + dur
        # Chord-fraction label above the first note of the bar.
        if label and not label_applied:
            note += '^\\markup { ' + label + ' }'
            label_applied = True
        # Dynamic attaches to the first note of the bar only.
        if dynamic and not dyn_applied:
            note += '\\' + dynamic
            dyn_applied = True
        # Arpeggio for multi-note chords.
        if arpeggiate and len(e.get('midis', [])) > 1:
            note += '\\arpeggio'
        pieces.append(note)
        out.append(' '.join(pieces))
    return ' '.join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Bar data extraction
# ─────────────────────────────────────────────────────────────────────────────
def bar_melody_notes(s1v1, bar_num):
    """Return list of {'beat', 'duration_ql', 'midi'} for a single bar."""
    notes = []
    for n in s1v1:
        if n.get('bar') != bar_num:
            continue
        if n.get('is_rest'):
            continue
        midi = pitch_to_midi(n.get('pitch'))
        if midi is None:
            continue
        notes.append({
            'beat': n.get('beat', 1),
            'offset_ql': n.get('offset_ql', 0),
            'duration_ql': n.get('duration_ql', 1),
            'midi': midi,
        })
    return notes


def bar_assignment(assignments, bar_num):
    for a in assignments:
        if a.get('bar') == bar_num:
            return a
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Layout — unchanged from ABC version (backend-agnostic)
# ─────────────────────────────────────────────────────────────────────────────
def layout_bar_grand(assignment, melody_notes, key_root, mode, meter_num, meter_den,
                      next_assignment=None):
    """Return per-bar events for each voice.  See PLAN.md's style palette.

    `next_assignment` is unused here (grand-chord style doesn't look ahead).
    Accepted for signature compatibility with pickup-aware layouts.
    """
    lh_fig = assignment.get('lh_fig') or assignment.get('lh_figure', '')
    rh_fig = assignment.get('rh_fig') or assignment.get('rh_figure', '')
    rn = assignment.get('rn', '')
    bar_duration = meter_num * (4.0 / meter_den)

    # Pedal grace note — RN root at harp's low octave, rings under everything
    grace_midis = []
    root_degree = rn_to_root_degree(rn)
    if root_degree:
        pedal_midi = string_to_midi(root_degree, key_root, mode, base_octave=1)
        while pedal_midi < HARP_LOW_MIDI:
            pedal_midi += 12
        grace_midis = [pedal_midi]

    # LH figure in bass register.  If the pedal grace happens to share a
    # pitch with the LH bottom, accept the unison — it reads as a quick
    # grace-note re-strike of the same string on harp, which is idiomatic.
    # Never shift LH up (lands moving notes in treble and crosses RH).
    lh_events = []
    if lh_fig:
        lh_strings = figure_to_strings(lh_fig)
        lh_midis = [string_to_midi(s, key_root, mode, base_octave=2) for s in lh_strings]
        lh_events.append({
            'offset_ql': 0.0,
            'duration_ql': bar_duration,
            'midis': lh_midis,
            'grace_midis': grace_midis,
        })
    elif grace_midis:
        lh_events.append({
            'offset_ql': 0.0,
            'duration_ql': bar_duration,
            'midis': grace_midis,
        })

    # RH fill: octave-down if above melody top, drop pitches that double melody
    rh_events = []
    if rh_fig:
        rh_strings = figure_to_strings(rh_fig)
        rh_midis = [string_to_midi(s, key_root, mode, base_octave=3) for s in rh_strings]
        melody_midis = {n['midi'] for n in melody_notes}
        if melody_notes:
            melody_top = max(n['midi'] for n in melody_notes)
            while rh_midis and max(rh_midis) > melody_top:
                rh_midis = [m - 12 for m in rh_midis]
        rh_midis = [m for m in rh_midis if m not in melody_midis]
        if rh_midis:
            rh_events.append({
                'offset_ql': 0.0,
                'duration_ql': bar_duration,
                'midis': rh_midis,
            })

    melody_events = [
        {'offset_ql': n['offset_ql'] - (n['offset_ql'] // bar_duration) * bar_duration,
         'duration_ql': n['duration_ql'],
         'midis': [n['midi']]}
        for n in melody_notes
    ]
    return {'lh_events': lh_events, 'rh_events': rh_events,
            'melody_events': melody_events}


def _chord_then_motion(base_lh_events, bar_duration, tail_midi):
    """Shared layout: beat-1 block chord (arpeggiated, with grace pedal) +
    eighth-note arpeggio through the middle beats + a quarter-note tail on
    the final beat (pickup or landing tone).

    Harp strings ring after the strum, so the chord remains audible while
    the moving notes play on top — single-voice, no extra notation.
    """
    new_lh = []
    for ev in base_lh_events:
        midis = ev['midis']
        grace = ev.get('grace_midis')
        if len(midis) <= 1:
            new_lh.append(ev)
            continue

        # Beat 1 — block chord (quarter), arpeggiated, carries the grace pedal
        new_lh.append({
            'offset_ql': 0.0,
            'duration_ql': 1.0,
            'midis': midis,
            'grace_midis': grace,
        })

        # Middle beats — fill with eighth-note arpeggio of upper chord tones
        mid_start = 1.0
        mid_end = bar_duration - 1.0
        num_eighths = max(0, int(round((mid_end - mid_start) / 0.5)))
        arp_pool = midis[1:] if len(midis) > 1 else midis
        for i in range(num_eighths):
            new_lh.append({
                'offset_ql': mid_start + i * 0.5,
                'duration_ql': 0.5,
                'midis': [arp_pool[i % len(arp_pool)]],
            })

        # Final beat — pickup or landing tone (quarter)
        if mid_end < bar_duration - 1e-6:
            new_lh.append({
                'offset_ql': mid_end,
                'duration_ql': 1.0,
                'midis': [tail_midi],
            })
    return new_lh


def layout_bar_strum_pickup(assignment, melody_notes, key_root, mode,
                              meter_num, meter_den, next_assignment=None):
    """Beat-1 strum + eighth-note arpeggio + pickup-tone on the final beat
    that walks (upper diatonic neighbor) to the NEXT bar's chord root.

    Diatonic-only.  Falls back to grand-chord when there's no next bar.
    """
    base = layout_bar_grand(assignment, melody_notes, key_root, mode,
                             meter_num, meter_den)
    if next_assignment is None:
        return base
    next_root = rn_to_root_degree(next_assignment.get('rn', ''))
    if not next_root:
        return base

    bar_duration = meter_num * (4.0 / meter_den)
    if bar_duration < 2.0 + 1e-6:
        return base   # too short to fit chord + tail; keep grand_chord

    # Pickup target — upper diatonic neighbor of next root, kept in the
    # same bass register as the LH chord so we don't leap up to the RH.
    ref = base['lh_events'][0]['midis'][0] if base['lh_events'] else HARP_LOW_MIDI + 12
    target = string_to_midi(next_root, key_root, mode, base_octave=2)
    while target < ref - 7:
        target += 12
    pickup_midi = diatonic_neighbor(target, key_root, mode, +1)

    base['lh_events'] = _chord_then_motion(base['lh_events'], bar_duration,
                                            pickup_midi)
    return base


def layout_bar_mellow_pair(assignment, melody_notes, key_root, mode,
                            meter_num, meter_den, next_assignment=None):
    """Mid-phrase style: re-strike the LH figure at mid-bar for rhythmic
    re-articulation instead of one held block."""
    base = layout_bar_grand(assignment, melody_notes, key_root, mode,
                             meter_num, meter_den)
    bar_duration = meter_num * (4.0 / meter_den)
    half = bar_duration / 2.0
    # Split each LH event into two halves (keep the grace on the first half only)
    split_events = []
    for ev in base['lh_events']:
        midis = ev['midis']
        grace = ev.get('grace_midis')
        split_events.append({
            'offset_ql': 0.0, 'duration_ql': half,
            'midis': midis,
            'grace_midis': grace,
        })
        split_events.append({
            'offset_ql': half, 'duration_ql': half,
            'midis': midis,
        })
    base['lh_events'] = split_events
    return base


def layout_bar_cadence_arp(assignment, melody_notes, key_root, mode,
                             meter_num, meter_den, next_assignment=None):
    """Cadential variant: beat-1 strum + eighth arpeggio + landing on the
    chord root (bottom of the figure) on the final beat.  Same skeleton as
    strum_pickup but stays on the chord for resolution.
    """
    base = layout_bar_grand(assignment, melody_notes, key_root, mode,
                             meter_num, meter_den)
    bar_duration = meter_num * (4.0 / meter_den)
    if bar_duration < 2.0 + 1e-6:
        return base
    if not base['lh_events']:
        return base
    landing = base['lh_events'][0]['midis'][0]
    base['lh_events'] = _chord_then_motion(base['lh_events'], bar_duration,
                                            landing)
    return base


def pick_style(bar_num, phrases, is_last_bar=False):
    """Return the style name for this bar.

    - Very first bar & very last bar → 'grand_chord' (frame the piece)
    - Other phrase-ending bars → 'cadence_arp' (arpeggio + landing tone)
    - Everything else (interior + phrase-openers) → 'strum_pickup'
      (arpeggio + approach tone into next chord)
    """
    if is_last_bar or bar_num == 1:
        return 'grand_chord'
    for p in phrases or []:
        pb = p.get('bars') or []
        if bar_num not in pb:
            continue
        if bar_num == pb[-1]:
            return 'cadence_arp'
        return 'strum_pickup'
    return 'grand_chord'


_STYLE_LAYOUTS = {
    'grand_chord': layout_bar_grand,
    'mellow_pair': layout_bar_mellow_pair,
    'strum_pickup': layout_bar_strum_pickup,
    'cadence_arp': layout_bar_cadence_arp,
}


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — entrance ornaments (enclosure on phrase-ending melody notes)
# ─────────────────────────────────────────────────────────────────────────────
def diatonic_neighbor(midi, key_root, mode, direction):
    """Return the MIDI of the diatonic note one scale-step ±1 from `midi`.

    direction=+1 → upper neighbor; direction=-1 → lower neighbor.
    If `midi` is chromatic (not on the scale), fall back to ±2 semitones.
    """
    tonic_pc = parse_key_root(key_root)
    steps = MAJOR_STEPS if mode == 'major' else MINOR_STEPS
    pc_above = (midi - tonic_pc) % 12
    if pc_above not in steps:
        return midi + direction * 2
    idx = steps.index(pc_above)
    new_idx = idx + direction
    octave_shift = 0
    if new_idx < 0:
        new_idx += 7
        octave_shift = -1
    elif new_idx >= 7:
        new_idx -= 7
        octave_shift = 1
    orig_octaves = (midi - tonic_pc) // 12
    return tonic_pc + 12 * (orig_octaves + octave_shift) + steps[new_idx]


def add_phrase_ending_ornaments(bars, phrases, key_root, mode):
    """On the LAST melody note of each phrase, add an enclosure
    (upper-neighbor + lower-neighbor grace-note pair).

    Only applied if the target note is ≥ 1.0 quarter-length (leaves
    transit time for the two quick graces).  Density hovers around 5 / N
    where N = total melody notes — well inside the plan's 25% cap.
    """
    for p in phrases or []:
        pb = p.get('bars') or []
        if not pb:
            continue
        final_bar = pb[-1]
        if final_bar < 1 or final_bar > len(bars):
            continue
        mel_events = bars[final_bar - 1].get('melody_events') or []
        if not mel_events:
            continue
        last = max(mel_events, key=lambda e: e['offset_ql'])
        if last.get('duration_ql', 0) < 1.0:
            continue
        target = last['midis'][0]
        upper = diatonic_neighbor(target, key_root, mode, +1)
        lower = diatonic_neighbor(target, key_root, mode, -1)
        last['ornament_midis'] = [upper, lower]


# ─────────────────────────────────────────────────────────────────────────────
# LilyPond emission
# ─────────────────────────────────────────────────────────────────────────────
_LY_TEMPLATE = r"""\version "2.22.1"

\header {
  title = "__TITLE__"
  subtitle = "__SUBTITLE__"
  tagline = ##f
}

global = {
  \key __KEYSIG__
  \time __METER__
}

upper = {
  \global
  <<
    { \voiceOne __MELODY__ }
    { \voiceTwo __RHFILL__ }
  >>
}

lower = {
  \clef bass
  \global
  __LH__
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=__BPM__ }
}
"""


def emit_lilypond(title, key_root, mode, meter_num, meter_den, bpm, bars,
                   subtitle=None):
    """Build a complete .ly source string for the piano score."""
    keysig = music21_key_to_ly(key_root, mode)
    pc_spelling = key_pc_to_ly_spelling(key_root, mode)
    full_bar_ql = meter_num * (4.0 / meter_den)

    def voice_line(events_key, arpeggiate, dynamic, with_labels=False):
        parts = []
        for i, bar in enumerate(bars):
            dyn = dynamic if i == 0 else None
            label = bar.get('label_markup') if with_labels else None
            parts.append(events_to_lilypond_bar(
                bar.get(events_key, []), full_bar_ql,
                pc_spelling, arpeggiate=arpeggiate, dynamic=dyn, label=label))
        # Join bars with bar lines
        return ' | '.join(parts) + ' |'

    melody = voice_line('melody_events', arpeggiate=False, dynamic='mf', with_labels=True)
    rh_fill = voice_line('rh_events', arpeggiate=True, dynamic='p')
    lh = voice_line('lh_events', arpeggiate=True, dynamic='p')

    if subtitle is None:
        subtitle = ''

    ly = _LY_TEMPLATE
    ly = ly.replace('__TITLE__', title.replace('"', r'\"'))
    ly = ly.replace('__SUBTITLE__', subtitle.replace('"', r'\"'))
    ly = ly.replace('__KEYSIG__', keysig)
    ly = ly.replace('__METER__', f'{meter_num}/{meter_den}')
    ly = ly.replace('__BPM__', str(int(bpm)))
    ly = ly.replace('__MELODY__', melody)
    ly = ly.replace('__RHFILL__', rh_fill)
    ly = ly.replace('__LH__', lh)
    return ly


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def get_hymn_id(title, export_dir='hymnal_export'):
    """Return zero-padded 3-digit ID matching review.html's numbering.

    review.html assigns IDs by case-insensitive alphabetical sort of all
    hymnal_export/*.json titles, 1-indexed, zero-padded to 3 digits.
    """
    titles = []
    for path in glob.glob(os.path.join(export_dir, '*.json')):
        try:
            with open(path) as f:
                d = json.load(f)
            t = d.get('title') or os.path.splitext(os.path.basename(path))[0]
            titles.append(t)
        except Exception:
            pass
    titles.sort(key=lambda s: s.lower())
    for i, t in enumerate(titles):
        if t == title:
            return f'{i + 1:03d}'
    return None


def build_score(export_json_path, reharm_json_path):
    with open(export_json_path) as f:
        export = json.load(f)
    with open(reharm_json_path) as f:
        reharm = json.load(f)

    title = export.get('title', 'Untitled')
    # Prefix with the 3-digit zero-padded hymn ID (same numbering as review.html)
    hid = get_hymn_id(title)
    if hid:
        title = f'{hid}  {title}'   # e.g. "228  Silent Night"
    music = export.get('music', {})
    key_root = music.get('key_root', 'C')
    mode = music.get('mode', 'major')
    meter = music.get('meter', '4/4')
    meter_num, meter_den = map(int, meter.split('/'))
    bpm = music.get('bpm') or 80
    total_bars = music.get('total_bars', 0)

    s1v1 = export.get('voices', {}).get('S1V1', [])
    assignments = reharm.get('assignments', [])
    phrases = reharm.get('phrases', [])

    # Resolve per-bar assignments with carry-forward so lookup of "next bar's
    # chord" always works for approach-tone pickups.
    assignments_by_bar = {}
    last_a = None
    for bar_num in range(1, total_bars + 1):
        a = bar_assignment(assignments, bar_num)
        if a is None and last_a is not None:
            a = last_a
        if a is not None:
            last_a = a
        assignments_by_bar[bar_num] = a

    bars = []
    for bar_num in range(1, total_bars + 1):
        melody_notes = bar_melody_notes(s1v1, bar_num)
        assignment = assignments_by_bar.get(bar_num)
        next_assignment = assignments_by_bar.get(bar_num + 1)
        if assignment is None:
            bars.append({
                'lh_events': [],
                'rh_events': [],
                'melody_events': [
                    {'offset_ql': n['offset_ql'] - (n['offset_ql'] // (meter_num * 4.0 / meter_den)) * (meter_num * 4.0 / meter_den),
                     'duration_ql': n['duration_ql'],
                     'midis': [n['midi']]}
                    for n in melody_notes
                ],
            })
            continue
        is_last = (bar_num == total_bars)
        style = pick_style(bar_num, phrases, is_last_bar=is_last)
        layout_fn = _STYLE_LAYOUTS.get(style, layout_bar_grand)
        bar_data = layout_fn(assignment, melody_notes,
                              key_root, mode, meter_num, meter_den,
                              next_assignment=next_assignment)
        bar_data['label_markup'] = chord_label_markup(assignment)
        bars.append(bar_data)

    # Phase 2: entrance ornaments on phrase-ending melody notes.
    add_phrase_ending_ornaments(bars, phrases, key_root, mode)

    subtitle = f'\u2669 = {int(bpm)}'   # quarter-note = BPM in the subtitle area
    return emit_lilypond(title, key_root, mode, meter_num, meter_den, bpm, bars,
                          subtitle=subtitle)


def run_lilypond(ly_path, emit_svg=False):
    """Invoke lilypond CLI to produce PDF (+ SVG, + MIDI)."""
    ly_dir = os.path.dirname(os.path.abspath(ly_path)) or '.'
    ly_base = os.path.splitext(os.path.basename(ly_path))[0]

    cmd = ['lilypond', '-dno-point-and-click', '-o', ly_base]
    if emit_svg:
        cmd += ['-dbackend=svg']
    cmd.append(os.path.basename(ly_path))

    result = subprocess.run(cmd, cwd=ly_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print('--- lilypond stderr ---', file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        print('--- lilypond stdout ---', file=sys.stderr)
        print(result.stdout, file=sys.stderr)
    else:
        # Short summary
        tail = [ln for ln in result.stderr.splitlines() if ln.strip()][-3:]
        for ln in tail:
            print(ln, file=sys.stderr)
    return result.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('export_json', nargs='?')
    ap.add_argument('reharm_json', nargs='?')
    ap.add_argument('-o', '--output', required=True,
                     help='Output .ly path (LilyPond also writes .pdf and .midi next to it)')
    ap.add_argument('--title', help='Resolve JSON paths by title substring')
    ap.add_argument('--svg', action='store_true',
                     help='Also produce .svg via `lilypond -dbackend=svg`')
    ap.add_argument('--no-compile', action='store_true',
                     help='Write only the .ly source; skip the lilypond invocation')
    args = ap.parse_args()

    if args.title:
        slug = re.sub(r'[^A-Za-z0-9]+', '_', args.title).strip('_')
        export_candidates = glob.glob(f'hymnal_export/*{slug}*.json') + glob.glob(f'hymnal_export/{slug}.json')
        reharm_candidates = glob.glob(f'hymnal_html/reharms/*{slug}*.json') + glob.glob(f'hymnal_html/reharms/{slug}.json')
        if not export_candidates or not reharm_candidates:
            print(f"Could not resolve title {args.title!r}", file=sys.stderr)
            sys.exit(2)
        args.export_json = export_candidates[0]
        args.reharm_json = reharm_candidates[0]

    if not args.export_json or not args.reharm_json:
        ap.error('Need either both export_json + reharm_json, or --title')

    ly = build_score(args.export_json, args.reharm_json)
    with open(args.output, 'w') as f:
        f.write(ly)
    print(f'Wrote {args.output} ({len(ly)} chars)', file=sys.stderr)

    if args.no_compile:
        return

    if not shutil.which('lilypond'):
        print('lilypond not found in PATH — skipping compile step', file=sys.stderr)
        return

    rc = run_lilypond(args.output, emit_svg=args.svg)
    if rc != 0:
        sys.exit(rc)


if __name__ == '__main__':
    main()
