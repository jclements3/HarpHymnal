"""Round-trip tests for grammar.parse ↔ grammar.emit."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from grammar.parse import parse_roman, parse_figure, parse_shape
from grammar.emit  import emit_roman, emit_shape
from grammar.types import Roman, Shape


# ─────────────── Roman numerals ───────────────

def test_parse_simple_I():
    assert parse_roman("I") == Roman("I", None, None)


def test_parse_dominant_seven():
    assert parse_roman("V7") == Roman("V", "7", None)


def test_parse_major_seven():
    assert parse_roman("IΔ7") == Roman("I", "Δ7", None)


def test_parse_inversion_superscript():
    assert parse_roman("iii¹") == Roman("iii", None, "¹")


def test_parse_inversion_ascii_digit():
    # '3' at the end of 'iii3' should parse as inversion
    assert parse_roman("iii3") == Roman("iii", None, "³")


def test_parse_quality_and_inversion():
    # Canonical order: numeral, quality, inversion
    assert parse_roman("IV+8²") == Roman("IV", "+8", "²")


def test_parse_half_dim():
    assert parse_roman("iiø7") == Roman("ii", "ø7", None)


def test_parse_diminished_circle():
    assert parse_roman("vii○7") == Roman("vii○", "7", None)


def test_roman_round_trip_simple():
    for s in ["I", "ii", "V7", "IΔ7", "iii¹"]:
        assert emit_roman(parse_roman(s)) == s


# ─────────────── Figures / shapes ───────────────

def test_parse_figure_decimal_anchor():
    assert parse_figure("533") == (5, (3, 3))


def test_parse_figure_hex_anchor():
    assert parse_figure("A33") == (10, (3, 3))
    assert parse_figure("F33") == (15, (3, 3))


def test_parse_shape_preserves_intervals():
    s = parse_shape("533", degree=5)
    assert s == Shape(degree=5, intervals=(3, 3))


def test_shape_round_trip():
    s = Shape(degree=1, intervals=(3, 3))
    assert emit_shape(s) == "133"
    s4 = Shape(degree=1, intervals=(3, 3, 3))
    assert emit_shape(s4) == "1333"
