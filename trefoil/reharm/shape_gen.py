"""Generate a 47-string shape library for the diatonic jazz-harp selector.

Produces `data/reharm/shape_library.json`: a catalog of (LH, RH) shape
candidates spanning the full 47-string range (C1..G7), tagged with
metadata that maps each shape onto the `shape.*` tactics in
`data/reharm/tactics.json`.

Conceptually reuses the scoring/generation logic of
`trefoil/pretty_fraction.py` but parameterised over the 47-string range.
The existing `pretty_fraction` module is left untouched because other
scripts (sabt2jazz, build_compare_pages) import it.

String index formula (this module):
    string_index(deg, oct) = (oct - 1) * 7 + (deg - 1) + 1
    deg ∈ 1..7  (C..B)
    oct ∈ 1..7  (C1..B7, plus the extra strings C7..G7 in octave 7)
    C1 = 1, C4 = 22, G7 = 47  (G is deg 5 → (7-1)*7 + 4 + 1 = 47)

Run as a script to regenerate the library:
    python3 -m trefoil.reharm.shape_gen
"""
from __future__ import annotations

import json
import os
from collections import Counter
from itertools import combinations
from typing import Iterable


# ──────────────────── Constants (47-string variant) ────────────────────

STRING_MIN = 1          # C1
STRING_MAX = 47         # G7  = (7-1)*7 + (5-1) + 1
MIDDLE_C_STRING = 22    # C4

# Re-use quality tone offsets from pretty_fraction so shape semantics stay
# aligned with the 29-string selector's scoring.  We then extend the table
# locally with added-extension qualities (add9 / add11 / add13) that live
# only in the shape-library domain — they're not emitted by the legacy
# `pretty` API, so no need to push the additions upstream.
from trefoil.pretty_fraction import (
    QUALITY_TONES as _BASE_QUALITY_TONES,
    NUM_TO_DEG,
    C_MAJOR_LETTERS,
)

# Local copy with add9 / add11 / add13 appended.  These are *triads plus one
# extension above the octave*; the extension's octave placement is enforced
# at tagging time so a random pc-match doesn't masquerade as an extension.
QUALITY_TONES = dict(_BASE_QUALITY_TONES)
QUALITY_TONES.update({
    'add9':  [0, 2, 4, 8],   # triad (1,3,5) + 9 (= 2nd, an octave up)
    'add11': [0, 2, 4, 10],  # triad + 11 (= 4th, an octave up)
    'add13': [0, 2, 4, 12],  # triad + 13 (= 6th, an octave up)
})

# Which scale-degree offset (from the root, mod 7) is the "extension" for each
# add-quality.  Used by the tagger to find the extension note in a shape.
ADD_EXTENSION_OFFSET = {
    'add9':  1,   # 9 ≡ 2nd
    'add11': 3,   # 11 ≡ 4th
    'add13': 5,   # 13 ≡ 6th
}

MAX_HAND_SPAN = 10      # ≤10-string hand span per hand
MAX_NOTES_PER_HAND = 4  # 4 fingers per hand

# LH / RH octave ranges we enumerate over.  Deliberately asymmetric: the LH
# lives below middle C in most shapes, the RH lives above it.  A generous
# overlap (octaves 3–4 common to both) lets mid-register "hand-together"
# shapes appear too.
LH_OCTAVE_RANGE = range(1, 7)   # 1..6
RH_OCTAVE_RANGE = range(3, 8)   # 3..7

# Target chord vocabulary.
#
# Core set (unchanged): every diatonic triad × (triad, Δ, 7) — preserves the
# original 1680 shapes.
#
# Color set (new): sus / quartal / added-extension qualities on a subset of
# chords where those colors are musically common.  We skip combinations that
# are rare-to-nonsense (e.g. vii° add9, ii° quartal-on-tritone), using the
# lists below as a conservative curation.
TARGET_CHORDS = []

# --- Core set (preserves existing 1680 shapes) -------------------------- #
for numeral in ('I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°'):
    for quality in (None, 'Δ', '7'):
        TARGET_CHORDS.append({'numeral': numeral, 'quality': quality})

