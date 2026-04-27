#!/usr/bin/env python3
"""Phrase-anchor shape selection.

Implements the principle from the encoding spec: pick one shape per phrase
that covers as much of the phrase's harmonic content as the hand can hold,
then mark only the bars whose chord-tones spill outside that anchor as
forced re-setups.

The pipeline:

  1. generate_candidates(phrase_chords, key)
       Enumerate shape candidates that *might* anchor the phrase.
       Pulled from the universal-winner pattern set + diatonic 7th-chord
       tetrads, rooted on each chord-tone of the phrase's dominant chord.

  2. is_setable(shape, reach)
       Per-position bounds check against the calibrated reach.

  3. coverage(shape, chord)
       Fraction of the chord's notes that the shape's pitch-set contains.

  4. aesthetic_score(shape, mode)
       README rule table: open-top reward, low-octave stepwise penalty,
       pitch-class diversity reward.

  5. select_anchor(phrase_chords, key, reach)
       Score every setable candidate as
           (coverage of every chord summed) * w_cov
         + aesthetic_score                  * w_aes
       and return the highest-scoring shape.

  6. mark_resets(anchor, phrase_chords)
       For each bar, if the anchor doesn't cover the bar's chord (cov < 1.0),
       flag it as a forced re-setup and pick a per-bar tetrad fallback.
"""
from __future__ import annotations

from dataclasses import dataclass

# Diatonic letter index — Tonic-relative scale-step lookup.
SCALE_INDEX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}
INDEX_TO_LETTER = {v: k for k, v in SCALE_INDEX.items()}

# Roman numeral → 0-based degree (chord root = scale degree N-1 of tonic).
NUMERAL_TO_DEGREE = {
    'I': 0, 'i': 0,
    'II': 1, 'ii': 1, 'ii°': 1,
    'III': 2, 'iii': 2,
    'IV': 3, 'iv': 3,
    'V': 4, 'v': 4,
    'VI': 5, 'vi': 5,
    'VII': 6, 'vii': 6, 'vii°': 6,
}

# README default reach (interval digits = scale-step intervals + 1).
DEFAULT_REACH = {
    'ring_middle':  4,    # ring → middle hard ceiling
    'middle_index': 5,    # middle → index
    'index_thumb':  6,    # index → thumb
    'thumb_ring':   13,   # thumb → ring (dyad-only)
}

# Universal-winner patterns (12) + the diatonic 7th-chord tetrad. These form
# the core candidate pool. Triads are also included for sparser anchors.
CANDIDATE_PATTERNS = [
    '33', '34', '35', '43', '44', '45', '53',  # triads
    '333', '335', '336', '344', '345', '346',
    '355', '356', '435', '436', '446', '456',
]


@dataclass(frozen=True)
class Shape:
    """A simple shape with a degree (1-7) and an interval-digit string.

    `pitch_set_in_key(key_root)` returns the diatonic pitch classes the
    shape contains when rooted on a given tonic.
    """
    degree: int                # 1..7 (mode root, scale degree)
    intervals: str             # e.g. '333', '346'

    def code(self) -> str:
        return f'^{self.degree}{self.intervals}'

    def pitch_classes(self, key_root: str) -> frozenset[str]:
        """Diatonic pitch classes (letters only) the shape contains.

        Walks the scale-step ladder from the shape's root, accumulating
        the letter at each finger position.
        """
        key_letter = key_root[0]
        idx = SCALE_INDEX[key_letter] + (self.degree - 1)
        out = [INDEX_TO_LETTER[idx % 7]]
        for digit in self.intervals:
            steps = int(digit, 16) - 1
            idx += steps
            out.append(INDEX_TO_LETTER[idx % 7])
        return frozenset(out)


# ─────────────────────── candidate generation ────────────────────────

def generate_candidates(phrase_chords: list[tuple[str, str]],
                        key_root: str) -> list[Shape]:
    """Enumerate shape candidates rooted on each chord-tone of every chord
    in the phrase. Deduplicated."""
    seen: set[tuple[int, str]] = set()
    candidates: list[Shape] = []
    for numeral, _quality in phrase_chords:
        deg0 = NUMERAL_TO_DEGREE.get(numeral)
        if deg0 is None:
            continue
        # Root candidates on the chord's root + 3rd + 5th + 7th degrees.
        for offset in (0, 2, 4, 6):
            cand_deg = ((deg0 + offset) % 7) + 1
            for pat in CANDIDATE_PATTERNS:
                key = (cand_deg, pat)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(Shape(degree=cand_deg, intervals=pat))
    return candidates


# ─────────────────────── setability filter ───────────────────────────

def is_setable(shape: Shape, reach: dict = DEFAULT_REACH) -> bool:
    """Each interval digit must fit its position's reach ceiling."""
    digits = shape.intervals
    if not digits:
        return True
    if ',' in digits:
        # Two-hand comma form: each side must satisfy its own one-hand limits.
        lh, rh = digits.split(',', 1)
        return _is_setable_one_hand(lh, reach) and _is_setable_one_hand(rh, reach)
    if len(digits) == 1:
        # Dyad: the only interval is treated as thumb-ring (longest reach).
        return int(digits, 16) <= reach['thumb_ring']
    return _is_setable_one_hand(digits, reach)


