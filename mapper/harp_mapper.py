"""Score the 118-fraction pool against a roman numeral + key + melody note.

This is the grammar-native port of ``legacy/tools/harp_mapper.py``. The public
surface is the same three functions plus helpers:

    pick_fraction(pool, rn, key_root, melody=None, mode='major', top_n=3, prefer_color=True)
    pick_transition(pool, rn_from, rn_to, key_root, melody_to=None, mode='major', contour=None, top_n=3)
    pick_with_substitution(pool, rn, key_root, *, next_rn=None, prev_rn=None, melody=None,
                           mode='major', contour=None, is_final_cadence=False,
                           ending_marker=None, v_duration_beats=None, top_n=3)

All three return ``list[Pick]`` where ``Pick`` carries the ``Bishape`` grammar
object, the LH/RH ``Roman`` chords, the pool index, the numeric score, the
source bucket ('paths' | 'reserve'), the entry's ``meta``
dict (mood/cw_label/ccw_label/cycle), and the substitution bookkeeping fields
``harmonic_substitution`` + ``requested_rn``.

The 118 vocabulary is strictly diatonic and Ionian-labeled. Minor-mode lookup
is translated to the relative major; harmonic-minor V falls out to one of four
substitution strategies (see ``choose_minor_V_substitution``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from music21 import key as m21_key, pitch as m21_pitch

from grammar.types import Bishape, Roman
from trefoil.pool import Pool, PoolEntry, load_pool


# ═════════════════════════════════════════════════════════════════════════════
#   Result type
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class Pick:
    """One scored pool entry returned by the mapper.

    ``bishape`` / ``lh_chord`` / ``rh_chord`` / ``ipool`` / ``meta`` / ``source``
    mirror the underlying ``PoolEntry``. ``score`` is the numeric match score.
    ``harmonic_substitution`` and ``requested_rn`` are set by
    ``pick_with_substitution`` when a minor-V substitution was applied.
    ``technique`` is set by ``pick_with_techniques`` when a reharm technique
    (Third sub / Deceptive sub / Common-tone pivot) replaced the input RN.
    """
    bishape: Bishape
    lh_chord: Roman
    rh_chord: Roman
    ipool: str
    score: float
    source: str                             # 'paths' | 'reserve'
    meta: dict = field(default_factory=dict)
    harmonic_substitution: Optional[str] = None
    requested_rn: Optional[str] = None
    technique: Optional[str] = None


# ═════════════════════════════════════════════════════════════════════════════
#   Scale-degree / quality helpers (legacy-compatible)
# ═════════════════════════════════════════════════════════════════════════════

ROMAN_TO_DEG = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7,
}


def parse_rn(rn_str: str):
    """Return ``(root_degree_1to7, quality, inversion)`` for a roman numeral.

    Mirrors ``legacy/tools/harp_mapper.py::parse_rn`` so the scoring tables below
    continue to behave identically.
    """
    s = rn_str.strip()
    m = re.match(r'^[#b]?([ivIV]+)([oø°Δ]?)(\d*)([+b#]*\d*)?', s)
    if not m:
        return None, None, 0
    numerals, qual_char, digits, _extras = m.groups()
    deg = ROMAN_TO_DEG.get(numerals)
    if deg is None:
        return None, None, 0

    is_upper = numerals[0].isupper()

    if qual_char == '°':
        quality = 'dim'
    elif qual_char == 'ø':
        quality = 'halfdim'
    elif qual_char == 'Δ':
        quality = 'maj7'
    else:
        quality = 'maj' if is_upper else 'min'

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


def _roman_to_str(r: Roman) -> str:
    """Reconstruct the raw pool-string form of a ``Roman`` for legacy regex.

    Pool entries like ``IΔii`` come through as ``Roman(numeral='IΔii', ...)``,
    while clean entries like ``V7`` come through as
    ``Roman(numeral='V', quality='7', inversion=None)``. Either way we
    concatenate back so the legacy regex sees what the legacy JSON did.
    """
    return (r.numeral or '') + (r.quality or '') + (r.inversion or '')


def harp_rn_to_degree(harp_rn) -> Optional[int]:
    """Degree 1..7 of a pool LH/RH chord (``Roman`` or raw string)."""
    s = _roman_to_str(harp_rn) if isinstance(harp_rn, Roman) else harp_rn
    m = re.match(r'^([#b]?)([ivIV]+)', s)
    if not m:
        return None
    return ROMAN_TO_DEG.get(m.group(2))


def harp_rn_quality(harp_rn) -> str:
    """Quality tag of a pool LH/RH chord (matches legacy)."""
    s = _roman_to_str(harp_rn) if isinstance(harp_rn, Roman) else harp_rn
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
#   Pitch arithmetic (music21-backed)
# ═════════════════════════════════════════════════════════════════════════════

def figure_pitches(figure: str, K) -> list:
    """Return the music21 ``Pitch`` objects produced by a figure in key ``K``.

    First char = starting scale degree ('1'..'9','A'..'F'); subsequent chars
    are inclusive intervals (each one of 2/3/4).
    """
    vals: list[int] = []
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
    result = []
    for d in degrees:
        octave_shift = (d - 1) // 7
        scale_deg = ((d - 1) % 7) + 1
        base_pitch_name = K.pitchFromDegree(scale_deg).name
        p = m21_pitch.Pitch(f"{base_pitch_name}{3 + octave_shift}")
        result.append(p)
    return result


# ═════════════════════════════════════════════════════════════════════════════
#   Entry scoring
# ═════════════════════════════════════════════════════════════════════════════

def score_entry(entry: PoolEntry, target_deg, target_quality, target_inv,
                melody_pitch, K, prefer_color: bool = True) -> float:
    """Score a ``PoolEntry`` for the (rn, key, melody) target. Legacy-compatible."""
    lh_deg = harp_rn_to_degree(entry.lh_chord)
    rh_deg = harp_rn_to_degree(entry.rh_chord)
    lh_qual = harp_rn_quality(entry.lh_chord)

    score = 0.0

    # 1. LH root match — critical.
    if lh_deg == target_deg:
        score += 10
    elif rh_deg == target_deg:
        score += 5
    else:
        return -100

    # 2. Quality match on LH.
    if lh_qual == target_quality:
        score += 8
    elif target_quality == 'dom7' and lh_qual in ('maj', 'dom7'):
        score += 5
    elif target_quality == 'min7' and lh_qual in ('min', 'min7'):
        score += 5

    # 3. Melody compatibility.
    if melody_pitch:
        try:
            rh_pitches = figure_pitches(entry.rh_figure, K)
            lh_pitches = figure_pitches(entry.lh_figure, K)
            all_pcs = {p.pitchClass for p in (rh_pitches + lh_pitches)}
            if melody_pitch.pitchClass in all_pcs:
                score += 6
                if rh_pitches and melody_pitch.pitchClass == rh_pitches[-1].pitchClass:
                    score += 3
            else:
                score -= 4
        except Exception:
            pass

    # 4. Color preference — stacked moods get a small bump.
    if prefer_color:
        mood = entry.meta.get('mood')
        if mood:
            rich_moods = {'Radiant', 'Commanding', 'Sultry', 'Pealing', 'Urgent',
                          'Chiming', 'Soulful', 'Poised', 'Lush', 'Shimmer',
                          'Ethereal', 'Velvety', 'Layered', 'Anchored'}
            score += 2 if mood in rich_moods else 1

    # 5. Inversion preference.
    if target_inv > 0:
        rh_str = _roman_to_str(entry.rh_chord)
        if '¹' in rh_str or '²' in rh_str or '³' in rh_str:
            score += 2

    return score


# ═════════════════════════════════════════════════════════════════════════════
#   Minor-key → relative-major translation (for the Ionian-labeled 118)
# ═════════════════════════════════════════════════════════════════════════════

MINOR_TO_RELATIVE_MAJOR_DEG = {
    1: 6,   # i  → vi
    2: 7,   # ii° → vii°
    3: 1,   # III → I
    4: 2,   # iv  → ii
    5: 3,   # V   → iii (harmonic-minor V — special-cased via substitution)
    6: 4,   # VI  → IV
    7: 5,   # VII → V
}


def translate_minor_to_major(rn_str: str) -> str:
    """Translate a minor-mode RN to its relative-major equivalent string.

    E.g. ``'i' → 'vi'``, ``'iv' → 'ii'``, ``'V' → 'iii'``.
    """
    target_deg, target_quality, target_inv = parse_rn(rn_str)
    if target_deg is None:
        return rn_str
    new_deg = MINOR_TO_RELATIVE_MAJOR_DEG.get(target_deg, target_deg)
    if new_deg in (1, 4, 5):
        numerals = {1: 'I', 4: 'IV', 5: 'V'}[new_deg]
    elif new_deg in (2, 3, 6):
        numerals = {2: 'ii', 3: 'iii', 6: 'vi'}[new_deg]
    elif new_deg == 7:
        numerals = 'vii'
    else:
        return rn_str
    suffix = ''
    if target_quality in ('dom7', 'min7'):
        suffix = '7'
    elif target_quality == 'maj7':
        suffix = 'Δ'
    elif target_quality == 'dim':
        suffix = '°'
    elif target_quality == 'halfdim':
        suffix = 'ø7'
    inv_suffix = {0: '', 1: '6', 2: '64', 3: '42'}.get(target_inv, '')
    return f"{numerals}{suffix}{inv_suffix}"


# ═════════════════════════════════════════════════════════════════════════════
#   Harmonic-minor V substitution strategies
# ═════════════════════════════════════════════════════════════════════════════

def choose_minor_V_substitution(prev_rn=None, is_final_cadence=False,
                                ending_marker=None, v_duration_beats=None,
                                melody=None, key_root=None) -> str:
    """Pick one of four substitution strategies for minor-mode V.

    Returns one of ``'modal_v'``, ``'bVII_backdoor'``, ``'III_deceptive'``,
    ``'pedal_i'``. See the legacy module for the full rationale; the rules:

    1. ``iv → V`` continues plagal pull → ``bVII_backdoor``.
    2. Fermata-marked final cadence → ``III_deceptive``.
    3. Short V (≤1 beat) with tonic-compatible melody → ``pedal_i``.
    4. Otherwise ``modal_v`` (natural-minor v7).
    """
    if prev_rn:
        prev_base_m = re.match(r'^([ivIV]+)', prev_rn)
        prev_base = prev_base_m.group(1).lower() if prev_base_m else ''
        if prev_base == 'iv':
            return 'bVII_backdoor'

    if is_final_cadence and ending_marker == 'fermata':
        return 'III_deceptive'

    if v_duration_beats is not None and v_duration_beats <= 1 and melody and key_root:
        try:
            mel_pc = m21_pitch.Pitch(melody).pitchClass
            tonic_pc = m21_pitch.Pitch(key_root).pitchClass
            tonic_triad_pcs = {tonic_pc, (tonic_pc + 3) % 12, (tonic_pc + 7) % 12}
            if mel_pc in tonic_triad_pcs:
                return 'pedal_i'
        except Exception:
            pass

    return 'modal_v'


def translate_minor_V_with_strategy(strategy: str) -> str:
    """Return the relative-major RN to look up in the 118 for this strategy."""
    return {
        'modal_v':       'iii7',
        'bVII_backdoor': 'V',
        'III_deceptive': 'I',
        'pedal_i':       'vi',
    }.get(strategy, 'iii')


# ═════════════════════════════════════════════════════════════════════════════
#   Cycle detection + contour inference
# ═════════════════════════════════════════════════════════════════════════════

def cycle_of_transition(deg_from, deg_to):
    """Return ``(cycle, direction)`` or ``(None, None)`` for non-cycle edges.

    Cycle traversals (CW, returning to 1 after 7 steps):
      2nds CW: 1 2 3 4 5 6 7
      3rds CW: 1 3 5 7 2 4 6
      4ths CW: 1 4 7 3 6 2 5
    """
    if deg_from is None or deg_to is None or deg_from == deg_to:
        return None, None
    cw_traversals = {
        '2nds': [1, 2, 3, 4, 5, 6, 7],
        '3rds': [1, 3, 5, 7, 2, 4, 6],
        '4ths': [1, 4, 7, 3, 6, 2, 5],
    }
    for cyc, order in cw_traversals.items():
        try:
            idx_from = order.index(deg_from)
            idx_to = order.index(deg_to)
            if (idx_to - idx_from) % 7 == 1:
                return cyc, 'CW'
            if (idx_from - idx_to) % 7 == 1:
                return cyc, 'CCW'
        except ValueError:
            continue
    return None, None


def infer_contour(melody_prev, melody_cur, melody_next) -> str:
    """Classify melodic contour as ``'ascending'``, ``'descending'``, or ``'static'``."""
    def pc_midi(p):
        try:
            return m21_pitch.Pitch(p).midi if p else None
        except Exception:
            return None
    p0, p1, p2 = pc_midi(melody_prev), pc_midi(melody_cur), pc_midi(melody_next)
    if p1 is None:
        return 'static'
    if p2 is not None:
        if p2 > p1:
            return 'ascending'
        if p2 < p1:
            return 'descending'
    if p0 is not None:
        if p1 > p0:
            return 'ascending'
        if p1 < p0:
            return 'descending'
    return 'static'


# ═════════════════════════════════════════════════════════════════════════════
#   Key construction
# ═════════════════════════════════════════════════════════════════════════════

def _build_key(key_root: str, mode: str):
    """Return the music21 ``Key`` used for pitch arithmetic.

    For minor, we use the *relative major* so the Ionian-labeled 118 entries
    resolve to the right diatonic pitches.
    """
    if mode == 'minor':
        minor_tonic = m21_pitch.Pitch(key_root)
        rel_maj_tonic = minor_tonic.transpose(3)
        return m21_key.Key(rel_maj_tonic.name, 'major')
    return m21_key.Key(key_root, 'major')


def _mk_pick(entry: PoolEntry, score: float,
             *, meta_override: Optional[dict] = None) -> Pick:
    """Build a ``Pick`` from a ``PoolEntry`` + score."""
    return Pick(
        bishape=entry.bishape,
        lh_chord=entry.lh_chord,
        rh_chord=entry.rh_chord,
        ipool=entry.ipool,
        score=float(score),
        source=entry.source,
        meta=dict(meta_override if meta_override is not None else entry.meta),
    )


# ═════════════════════════════════════════════════════════════════════════════
#   Picker: single chord
# ═════════════════════════════════════════════════════════════════════════════

def pick_fraction(pool: Pool, rn: str, key_root: str, melody: Optional[str] = None,
                  mode: str = 'major', top_n: int = 3,
                  prefer_color: bool = True) -> list[Pick]:
    """Top-N pool entries matching ``rn`` in ``key_root`` ``mode``.

    Minor-mode queries are translated to relative-major for the lookup; the
    returned LH/RH labels read relative-major but the pitches are correct for
    the minor key.
    """
    if mode == 'minor':
        rn = translate_minor_to_major(rn)
    target_deg, target_quality, target_inv = parse_rn(rn)
    if target_deg is None:
        return []
    K = _build_key(key_root, mode)

    melody_pitch = None
    if melody:
        try:
            melody_pitch = m21_pitch.Pitch(melody)
        except Exception:
            melody_pitch = None

    scored: list[tuple[float, PoolEntry]] = []
    for e in pool.entries:
        s = score_entry(e, target_deg, target_quality, target_inv,
                        melody_pitch, K, prefer_color)
        if s > 0:
            scored.append((s, e))
    scored.sort(key=lambda x: -x[0])
    return [_mk_pick(e, s) for s, e in scored[:top_n]]


# ═════════════════════════════════════════════════════════════════════════════
#   Picker: cycle-edge transition
# ═════════════════════════════════════════════════════════════════════════════

def pick_transition(pool: Pool, rn_from: str, rn_to: str, key_root: str,
                    melody_to: Optional[str] = None, mode: str = 'major',
                    contour: Optional[str] = None, top_n: int = 3) -> list[Pick]:
    """Pick path entries for the move ``rn_from → rn_to``.

    If the transition is not a cycle edge, falls back to ``pick_fraction(pool, rn_to, ...)``.
    Contour ('ascending'|'descending'|'static'|None) tilts CW vs CCW selection.
    """
    if mode == 'minor':
        rn_from_t = translate_minor_to_major(rn_from)
        rn_to_t = translate_minor_to_major(rn_to)
    else:
        rn_from_t, rn_to_t = rn_from, rn_to
    K = _build_key(key_root, mode)

    deg_from, _, _ = parse_rn(rn_from_t)
    deg_to, _, _ = parse_rn(rn_to_t)
    if deg_from is None or deg_to is None:
        return []

    cycle, direction = cycle_of_transition(deg_from, deg_to)
    if cycle is None:
        return pick_fraction(pool, rn_to, key_root, melody_to, mode, top_n)

    melody_pitch = None
    if melody_to:
        try:
            melody_pitch = m21_pitch.Pitch(melody_to)
        except Exception:
            melody_pitch = None

    scored: list[tuple[float, PoolEntry, dict]] = []
    for e in pool.entries:
        if e.source != 'paths':
            continue
        if e.meta.get('cycle') != cycle:
            continue
        lh_deg = harp_rn_to_degree(e.lh_chord)
        rh_deg = harp_rn_to_degree(e.rh_chord)
        if {lh_deg, rh_deg} != {deg_from, deg_to}:
            continue

        score = 15.0

        if contour == 'ascending' and direction == 'CW':
            score += 6
        elif contour == 'descending' and direction == 'CCW':
            score += 6
        elif contour in ('ascending', 'descending') and direction != contour[:2].upper():
            # Legacy branch that never fires (contour[:2] is 'as'/'de', direction is
            # 'CW'/'CCW'), preserved for fidelity.
            score -= 2

        if melody_pitch:
            try:
                rh_pitches = figure_pitches(e.rh_figure, K)
                lh_pitches = figure_pitches(e.lh_figure, K)
                all_pcs = {p.pitchClass for p in (rh_pitches + lh_pitches)}
                if melody_pitch.pitchClass in all_pcs:
                    score += 5
                    if rh_pitches and melody_pitch.pitchClass == rh_pitches[-1].pitchClass:
                        score += 3
                else:
                    score -= 3
            except Exception:
                pass

        if e.meta.get('verse') == 2:
            score += 2

        # Transition picks surface the direction-appropriate mood label.
        mood_key = 'cw_label' if direction == 'CW' else 'ccw_label'
        meta_override = dict(e.meta)
        meta_override['mood'] = e.meta.get(mood_key, '')
        meta_override['cycle_inferred'] = cycle
        meta_override['direction'] = direction
        scored.append((score, e, meta_override))

    scored.sort(key=lambda x: -x[0])
    return [_mk_pick(e, s, meta_override=m) for s, e, m in scored[:top_n]]


# ═════════════════════════════════════════════════════════════════════════════
#   High-level picker: substitution + cycle + reserve fallback in one call
# ═════════════════════════════════════════════════════════════════════════════

def pick_with_substitution(pool: Pool, rn: str, key_root: str, *,
                           next_rn: Optional[str] = None,
                           prev_rn: Optional[str] = None,
                           melody: Optional[str] = None,
                           mode: str = 'major',
                           contour: Optional[str] = None,
                           is_final_cadence: bool = False,
                           ending_marker: Optional[str] = None,
                           v_duration_beats: Optional[float] = None,
                           top_n: int = 3) -> list[Pick]:
    """Main entry point. Handles cycle edges, reserve fallback, and minor-V
    substitution. Picks are annotated with ``harmonic_substitution`` /
    ``requested_rn`` for downstream renderers.
    """
    requested_rn = rn
    substitution: Optional[str] = None

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
            substituted_rn = translate_minor_V_with_strategy(substitution)
            rn = substituted_rn
            if next_rn:
                nb_m = re.match(r'^(b?[ivIV]+)', next_rn)
                nb = nb_m.group(1) if nb_m else ''
                if nb in ('i', 'i6', 'i64'):
                    next_rn = 'vi'
            minor_tonic_p = m21_pitch.Pitch(key_root)
            rel_maj_tonic = minor_tonic_p.transpose(3)
            lookup_key_root = rel_maj_tonic.name
            lookup_mode = 'major'
        else:
            lookup_key_root = key_root
            lookup_mode = mode
    else:
        lookup_key_root = key_root
        lookup_mode = mode

    picks: list[Pick] = []
    if next_rn:
        from_t = translate_minor_to_major(rn) if lookup_mode == 'minor' else rn
        to_t = translate_minor_to_major(next_rn) if lookup_mode == 'minor' else next_rn
        d_from, _, _ = parse_rn(from_t)
        d_to, _, _ = parse_rn(to_t)
        cyc, _dir = cycle_of_transition(d_from, d_to)
        if cyc:
            picks = pick_transition(pool, rn, next_rn, lookup_key_root,
                                    melody, lookup_mode, contour, top_n=top_n)

    if not picks:
        picks = pick_fraction(pool, rn, lookup_key_root, melody,
                              lookup_mode, top_n=top_n)

    for p in picks:
        p.harmonic_substitution = substitution
        p.requested_rn = requested_rn

    return picks


# ═════════════════════════════════════════════════════════════════════════════
#   Technique-aware picker: substitution techniques as candidate alternates
# ═════════════════════════════════════════════════════════════════════════════

# Ionian diatonic ladder (tuple of plain numerals, no quality marks).
_DIATONIC_NUMERALS = ('I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii')

# Diatonic triad scale-degree sets (indices into the 7-note ladder, 0-based).
_DIATONIC_TRIADS = {
    0: frozenset({0, 2, 4}),   # I
    1: frozenset({1, 3, 5}),   # ii
    2: frozenset({2, 4, 6}),   # iii
    3: frozenset({3, 5, 0}),   # IV
    4: frozenset({4, 6, 1}),   # V
    5: frozenset({5, 0, 2}),   # vi
    6: frozenset({6, 1, 3}),   # vii
}

# Per-technique score bonus. The baseline gets an incumbency bonus of
# ``_INCUMBENT_BONUS`` below, so effective net tilt = bonus - incumbency.
# Deceptive sub (V→vi on phrase-end cadence) is the only technique tilted to
# beat baseline on a tie; the others must earn their win with raw pool score.
_TECHNIQUE_BONUS = {
    'Deceptive sub':      4.0,   # phrase-end cadence swap — explicit intent
    'Third sub':          0.0,   # only when alternate's melody match is stronger
    'Common-tone pivot':  0.5,   # very narrow — shares ≥2 pcs with both sides
}
_INCUMBENT_BONUS = 4.0           # default bar keeps its chord unless clearly beaten


def _rn_numeral(rn: str) -> Optional[str]:
    """Extract the ladder numeral (e.g. ``'V7' → 'V'``, ``'iii¹' → 'iii'``)."""
    m = re.match(r'^[#b\u266d\u266f]?([ivIV]+)', rn or '')
    if not m:
        return None
    return m.group(1)


def _ladder_index(rn: str) -> Optional[int]:
    """0..6 position of ``rn`` on the Ionian ladder, else None."""
    num = _rn_numeral(rn)
    if num is None:
        return None
    for i, canonical in enumerate(_DIATONIC_NUMERALS):
        if canonical.lower() == num.lower():
            return i
    return None


def _third_sub_alternates(rn: str) -> list[str]:
    """Return up-a-third and down-a-third diatonic neighbors of ``rn``."""
    idx = _ladder_index(rn)
    if idx is None:
        return []
    return [
        _DIATONIC_NUMERALS[(idx - 2) % 7],
        _DIATONIC_NUMERALS[(idx + 2) % 7],
    ]


def _deceptive_sub_alternate(rn: str, next_rn: Optional[str]) -> Optional[str]:
    """Return ``'vi'`` iff ``rn`` is ``V`` / ``V7`` and ``next_rn`` starts with ``I``."""
    num = _rn_numeral(rn)
    if num != 'V':
        return None
    if not next_rn:
        return None
    next_num = _rn_numeral(next_rn)
    if next_num != 'I':
        return None
    return 'vi'


def _common_tone_pivot_alternates(rn: str, next_rn: Optional[str]) -> list[str]:
    """Return diatonic neighbors sharing ≥2 tones with both current and next RN."""
    cur_idx = _ladder_index(rn)
    nxt_idx = _ladder_index(next_rn) if next_rn else None
    if cur_idx is None or nxt_idx is None:
        return []
    cur_pcs = _DIATONIC_TRIADS[cur_idx]
    nxt_pcs = _DIATONIC_TRIADS[nxt_idx]
    alts: list[str] = []
    for i, numeral in enumerate(_DIATONIC_NUMERALS):
        if i == cur_idx or i == nxt_idx:
            continue
        pcs = _DIATONIC_TRIADS[i]
        if len(pcs & cur_pcs) >= 2 and len(pcs & nxt_pcs) >= 2:
            alts.append(numeral)
    return alts


def _rescore_via_score_entry(pool: Pool, pick: Pick, rn: str, key_root: str,
                              melody: Optional[str], mode: str) -> float:
    """Re-score a ``Pick`` via :func:`score_entry` against the caller's RN.

    The baseline from :func:`pick_with_substitution` may have been scored on
    the :func:`pick_transition` scale (smaller range). This helper rescales
    the baseline so technique alternates (which are scored via
    :func:`pick_fraction`) can be compared against it on equal footing.
    """
    lookup_rn = translate_minor_to_major(rn) if mode == 'minor' else rn
    target_deg, target_quality, target_inv = parse_rn(lookup_rn)
    if target_deg is None:
        return pick.score
    K = _build_key(key_root, mode)
    melody_pitch = None
    if melody:
        try:
            melody_pitch = m21_pitch.Pitch(melody)
        except Exception:
            melody_pitch = None
    try:
        entry = pool.get(pick.ipool)
    except Exception:
        return pick.score
    return score_entry(entry, target_deg, target_quality, target_inv,
                       melody_pitch, K, prefer_color=True)


def _voice_leading_bonus(prev_pick: Optional[Pick], cand: Pick,
                          key_root: str, mode: str) -> float:
    """Reward pitch-class overlap between ``prev_pick`` and ``cand`` voicings.

    Shared pitch classes → smoother voice leading. Returns 0..2.5.
    """
    if prev_pick is None:
        return 0.0
    try:
        K = _build_key(key_root, mode)
        prev_pcs = {p.pitchClass for p in (
            figure_pitches(prev_pick.bishape.rh.figure, K) +
            figure_pitches(prev_pick.bishape.lh.figure, K)
        )}
        cand_pcs = {p.pitchClass for p in (
            figure_pitches(cand.bishape.rh.figure, K) +
            figure_pitches(cand.bishape.lh.figure, K)
        )}
        shared = len(prev_pcs & cand_pcs)
        return min(shared * 0.5, 2.5)
    except Exception:
        return 0.0


def pick_with_techniques(pool: Pool, rn: str, key_root: str, *,
                          next_rn: Optional[str] = None,
                          prev_rn: Optional[str] = None,
                          melody: Optional[str] = None,
                          mode: str = 'major',
                          contour: Optional[str] = None,
                          is_final_cadence: bool = False,
                          ending_marker: Optional[str] = None,
                          v_duration_beats: Optional[float] = None,
                          is_phrase_end: bool = False,
                          prev_pick: Optional[Pick] = None,
                          enabled: tuple[str, ...] = (
                              'Deceptive sub',
                              'Third sub',
                              'Common-tone pivot',
                          )) -> list[Pick]:
    """Technique-aware wrapper around :func:`pick_with_substitution`.

    Generates candidate alternate RNs via substitution techniques (Third sub,
    Deceptive sub, Common-tone pivot), scores each alternate's best pool
    entry, adds a technique bonus plus a voice-leading bonus vs. ``prev_pick``,
    and returns the winning pick (top-1). The winning pick's ``technique``
    field records which technique (if any) was applied; baseline picks have
    ``technique=None``.

    Techniques are gated by musical context:
      - Deceptive sub: only on phrase-final V → I cadences.
      - Third sub: everywhere, but bonus is small.
      - Common-tone pivot: only when both current and next RN exist.

    Minor-key V substitution (``harmonic_substitution``) is delegated to
    :func:`pick_with_substitution` and preserved on the returned pick.
    """
    baseline_picks = pick_with_substitution(
        pool, rn, key_root,
        next_rn=next_rn, prev_rn=prev_rn, melody=melody, mode=mode,
        contour=contour, is_final_cadence=is_final_cadence,
        ending_marker=ending_marker, v_duration_beats=v_duration_beats,
        top_n=1,
    )
    if not baseline_picks:
        return []

    best = baseline_picks[0]
    best.technique = None
    # Re-score baseline via score_entry so it's on the same scale as alternates
    # (pick_with_substitution may have gone through pick_transition, which uses
    # a smaller scoring range). The baseline's pool choice is preserved; only
    # the comparison score changes.
    baseline_rescore = _rescore_via_score_entry(
        pool, best, rn, key_root, melody, mode
    )
    best_score = (
        baseline_rescore
        + _INCUMBENT_BONUS
        + _voice_leading_bonus(prev_pick, best, key_root, mode)
    )

    # In minor mode, the mapper already translated the lookup; we should only
    # apply substitution techniques in major mode to keep the Ionian ladder
    # assumption in _third_sub_alternates / _common_tone_pivot_alternates
    # valid. (Minor-mode V substitution is still handled by pick_with_substitution.)
    if mode == 'minor':
        return [best]

    # Cycle-edge bars are where the trefoil-path pedagogy earns its keep —
    # the 42 paths encode direction-aware voice-leading between adjacent
    # diatonic degrees. We never override a cycle-edge baseline with a
    # substitution technique; the cycle pick is the lesson.
    cur_deg = _ladder_index(rn)
    nxt_deg = _ladder_index(next_rn) if next_rn else None
    on_cycle_edge = False
    if cur_deg is not None and nxt_deg is not None:
        # cycle_of_transition wants 1-based degrees.
        cyc, _direction = cycle_of_transition(cur_deg + 1, nxt_deg + 1)
        on_cycle_edge = cyc is not None

    # Gate techniques by musical context so they only fire when there's a
    # clear motivation — otherwise baseline wins by default.
    candidates: list[tuple[str, str]] = []      # (technique_name, alt_rn)

    # Deceptive sub: phrase-final V → I cadence only. Fires even on cycle
    # edges because V→I is always a 4ths-cycle edge and the deceptive
    # cadence is the musical point.
    if 'Deceptive sub' in enabled and is_phrase_end:
        alt = _deceptive_sub_alternate(rn, next_rn)
        if alt:
            candidates.append(('Deceptive sub', alt))

    # Third sub: only on non-cycle-edge bars where the baseline rescored
    # poorly on melody. Cycle edges keep their trefoil path.
    if ('Third sub' in enabled and melody and not on_cycle_edge
            and baseline_rescore < 20.0):
        for alt in _third_sub_alternates(rn):
            candidates.append(('Third sub', alt))

    # Common-tone pivot: only on repeated chords (current RN == prev RN),
    # and only off cycle edges. Repeated bars are the classic target for
    # pivot variety; applying it to every transition produces noise.
    if ('Common-tone pivot' in enabled and next_rn and prev_rn
            and not on_cycle_edge):
        cur_num = _rn_numeral(rn)
        prev_num = _rn_numeral(prev_rn)
        if cur_num and prev_num and cur_num == prev_num:
            for alt in _common_tone_pivot_alternates(rn, next_rn):
                candidates.append(('Common-tone pivot', alt))

    for tech_name, alt_rn in candidates:
        alt_picks = pick_fraction(pool, alt_rn, key_root, melody, mode, top_n=1)
        if not alt_picks:
            continue
        cand = alt_picks[0]
        combined = (
            cand.score
            + _TECHNIQUE_BONUS.get(tech_name, 0.0)
            + _voice_leading_bonus(prev_pick, cand, key_root, mode)
        )
        if combined > best_score:
            cand.technique = tech_name
            cand.requested_rn = rn
            best, best_score = cand, combined

    return [best]


# ═════════════════════════════════════════════════════════════════════════════
#   Convenience: module-level pool cache for ad-hoc callers
# ═════════════════════════════════════════════════════════════════════════════

_default_pool: Optional[Pool] = None


def default_pool() -> Pool:
    """Lazy-loaded singleton of ``load_pool()`` for one-off callers."""
    global _default_pool
    if _default_pool is None:
        _default_pool = load_pool()
    return _default_pool


__all__ = [
    'Pick',
    'pick_fraction',
    'pick_transition',
    'pick_with_substitution',
    'pick_with_techniques',
    'cycle_of_transition',
    'infer_contour',
    'choose_minor_V_substitution',
    'translate_minor_V_with_strategy',
    'translate_minor_to_major',
    'parse_rn',
    'harp_rn_to_degree',
    'harp_rn_quality',
    'figure_pitches',
    'score_entry',
    'MINOR_TO_RELATIVE_MAJOR_DEG',
    'default_pool',
]