# --- Color set --------------------------------------------------------- #
# sus2 / sus4 — commonly used on major & minor tonic-class chords (I, IV, V,
# vi) and ii.  iii is iffy in diatonic (the 4th over iii is the 6th scale
# degree — a pleasant Phrygian color, but niche); we include it lightly.
# vii° is skipped — a sus on the half-dim chord loses its diminished identity.
for numeral in ('I', 'ii', 'IV', 'V', 'vi'):
    for quality in ('s2', 's4'):
        TARGET_CHORDS.append({'numeral': numeral, 'quality': quality})
# One extra sparkle: iii s4 (iii with a 6 on top) — rare but legal.
TARGET_CHORDS.append({'numeral': 'iii', 'quality': 's4'})

# Quartal voicings — pedagogically "the jazz sound" on ii / V / I and on vi.
# We generate q (3-note quartal triad) and q7 (4-note) on the same set.
for numeral in ('I', 'ii', 'IV', 'V', 'vi'):
    for quality in ('q', 'q7'):
        TARGET_CHORDS.append({'numeral': numeral, 'quality': quality})

# Added extensions — add9 is very common on I, IV, vi; add11 tasteful on ii,
# iv (minor i → ii in Ionian-rel), IV; add13 common on I, V, vi.  vii° gets
# nothing (add9 on a diminished triad clashes with the b5).
for numeral in ('I', 'IV', 'V', 'vi'):
    TARGET_CHORDS.append({'numeral': numeral, 'quality': 'add9'})
for numeral in ('ii', 'IV'):
    TARGET_CHORDS.append({'numeral': numeral, 'quality': 'add11'})
for numeral in ('I', 'V', 'vi'):
    TARGET_CHORDS.append({'numeral': numeral, 'quality': 'add13'})


# ──────────────────── Utilities ────────────────────

def string_index(deg: int, oct: int) -> int:
    """(degree, octave) → string index in [1..47]."""
    return (oct - 1) * 7 + (deg - 1) + 1


def to_abc(deg: int, oct: int) -> str:
    """(degree, octave) → ABC-ish note name, for logging."""
    L = C_MAJOR_LETTERS[deg - 1]
    if oct == 4:
        return L
    if oct < 4:
        return L + ',' * (4 - oct)
    if oct == 5:
        return L.lower()
    return L.lower() + "'" * (oct - 5)


def chord_pitch_classes(chord: dict) -> set[int]:
    """All diatonic scale degrees (1..7) present in the chord."""
    root = NUM_TO_DEG[chord['numeral']]
    q = chord.get('quality')
    offsets = list(QUALITY_TONES.get(q, QUALITY_TONES[None]))
    return {((root - 1) + off) % 7 + 1 for off in offsets}


def span(notes: list[tuple[int, int]]) -> int:
    """Number of strings covered by a hand (inclusive).  Empty hand → 0."""
    if not notes:
        return 0
    idxs = [string_index(*n) for n in notes]
    return max(idxs) - min(idxs) + 1


def all_positions(pc_set: Iterable[int], oct_range: Iterable[int]) -> list[tuple[int, int]]:
    """All (deg, oct) positions within pc_set × oct_range inside [1..47]."""
    out = []
    for d in pc_set:
        for o in oct_range:
            si = string_index(d, o)
            if STRING_MIN <= si <= STRING_MAX:
                out.append((d, o))
    return sorted(out, key=lambda n: string_index(*n))


def hand_combos(positions: list[tuple[int, int]], min_notes: int, max_notes: int,
                max_span: int) -> Iterable[tuple[tuple[int, int], ...]]:
    """Yield note-tuples of size min_notes..max_notes from positions, span-capped."""
    n = len(positions)
    for size in range(min_notes, max_notes + 1):
        for combo in combinations(positions, size):
            idxs = [string_index(*p) for p in combo]
            if max(idxs) - min(idxs) + 1 > max_span:
                continue
            yield combo


# ──────────────────── Tagging logic ────────────────────

