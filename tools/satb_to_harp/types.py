"""Shared dataclasses for the SATB→harp pipeline.

The 8-voice ledger is the contract between analyzer.py and consolidator.py.
analyzer.py produces it; consolidator.py consumes it.

Voice roster (from docs/harprules.md, lines 11-23):

    Dr   C1-B1  Sub-bass drone (pedal harp only)
    B    C2-C4  Bass. SATB bass lives here.
    T2   C3-E4  LH inner. Empty; receives freed-finger fills.
    T1   E3-G4  LH upper inner. SATB tenor lives here.
    A2   G3-C5  RH lower inner. Empty; receives freed-finger fills.
    A1   C4-E5  RH inner. SATB alto lives here.
    S2   E4-G5  RH upper. Empty; receives freed-finger fills.
    S1   G4-C6  Melody. SATB soprano lives here.
    Gl   B6-G7  Glissando (pedal harp only)

Default hand routing:
    LH = {Dr, B, T2, T1}
    RH = {A1, A2, S2, S1, Gl}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


VoiceName = Literal['Dr', 'B', 'T2', 'T1', 'A2', 'A1', 'S2', 'S1', 'Gl']

VOICE_ORDER: tuple[VoiceName, ...] = (
    'Dr', 'B', 'T2', 'T1', 'A2', 'A1', 'S2', 'S1', 'Gl'
)

LH_VOICES: frozenset[VoiceName] = frozenset({'Dr', 'B', 'T2', 'T1'})
RH_VOICES: frozenset[VoiceName] = frozenset({'A1', 'A2', 'S2', 'S1', 'Gl'})

# MIDI pitch range per voice (inclusive). Scientific octave numbering.
VOICE_RANGE: dict[VoiceName, tuple[int, int]] = {
    'Dr': (24, 35),   # C1-B1
    'B':  (36, 60),   # C2-C4
    'T2': (48, 64),   # C3-E4
    'T1': (52, 67),   # E3-G4
    'A2': (55, 72),   # G3-C5
    'A1': (60, 76),   # C4-E5
    'S2': (64, 79),   # E4-G5
    'S1': (67, 84),   # G4-C6
    'Gl': (95, 103),  # B6-G7
}

# Source SATB → natural voice slot (no octave shift). The hand_router decides
# per beat which hand actually plays each pitch, so the slot assignment is
# now just a label, not a hand-routing decision.
SATB_TO_VOICE: dict[str, VoiceName] = {
    'S1V1': 'S1',   # soprano
    'S1V2': 'A1',   # alto
    'S2V1': 'T1',   # tenor
    'S2V2': 'B',    # bass
}


# Kinds an event can take on a single beat.
EventKind = Literal['attack', 'sustain', 'rest']

# Source of an event: either a SATB source voice (preserved) or a fill rule
# (synthesized). Used downstream for auditing and rendering decisions.
EventSource = Literal[
    'satb',                # carried over directly from a source SATB voice
    'idle',                # explicitly left silent though the finger was free
    'chord-tone',          # fill: pluck a chord tone not currently sounding
    'neighbor',            # fill: step away/back to a held pitch
    'anticipation',        # fill: pluck the next beat's pitch one beat early
    'octave-fill',         # fill: double an outer voice at the octave
    'passing-tone',        # fill: step between two adjacent chord tones
    'drone',               # Dr: pedal-point drone
    'gliss',               # Gl: glissando event
    'countermelody',       # phrase-level inner line from countermelody.py
]


@dataclass(frozen=True)
class VoiceEvent:
    """One voice's state on one beat.

    `pitch_midi` is None on rest events.
    `kind`:
      attack  — plucked on this beat.
      sustain — string is still ringing from an earlier attack.
      rest    — voice is silent.
    """
    kind: EventKind
    pitch_midi: Optional[int]
    source: EventSource


REST_EVENT = VoiceEvent(kind='rest', pitch_midi=None, source='satb')


@dataclass(frozen=True)
class Beat:
    """All 8 voices at one beat-index, plus bar/beat-within-bar bookkeeping."""
    index: int                              # global beat index, 0-based
    bar: int                                # 1-based bar number
    beat_in_bar: int                        # 1-based beat within bar
    voices: dict[VoiceName, VoiceEvent]     # one entry per VOICE_ORDER


@dataclass
class Audit:
    """Per-beat or per-bar warnings raised during analysis or consolidation."""
    beat: int
    message: str
    severity: Literal['info', 'warn', 'error'] = 'warn'


@dataclass
class BeatLedger:
    """Full 8-voice arrangement for one hymn, beat-by-beat."""
    title: str
    key_root: str                           # 'Bb', 'D', 'F#', etc.
    key_mode: Literal['major', 'minor']
    modal_name: str                         # 'ionian', 'dorian', ...
    meter_beats: int                        # numerator
    meter_unit: int                         # denominator (4, 8, 2, ...)
    beats_per_bar: int                      # usually == meter_beats
    tempo_bpm: int
    beats: list[Beat]                       # ordered globally
    bar_chords: dict[int, str] = field(default_factory=dict)  # bar# → roman numeral
    audits: list[Audit] = field(default_factory=list)

    def beats_by_bar(self) -> dict[int, list[Beat]]:
        out: dict[int, list[Beat]] = {}
        for b in self.beats:
            out.setdefault(b.bar, []).append(b)
        return out


@dataclass
class ArrangementResult:
    """Pipeline output: ledger + emitted ABC + all audits."""
    ledger: BeatLedger
    abc: str
    audits: list[Audit]
