"""End-to-end tests for ``trefoil.rebuild``.

The rebuild reads ``source/HarpTrefoil.tex`` (the byte-exact mirror of
the canonical ``HarpChordSystem.tex``) plus the existing
``source/HarpChordSystem.json`` for prose pass-through, and emits a
grammar-native JSON at ``data/trefoil/HarpTrefoil.json``.  The pool
splits into `paths` (42 cycle voicings) and `reserve` (76 coloristic).
These tests verify counts, per-entry keys, and top-level schema.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from trefoil.rebuild import rebuild, write_rebuilt  # noqa: E402


TEX_SRC   = ROOT / 'source' / 'HarpTrefoil.tex'
PROSE_SRC = ROOT / 'source' / 'HarpChordSystem.json'


# ──────────────────────── Fixtures ────────────────────────

@pytest.fixture(scope='module')
def rebuilt() -> dict:
    assert TEX_SRC.is_file(), f"missing TeX source: {TEX_SRC}"
    assert PROSE_SRC.is_file(), f"missing prose JSON: {PROSE_SRC}"
    return rebuild(TEX_SRC, PROSE_SRC)


@pytest.fixture(scope='module')
def reference() -> dict:
    with open(PROSE_SRC, encoding='utf-8') as f:
        return json.load(f)


# ──────────────────────── End-to-end smoke ────────────────

def test_rebuild_runs_end_to_end(rebuilt):
    assert isinstance(rebuilt, dict)
    assert 'paths' in rebuilt
    assert 'reserve' in rebuilt


def test_write_rebuilt_round_trips(tmp_path, rebuilt):
    out = tmp_path / 'out' / 'HarpTrefoil.json'
    write_rebuilt(rebuilt, out)
    assert out.is_file()
    back = json.loads(out.read_text(encoding='utf-8'))
    assert back['schema_version'] == rebuilt['schema_version']
    assert len(back['paths']['entries']) == 42
    assert len(back['reserve']['entries']) == 76


# ──────────────────────── Entry counts ────────────────────

def test_paths_count(rebuilt):
    assert len(rebuilt['paths']['entries']) == 42


def test_reserve_count(rebuilt):
    assert len(rebuilt['reserve']['entries']) == 76


def test_pool_is_paths_plus_reserve(rebuilt):
    """pool = paths ∪ reserve = 118 fractions total."""
    total = len(rebuilt['paths']['entries']) + len(rebuilt['reserve']['entries'])
    assert total == 118


def test_cycle_breakdown(rebuilt):
    """42 path rows = 3 cycles × 14.  One-to-one on each cycle label."""
    by_cycle: dict[str, int] = {}
    for e in rebuilt['paths']['entries']:
        by_cycle[e['cycle']] = by_cycle.get(e['cycle'], 0) + 1
    assert by_cycle == {'2nds': 14, '3rds': 14, '4ths': 14}


# ──────────────────────── Per-entry shape ─────────────────

def test_path_entry_keys(rebuilt):
    expected = {'cycle', 'lh_roman', 'lh_figure',
                'rh_roman', 'rh_figure', 'cw_label', 'ccw_label'}
    for e in rebuilt['paths']['entries']:
        assert set(e.keys()) == expected, f"unexpected path keys: {set(e.keys())}"


def test_reserve_entry_keys(rebuilt):
    expected = {'lh_roman', 'lh_figure', 'rh_roman', 'rh_figure', 'mood'}
    for e in rebuilt['reserve']['entries']:
        assert set(e.keys()) == expected, f"unexpected reserve keys: {set(e.keys())}"


# ──────────────────────── Top-level keys ──────────────────

def test_top_level_has_refactored_pool_sections(rebuilt):
    """The rebuilt JSON carries the refactored section names and drops
    the legacy `jazz_progressions` / `stacked_chords` keys."""
    assert 'paths' in rebuilt
    assert 'reserve' in rebuilt
    assert 'jazz_progressions' not in rebuilt
    assert 'stacked_chords' not in rebuilt


def test_schema_version_bumped(rebuilt, reference):
    ref_sv = reference['schema_version']
    assert isinstance(ref_sv, int)
    assert rebuilt['schema_version'] == ref_sv + 1


# ──────────────────────── Prose pass-through ──────────────

def test_prose_sections_preserved(rebuilt, reference):
    """Conventions / patterns / cycles pass through verbatim from the
    reference.  how_to_use is rewritten to match the new terminology
    (tested separately below)."""
    for k in ('conventions', 'instrument', 'patterns',
              'chords_by_pattern_and_degree', 'cycles'):
        assert rebuilt[k] == reference[k], f"{k} diverged from reference"


def test_how_to_use_rewrites_legacy_section_names(rebuilt):
    """Pass-through prose has legacy section names rewritten so downstream
    readers see the refactored vocabulary."""
    text = json.dumps(rebuilt['how_to_use'], ensure_ascii=False)
    assert 'jazz_progressions' not in text
    assert 'stacked_chords' not in text


# ──────────────────────── Figure / Roman sanity ───────────

def test_figures_are_valid_wire_format(rebuilt):
    from grammar.parse import parse_figure
    for e in rebuilt['paths']['entries']:
        parse_figure(e['lh_figure'])
        parse_figure(e['rh_figure'])
    for e in rebuilt['reserve']['entries']:
        parse_figure(e['lh_figure'])
        parse_figure(e['rh_figure'])
