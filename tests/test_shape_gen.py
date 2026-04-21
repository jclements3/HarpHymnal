"""Tests for `trefoil/reharm/shape_gen.py` and the generated
`data/reharm/shape_library.json`.

Runnable both under pytest and as a script:
    python3 tests/test_shape_gen.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

# Ensure the repo root is on sys.path when running as a script.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from trefoil.reharm.shape_gen import (
    STRING_MIN, STRING_MAX, MIDDLE_C_STRING,
    MAX_HAND_SPAN, MAX_NOTES_PER_HAND,
    string_index, span, compute_gap,
    chord_pitch_classes, write_library,
)


LIB_PATH = os.path.join(REPO_ROOT, 'data', 'reharm', 'shape_library.json')
TACTICS_PATH = os.path.join(REPO_ROOT, 'data', 'reharm', 'tactics.json')


def _load_library() -> dict:
    """Load the generated shape library, rebuilding if absent."""
    if not os.path.exists(LIB_PATH):
        write_library(LIB_PATH)
    with open(LIB_PATH) as fh:
        return json.load(fh)


def _load_tactic_ids() -> set[str]:
    with open(TACTICS_PATH) as fh:
        tactics_doc = json.load(fh)
    return {t['id'] for t in tactics_doc['tactics']}


# ──────────────────── Constants tests ────────────────────

def test_constants_are_correct_for_47_string_harp():
    assert STRING_MIN == 1
    assert STRING_MAX == 47
    assert MIDDLE_C_STRING == 22
    # Sanity: the G7 mapping must land on string 47.  G = deg 5, oct 7.
    assert string_index(5, 7) == 47
    assert string_index(1, 1) == 1
    assert string_index(1, 4) == MIDDLE_C_STRING


# ──────────────────── Library structural tests ────────────────────

def test_library_top_level_fields():
    lib = _load_library()
    for key in ('version', 'generator', 'count', 'per_chord_counts', 'shapes'):
        assert key in lib, f'missing top-level field: {key}'
    assert lib['count'] == len(lib['shapes'])
    assert sum(lib['per_chord_counts'].values()) == lib['count']


def test_every_shape_within_47_string_bounds():
    lib = _load_library()
    for sh in lib['shapes']:
        for (d, o) in sh['lh'] + sh['rh']:
            si = string_index(d, o)
            assert STRING_MIN <= si <= STRING_MAX, (
                f"{sh['id']} has note deg={d} oct={o} at string {si}, "
                f"outside [{STRING_MIN}, {STRING_MAX}]"
            )


def test_every_shape_has_hand_span_le_10():
    lib = _load_library()
    for sh in lib['shapes']:
        lh_pairs = [tuple(n) for n in sh['lh']]
        rh_pairs = [tuple(n) for n in sh['rh']]
        sp_lh = span(lh_pairs)
        sp_rh = span(rh_pairs)
        assert sp_lh <= MAX_HAND_SPAN, f"{sh['id']} LH span {sp_lh} > {MAX_HAND_SPAN}"
        assert sp_rh <= MAX_HAND_SPAN, f"{sh['id']} RH span {sp_rh} > {MAX_HAND_SPAN}"
        # Also verify the record's own span fields agree
        assert sh['span_lh'] == sp_lh
        assert sh['span_rh'] == sp_rh


def test_every_shape_has_fingers_le_4_per_hand():
    lib = _load_library()
    for sh in lib['shapes']:
        assert sh['finger_count_lh'] == len(sh['lh'])
        assert sh['finger_count_rh'] == len(sh['rh'])
        assert sh['finger_count_lh'] <= MAX_NOTES_PER_HAND
        assert sh['finger_count_rh'] <= MAX_NOTES_PER_HAND


def test_bass_is_lowest_lh_and_top_is_highest_rh():
    lib = _load_library()
    for sh in lib['shapes']:
        # bass is the lowest note of whichever hands are present; for
        # two-handed shapes that means lowest LH.  For LH-only shells
        # (shape.shell_37) it's lowest LH; for RH-only shapes (none at
        # present) it'd be lowest RH.
        all_notes = [tuple(n) for n in sh['lh'] + sh['rh']]
        assert all_notes, f"{sh['id']} has no notes at all"
        lowest = min(all_notes, key=lambda n: string_index(*n))
        highest = max(all_notes, key=lambda n: string_index(*n))
        assert list(lowest) == sh['bass'], (
            f"{sh['id']}: bass {sh['bass']} is not lowest note {list(lowest)}"
        )
        assert list(highest) == sh['top'], (
            f"{sh['id']}: top {sh['top']} is not highest note {list(highest)}"
        )


def test_gap_formula_matches():
    """gap is defined as `rh_bot - lh_top - 1` in strings.

    Equivalent form from the brief:
        gap = top.si - bass.si - (span_lh - 1) - (span_rh - 1) - 1
    because
        top.si - bass.si
            = (lh_top.si - bass.si) + 1 + gap + (top.si - rh_bot.si)
            = (span_lh - 1) + 1 + gap + (span_rh - 1)
    so gap = top.si - bass.si - (span_lh - 1) - (span_rh - 1) - 1.
    """
    lib = _load_library()
    for sh in lib['shapes']:
        if not sh['lh'] or not sh['rh']:
            continue
        lh_pairs = [tuple(n) for n in sh['lh']]
        rh_pairs = [tuple(n) for n in sh['rh']]
        expected_gap_v1 = compute_gap(lh_pairs, rh_pairs)
        bass_si = string_index(*sh['bass'])
        top_si = string_index(*sh['top'])
        expected_gap_v2 = top_si - bass_si - (sh['span_lh'] - 1) - (sh['span_rh'] - 1) - 1
        assert sh['gap'] == expected_gap_v1 == expected_gap_v2, (
            f"{sh['id']}: gap {sh['gap']} vs v1 {expected_gap_v1} vs v2 {expected_gap_v2}"
        )


# ──────────────────── Semantic tests ────────────────────

def test_supports_reference_only_real_tactic_ids():
    lib = _load_library()
    valid_ids = _load_tactic_ids()
    for sh in lib['shapes']:
        for tid in sh['supports']:
            assert tid in valid_ids, (
                f"{sh['id']}: supports references unknown tactic id {tid!r}"
            )
            # And it must be a shape.* id, not something from another dimension
            assert tid.startswith('shape.'), (
                f"{sh['id']}: supports references non-shape tactic {tid!r}"
            )


def test_every_shape_has_at_least_one_support():
    lib = _load_library()
    for sh in lib['shapes']:
        assert sh['supports'], f"{sh['id']} has empty supports list"


def test_full_shapes_cover_every_chord_tone():
    """Any shape tagged shape.full_4 must have zero missing_chord_tones."""
    lib = _load_library()
    for sh in lib['shapes']:
        if 'shape.full_4' in sh['supports']:
            assert not sh['missing_chord_tones'], (
                f"{sh['id']} is full_4 but missing {sh['missing_chord_tones']}"
            )


def test_total_shape_count_at_least_300():
    lib = _load_library()
    assert lib['count'] >= 300, f"expected >= 300 shapes, got {lib['count']}"


def test_total_shape_count_grew_past_phase3_baseline():
    """Phase 3.5 extended the vocabulary beyond the original 1680 Phase 3
    library.  We require the new library to have at least a few hundred
    more shapes than the old baseline so the added color qualities are
    actually represented."""
    lib = _load_library()
    assert lib['count'] > 1680, (
        f"expected > 1680 shapes (Phase 3 baseline), got {lib['count']}"
    )


def test_every_non_meta_shape_tactic_has_at_least_5_shapes():
    """Every `shape.*` tactic (except the meta `shape.no_lh`) must be
    supported by ≥5 concrete shapes so the selector has real choice."""
    lib = _load_library()
    with open(TACTICS_PATH) as fh:
        tactics_doc = json.load(fh)
    shape_tactic_ids = [
        t['id'] for t in tactics_doc['tactics']
        if t['id'].startswith('shape.') and t['id'] != 'shape.no_lh'
    ]
    per_tactic = Counter()
    for sh in lib['shapes']:
        for tid in sh['supports']:
            per_tactic[tid] += 1
    for tid in shape_tactic_ids:
        assert per_tactic[tid] >= 5, (
            f'tactic {tid} has only {per_tactic[tid]} shapes, want ≥5'
        )


def test_per_shape_tactic_counts_field_matches_shapes():
    """The top-level `per_shape_tactic_counts` field must agree with
    what you'd get by re-counting `supports` across all shapes."""
    lib = _load_library()
    assert 'per_shape_tactic_counts' in lib
    computed = Counter()
    for sh in lib['shapes']:
        for tid in set(sh['supports']):
            computed[tid] += 1
    assert dict(computed) == lib['per_shape_tactic_counts'], (
        f'per_shape_tactic_counts field out of sync with shapes'
    )