def _tags_and_supports(chord: dict, lh: list[tuple[int, int]], rh: list[tuple[int, int]]) -> tuple[list[str], list[str]]:
    """Derive tag + supports lists from a fully-assembled (lh, rh) shape.

    Supports are tactic ids from tactics.json (the `shape.*` dimension);
    tags are free-form keywords lifted from those tactics' `tags` arrays so
    the selector can filter by coarse category.
    """
    all_notes = lh + rh
    pc = chord_pitch_classes(chord)
    present_pc = {n[0] for n in all_notes}

    root = NUM_TO_DEG[chord['numeral']]
    third = ((root - 1) + 2) % 7 + 1
    fifth = ((root - 1) + 4) % 7 + 1
    seventh = ((root - 1) + 6) % 7 + 1
    q = chord.get('quality')

    total_notes = len(all_notes)
    rooted = root in present_pc
    has_third = third in present_pc
    has_seventh = seventh in present_pc
    covers_all = not (pc - present_pc)

    tags: list[str] = []
    supports: list[str] = []

    # shape.full_4 — a "full 4-finger" voicing: 4+ distinct pitches and every
    # chord pitch class present.  We allow up to MAX_NOTES_PER_HAND per hand
    # (= 8 total) so "full_4" meaningfully lands on ~4-note shapes.
    if covers_all and total_notes >= 4 and total_notes <= 6:
        supports.append('shape.full_4')
        if 'full' not in tags:
            tags.append('full')
        if rooted and 'rooted' not in tags:
            tags.append('rooted')

    # shape.three_finger — drop one chord tone (so 3 pitch classes out of a
    # 4-tone chord, or the full triad).  Triads always satisfy this.
    if total_notes >= 3 and total_notes <= 5:
        if q in (None, '', 's2', 's4', 'q'):
            # triads: covers_all ⇒ three_finger
            if covers_all:
                supports.append('shape.three_finger')
                if 'full' not in tags:
                    tags.append('full')
        else:
            # 4-tone chords (7th-chord or add-extension or q7): "drop one"
            # is tolerated.  For add9/11/13 we never drop the extension
            # (that's the point of the chord); we tolerate dropping the 5th.
            missing = pc - present_pc
            if q in ADD_EXTENSION_OFFSET:
                ext_pc = ((root - 1) + ADD_EXTENSION_OFFSET[q]) % 7 + 1
                if ext_pc not in missing and len(missing) <= 1:
                    supports.append('shape.three_finger')
                    if 'full' not in tags:
                        tags.append('full')
            elif len(missing) <= 1:
                supports.append('shape.three_finger')
                if 'full' not in tags:
                    tags.append('full')

    # shape.shell_37 — 2-finger shell: 3rd + 7th, no root.  We read it
    # loosely: the shape contains the 3rd and the 7th, does NOT contain the
    # root, and is lean (≤4 total notes).  Only applies to 7-chord qualities.
    if q in ('7', 'Δ', 'h7'):
        if has_third and has_seventh and not rooted and total_notes <= 4:
            supports.append('shape.shell_37')
            if 'shell' not in tags:
                tags.append('shell')
            if 'rootless' not in tags:
                tags.append('rootless')

    # shape.root_10 — root + 10th (= 3rd up an octave).  Detect: LH has
    # root, RH lowest tone is the 3rd an octave+ above.  Only tag on
    # base-triad / seventh qualities; color qualities (sus / quartal /
    # add) that happen to have root and third get their own tags and
    # shouldn't also masquerade as a root_10 shell.
    if (q in (None, '', '7', 'Δ', 'h7', 'ø7', '6')
            and lh and rh and rooted and has_third):
        lh_root_notes = [n for n in lh if n[0] == root]
        rh_third_notes = [n for n in rh if n[0] == third]
        if lh_root_notes and rh_third_notes:
            # find any root/third pair where the third sits a 10th (or more)
            # above the root
            found = False
            for r in lh_root_notes:
                r_idx = string_index(*r)
                for t in rh_third_notes:
                    t_idx = string_index(*t)
                    if t_idx - r_idx >= 9:   # ≥ 9 strings = ≥ a 10th
                        found = True
                        break
                if found:
                    break
            if found:
                supports.append('shape.root_10')
                if 'shell' not in tags:
                    tags.append('shell')
                if 'rooted' not in tags:
                    tags.append('rooted')

    # shape.quartal — the chord itself is a quartal voicing (q / q7).  The
    # quartal qualities produce pitch-class sets that already look like
    # stacked-4ths constructions, so any voicing of them gets the tag.
    if q in ('q', 'q7') and covers_all:
        supports.append('shape.quartal')
        if 'quartal' not in tags:
            tags.append('quartal')
        if 'color' not in tags:
            tags.append('color')

    # shape.sus — sus2 / sus4 qualities.  Both the 2 (sus2) and the 4 (sus4)
    # must be present, along with the root and 5th, for the voicing to read
    # as "sus".  covers_all already enforces this but we keep the check
    # explicit for clarity.
    if q in ('s2', 's4') and covers_all:
        supports.append('shape.sus')
        if 'sus' not in tags:
            tags.append('sus')
        if 'color' not in tags:
            tags.append('color')

    # shape.add9 / shape.add11 / shape.add13 — triad + one specific
    # extension above the octave.
    #
    # Rule: the extension pc must be voiced *at or above* the octave above
    # the lowest root.  Otherwise the 9/11/13 collapses into a 2/4/6 that
    # reads as sus / passing / 6-chord, not as an extension.  We also require
    # the full triad (1-3-5) to be present so the ear has something for the
    # extension to hang on.
    if q in ADD_EXTENSION_OFFSET and covers_all:
        ext_pc = ((root - 1) + ADD_EXTENSION_OFFSET[q]) % 7 + 1
        # Find lowest root (LH first, then whole shape) string index.
        root_notes = [n for n in all_notes if n[0] == root]
        ext_notes = [n for n in all_notes if n[0] == ext_pc]
        if root_notes and ext_notes:
            lowest_root = min(string_index(*n) for n in root_notes)
            highest_ext = max(string_index(*n) for n in ext_notes)
            # Extension must sit ≥ 7 strings (one diatonic octave) above
            # the lowest root to voice as an extension rather than as an
            # inner-voice colour tone.
            if highest_ext - lowest_root >= 7:
                tag_id = 'shape.' + q  # shape.add9 / .add11 / .add13
                supports.append(tag_id)
                if 'extension' not in tags:
                    tags.append('extension')
                if 'color' not in tags:
                    tags.append('color')

    # Ensure at least one shape.* support is recorded.  A voicing that
    # doesn't match any of the above (e.g. a two-note triad shell we happen
    # to generate) gets dropped by the filter step.
    return tags, supports


