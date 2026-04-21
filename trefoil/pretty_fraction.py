"""Score and generate pretty chord fractions for the jazz hymnal.

A fraction = LH shape + gap + RH shape on a diatonic harp (C2..C6, 29
strings).  This module:

  1. scores a fraction (lower = prettier)
  2. generates candidate fractions for a target chord
  3. picks the best candidate

Input: chord dict {numeral, quality?, additions[], omissions[]}.
Output: fraction dict {lh: [(deg, oct), ...], gap, rh: [(deg, oct), ...]}.

Scale-degree and octave are both 1-indexed.  Degrees 1–7 map to C-major
scale tones; octaves 2–6 span the hymnal range (string 1 = C2, 29 = C6).

Usage:
    from trefoil.pretty_fraction import pretty, score_fraction
    frac = pretty({"numeral": "V", "additions": [7]})        # V7
    frac = pretty({"numeral": "I", "quality": "Δ"})          # IΔ
"""
from __future__ import annotations
from typing import Optional


# ──────────────────── Constants ────────────────────

C_MAJOR_LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
NUM_TO_DEG = {'I':1, 'ii':2, 'iii':3, 'IV':4, 'V':5, 'vi':6, 'vii°':7}
STRING_MIN = 1    # C2
STRING_MAX = 29   # C6
MIDDLE_C_STRING = 15  # C4 = string index 15

# Interval offsets (in scale steps) that each quality adds on top of the root
QUALITY_TONES = {
    None: [0, 2, 4],        # triad (1, 3, 5)
    '':   [0, 2, 4],
    '7':  [0, 2, 4, 6],     # 7-chord (1, 3, 5, 7)
    'Δ':  [0, 2, 4, 6],     # maj7 (same in diatonic context)
    'h7': [0, 2, 4, 6],     # half-dim 7 (vii° + dim 7)
    '6':  [0, 2, 4, 5],     # 1,3,5,6
    's2': [0, 1, 4],        # sus2 (1, 2, 5) — 3 replaced
    's4': [0, 3, 4],        # sus4 (1, 4, 5)
    'q':  [0, 3, 6],        # quartal triad (1, 4, 7)
    'q7': [0, 3, 6, 9],     # quartal 4-chord (1, 4, 7, 10)
    '+8': [0, 2, 4, 7],     # triad + octave doubling
}


# ──────────────────── Utilities ────────────────────

def string_index(deg: int, oct: int) -> int:
    """(degree, octave) → string index in [1..29]."""
    return (oct - 2) * 7 + (deg - 1) + 1


def to_abc(deg: int, oct: int) -> str:
    """(degree, octave) → ABC notation."""
    L = C_MAJOR_LETTERS[deg - 1]
    if oct == 4:       return L
    elif oct < 4:      return L + ',' * (4 - oct)
    elif oct == 5:     return L.lower()
    else:              return L.lower() + "'" * (oct - 5)


def chord_pitch_classes(chord: dict) -> set[int]:
    """All diatonic scale degrees (1..7) present in the chord."""
    root = NUM_TO_DEG[chord['numeral']]
    q = chord.get('quality')
    offsets = list(QUALITY_TONES.get(q, QUALITY_TONES[None]))
    for a in chord.get('additions', []):
        offsets.append(a - 1)
    for o in chord.get('omissions', []):
        off = o - 1
        if off in offsets:
            offsets.remove(off)
    return {((root - 1) + off) % 7 + 1 for off in offsets}


def span(notes: list[tuple[int, int]]) -> int:
    """Number of strings covered by a hand (inclusive)."""
    if not notes:
        return 0
    idxs = [string_index(*n) for n in notes]
    return max(idxs) - min(idxs) + 1


# ──────────────────── Scoring ────────────────────