def _is_setable_one_hand(digits: str, reach: dict) -> bool:
    if not digits:
        return True
    limits = [
        reach['ring_middle'],
        reach['middle_index'],
        reach['index_thumb'],
    ]
    for i, d in enumerate(digits):
        if i >= len(limits):
            return False  # too many fingers for one hand
        if int(d, 16) > limits[i]:
            return False
    return True


# ─────────────────────── coverage scoring ────────────────────────────

# Diatonic chord pitch-classes per Roman numeral, in a major-key tonic.
# Returned as offsets from the key root letter.
TRIAD_OFFSETS = {
    'I': (0, 2, 4),
    'ii': (1, 3, 5),
    'iii': (2, 4, 6),
    'IV': (3, 5, 0),
    'V': (4, 6, 1),
    'vi': (5, 0, 2),
    'vii': (6, 1, 3),
    'vii°': (6, 1, 3),
}
SEVENTH_OFFSETS = {k: v + ((v[2] + 2) % 7,) for k, v in TRIAD_OFFSETS.items()}


def chord_pitch_classes(numeral: str, quality: str, key_root: str) -> frozenset[str]:
    """Letter pitch classes the chord contains, in the given major key."""
    base = SCALE_INDEX[key_root[0]]
    src = SEVENTH_OFFSETS if quality == '7' else TRIAD_OFFSETS
    offsets = src.get(numeral, src.get(numeral.lower(), TRIAD_OFFSETS.get(numeral, (0, 2, 4))))
    return frozenset(INDEX_TO_LETTER[(base + o) % 7] for o in offsets)


def coverage(shape: Shape, numeral: str, quality: str, key_root: str) -> float:
    """Fraction of the chord's pitch-classes contained in the shape (0..1)."""
    chord_pcs = chord_pitch_classes(numeral, quality, key_root)
    if not chord_pcs:
        return 0.0
    shape_pcs = shape.pitch_classes(key_root)
    return len(chord_pcs & shape_pcs) / len(chord_pcs)


# ─────────────────────── aesthetic scoring ───────────────────────────

def aesthetic_score(shape: Shape) -> float:
    """README rule table — applied to the interval digits.

    Positive: open-top profile, no stepwise clash, pitch-class diversity.
    Negative: stepwise (`2`) digits, three adjacent stepwise intervals.
    """
    digits = shape.intervals.replace(',', '')
    if not digits:
        return 0.0
    score = 0.0
    ints = [int(d, 16) for d in digits]
    # Open-top profile reward: top interval > bottom interval.
    if len(ints) >= 2 and ints[-1] > ints[0]:
        score += 1.0
    # Wide-interval reward: any interval ≥ 5.
    if any(i >= 5 for i in ints):
        score += 0.5
    # Stepwise clash penalty.
    score -= 0.5 * sum(1 for i in ints if i == 2)
    # Three adjacent stepwise intervals.
    if any(ints[k] == ints[k + 1] == ints[k + 2] == 2
           for k in range(len(ints) - 2)):
        score -= 2.0
    # Pitch-class diversity reward.
    distinct = len(set(digits)) / max(len(digits), 1)
    score += 0.3 * distinct
    return score


# ─────────────────────── anchor selection ────────────────────────────

@dataclass(frozen=True)
class AnchorChoice:
    shape: Shape
    coverage_per_bar: tuple[float, ...]
    score: float


def select_anchor(phrase_chords: list[tuple[str, str]],
                  key_root: str,
                  reach: dict = DEFAULT_REACH,
                  w_cov: float = 4.0,
                  w_aes: float = 1.0) -> AnchorChoice | None:
    """Pick the shape whose total coverage of the phrase's chords + aesthetic
    score is highest, subject to setability."""
    candidates = generate_candidates(phrase_chords, key_root)
    best: AnchorChoice | None = None
    for shape in candidates:
        if not is_setable(shape, reach):
            continue
        cov = tuple(coverage(shape, n, q, key_root) for n, q in phrase_chords)
        total_score = w_cov * sum(cov) + w_aes * aesthetic_score(shape)
        if best is None or total_score > best.score:
            best = AnchorChoice(shape=shape, coverage_per_bar=cov, score=total_score)
    return best


# ─────────────────────── re-setup detection ──────────────────────────

def mark_resets(anchor: AnchorChoice,
                phrase_chords: list[tuple[str, str]],
                threshold: float = 0.66) -> list[bool]:
    """True if the anchor's coverage of bar i drops below `threshold`.

    Bars marked True need a forced re-setup (per-bar tetrad fallback);
    bars marked False are coasted on the anchor.
    """
    return [c < threshold for c in anchor.coverage_per_bar]


def fallback_shape(numeral: str, quality: str) -> Shape:
    """Per-bar diatonic-7th tetrad on the chord's root (the retab L5 default)."""
    deg = NUMERAL_TO_DEGREE.get(numeral, 0) + 1 if numeral else 1
    return Shape(degree=deg, intervals='333')