# ──────────────────── Scoring (47-string variant) ────────────────────

def score_fraction(chord: dict, lh: list[tuple[int, int]], rh: list[tuple[int, int]]) -> int:
    """Penalty score for a (LH, RH) shape.  Lower = prettier.

    Mirrors pretty_fraction.score_fraction's spirit but:
      - uses the 47-string bounds
      - does NOT penalize wide gaps (per REHARM_TACTICS decision 1:
        the gap is flexible, the selector picks per goal)
      - preserves the "low close 2nds" penalty, essential-tone bonus,
        bass-clarity bonus, top-is-chord-tone bonus.
    """
    all_notes = lh + rh
    if not all_notes:
        return 9999
    for n in all_notes:
        si = string_index(*n)
        if si < STRING_MIN or si > STRING_MAX:
            return 9999
    if span(lh) > MAX_HAND_SPAN or span(rh) > MAX_HAND_SPAN:
        return 9999
    if len(lh) > MAX_NOTES_PER_HAND or len(rh) > MAX_NOTES_PER_HAND:
        return 9999

    pc = chord_pitch_classes(chord)
    for n in all_notes:
        if n[0] not in pc:
            return 9999

    penalty = 0
    root = NUM_TO_DEG[chord['numeral']]
    third = ((root - 1) + 2) % 7 + 1
    fifth = ((root - 1) + 4) % 7 + 1
    q = chord.get('quality')
    present_pc = {n[0] for n in all_notes}

    # Root bonus (soft): root present is preferred, but rootless shells
    # are legal so this is a small tilt.
    if root not in present_pc:
        penalty += 1

    # Density guardrails
    if len(all_notes) > 6:
        penalty += 2 * (len(all_notes) - 6)

    # Bass clarity: lowest LH note should be a chord tone (root/3rd/5th)
    if lh:
        bass_deg = sorted(lh, key=lambda n: string_index(*n))[0][0]
        if bass_deg not in (root, third, fifth):
            penalty += 2

    # Top clarity: highest RH note should be a chord tone
    if rh:
        top_deg = sorted(rh, key=lambda n: string_index(*n))[-1][0]
        if top_deg not in pc:
            penalty += 2

    # Close 2nds in low register (below C4) are muddy on a harp
    idxs = sorted(string_index(*n) for n in all_notes)
    for a, b in zip(idxs, idxs[1:]):
        if b - a == 1 and a < MIDDLE_C_STRING:
            penalty += 3
            break

    # Missing 3rd (unless quality inherently omits it)
    if q not in ('s2', 's4', 'q', 'q7'):
        if third not in present_pc:
            penalty += 2

    return penalty