def score_fraction(frac: dict, chord: dict, context: dict = None) -> int:
    """Penalty score: lower = prettier.  9999 = reject (invalid)."""
    lh, rh = frac['lh'], frac['rh']
    all_notes = lh + rh
    if not all_notes:
        return 9999

    # Hard constraints
    for n in all_notes:
        si = string_index(*n)
        if si < STRING_MIN or si > STRING_MAX:
            return 9999
    if span(lh) > 10 or span(rh) > 10:
        return 9999
    # A fraction needs ≥ 2 notes per hand — single-note-per-hand is plucking
    if len(lh) < 2 or len(rh) < 2:
        return 9999
    # Every pitch class must be in the chord's set (no sneaking in omitted notes)
    chord_pc = chord_pitch_classes(chord)
    for n in all_notes:
        if n[0] not in chord_pc:
            return 9999

    penalty = 0
    pc = chord_pitch_classes(chord)
    root = NUM_TO_DEG[chord['numeral']]
    third = ((root - 1) + 2) % 7 + 1
    fifth = ((root - 1) + 4) % 7 + 1
    seventh = ((root - 1) + 6) % 7 + 1
    q = chord.get('quality')
    present_pc = {n[0] for n in all_notes}

    # Every pitch class in the chord's full set must appear in the fraction —
    # otherwise the chord isn't actually being played
    missing = pc - present_pc
    if missing:
        return 9999   # reject — this voicing doesn't represent the chord
    # Bonus essential-tone checks (redundant with above but preserved for clarity)
    if root not in present_pc:
        penalty += 3

    # Density: only penalize >5 notes (4-note 7-chords should be fine)
    if len(all_notes) > 5:
        penalty += 2 * (len(all_notes) - 5)
    if len(lh) > 3:
        penalty += 2 * (len(lh) - 3)
    if len(rh) > 4:
        penalty += 2 * (len(rh) - 4)

    # Bass clarity
    if lh:
        bass_deg = sorted(lh, key=lambda n: string_index(*n))[0][0]
        if bass_deg not in (root, third, fifth):
            penalty += 3

    # Top must be a chord tone
    if rh:
        top_deg = sorted(rh, key=lambda n: string_index(*n))[-1][0]
        if top_deg not in pc:
            penalty += 2

    # Close 2nds in low register
    idxs = sorted(string_index(*n) for n in all_notes)
    for a, b in zip(idxs, idxs[1:]):
        if b - a == 1 and a < MIDDLE_C_STRING:
            penalty += 3
            break

    # Missing 3rd (unless sus/quartal)
    if q not in ('s2', 's4', 'q', 'q7'):
        if third not in {n[0] for n in all_notes}:
            penalty += 2

    # Gap
    if lh and rh:
        lh_top = max(string_index(*n) for n in lh)
        rh_bot = min(string_index(*n) for n in rh)
        gap = rh_bot - lh_top - 1
        if gap < 2:
            penalty += 2 - gap
        if gap > 15:
            penalty += gap - 15

    return penalty


# ──────────────────── Generator ────────────────────

def _placements(pc_set: set[int], oct_low: int, oct_high: int) -> list[tuple[int, int]]:
    """All (deg, oct) positions within the octave range for the given pitch classes."""
    return [(d, o) for d in pc_set for o in range(oct_low, oct_high + 1)
            if STRING_MIN <= string_index(d, o) <= STRING_MAX]