def test_at_least_5_per_valid_chord_quality():
    lib = _load_library()
    counts = lib['per_chord_counts']
    for label, n in counts.items():
        assert n >= 5, f'chord {label} has only {n} shapes, want ≥5'


def test_register_variety_per_chord():
    """At minimum a chord should cover ≥3 distinct octave centroids —
    otherwise the register bucketing didn't distribute properly."""
    lib = _load_library()
    by_chord: dict[str, set[int]] = defaultdict(set)
    for sh in lib['shapes']:
        label = sh['chord']['numeral'] + (sh['chord']['quality'] or '')
        by_chord[label].add(sh['register_centroid'])
    for label, centroids in by_chord.items():
        assert len(centroids) >= 3, (
            f'chord {label} covers only centroids {sorted(centroids)}'
        )


def test_no_duplicate_shapes_within_same_chord():
    """(chord, lh, rh) must be unique."""
    lib = _load_library()
    seen: set[tuple] = set()
    for sh in lib['shapes']:
        key = (
            sh['chord']['numeral'],
            sh['chord']['quality'],
            tuple(tuple(n) for n in sh['lh']),
            tuple(tuple(n) for n in sh['rh']),
        )
        assert key not in seen, f'duplicate shape found: {sh["id"]}'
        seen.add(key)