# ──────────────────── Gap formula ────────────────────

def compute_gap(lh: list[tuple[int, int]], rh: list[tuple[int, int]]) -> int:
    """Number of empty strings between LH top and RH bottom.

    gap = rh_bot_idx - lh_top_idx - 1
    (equivalent to top_idx - bass_idx - (span_lh - 1) - (span_rh - 1) - 1,
    because top_idx - bass_idx = (lh_top_idx - bass_idx) + 1 + gap +
    (top_idx - rh_bot_idx), and the first/last parens equal span-1 each.)

    Can be negative when the hands interleave — that's a legal "overlap"
    and the selector can reject it downstream if desired.
    """
    if not lh or not rh:
        return 0
    lh_top = max(string_index(*n) for n in lh)
    rh_bot = min(string_index(*n) for n in rh)
    return rh_bot - lh_top - 1


# ──────────────────── Generator ────────────────────

def generate_rootless_shells(chord: dict) -> list[dict]:
    """Generate 2-note rootless 3+7 shells (shape.shell_37).

    Structurally distinct from two-handed voicings: a single hand (LH),
    exactly two notes (the chord's 3rd and 7th), no root.  Only applicable
    to 7-chord qualities (7, Δ, h7).  We enumerate shells across LH
    octaves 2..5 so the selector has register variety.
    """
    q = chord.get('quality')
    if q not in ('7', 'Δ', 'h7'):
        return []

    root = NUM_TO_DEG[chord['numeral']]
    third = ((root - 1) + 2) % 7 + 1
    seventh = ((root - 1) + 6) % 7 + 1

    out: list[dict] = []
    seen: set = set()
    # LH octaves 2..5 give us shells across the useful register.  For each
    # 3rd-octave choice, pair it with the 7th placed either just above or
    # just below (within the 10-string hand span).
    for oct3 in range(2, 6):
        third_pos = (third, oct3)
        s3 = string_index(*third_pos)
        if s3 < STRING_MIN or s3 > STRING_MAX:
            continue
        for oct7 in range(max(1, oct3 - 1), min(6, oct3 + 1) + 1):
            seventh_pos = (seventh, oct7)
            s7 = string_index(*seventh_pos)
            if s7 < STRING_MIN or s7 > STRING_MAX:
                continue
            if s3 == s7:
                continue
            lo, hi = (third_pos, seventh_pos) if s3 < s7 else (seventh_pos, third_pos)
            lh = [lo, hi]
            if span(lh) > MAX_HAND_SPAN:
                continue
            key = tuple(sorted(lh))
            if key in seen:
                continue
            seen.add(key)

            # Score mirrors score_fraction but we deliberately don't penalize
            # the missing root — that's the point of the shell.
            penalty = 0
            # Close 2nds in low register
            s_lo, s_hi = string_index(*lh[0]), string_index(*lh[1])
            if s_hi - s_lo == 1 and s_lo < MIDDLE_C_STRING:
                penalty += 3
            # Prefer shells that sit near middle of the harp (centered on
            # middle C ± one octave) — extreme-low shells sound muddy, and
            # very-high ones read as harmonics rather than shells.
            centroid_idx = (s_lo + s_hi) // 2
            penalty += abs(centroid_idx - MIDDLE_C_STRING) // 7

            out.append({
                'chord': dict(chord),
                'lh': [list(n) for n in lh],
                'rh': [],
                'score': penalty,
                '_tags': ['shell', 'rootless'],
                '_supports': ['shape.shell_37'],
                '_voicing_quality': chord.get('quality'),
            })

    # Sort: cleanest shells first.
    out.sort(key=lambda sh: (sh['score'], string_index(*sh['lh'][0])))
    return out