def generate_candidates(chord: dict, max_candidates: int = 64) -> list[dict]:
    """Generate plausible fractions for the chord.

    Strategy: for each (bass choice, gap choice, RH-top-note choice),
    build a fraction that respects span constraints.  Returns a list of
    candidate dicts ready for scoring.
    """
    pc = chord_pitch_classes(chord)
    root = NUM_TO_DEG[chord['numeral']]
    candidates = []

    # Bass choices: every chord tone in octaves 2-3 (only pitch classes actually in the chord)
    bass_options = [(d, o) for d in pc for o in (2, 3)
                    if STRING_MIN <= string_index(d, o) <= STRING_MAX]

    # RH top-note: any chord tone in C4–C6
    top_candidates = [(d, o) for d in pc for o in (4, 5, 6)
                      if STRING_MIN <= string_index(d, o) <= STRING_MAX]

    for bass in bass_options:
        bass_idx = string_index(*bass)
        for top in top_candidates:
            top_idx = string_index(*top)
            if top_idx <= bass_idx:
                continue
            # LH: bass + at least 1 more chord tone (≥2 notes total), within 10 strings
            lh_candidates_1 = []
            for extra_deg in pc:
                for extra_oct in range(bass[1], bass[1] + 2):
                    extra = (extra_deg, extra_oct)
                    si = string_index(*extra)
                    if si <= bass_idx: continue
                    if si - bass_idx >= 10: continue
                    if si >= top_idx: continue
                    lh_candidates_1.append([bass, extra])
                    # Also allow LH with 3 notes
                    for third_deg in pc:
                        for third_oct in range(extra[1], extra[1] + 2):
                            third_note = (third_deg, third_oct)
                            si3 = string_index(*third_note)
                            if si3 <= si: continue
                            if si3 - bass_idx >= 10: continue
                            if si3 >= top_idx: continue
                            if third_note in (bass, extra): continue
                            lh_candidates_1.append([bass, extra, third_note])

            # RH: top + 1-2 more chord tones below top, within 10 strings
            for lh in lh_candidates_1:
                lh_top_idx = max(string_index(*n) for n in lh)
                # Fill RH with 2-3 chord tones ending at top
                rh_candidates = [[top]]
                for mid1_deg in pc:
                    for mid1_oct in (top[1] - 1, top[1]):
                        mid1 = (mid1_deg, mid1_oct)
                        si1 = string_index(*mid1)
                        if si1 <= lh_top_idx or si1 >= top_idx:
                            continue
                        if top_idx - si1 >= 10:
                            continue
                        rh_candidates.append([mid1, top])
                        # 3-note RH: add another middle note
                        for mid2_deg in pc:
                            for mid2_oct in (top[1] - 1, top[1]):
                                mid2 = (mid2_deg, mid2_oct)
                                si2 = string_index(*mid2)
                                if si2 <= si1 or si2 >= top_idx:
                                    continue
                                if mid2 in (mid1, top):
                                    continue
                                rh_candidates.append([mid1, mid2, top])

                for rh in rh_candidates:
                    frac = {'lh': lh, 'rh': rh}
                    candidates.append(frac)

                if len(candidates) >= max_candidates * 8:
                    break
            if len(candidates) >= max_candidates * 8:
                break
        if len(candidates) >= max_candidates * 8:
            break

    # De-dupe
    seen = set()
    unique = []
    for c in candidates:
        key = (tuple(sorted(c['lh'])), tuple(sorted(c['rh'])))
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
    return unique[:max_candidates * 4]


# ──────────────────── Main API ────────────────────

def pretty(chord: dict, context: dict = None, verbose: bool = False) -> dict:
    """Return the prettiest fraction for the given chord."""
    cands = generate_candidates(chord)
    scored = [(score_fraction(c, chord, context), c) for c in cands]
    scored = [(s, c) for s, c in scored if s < 9999]
    scored.sort(key=lambda x: x[0])
    if not scored:
        raise ValueError(f"no valid fractions for {chord}")
    best_score, best = scored[0]
    if verbose:
        print(f"top 5 for {chord['numeral']}{chord.get('quality','')}: ")
        for s, f in scored[:5]:
            print(f"  [{s}] {format_fraction(f)}")
    return best


def format_fraction(frac: dict) -> str:
    """Render a fraction as ABC-like notation (notes separated by ·)."""
    lh_abc = "·".join(to_abc(*n) for n in sorted(frac['lh'], key=lambda n: string_index(*n)))
    rh_abc = "·".join(to_abc(*n) for n in sorted(frac['rh'], key=lambda n: string_index(*n)))
    lh_top = max(string_index(*n) for n in frac['lh']) if frac['lh'] else 0
    rh_bot = min(string_index(*n) for n in frac['rh']) if frac['rh'] else 0
    gap = rh_bot - lh_top - 1 if frac['lh'] and frac['rh'] else 0
    return f"LH[{lh_abc}] gap={gap} RH[{rh_abc}]"


if __name__ == "__main__":
    # Demo: generate pretty fractions for each C-major diatonic chord
    demo_chords = [
        {"numeral": "I"},
        {"numeral": "I", "quality": "Δ"},
        {"numeral": "ii", "quality": "7"},
        {"numeral": "iii", "quality": "7"},
        {"numeral": "IV", "quality": "Δ"},
        {"numeral": "V", "quality": "7"},
        {"numeral": "vi", "quality": "7"},
        {"numeral": "vii°", "quality": "h7"},
        {"numeral": "I", "additions": [9]},
        {"numeral": "V", "quality": "s4"},
    ]
    print(f"{'chord':<14} {'best fraction':<50}")
    print("-" * 65)
    for ch in demo_chords:
        label = ch['numeral'] + (ch.get('quality','') or '')
        if ch.get('additions'):
            label += ''.join(str(a) for a in ch['additions'])
        best = pretty(ch)
        print(f"{label:<14} {format_fraction(best)}")
