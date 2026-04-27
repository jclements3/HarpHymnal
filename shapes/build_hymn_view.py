#!/usr/bin/env python3
"""Render a hymn JSON (data/hymns/<slug>.json) as a multi-level shape-table
practice page.

Each bar gets a row with **Shape | Bar | Chord | Melody** columns. The Shape
column carries one shape per level (SATB, retab L1-L7, reharm L1-L7); a
selector at the top of the page swaps which one is visible.

Shape templates per level approximate the texture / harmonic-substitution
intent of the existing retab and reharm pipelines:

  SATB        2L^N3 4R^N3    bass + tenor (oct 2) + alto + soprano (oct 4)
  retab L1    2L^N3 4R^N3    SATB keyboard reduction (block chords)
  retab L2    2L^N           lead sheet — bass only, melody plays separately
  retab L3    2L^N 3R^N33    trefoil block-135 triad
  retab L4    2L^N 3R^N33    same shape, phrase-role rhythm differs
  retab L5    1L^N 3R^N333   + structural low-bass anchor (oct 1) + tetrad
  retab L6    1L^N 3R^N346   + trefoil-path contour: universal-winner tetrad
  retab L7    1L^N 3R^N1333,3333  full harp texture: 8-finger comma tower
  reharm L1   2L^N 3R^N33    baseline diatonic triads
  reharm L2   2L^N 3R^N333   diatonic 7ths (Imaj7, ii7, V7, ...)
  reharm L3   substitution (I→vi7, IV→ii7, V→iii7) on top of L2
  reharm L4   relative-minor (vi-centred); same shape, chord re-aimed
  reharm L5   modal (Dorian/Mix/Lyd/Phrygian section); add9 colour
  reharm L6   chromatic-mediant slash chords
  reharm L7   voice-leading-first; pick universal-winner per chord

Where a reharm level rewrites the chord, the Chord column shows the new
Roman numeral; the Shape column tracks the rewritten degree.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHAPES = REPO / 'shapes'
sys.path.insert(0, str(SHAPES))
from abc_satb import extract_satb_per_bar, Pitch  # noqa: E402
from phrase_select import (  # noqa: E402
    select_anchor, mark_resets, fallback_shape, AnchorChoice,
)
from voice_lead import (  # noqa: E402
    Voice, chord_letters, initial_voicing_for, initial_voicing_with_melody,
    solve_next_voicing, voicing_motion, voicing_to_shape_html,
)
from render_phrase_svg import render_phrase_svg  # noqa: E402
from render_phrase_midi import render_phrase_midi  # noqa: E402
from render_chopin_piano import render_phrase_piano_svg  # noqa: E402

# Diatonic letter index for scale-step calculations (Tonic C of any major key
# normalises against this 7-letter cycle; key-root offset gives the degree).
SCALE_INDEX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}

NUMERAL_TO_DEGREE: dict[str, int] = {
    'I': 1, 'i': 1,
    'II': 2, 'ii': 2, 'ii°': 2,
    'III': 3, 'iii': 3,
    'IV': 4, 'iv': 4,
    'V': 5, 'v': 5,
    'VI': 6, 'vi': 6,
    'VII': 7, 'vii': 7, 'vii°': 7,
}

# Texture templates — `{N}` slot for the degree digit (1-7). A "no-shape"
# value of None means the level has no rendered shape for that bar (used
# by retab L2 lead-sheet, where the LH alone carries the harmony).
RETAB_TEMPLATES: dict[str, str] = {
    'retab-L1': '2L{N}3 4R{N}3',
    'retab-L2': '2L{N}',
    'retab-L3': '2L{N} 3R{N}33',
    'retab-L4': '2L{N} 3R{N}33',
    'retab-L5': '1L{N} 3R{N}333',
    'retab-L6': '1L{N} 3R{N}346',
    'retab-L7': '1L{N} 3R{N}1333,3333',
}

REHARM_FLAT: dict[str, str] = {
    'reharm-L1': '2L{N} 3R{N}33',
    'reharm-L2': '2L{N} 3R{N}333',
}

# Functional substitution map for reharm-L3 (jazz "tonic family" subs).
# Maps Ionian-relative numeral → substitute numeral.
L3_SUB = {
    'I':   'vi',   # tonic → relative minor (vim7)
    'IV':  'ii',   # subdominant → ii7
    'V':   'iii',  # dominant → iii7 (deceptive feel)
}

# Relative-minor (L4): everything stays diatonic but tonicises vi.
# Practical effect on a Roman numeral is identity — the centre shifts
# without rewriting the local symbols.
def _l4_recentre(numeral: str, quality: str) -> tuple[str, str]:
    return numeral, '7' if quality != '7' else quality

# Modal (L5): keep the numeral, swap quality to add-9 colour.
def _l5_modal(numeral: str, quality: str) -> tuple[str, str]:
    return numeral, '(add9)'

# Slash-chord (L6): turn V → V/I and IV → IV/V for chromatic motion.
L6_SUB = {
    'V':  ('V',  '/I'),
    'IV': ('IV', '/V'),
}

# Voice-leading (L7): keep the numeral but use the universal-winner 346
# voicing across all chords.
L7_SHAPE = '1L{N} 3R{N}346'


def _melody_str(melody: list[dict]) -> str:
    parts: list[str] = []
    for n in melody:
        if n.get('kind') == 'note':
            p = n['pitch']
            acc = p.get('accidental') or ''
            parts.append(f"{p['letter']}{acc}{p['octave']}")
        elif n.get('kind') == 'rest':
            parts.append('·')
    return ' '.join(parts)


def _hat(d: int) -> str:
    return f'<span class="deg">{d}̂</span>'


# 47-string concert pedal harp: position 1 = C1, position 47 = G7. Sharps
# and flats share a string with their natural (the pedal sets the actual
# pitch); only the letter matters for the strings-row visualization.
_LETTERS = 'CDEFGAB'
_HARP_STRINGS = 47


def _string_position(letter: str, octave: int) -> int | None:
    if letter not in _LETTERS:
        return None
    pos = (octave - 1) * 7 + _LETTERS.index(letter) + 1
    return pos if 1 <= pos <= _HARP_STRINGS else None


def _strings_row_html(pitches: list[tuple[str, int]]) -> str:
    if not pitches:
        return ''
    row = ['·'] * _HARP_STRINGS
    for letter, octave in pitches:
        pos = _string_position(letter, octave)
        if pos is not None:
            row[pos - 1] = letter
    return '<code class="strings-row">' + ''.join(row) + '</code>'


def _scale_letter(degree: int, key_root: str) -> str:
    """Diatonic letter for `degree` (1-7) of the major key whose tonic
    letter is the first character of `key_root`. Accidentals are dropped
    — the strings-row only needs natural letters."""
    key_letter = key_root[0]
    return _LETTERS[(SCALE_INDEX[key_letter] + degree - 1) % 7]


def _step_up(letter: str, octave: int, n_steps: int) -> tuple[str, int]:
    """Climb `n_steps` diatonic steps from (letter, octave). 0 = unison."""
    idx = _LETTERS.index(letter) + n_steps
    return _LETTERS[idx % 7], octave + idx // 7


def _expand_template_pitches(template: str, degree: int, key_root: str) -> list[tuple[str, int]]:
    """Expand a shape template like '2L{N}3 4R{N}33' into (letter, octave)
    pitches. Each space-separated token is one hand: octave digit + hand
    letter + {N} placeholder + interval-digit string.
    """
    if not template or degree == 0:
        return []
    import re as _re
    pitches: list[tuple[str, int]] = []
    for tok in template.split():
        m = _re.match(r'(\d)[LRx]\{N\}([0-9a-f,]*)', tok)
        if not m:
            continue
        octave_digit = int(m.group(1))
        intervals_str = m.group(2)
        bottom_letter = _scale_letter(degree, key_root)
        cur = (bottom_letter, octave_digit)
        pitches.append(cur)
        for ch in intervals_str:
            if ch == ',':
                continue
            try:
                gap = int(ch, 16)
            except ValueError:
                continue
            steps = max(0, gap - 1)
            cur = _step_up(cur[0], cur[1], steps)
            pitches.append(cur)
    return pitches


def _shape_html(template: str, degree: int) -> str:
    """Inline the degree digit (with its hat span) into a shape template."""
    if degree == 0 or template is None:
        return ''
    rendered = template.replace('{N}', f'<HAT>{degree}</HAT>')
    rendered = rendered.replace('<HAT>', '<span class="deg">').replace('</HAT>', '̂</span>')
    return rendered


def _diatonic_steps(p1: Pitch, p2: Pitch) -> int:
    """Number of scale steps from p1 up to p2 (zero for unison)."""
    return (SCALE_INDEX[p2.letter] - SCALE_INDEX[p1.letter]) + (p2.octave - p1.octave) * 7


def _degree_in_key(letter: str, key_root: str) -> int:
    """Scale degree 1-7 of `letter` in the major key whose tonic letter is
    the first character of `key_root` (e.g. 'Bb' → tonic letter 'B')."""
    key_letter = key_root[0]
    return ((SCALE_INDEX[letter] - SCALE_INDEX[key_letter]) % 7) + 1


def _interval_digit(steps: int) -> str:
    """Convert scale-step count to an interval digit. 0 steps (unison) is
    invalid as an intra-shape interval, so the caller should detect it."""
    interval_num = steps + 1
    return f'{interval_num:x}'


def _satb_shape_html(s: Pitch | None, a: Pitch | None,
                     t: Pitch | None, b: Pitch | None,
                     key_root: str) -> str:
    """Build the SATB shape token: LH dyad (bass+tenor) + RH dyad (alto+soprano).

    Each hand uses the pitch's actual harp octave and the degree of its
    bottom note relative to the hymn's tonic. The interval digit is the
    scale-step distance between the two notes in that hand.
    """
    if not (s and a and t and b):
        return ''

    bt_steps = _diatonic_steps(b, t)
    as_steps = _diatonic_steps(a, s)
    if bt_steps <= 0 or as_steps <= 0:
        # Crossed voices or a unison — bail to the chord-template SATB.
        return ''

    bass_deg = _degree_in_key(b.letter, key_root)
    alto_deg = _degree_in_key(a.letter, key_root)
    bt = _interval_digit(bt_steps)
    asp = _interval_digit(as_steps)
    return (
        f'{b.octave}L<span class="deg">{bass_deg}̂</span>{bt} '
        f'{a.octave}R<span class="deg">{alto_deg}̂</span>{asp}'
    )


def _level_shapes(numeral: str, quality: str, degree: int,
                  satb: tuple[Pitch | None, ...] | None = None,
                  key_root: str = 'C',
                  auto_shape: str = '', auto_chord: str = '',
                  auto_template: str = '', auto_degree: int = 0,
                  chopin_shape: str = '', chopin_chord: str = '',
                  chopin_voicing=None) -> dict[str, dict]:
    """Compute shape + chord-display + harp-string row per level for one bar."""
    out: dict[str, dict] = {}

    def lvl(shape: str, chord: str, pitches: list[tuple[str, int]]) -> dict:
        return {
            'shape': shape,
            'chord': chord,
            'strings': _strings_row_html(pitches),
        }

    base_chord = f'{numeral}{quality}'
    # SATB: actual hymn pitches if available, fall back to chord template.
    satb_shape = ''
    satb_pitches: list[tuple[str, int]] = []
    if satb:
        s, a, t, b = satb
        satb_shape = _satb_shape_html(s, a, t, b, key_root)
        satb_pitches = [(p.letter, p.octave) for p in (s, a, t, b) if p is not None]
    if not satb_shape:
        satb_shape = _shape_html('2L{N}3 4R{N}3', degree)
        satb_pitches = _expand_template_pitches('2L{N}3 4R{N}3', degree, key_root)
    out['SATB'] = lvl(satb_shape, base_chord, satb_pitches)

    for level, tmpl in RETAB_TEMPLATES.items():
        out[level] = lvl(
            _shape_html(tmpl, degree) if degree else '',
            base_chord,
            _expand_template_pitches(tmpl, degree, key_root) if degree else [],
        )

    # Reharm levels — may rewrite the chord.
    out['reharm-L1'] = lvl(
        _shape_html(REHARM_FLAT['reharm-L1'], degree),
        numeral,  # bare triad, drop quality
        _expand_template_pitches(REHARM_FLAT['reharm-L1'], degree, key_root),
    )
    out['reharm-L2'] = lvl(
        _shape_html(REHARM_FLAT['reharm-L2'], degree),
        f'{numeral}7' if numeral else '',
        _expand_template_pitches(REHARM_FLAT['reharm-L2'], degree, key_root),
    )

    # L3: functional sub
    sub_num = L3_SUB.get(numeral, numeral)
    sub_deg = NUMERAL_TO_DEGREE.get(sub_num, degree)
    out['reharm-L3'] = lvl(
        _shape_html('2L{N} 3R{N}333', sub_deg),
        f'{sub_num}7' if sub_num else '',
        _expand_template_pitches('2L{N} 3R{N}333', sub_deg, key_root),
    )

    # L4: relative-minor recentre
    n4, q4 = _l4_recentre(numeral, quality)
    out['reharm-L4'] = lvl(
        _shape_html('2L{N} 3R{N}333', degree),
        f'{n4}{q4}' if n4 else '',
        _expand_template_pitches('2L{N} 3R{N}333', degree, key_root),
    )

    # L5: modal (add9)
    n5, q5 = _l5_modal(numeral, quality)
    out['reharm-L5'] = lvl(
        _shape_html('2L{N} 3R{N}335', degree),
        f'{n5}{q5}' if n5 else '',
        _expand_template_pitches('2L{N} 3R{N}335', degree, key_root),
    )

    # L6: slash chord
    n6, slash6 = L6_SUB.get(numeral, (numeral, ''))
    out['reharm-L6'] = lvl(
        _shape_html('1L{N} 3R{N}356', degree),
        f'{n6}{slash6}' if n6 else '',
        _expand_template_pitches('1L{N} 3R{N}356', degree, key_root),
    )

    # L7: voice-leading universal-winner
    out['reharm-L7'] = lvl(
        _shape_html(L7_SHAPE, degree),
        f'{numeral}{quality}',
        _expand_template_pitches(L7_SHAPE, degree, key_root),
    )

    # Auto: phrase-anchor selector. Filled in by the caller, who knows the
    # phrase boundaries and runs select_anchor() once per phrase.
    out['auto'] = lvl(
        auto_shape,
        auto_chord or base_chord,
        _expand_template_pitches(auto_template, auto_degree, key_root)
            if auto_template and auto_degree else [],
    )

    # Chopin: voice-leading-first solver. Filled in by the caller, who walks
    # the voice-leading chain across all bars.
    chopin_pitches: list[tuple[str, int]] = []
    if chopin_voicing is not None:
        chopin_pitches = [
            (chopin_voicing.s.letter, chopin_voicing.s.octave),
            (chopin_voicing.a.letter, chopin_voicing.a.octave),
            (chopin_voicing.t.letter, chopin_voicing.t.octave),
            (chopin_voicing.b.letter, chopin_voicing.b.octave),
        ]
    out['chopin'] = lvl(
        chopin_shape,
        chopin_chord or base_chord,
        chopin_pitches,
    )

    return out


LEVEL_ORDER = [
    'SATB',
    'retab-L1', 'retab-L2', 'retab-L3', 'retab-L4',
    'retab-L5', 'retab-L6', 'retab-L7',
    'reharm-L1', 'reharm-L2', 'reharm-L3', 'reharm-L4',
    'reharm-L5', 'reharm-L6', 'reharm-L7',
    'auto',
    'chopin',
]

LEVEL_LABEL = {
    'SATB':      'SATB',
    'retab-L1':  'retab L1',
    'retab-L2':  'retab L2',
    'retab-L3':  'retab L3',
    'retab-L4':  'retab L4',
    'retab-L5':  'retab L5',
    'retab-L6':  'retab L6',
    'retab-L7':  'retab L7',
    'reharm-L1': 'reharm L1',
    'reharm-L2': 'reharm L2',
    'reharm-L3': 'reharm L3',
    'reharm-L4': 'reharm L4',
    'reharm-L5': 'reharm L5',
    'reharm-L6': 'reharm L6',
    'reharm-L7': 'reharm L7',
    'auto':      'auto',
    'chopin':    'chopin',
}

LEVEL_DESC = {
    'SATB':      'Original 4-voice setting: bass + tenor in octave 2, alto + soprano in octave 4 (close keyboard voicing).',
    'retab-L1':  'SATB close-score keyboard reduction (block chords, four per beat).',
    'retab-L2':  'Lead-sheet: LH bass alone, melody played separately. Two attacks per bar.',
    'retab-L3':  'Trefoil block-135 triads: bass + RH triad in octave 3.',
    'retab-L4':  'L3 + phrase-role articulation (timing only — same shape).',
    'retab-L5':  'L4 + structural low-bass anchor (octave 1) + RH diatonic-7th tetrad.',
    'retab-L6':  'L5 + trefoil-path contour: universal-winner 1346 open tetrad.',
    'retab-L7':  'L6 + full harp texture: 8-finger comma tower (rolled, sustained).',
    'reharm-L1': 'Baseline: bare diatonic triads, qualities stripped.',
    'reharm-L2': 'Diatonic 7ths: every triad lifted to its diatonic 7th-chord form.',
    'reharm-L3': 'Functional substitution: I→vi7, IV→ii7, V→iii7 (tonic-family rotations).',
    'reharm-L4': 'Relative-minor reharm: vi-centred with natural-minor v.',
    'reharm-L5': 'Modal section: add-9 colour replaces straight 7ths in the middle phrases.',
    'reharm-L6': 'Non-functional chromatic mediants and slash chords (V/I, IV/V).',
    'reharm-L7': 'Voice-leading-first: universal-winner 1346 voicing chosen per chord.',
    'auto':      'Phrase-anchor selector: one shape held for the whole phrase, with per-bar re-setups only on bars whose chord falls outside the anchor’s coverage.',
    'chopin':    'Voice-leading-first (Chopin-style): pick the 4-voice voicing closest to the previous bar. Each transition is annotated with the per-voice motion (S/A/T/B, semitones).',
}


def render_hymn(hymn_path: Path, chopin_only: bool = False) -> str:
    d = json.loads(hymn_path.read_text())
    title = d['title']
    key = d['key']
    meter = d['meter']
    bars = d['bars']
    phrases = d['phrases']

    # Extract SATB downbeats from the raw ABC. The list is 1-indexed with the
    # pickup absorbed (so `satb_per_bar[i-1]` is the downbeat of original bar i).
    try:
        satb_per_bar = extract_satb_per_bar(d['_abc_source'], key['root'])
    except Exception:
        satb_per_bar = []

    rows: list[str] = []
    rows.append('<!doctype html>')
    rows.append('<html lang="en"><head><meta charset="utf-8">')
    rows.append(f'<title>{title} — shape practice</title>')
    rows.append('<link rel="stylesheet" href="../style.css">')
    rows.append('<script src="../vendor/midiplayer.min.js"></script>')
    rows.append('<script src="../vendor/soundfont-player.min.js"></script>')
    rows.append('</head><body class="chopin-active">')
    hymns_self = 'index.html' if not chopin_only else '../hymns/index.html'
    chopin_self = '../chopin/index.html' if not chopin_only else 'index.html'
    rows.append(f'''<nav class="shape-nav">
  <a href="../index.html">index</a>
  <a href="../QRG.html">QRG</a>
  <a href="../README.html">README</a>
  <a href="../DRILLS.html">DRILLS</a>
  <a href="../SAMPLES.html">SAMPLES</a>
  <a href="../HANDOUT.html">HANDOUT</a>
  <a href="../VERIFY.html">VERIFY</a>
  <a href="../Chords.html">Chords</a>
  <a href="{hymns_self}">Hymns</a>
  <a href="{chopin_self}">Chopin</a>
  <a href="../HANDOFF.html">HANDOFF</a>
  <a href="../NEXTSESSION.html">NEXTSESSION</a>
</nav>''')

    rows.append(f'<h1>{title}</h1>')
    mode_label = key.get('mode', '')
    rows.append(
        '<p>'
        f'<strong>Tonic:</strong> <code>{key["root"]}</code> '
        f'({mode_label}) &nbsp;·&nbsp; '
        f'<strong>Meter:</strong> {meter["beats"]}/{meter["unit"]} &nbsp;·&nbsp; '
        f'<strong>Bars:</strong> {len(bars)} &nbsp;·&nbsp; '
        f'<strong>Phrases:</strong> {len(phrases)}'
        '</p>'
    )

    # Level selector — only for the multi-level Hymns view; the Chopin
    # tab's pages skip it (one view, no buttons).
    if not chopin_only:
        rows.append('<div class="level-selector">')
        rows.append('<strong>Level:</strong>')
        for level in LEVEL_ORDER:
            active = ' active' if level == 'chopin' else ''
            rows.append(f'<button class="level-btn{active}" data-level="{level}">'
                        f'{LEVEL_LABEL[level]}</button>')
        rows.append('</div>')

        rows.append('<p class="level-desc" id="level-desc">'
                    f'{LEVEL_DESC["chopin"]}</p>')

    # Pre-compute the voice-leading chain for the whole hymn. Soprano is
    # pinned to the actual melody (SATB extractor's S1V1 downbeat); the
    # chord pitch-classes come from the actual SATB voicing of the bar
    # (not the JSON's chord-analysis label, which can disagree with what
    # the hymn really plays). The solver re-voices A/T/B beneath the
    # melody for minimum motion.
    chopin_per_bar: list[dict] = []
    prev_voicing = None
    for bar_idx, bar in enumerate(bars):
        chord = bar.get('chord') or {}
        numeral = chord.get('numeral') or ''
        quality = chord.get('quality') or ''

        # Chord pcs come from the JSON's harmonic analysis (I, V7, IV …)
        # rather than the actual SATB pitches — the analysis gives more
        # variety, which is what the voice-leading solver needs to side-
        # slip across. The melody soprano still comes from the SATB
        # extractor (S1V1 downbeat).
        pcs = chord_letters(numeral, quality, key['root']) if numeral else []
        bar_satb = satb_per_bar[bar_idx] if bar_idx < len(satb_per_bar) else None
        melody_s: Voice | None = None
        if bar_satb:
            sop = bar_satb[0]
            if sop is not None:
                melody_s = Voice(sop.letter, sop.accidental, sop.octave)

        if not pcs:
            chopin_per_bar.append({
                'shape': '', 'chord': f'{numeral}{quality}', 'motion': None,
            })
            continue

        if prev_voicing is None:
            if melody_s is not None:
                voicing = initial_voicing_with_melody(pcs, melody_s)
            else:
                voicing = initial_voicing_for(pcs)
            motion = None
        else:
            voicing = solve_next_voicing(prev_voicing, pcs, fixed_s=melody_s)
            motion = voicing_motion(prev_voicing, voicing)
        shape_html = voicing_to_shape_html(voicing, key['root'], _hat)
        chopin_per_bar.append({
            'shape': shape_html,
            'voicing': voicing,
            'motion': motion,
            'chord': f'{voicing.s.name()} {voicing.a.name()} {voicing.t.name()} {voicing.b.name()}',
        })
        prev_voicing = voicing

    # One table per phrase.
    for phrase_idx, phrase in enumerate(phrases, start=1):
        rows.append(f'<h2>Phrase {phrase_idx}</h2>')

        # Chopin-only: render the phrase as a piano grand-staff arrangement
        # with the melody at original rhythm on top and the voice-led ATB
        # pad held below (Chopin treatment). For the non-chopin level
        # selector we still also need a voicings list for MIDI playback.
        phrase_voicings_all = [
            chopin_per_bar[b - 1].get('voicing')
            for b in phrase['ibars']
            if 0 < b <= len(chopin_per_bar)
        ]
        phrase_voicings = [v for v in phrase_voicings_all if v is not None]
        if phrase_voicings:
            phrase_bar_dicts = [
                bars[b - 1] for b in phrase['ibars']
                if 0 < b <= len(bars)
            ]
            if chopin_only:
                svg = render_phrase_piano_svg(
                    phrase_bar_dicts, phrase_voicings_all,
                    key['root'], key.get('mode', 'major'),
                    meter['beats'], meter['unit'],
                )
            else:
                svg = render_phrase_svg(phrase_voicings)
            # Write a MIDI file alongside the page so the play button can
            # fetch it. Filename keys off the slug + phrase index.
            slug = hymn_path.stem
            midi_name = f'{slug}_phrase{phrase_idx}.mid'
            midi_dir = SHAPES / ('chopin' if chopin_only else 'hymns') / 'midi'
            try:
                render_phrase_midi(phrase_voicings, midi_dir / midi_name)
                midi_url = f'midi/{midi_name}'
            except Exception:
                midi_url = ''
            play_btn = (
                f'<button class="play-phrase" data-midi="{midi_url}" '
                f'aria-label="Play phrase {phrase_idx}">▶</button>'
                if midi_url else ''
            )
            if svg:
                rows.append(
                    '<div class="phrase-svg chopin-only">'
                    f'{play_btn}{svg}</div>'
                )

        # Run the phrase-anchor selector once per phrase. The result drives
        # the `auto` level: every bar gets either the anchor shape (coast)
        # or a per-bar fallback (re-setup).
        phrase_chords = [
            ((bars[b - 1].get('chord') or {}).get('numeral') or '',
             (bars[b - 1].get('chord') or {}).get('quality') or '')
            for b in phrase['ibars']
        ]
        anchor = select_anchor(phrase_chords, key['root']) if phrase_chords else None
        resets = mark_resets(anchor, phrase_chords) if anchor else []
        if anchor:
            anchor_shape_html = _shape_html(
                f'3R{{N}}{anchor.shape.intervals}', anchor.shape.degree
            )
            rows.append(
                '<p class="phrase-anchor auto-only"><strong>Phrase anchor:</strong> '
                f'<code>{anchor_shape_html}</code> '
                f'<em>(coverage {", ".join(f"{c:.0%}" for c in anchor.coverage_per_bar)})</em></p>'
            )

        rows.append('<table class="hymn-bars">')
        rows.append('<thead><tr>'
                    '<th>Strings</th>'
                    '<th>Shape</th>'
                    '<th>Bar</th>'
                    '<th>Chord</th>'
                    '<th>Melody</th>'
                    '</tr></thead>')
        rows.append('<tbody>')
        for bar_idx_in_phrase, bar_num in enumerate(phrase['ibars']):
            bar = bars[bar_num - 1]
            chord = bar.get('chord') or {}
            numeral = chord.get('numeral') or ''
            quality = chord.get('quality') or ''
            inversion = chord.get('inversion') or ''
            degree = NUMERAL_TO_DEGREE.get(numeral, 0)
            satb = satb_per_bar[bar_num - 1] if 0 < bar_num <= len(satb_per_bar) else None

            # Auto level for this bar.
            if anchor and not resets[bar_idx_in_phrase]:
                auto_template = f'3R{{N}}{anchor.shape.intervals}'
                auto_template_degree = anchor.shape.degree
                auto_shape = (
                    '<span class="coast">coast</span> '
                    f'{_shape_html(auto_template, auto_template_degree)}'
                )
                auto_chord = f'{numeral}{quality}'
            elif anchor:
                fb = fallback_shape(numeral, quality)
                auto_template = f'3R{{N}}{fb.intervals}'
                auto_template_degree = fb.degree
                auto_shape = (
                    '<span class="reset">reset</span> '
                    f'{_shape_html(auto_template, auto_template_degree)}'
                )
                auto_chord = f'{numeral}{quality}'
            else:
                auto_template = ''
                auto_template_degree = 0
                auto_shape = ''
                auto_chord = f'{numeral}{quality}'

            # Chopin level for this bar — pull from the precomputed chain.
            sb = chopin_per_bar[bar_num - 1] if 0 < bar_num <= len(chopin_per_bar) else {}
            chopin_shape = sb.get('shape', '')
            chopin_chord = sb.get('chord', '')
            motion = sb.get('motion')
            if motion is not None and chopin_shape:
                # Annotate moves: e.g. "S· A↑1 T↓1 B↓1"
                bits = []
                for vname in ('S', 'A', 'T', 'B'):
                    delta = motion[vname]
                    if delta == 0:
                        bits.append(f'<span class="hold">{vname}·</span>')
                    elif delta > 0:
                        bits.append(f'<span class="move-up">{vname}↑{delta}</span>')
                    else:
                        bits.append(f'<span class="move-down">{vname}↓{abs(delta)}</span>')
                chopin_shape = (
                    f'<span class="motion">{" ".join(bits)}</span> '
                    f'{chopin_shape}'
                )

            level_data = _level_shapes(numeral, quality, degree, satb, key['root'],
                                       auto_shape=auto_shape, auto_chord=auto_chord,
                                       auto_template=auto_template,
                                       auto_degree=auto_template_degree,
                                       chopin_shape=chopin_shape, chopin_chord=chopin_chord,
                                       chopin_voicing=sb.get('voicing'))

            shape_cells = ''.join(
                f'<span class="lvl-shape {lvl}{ " active" if lvl == "chopin" else ""}">'
                f'<code>{level_data[lvl]["shape"]}</code></span>'
                for lvl in LEVEL_ORDER
            )
            # Chopin picks its own bass, so the source hymn's inversion
            # marker (¹/²/³ from JSON) is suppressed for that level only.
            chord_cells = ''.join(
                f'<span class="lvl-chord {lvl}{ " active" if lvl == "chopin" else ""}">'
                f'<code>{level_data[lvl]["chord"]}'
                f'{"" if lvl == "chopin" else inversion}'
                f'</code></span>'
                for lvl in LEVEL_ORDER
            )
            strings_cells = ''.join(
                f'<span class="lvl-strings {lvl}{ " active" if lvl == "chopin" else ""}">'
                f'{level_data[lvl]["strings"]}</span>'
                for lvl in LEVEL_ORDER
            )
            rows.append(
                '<tr>'
                f'<td class="strings-cell">{strings_cells}</td>'
                f'<td class="shape-cell">{shape_cells}</td>'
                f'<td>{bar_num}</td>'
                f'<td class="chord-cell">{chord_cells}</td>'
                f'<td><code>{_melody_str(bar.get("melody", []))}</code></td>'
                '</tr>'
            )
        rows.append('</tbody></table>')

    # Level-switching JS
    rows.append('''
<script>
(function () {
  const descs = ''' + json.dumps(LEVEL_DESC) + ''';
  document.querySelectorAll('.level-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const level = btn.dataset.level;
      document.querySelectorAll('.level-btn.active').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.lvl-shape.active, .lvl-chord.active, .lvl-strings.active').forEach(s => s.classList.remove('active'));
      document.querySelectorAll('.lvl-shape.' + level + ', .lvl-chord.' + level + ', .lvl-strings.' + level).forEach(s => s.classList.add('active'));
      document.body.classList.toggle('auto-active', level === 'auto');
      document.body.classList.toggle('chopin-active', level === 'chopin');
      document.getElementById('level-desc').textContent = descs[level] || '';
    });
  });

  // Phrase MIDI playback. Clicks load the .mid via fetch+ArrayBuffer,
  // hand it to midi-player-js, and route note-on events through a
  // soundfont-player Piano instrument. Lazy-init the AudioContext +
  // instrument on first click so autoplay policies don't trip.
  let _ac = null, _instrument = null, _activePlayer = null;
  async function ensureInstrument() {
    if (_instrument) return _instrument;
    _ac = new (window.AudioContext || window.webkitAudioContext)();
    _instrument = await Soundfont.instrument(_ac, 'orchestral_harp', {
      soundfont: 'MusyngKite',
      nameToUrl: (name, sf, fmt) => '../vendor/soundfont/' + name + '-mp3.js',
    });
    return _instrument;
  }
  // Record this hymn into the shared "Recent" list. Both Hymns and
  // Chopin navigators read the same bucket so a hymn seen in either
  // view is one tap away from the other.
  try {
    const m = window.location.pathname.match(/\/shapes\/(hymns|chopin)\/([^/]+)\.html/);
    if (m) {
      const slug = m[2];
      let list = [];
      try { list = JSON.parse(localStorage.getItem('shapes.recent') || '[]'); } catch (e) {}
      list = [slug, ...list.filter(s => s !== slug)].slice(0, 10);
      localStorage.setItem('shapes.recent', JSON.stringify(list));
    }
  } catch (e) { /* localStorage may be disabled — fail quietly */ }

  document.querySelectorAll('.play-phrase').forEach(btn => {
    btn.addEventListener('click', async () => {
      const url = btn.dataset.midi;
      if (!url) return;
      btn.classList.add('playing');
      try {
        if (_activePlayer && _activePlayer.isPlaying()) _activePlayer.stop();
        const inst = await ensureInstrument();
        const buf = await fetch(url).then(r => r.arrayBuffer());
        const Player = new MidiPlayer.Player(function(event) {
          if (event.name === 'Note on' && event.velocity > 0) {
            inst.play(event.noteName, _ac.currentTime, {
              gain: event.velocity / 127,
              duration: 4 * (60 / (Player.tempo || 60)),
            });
          }
        });
        Player.loadArrayBuffer(buf);
        Player.on('endOfFile', () => { btn.classList.remove('playing'); });
        _activePlayer = Player;
        Player.play();
      } catch (e) {
        console.error(e);
        btn.classList.remove('playing');
      }
    });
  });
})();
</script>
''')

    rows.append('</body></html>')
    return '\n'.join(rows)


def _render_one(slug: str, chopin_only: bool) -> bool:
    hymn_path = REPO / 'data' / 'hymns' / f'{slug}.json'
    if not hymn_path.exists():
        return False
    sub = 'chopin' if chopin_only else 'hymns'
    out = SHAPES / sub / f'{slug}.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        out.write_text(render_hymn(hymn_path, chopin_only=chopin_only))
        return True
    except Exception as e:
        print(f'  ! {slug}: {type(e).__name__}: {e}')
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('slug', nargs='?', default='amazing_grace')
    ap.add_argument('--all', action='store_true',
                    help='render every hymn in data/hymns/')
    ap.add_argument('--chopin-only', action='store_true',
                    help='emit the chopin-only view (under shapes/chopin/)')
    ap.add_argument('--both', action='store_true',
                    help='emit both the full Hymns page and the Chopin-only page')
    args = ap.parse_args()

    if args.all:
        slugs = sorted(p.stem for p in (REPO / 'data' / 'hymns').glob('*.json'))
    else:
        slugs = [args.slug]

    flavours: list[bool] = []
    if args.both or (not args.chopin_only and not args.both):
        flavours.append(False)
    if args.both or args.chopin_only:
        flavours.append(True)

    n_ok = 0
    for slug in slugs:
        for chopin in flavours:
            tag = 'chopin' if chopin else 'full '
            ok = _render_one(slug, chopin_only=chopin)
            if ok:
                n_ok += 1
                if args.all:
                    print(f'  [{tag}] {slug}')
    print(f'wrote {n_ok} pages across {len(slugs)} hymns')


if __name__ == '__main__':
    main()