def generate_shapes_for_chord(chord: dict, max_per_chord: int = 80) -> list[dict]:
    """Enumerate (LH, RH) shapes for one chord, tagged and scored."""
    pc = chord_pitch_classes(chord)
    # Build LH position pool (LH_OCTAVE_RANGE × pc), and same for RH.
    lh_positions = all_positions(pc, LH_OCTAVE_RANGE)
    rh_positions = all_positions(pc, RH_OCTAVE_RANGE)

    shapes: list[dict] = []
    seen = set()

    # LH hand combos: 2..MAX_NOTES_PER_HAND notes, span ≤ 10.  Also allow
    # 1-note LH for bass-only shapes, handled separately later.
    lh_hands = list(hand_combos(lh_positions,
                                min_notes=2,
                                max_notes=MAX_NOTES_PER_HAND,
                                max_span=MAX_HAND_SPAN))
    rh_hands = list(hand_combos(rh_positions,
                                min_notes=2,
                                max_notes=MAX_NOTES_PER_HAND,
                                max_span=MAX_HAND_SPAN))

    # To keep the enumeration tractable on 4-note chords, we trim LH/RH
    # candidates that obviously fail the "every chord pc present" test when
    # merged with anything, and we require hands not to overlap (lh_top <
    # rh_bot or at-least lh_top <= rh_bot allowing shared pitch classes in
    # different octaves).
    for lh in lh_hands:
        lh_list = list(lh)
        lh_top_idx = max(string_index(*n) for n in lh_list)
        lh_pc = {n[0] for n in lh_list}

        for rh in rh_hands:
            rh_list = list(rh)
            rh_bot_idx = min(string_index(*n) for n in rh_list)
            # strict ordering: hands don't interleave on the string axis
            if rh_bot_idx <= lh_top_idx:
                continue

            # Score first (cheap reject)
            s = score_fraction(chord, lh_list, rh_list)
            if s >= 9999:
                continue

            # Tag + supports
            tags, supports = _tags_and_supports(chord, lh_list, rh_list)
            if not supports:
                # shape doesn't instantiate any shape.* tactic → skip
                continue

            key = (tuple(sorted(lh_list)), tuple(sorted(rh_list)))
            if key in seen:
                continue
            seen.add(key)

            shapes.append({
                'chord': dict(chord),
                'lh': [list(n) for n in sorted(lh_list, key=lambda p: string_index(*p))],
                'rh': [list(n) for n in sorted(rh_list, key=lambda p: string_index(*p))],
                'score': s,
                '_tags': tags,
                '_supports': supports,
                '_voicing_quality': chord.get('quality'),
            })

    # Sort by score first (ties: fewer notes, then lowest bass).
    shapes.sort(key=lambda sh: (
        sh['score'],
        len(sh['lh']) + len(sh['rh']),
        string_index(*sh['lh'][0]),
    ))

    # Register-aware bucketing: don't let all top-scoring shapes cluster in
    # one octave band.  We bucket by the octave of the lowest LH note
    # (bass's octave) and round-robin across buckets so every register is
    # represented before we start taking second-tier shapes from any one
    # register.
    buckets: dict[int, list[dict]] = {}
    for sh in shapes:
        bass_oct = sh['lh'][0][1]
        buckets.setdefault(bass_oct, []).append(sh)

    picked: list[dict] = []
    keys = sorted(buckets.keys())
    # Round-robin until we hit the cap or exhaust every bucket.
    idx = {k: 0 for k in keys}
    while len(picked) < max_per_chord:
        progressed = False
        for k in keys:
            if idx[k] < len(buckets[k]):
                picked.append(buckets[k][idx[k]])
                idx[k] += 1
                progressed = True
                if len(picked) >= max_per_chord:
                    break
        if not progressed:
            break
    return picked


