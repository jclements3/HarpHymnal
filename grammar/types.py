"""Typed domain objects for the HarpHymnal grammar (see GRAMMAR.md).

Ladder: interval → intervals → shape → bishape   (voicings)
        roman → chord → bichord                  (names)
        bar → song/piece                         (music)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Union


# ───────────────────────────── Atoms ─────────────────────────────

Interval = Literal[2, 3, 4]            # inter-finger step
Degree   = Literal[1, 2, 3, 4, 5, 6, 7]  # scale-degree anchor
Letter   = Literal['A', 'B', 'C', 'D', 'E', 'F', 'G']
Accidental = Literal['♭', '♯']
Unit     = Literal[1, 2, 4, 8, 16, 32]   # note-value denominator


# ───────────────────── Roman numerals (decomposed) ───────────────

@dataclass(frozen=True)
class Roman:
    """numeral + optional quality + optional inversion.  Examples:
       I, ii, V7, IΔ7, iii¹, vii○7, IV²+8.
    """
    numeral: str                       # 'I','ii','iii','IV','V','vi','vii○', etc.
    quality: Optional[str] = None      # 'Δ','Δ7','7','ø7','○7','6','9','s2','s4','q','q7','+8'
    inversion: Optional[str] = None    # '¹','²','³'


# ─────────────────────── Voicings (hand configurations) ──────────

@dataclass(frozen=True)
class Shape:
    """One hand's voicing: starting scale-degree + interval sequence.
    Intervals end on the thumb per the teacher's pedagogy.
    """
    degree: Degree
    intervals: tuple[Interval, ...]    # e.g. (3, 3) = 33 triad; (3, 3, 3) = 333 Δ7


@dataclass(frozen=True)
class Bishape:
    """Two shapes stacked (LH + RH)."""
    lh: Shape
    rh: Shape


# ───────────────────── Chord names (abstract) ────────────────────

Chord = Roman                          # alias — a chord is a roman numeral


@dataclass(frozen=True)
class Bichord:
    """Two chords layered top/bottom.  Rendering (slash, hrule, space)
    is a presentation choice, not a grammar one.
    """
    top: Chord
    bottom: Chord


# ──────────────────────── Ornaments ──────────────────────────────

OrnamentKind = Literal[
    'arp', 'grace', 'enc', 'upper', 'lower',
    'gliss', 'damp', 'harm', 'bisb',
]


@dataclass(frozen=True)
class Ornament:
    """Lever-harp idiomatic decoration attached to a note or a bar."""
    kind: OrnamentKind
    # Payload depends on kind: grace/enc/upper/lower/gliss/bisb carry pitches;
    # damp carries 'LH' or 'RH'; arp and harm carry nothing.
    payload: Optional[tuple] = None


# ────────────────────── Pedal harp ──────────────────────────────

PedalPos = Literal['flat', 'natural', 'sharp']


@dataclass(frozen=True)
class PedalState:
    """Seven pedal positions: D C B (left) | E F G A (right)."""
    D: PedalPos
    C: PedalPos
    B: PedalPos
    E: PedalPos
    F: PedalPos
    G: PedalPos
    A: PedalPos


@dataclass(frozen=True)
class PedalChange:
    pedal: Letter
    position: PedalPos


# ──────────────────── Metadata primitives ────────────────────────

Mode = Literal[
    'major', 'minor',
    'dorian', 'phrygian', 'lydian',
    'mixolydian', 'aeolian', 'locrian',
]


@dataclass(frozen=True)
class Key:
    root: str                          # e.g. 'Bb', 'F#', 'C'
    mode: Mode


@dataclass(frozen=True)
class Meter:
    beats: int
    unit: Unit


@dataclass(frozen=True)
class Tempo:
    value: int                         # BPM
    unit: Unit                         # beat unit (4 = quarter, 8 = eighth...)


# ───────────────────── Melody notes / rests ─────────────────────

@dataclass(frozen=True)
class Pitch:
    letter: Letter
    accidental: Optional[Accidental]
    octave: int


@dataclass(frozen=True)
class Note:
    pitch: Pitch
    duration: float                    # quarter-lengths
    ornaments: tuple[Ornament, ...] = ()


@dataclass(frozen=True)
class Rest:
    duration: float


# ───────────────────── Bars, Songs, Pieces ──────────────────────

Technique = str                        # enumeration checked at parse time


@dataclass(frozen=True)
class Bar:
    melody: tuple[Union[Note, Rest], ...]
    chord: Union[Chord, Bichord]
    voicing: Optional[Union[Shape, Bishape]] = None
    ornaments: tuple[Ornament, ...] = ()
    pedal_changes: tuple[PedalChange, ...] = ()
    technique: Optional[Technique] = None


@dataclass(frozen=True)
class Phrase:
    ibars: tuple[int, ...]              # 1-based bar indices
    path: Optional[str] = None          # e.g. '4ths CW'


@dataclass(frozen=True)
class Section:
    label: str                          # 'intro','verse','chorus','bridge','refrain','outro'
    first_ibar: int
    last_ibar: int


@dataclass(frozen=True)
class Syllable:
    ibar: int
    inote: int
    text: str
    melisma: bool = False


@dataclass(frozen=True)
class Verse:
    syllables: tuple[Syllable, ...]


@dataclass
class _Music:
    title: str
    key: Key
    meter: Meter
    tempo: Tempo
    bars: tuple[Bar, ...]
    pedals: Optional[PedalState] = None
    phrases: tuple[Phrase, ...] = field(default_factory=tuple)
    form: tuple[Section, ...] = field(default_factory=tuple)


@dataclass
class Song(_Music):
    """Music with lyrics."""
    verses: tuple[Verse, ...] = field(default_factory=tuple)


@dataclass
class Piece(_Music):
    """Music without lyrics."""
    pass