def test_all_notes_are_in_chord_pitch_classes():
    """Every note in a shape must belong to the pc set implied by the
    shape's voicing (voicing_quality), not by the base chord quality
    stored for selector lookup."""
    lib = _load_library()
    for sh in lib['shapes']:
        # Alias records store the base-triad quality on chord.quality so
        # the selector can find them on plain hymn bars; voicing_quality
        # holds the true color quality whose pc set the pitches satisfy.
        vq = sh.get('voicing_quality', sh['chord']['quality'])
        pc = chord_pitch_classes({
            'numeral': sh['chord']['numeral'],
            'quality': vq,
        })
        for (d, o) in sh['lh'] + sh['rh']:
            assert d in pc, (
                f"{sh['id']} has note deg={d} but voicing pc set is {sorted(pc)}"
            )


def test_hands_do_not_interleave_on_string_axis():
    """By construction, every shape must have lh_top_idx < rh_bot_idx."""
    lib = _load_library()
    for sh in lib['shapes']:
        if not sh['lh'] or not sh['rh']:
            continue
        lh_top = max(string_index(*n) for n in sh['lh'])
        rh_bot = min(string_index(*n) for n in sh['rh'])
        assert lh_top < rh_bot, (
            f"{sh['id']}: LH top {lh_top} ≥ RH bottom {rh_bot} — hands interleave"
        )


# ──────────────────── Script entry ────────────────────

def _run_all() -> int:
    """Run every test_* function in this module as a plain script."""
    import inspect

    tests = [(name, fn) for name, fn in inspect.getmembers(sys.modules[__name__])
             if name.startswith('test_') and callable(fn)]
    tests.sort(key=lambda kv: kv[0])

    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f'  PASS  {name}')
        except AssertionError as e:
            failures += 1
            print(f'  FAIL  {name}: {e}')
        except Exception as e:
            failures += 1
            print(f'  ERROR {name}: {type(e).__name__}: {e}')

    print()
    print(f'{len(tests) - failures}/{len(tests)} tests passed')
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(_run_all())