# ──────────────────── Library assembly ────────────────────

def build_library(max_per_chord: int = 80) -> dict:
    """Build the full shape library dict (pre-serialisation)."""
    all_shapes = []
    per_chord_counts: Counter = Counter()
    per_shape_tactic_counts: Counter = Counter()

    for chord in TARGET_CHORDS:
        # Skip quality/numeral combinations that don't exist in QUALITY_TONES
        if chord.get('quality') not in QUALITY_TONES:
            continue
        cshapes = generate_shapes_for_chord(chord, max_per_chord=max_per_chord)
        for sh in cshapes:
            all_shapes.append(sh)

    # Rootless 3+7 shells (shape.shell_37) — generated separately since
    # they're one-handed 2-note structures, not (LH, RH) pairs.  We attach
    # shells for every 7-chord-quality target in the core set.
    for chord in TARGET_CHORDS:
        q = chord.get('quality')
        if q not in ('7', 'Δ', 'h7'):
            continue
        for sh in generate_rootless_shells(chord):
            all_shapes.append(sh)

    # --------------------- Color-shape alias records ------------------- #
    #
    # The selector indexes shapes by (numeral, chord.quality) and hymns in
    # this corpus use only the plain-triad quality (None) and the dominant-7
    # quality ('7').  A sus / quartal / add shape labelled with quality
    # 's2' / 'q' / 'add9' / etc. therefore never gets picked for a plain-I
    # bar even though musically it IS the color re-voicing the harpist
    # wants.  We resolve this by cloning every color shape under the base
    # quality's lookup key.  The clone preserves the original voicing in
    # `voicing_quality` so pitch-class validation still has something to
    # check against.
    #
    # Aliasing rules:
    #   s2, s4, q, add9, add11, add13  → alias under quality=None  (triad base)
    #   q7                             → alias under quality=None AND '7' (dom-7 base)
    # Shell_37 is already a 7-chord voicing so no alias needed.
    COLOR_TO_BASE_ALIASES = {
        's2':    [None],
        's4':    [None],
        'q':     [None],
        'q7':    [None, '7'],
        'add9':  [None],
        'add11': [None],
        'add13': [None],
    }
    # Pre-compute (n, q, lh, rh) signatures of all primary (non-alias)
    # shapes so we can drop any alias whose notes already appear under
    # the same (n, q) key.  This avoids collisions between a color
    # voicing that coincidentally sits on only base-triad pitch classes
    # (e.g. a q7 shape whose drop-one variant happens to be a plain
    # I7 shell) and the existing plain-quality shape with those same
    # notes.
    def _sig(sh: dict) -> tuple:
        return (
            sh['chord']['numeral'],
            sh['chord'].get('quality'),
            tuple(tuple(n) for n in sh['lh']),
            tuple(tuple(n) for n in sh['rh']),
        )
    primary_sigs: set[tuple] = {_sig(sh) for sh in all_shapes}

    aliases: list[dict] = []
    alias_sigs: set[tuple] = set()
    for sh in list(all_shapes):
        q = sh.get('_voicing_quality')
        if q in COLOR_TO_BASE_ALIASES:
            for base_q in COLOR_TO_BASE_ALIASES[q]:
                alias = dict(sh)
                alias['chord'] = {
                    'numeral': sh['chord']['numeral'],
                    'quality': base_q,
                }
                alias['_is_alias'] = True
                sig = _sig(alias)
                if sig in primary_sigs or sig in alias_sigs:
                    # collision — a primary shape already covers these
                    # notes under the same (numeral, base_q) lookup key,
                    # or another alias got here first.  Skip.
                    continue
                alias_sigs.add(sig)
                # keep _voicing_quality = original color quality
                aliases.append(alias)
    all_shapes.extend(aliases)

    # Assign ids and finalise the record shape
    records = []
    for i, sh in enumerate(all_shapes, start=1):
        lh = [tuple(n) for n in sh['lh']]
        rh = [tuple(n) for n in sh['rh']]
        # bass = lowest of whichever hand has notes (falls back to rh if lh is
        # empty); top = highest of whichever has notes (falls back to lh).
        # Rootless shells live entirely in LH (rh = []), so we must be careful
        # here.
        all_nts = lh + rh
        bass = min(all_nts, key=lambda n: string_index(*n))
        top = max(all_nts, key=lambda n: string_index(*n))
        chord = sh['chord']

        present_pc = {n[0] for n in lh + rh}
        # Use voicing_quality (the actual color quality) for pc-set
        # derivation so alias records — whose chord.quality is reset to
        # the base-triad quality for selector lookup — still validate
        # their pitches against the true voicing's pc set.
        voicing_quality = sh.get('_voicing_quality', chord.get('quality'))
        voicing_chord = {'numeral': chord['numeral'], 'quality': voicing_quality}
        pc = chord_pitch_classes(voicing_chord)
        covered = sorted(pc & present_pc)
        missing = sorted(pc - present_pc)

        # Register centroid: average octave of all notes, rounded.
        octs = [n[1] for n in lh + rh]
        centroid = round(sum(octs) / len(octs))

        hand = 'both' if lh and rh else ('lh' if lh else 'rh')

        label = chord['numeral'] + (chord.get('quality') or '')
        if sh.get('_is_alias'):
            # distinguish alias entries in the per-chord counts so
            # duplication is inspectable.
            label += '[alias]'
        per_chord_counts[label] += 1
        for tid in set(sh['_supports']):
            per_shape_tactic_counts[tid] += 1

        rec = {
            'id': f'shape_{i:04d}',
            'chord': {
                'numeral': chord['numeral'],
                'quality': chord.get('quality'),
            },
            # voicing_quality = the actual quality implied by this shape's
            # pitches.  For alias records this differs from chord.quality,
            # which has been rewritten to the base-triad quality so the
            # selector's (numeral, chord.quality) index finds the shape on
            # plain hymn bars.  Test invariants check pitches against this
            # field, not chord.quality.
            'voicing_quality': voicing_quality,
            'is_alias': bool(sh.get('_is_alias')),
            'hand': hand,
            'lh': [[d, o] for (d, o) in lh],
            'rh': [[d, o] for (d, o) in rh],
            'bass': [bass[0], bass[1]],
            'top': [top[0], top[1]],
            'span_lh': span(lh),
            'span_rh': span(rh),
            'gap': compute_gap(lh, rh),
            'finger_count_lh': len(lh),
            'finger_count_rh': len(rh),
            'register_centroid': centroid,
            'chord_tones_covered': covered,
            'missing_chord_tones': missing,
            'tags': sorted(set(sh['_tags'])),
            'supports': sorted(set(sh['_supports'])),
            'score': sh['score'],
        }
        records.append(rec)

    library = {
        'version': 1,
        'generator': 'trefoil/reharm/shape_gen.py',
        'generator_notes': (
            '47-string (C1..G7) shape catalog generated by enumerating '
            'LH/RH chord-tone combinations under the 10-string hand-span '
            'and 4-finger-per-hand constraints.  Each shape declares which '
            'shape.* tactics from tactics.json it legitimately instantiates.'
        ),
        'string_range': {
            'min': STRING_MIN,
            'max': STRING_MAX,
            'middle_c': MIDDLE_C_STRING,
        },
        'count': len(records),
        'per_chord_counts': dict(per_chord_counts),
        'per_shape_tactic_counts': dict(per_shape_tactic_counts),
        'shapes': records,
    }
    return library


def write_library(path: str | None = None, max_per_chord: int = 80) -> str:
    """Generate and write the library to disk; return the path."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if path is None:
        path = os.path.join(repo_root, 'data', 'reharm', 'shape_library.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lib = build_library(max_per_chord=max_per_chord)
    with open(path, 'w') as fh:
        json.dump(lib, fh, indent=2)
    return path


if __name__ == '__main__':
    out = write_library()
    with open(out) as fh:
        lib = json.load(fh)
    print(f'wrote {out}')
    print(f'  total shapes: {lib["count"]}')
    print(f'  per-chord counts:')
    for chord, n in sorted(lib['per_chord_counts'].items()):
        print(f'    {chord:<8} {n}')
