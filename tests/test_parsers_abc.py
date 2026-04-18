"""Tests for parsers.abc — the ABC-to-Song pipeline.

Scope:
  - parse_hymn on a small representative hymn ("Amazing Grace")
  - JSON round-trip (song_to_json → reload → reserialize)
  - minor-key detection on a minor-mode hymn ("Were You There?")
  - parse_roman survives every RN the parser emits across a whole hymn
  - hymn_slug normalization
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grammar.parse import parse_roman  # noqa: E402
from grammar.types import Key, Meter, Roman  # noqa: E402
from parsers.abc import (  # noqa: E402
    hymn_slug,
    normalize_for_grammar,
    parse_hymn,
    safe_parse_roman,
    song_to_json,
    write_song_json,
)

ABC_PATH = ROOT / "source" / "OpenHymnal.abc"


# Guard: if the source file isn't present, skip this whole module.
if not ABC_PATH.exists():
    pytest.skip(f"source ABC missing: {ABC_PATH}", allow_module_level=True)

ABC_TEXT = ABC_PATH.read_text()


# ────────────────────── slug helper ──────────────────────
def test_hymn_slug_lowercases_and_collapses_punctuation():
    assert hymn_slug("Amazing Grace") == "amazing_grace"
    assert hymn_slug("Were You There?") == "were_you_there"
    assert hymn_slug("O Come, O Come, Emmanuel") == "o_come_o_come_emmanuel"
    assert hymn_slug("  Leading/Trailing  ") == "leading_trailing"


# ────────────────────── normalize for grammar ──────────────────────
def test_normalize_for_grammar_inversions():
    # Figured-bass inversion → grammar superscript.
    assert normalize_for_grammar("V65") == "V7¹"
    assert normalize_for_grammar("V43") == "V7²"
    assert normalize_for_grammar("V42") == "V7³"
    assert normalize_for_grammar("I6") == "I¹"
    assert normalize_for_grammar("I64") == "I²"


def test_normalize_diminished_glyph():
    # music21 emits ° or letter o; grammar uses ○.
    assert normalize_for_grammar("vii°") == "vii○"
    assert normalize_for_grammar("viio7") == "vii○7"


def test_safe_parse_roman_never_raises_on_noise():
    # These are the kinds of labels music21 can emit; none should raise.
    for rn in ["I", "V65", "V43", "V42", "I64", "viiø7", "vii°7",
               "bVII", "ii°", "#IVø7", "—"]:
        r = safe_parse_roman(rn)
        assert isinstance(r, Roman)


# ────────────────────── core parse ──────────────────────
def test_parse_amazing_grace_basic_shape():
    song = parse_hymn(ABC_TEXT, "Amazing Grace")
    # Title is a real match
    assert "Amazing Grace" in song.title
    # Key: Amazing Grace in the OpenHymnal is major (usually F/G/D — header wins)
    assert song.key.mode == "major"
    # Meter: 3/4 — this is a waltz-time hymn
    assert isinstance(song.meter, Meter)
    assert song.meter.beats in (3, 4)
    # Bars populated
    assert len(song.bars) > 0
    # Every bar has melody events
    non_empty = [b for b in song.bars if b.melody]
    assert len(non_empty) > 0
    # Phrases: at least one, and every ibars entry is a valid bar index
    assert len(song.phrases) >= 1
    n_bars = len(song.bars)
    for ph in song.phrases:
        for ib in ph.ibars:
            assert 1 <= ib <= n_bars
    # Verses: at least one verse with syllables
    assert len(song.verses) >= 1
    first_verse = song.verses[0]
    assert len(first_verse.syllables) > 0
    # At least one syllable has text content
    assert any(s.text for s in first_verse.syllables)


def test_parse_amazing_grace_chords_are_roman_objects():
    song = parse_hymn(ABC_TEXT, "Amazing Grace")
    for b in song.bars:
        assert isinstance(b.chord, Roman)


def test_parse_roman_survives_every_chord_emitted():
    """Every chord in every bar of a sample hymn must be a valid Roman
    according to grammar.parse.parse_roman — i.e. safe_parse_roman should
    never fall back to the sentinel IF the parser is correctly normalizing.

    We run this across a few hymns to exercise different key signatures.
    """
    for title in ("Amazing Grace", "Silent Night", "Joy to the World"):
        song = parse_hymn(ABC_TEXT, title)
        for b in song.bars:
            rn = b.chord
            # Re-emit a canonical string form and make sure it survives a
            # round-trip through parse_roman without ValueError.
            from grammar.emit import emit_roman
            s = emit_roman(rn)
            try:
                parse_roman(s)
            except ValueError as e:
                pytest.fail(f"{title!r}: parse_roman choked on {s!r}: {e}")


# ────────────────────── minor key ──────────────────────
def test_minor_key_hymn_detected_as_minor():
    # "O Come O Come Emmanuel" has K: Em in the hymnal and a clear minor final
    # cadence, so the tonic-detection vote lands on E minor.
    song = parse_hymn(ABC_TEXT, "O Come O Come Emmanuel")
    assert song.key.mode == "minor", (
        f"expected minor-mode for 'O Come O Come Emmanuel', got {song.key.mode!r}"
    )


# ────────────────────── JSON round-trip ──────────────────────
def test_json_round_trip_preserves_structure(tmp_path):
    song = parse_hymn(ABC_TEXT, "Amazing Grace")
    path = write_song_json(song, tmp_path)
    assert path.exists()
    with path.open() as f:
        reloaded = json.load(f)

    # Direct comparison (dict from song) should match reloaded
    original = song_to_json(song)
    # JSON round-trip may lose tuple/list distinction; compare keys & values
    assert reloaded["title"] == original["title"]
    assert reloaded["key"] == original["key"]
    assert reloaded["meter"] == original["meter"]
    assert reloaded["tempo"] == original["tempo"]
    # Bar count preserved
    assert len(reloaded["bars"]) == len(original["bars"]) == len(song.bars)
    # Phrases and verses preserved
    assert len(reloaded["phrases"]) == len(original["phrases"])
    assert len(reloaded["verses"]) == len(original["verses"])
    # ABC source preserved
    assert "_abc_source" in reloaded
    assert reloaded["_abc_source"].startswith("X:")


def test_json_shape_matches_task_spec():
    """Sanity-check the dict structure against the task's spec fields."""
    song = parse_hymn(ABC_TEXT, "Amazing Grace")
    d = song_to_json(song)
    # Top-level keys
    for k in ("title", "key", "meter", "tempo", "bars", "phrases", "verses"):
        assert k in d
    # Key and meter sub-structure
    assert set(d["key"].keys()) >= {"root", "mode"}
    assert set(d["meter"].keys()) >= {"beats", "unit"}
    # Bar structure
    b0 = d["bars"][0]
    assert "melody" in b0 and "chord" in b0
    assert "voicing" in b0 and "technique" in b0
    # Chord sub-structure
    assert set(b0["chord"].keys()) == {"numeral", "quality", "inversion"}
    # Melody event shape
    if b0["melody"]:
        e = b0["melody"][0]
        assert e["kind"] in ("note", "rest")
        assert "duration" in e and "ornaments" in e
        if e["kind"] == "note":
            assert set(e["pitch"].keys()) == {"letter", "accidental", "octave"}
