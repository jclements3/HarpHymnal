"""Emitters: grammar objects → canonical string forms.

Inverse of grammar.parse.  Round-trip: emit(parse(s)) == s for valid s.
"""
from grammar.types import Roman, Shape


def emit_roman(r: Roman) -> str:
    """Reassemble a Roman into its canonical string form."""
    out = r.numeral
    if r.quality:
        out += r.quality
    if r.inversion:
        out += r.inversion
    return out


def emit_shape(s: Shape, *, anchor_char: str | None = None) -> str:
    """Reassemble a Shape as a wire-format figure.  `anchor_char` is the
    string-position character; if omitted, derive from degree (1..7 → '1'..'7').
    """
    ch = anchor_char if anchor_char is not None else str(s.degree)
    return ch + ''.join(str(i) for i in s.intervals)
