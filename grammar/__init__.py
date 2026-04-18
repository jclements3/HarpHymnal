"""HarpHymnal grammar — typed domain objects for the EBNF in GRAMMAR.md.

Every script in the ecosystem parses into and emits from these types.
No other module invents its own chord-regex.
"""
from grammar.types import (
    Roman, Shape, Bichord, Bishape, Bar, Song, Piece,
    Ornament, PedalState, Meter, Tempo, Key,
)
from grammar.parse import parse_roman, parse_shape
from grammar.emit import emit_roman, emit_shape

__all__ = [
    'Roman', 'Shape', 'Bichord', 'Bishape', 'Bar', 'Song', 'Piece',
    'Ornament', 'PedalState', 'Meter', 'Tempo', 'Key',
    'parse_roman', 'parse_shape',
    'emit_roman', 'emit_shape',
]
