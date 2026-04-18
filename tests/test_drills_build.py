"""Tests for drills/build.py — drill construction, JSON emission, slugs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import techniques as _techniques_pkg

from drills import (
    PATH_NAMES,
    TECHNIQUES,
    build_all,
    build_drill,
    display_names,
    drill_to_dict,
    path_slug,
    technique_slug,
    write_drill,
)
from drills.types import Brace, Drill, DrillStep
from trefoil.pool import load_pool


# ──────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope='module')
def pool():
    return load_pool()


# ──────────────────────────────────────────────────────────────────────────
# Shape of a single drill
# ──────────────────────────────────────────────────────────────────────────

def test_build_drill_third_sub_4ths_cw_has_eight_steps(pool):
    d = build_drill('Third sub', '4ths CW', pool)
    assert isinstance(d, Drill)
    assert d.technique == 'Third sub'
    assert d.path == '4ths CW'
    assert len(d.steps) == 8


def test_path_is_closed_loop(pool):
    # Every path starts and ends at I.
    for path in PATH_NAMES:
        d = build_drill('Third sub', path, pool)
        assert d.steps[0].brace.chord_nonterminal == 'I'
        assert d.steps[-1].brace.chord_nonterminal == 'I'
        assert len(d.steps) == 8


def test_drill_step_types(pool):
    d = build_drill('Quality sub', '2nds CW', pool)
    for step in d.steps:
        assert isinstance(step, DrillStep)
        assert isinstance(step.brace, Brace)
        assert isinstance(step.comment, str) and step.comment


# ──────────────────────────────────────────────────────────────────────────
# Brace coverage — every diatonic chord in the 118 pool has ≥ 1 voicing
# ──────────────────────────────────────────────────────────────────────────

def test_every_step_brace_has_at_least_one_ipool(pool):
    # Exercise the Cartesian product rather than one technique — if any path's
    # chord nonterminal is un-realizable, the whole corpus fails.
    for display in display_names():
        for path in PATH_NAMES:
            d = build_drill(display, path, pool)
            for idx, step in enumerate(d.steps):
                ips = step.brace.ipools
                assert len(ips) >= 1, (
                    f'brace for {step.brace.chord_nonterminal!r} in '
                    f'{display!r} × {path!r} at step {idx} has zero ipools'
                )
                # Each ipool is a 3-digit zero-padded id in 001..118.
                for ip in ips:
                    assert ip.isdigit() and len(ip) == 3
                    assert 1 <= int(ip) <= 118


def test_brace_ipools_are_unique_within_step(pool):
    for path in PATH_NAMES:
        d = build_drill('Inversion', path, pool)
        for step in d.steps:
            assert len(set(step.brace.ipools)) == len(step.brace.ipools)


# ──────────────────────────────────────────────────────────────────────────
# build_all — 18 × 6 = 108 drills
# ──────────────────────────────────────────────────────────────────────────

def test_build_all_produces_108_drills(pool):
    drills = build_all(pool)
    assert len(drills) == 108
    # Each (technique, path) pair appears exactly once.
    seen = {(d.technique, d.path) for d in drills}
    assert len(seen) == 108


def test_build_all_covers_every_technique_and_path(pool):
    drills = build_all(pool)
    techniques_seen = {d.technique for d in drills}
    paths_seen = {d.path for d in drills}
    assert techniques_seen == set(display_names())
    assert paths_seen == set(PATH_NAMES)


# ──────────────────────────────────────────────────────────────────────────
# write_drill — slug layout + JSON round-trip
# ──────────────────────────────────────────────────────────────────────────

def test_write_drill_writes_expected_path(tmp_path, pool):
    d = build_drill('Third sub', '4ths CW', pool)
    out = write_drill(d, tmp_path)
    assert out == tmp_path / 'third_sub' / '4ths_cw.json'
    assert out.exists()


def test_write_drill_json_round_trips(tmp_path, pool):
    d = build_drill('Open/closed spread', '3rds CCW', pool)
    out = write_drill(d, tmp_path)
    payload = json.loads(out.read_text(encoding='utf-8'))
    assert payload['technique'] == 'Open/closed spread'
    assert payload['path'] == '3rds CCW'
    assert len(payload['steps']) == 8
    step0 = payload['steps'][0]
    assert step0['brace']['chord_nonterminal'] == 'I'
    assert isinstance(step0['brace']['ipools'], list)
    assert len(step0['brace']['ipools']) >= 1
    assert isinstance(step0['comment'], str)


def test_write_drill_matches_drill_to_dict(tmp_path, pool):
    d = build_drill('Step approach', '2nds CCW', pool)
    out = write_drill(d, tmp_path)
    payload = json.loads(out.read_text(encoding='utf-8'))
    assert payload == drill_to_dict(d)


# ──────────────────────────────────────────────────────────────────────────
# Slugs
# ──────────────────────────────────────────────────────────────────────────

def test_technique_slug_table():
    # Every export name in techniques.__all__ is the slug for some display name.
    for export, display in TECHNIQUES:
        assert technique_slug(display) == export


def test_path_slug_table():
    assert path_slug('4ths CW') == '4ths_cw'
    assert path_slug('3rds CCW') == '3rds_ccw'
    assert path_slug('2nds CW') == '2nds_cw'


def test_technique_slug_specific_cases():
    assert technique_slug('Third sub') == 'third_sub'
    assert technique_slug('Open/closed spread') == 'open_closed_spread'
    assert technique_slug('Common-tone pivot') == 'common_tone_pivot'


# ──────────────────────────────────────────────────────────────────────────
# Typo guard — drill exports mirror techniques.__init__ exactly
# ──────────────────────────────────────────────────────────────────────────

def test_technique_names_match_init_exports():
    """The drill TECHNIQUES table must list exactly the 18 exports from
    ``techniques/__init__.py``, same set and same length — catches typos.
    """
    drill_exports = [export for export, _ in TECHNIQUES]
    assert set(drill_exports) == set(_techniques_pkg.__all__)
    assert len(drill_exports) == len(_techniques_pkg.__all__) == 18


def test_technique_names_match_init_order():
    """Canonical ordering of TECHNIQUES is the same as ``techniques.__all__``."""
    drill_exports = [export for export, _ in TECHNIQUES]
    assert drill_exports == list(_techniques_pkg.__all__)


# ──────────────────────────────────────────────────────────────────────────
# Comment sanity — non-empty, references the chord or technique verb
# ──────────────────────────────────────────────────────────────────────────

def test_comments_are_non_empty(pool):
    for display in display_names():
        d = build_drill(display, '4ths CW', pool)
        for step in d.steps:
            assert step.comment.strip(), f'empty comment in {display}'


def test_third_sub_comment_mentions_target(pool):
    d = build_drill('Third sub', '4ths CW', pool)
    # The tonic step (I → vi by default-down third) should mention 'vi'.
    step0 = d.steps[0]
    assert step0.brace.chord_nonterminal == 'I'
    assert 'vi' in step0.comment
