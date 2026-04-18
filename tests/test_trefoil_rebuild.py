"""End-to-end tests for ``trefoil.rebuild``.

The rebuild reads ``source/HarpTrefoil.tex`` (the byte-exact mirror of
the canonical ``HarpChordSystem.tex``) plus the existing
``source/HarpChordSystem.json`` for prose pass-through, and emits a
grammar-native JSON at ``data/trefoil/HarpTrefoil.json``.  These tests
verify counts, per-entry keys, and top-level schema parity with the
reference JSON.
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
    """Run the rebuild once and reuse across assertions."""
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
    assert 'jazz_progressions' in rebuilt
    assert 'stacked_chords' in rebuilt


def test_write_rebuilt_round_trips(tmp_path, rebuilt):
    out = tmp_path / 'out' / 'HarpTrefoil.json'
    write_rebuilt(rebuilt, out)
    assert out.is_file()
    back = json.loads(out.read_text(encoding='utf-8'))
    assert back['schema_version'] == rebuilt['schema_version']
    assert len(back['jazz_progressions']['entries']) == 42
    assert len(back['stacked_chords']['entries']) == 76


# ──────────────────────── Entry counts ────────────────────

def test_jazz_progressions_count(rebuilt):
    assert len(rebuilt['jazz_progressions']['entries']) == 42


def test_stacked_chords_count(rebuilt):
    assert len(rebuilt['stacked_chords']['entries']) == 76


def test_cycle_breakdown(rebuilt):
    """42 rows = 3 cycles × 14.  One-to-one on each cycle label."""
    by_cycle: dict[str, int] = {}
    for e in rebuilt['jazz_progressions']['entries']:
        by_cycle[e['cycle']] = by_cycle.get(e['cycle'], 0) + 1
    assert by_cycle == {'2nds': 14, '3rds': 14, '4ths': 14}


# ──────────────────────── Per-entry shape ─────────────────

def test_jazz_entry_keys(rebuilt):
    expected = {'cycle', 'lh_roman', 'lh_figure',
                'rh_roman', 'rh_figure', 'cw_label', 'ccw_label'}
    for e in rebuilt['jazz_progressions']['entries']:
        assert set(e.keys()) == expected, f"unexpected jazz keys: {set(e.keys())}"


def test_pool_entry_keys(rebuilt):
    expected = {'lh_roman', 'lh_figure', 'rh_roman', 'rh_figure', 'mood'}
    for e in rebuilt['stacked_chords']['entries']:
        assert set(e.keys()) == expected, f"unexpected pool keys: {set(e.keys())}"


# ──────────────────────── Top-level key parity ────────────

def test_top_level_keys_match_reference(rebuilt, reference):
    """The new JSON must be field-for-field at the top level with the ref."""
    assert set(rebuilt.keys()) == set(reference.keys())


def test_schema_version_bumped(rebuilt, reference):
    """Schema version should increment by exactly 1 over the reference."""
    ref_sv = reference['schema_version']
    assert isinstance(ref_sv, int)
    assert rebuilt['schema_version'] == ref_sv + 1


# ──────────────────────── Prose pass-through ──────────────

def test_prose_sections_preserved(rebuilt, reference):
    """Prose sections are copied verbatim from the reference JSON."""
    for k in ('how_to_use', 'conventions', 'instrument', 'patterns',
              'chords_by_pattern_and_degree', 'cycles'):
        assert rebuilt[k] == reference[k], f"{k} diverged from reference"


# ──────────────────────── Figure / Roman sanity ───────────

def test_figures_are_valid_wire_format(rebuilt):
    """Every figure must parse back through grammar.parse.parse_figure."""
    from grammar.parse import parse_figure
    for e in rebuilt['jazz_progressions']['entries']:
        parse_figure(e['lh_figure'])
        parse_figure(e['rh_figure'])
    for e in rebuilt['stacked_chords']['entries']:
        parse_figure(e['lh_figure'])
        parse_figure(e['rh_figure'])
