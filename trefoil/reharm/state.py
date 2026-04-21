"""Per-variation HarpistState for the reharm selector.

The selector walks the hymn bar by bar; between bars it keeps a running
``HarpistState`` that records enough context for voice-leading, coverage
targeting, phrase bookkeeping, and lever state.

Stdlib-only (``dataclasses``, ``typing``); see ``trefoil/reharm/selector.py``
for the state's consumers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# --------------------------------------------------------------------------- #
# Pedal / lever defaults                                                      #
# --------------------------------------------------------------------------- #
#
# The 47-string lever harp is tuned to a diatonic key signature before play.
# For the reharm selector we treat the starting state as the mode's natural
# collection: every "letter" gets an alter of 0 (natural) or -1 (flat) or
# +1 (sharp) based on the hymn's key signature.  During modal play we never
# flip (lever.no_flip is the default pick in selector.py).
#
# This dict maps a (root_letter, modal_name) pair to the alter of each of the
# seven letter names (C D E F G A B).  We only need Ionian, Aeolian, and
# Dorian per REHARM_TACTICS Decision 5; other modes get Ionian defaults
# (they'll still sound diatonic under the modal override).
#
_NATURAL = {L: 0 for L in "CDEFGAB"}

# Key-signature sharps/flats by major-key tonic.
_MAJOR_KEY_SIG = {
    "C":  _NATURAL.copy(),
    "G":  {**_NATURAL, "F": 1},
    "D":  {**_NATURAL, "F": 1, "C": 1},
    "A":  {**_NATURAL, "F": 1, "C": 1, "G": 1},
    "E":  {**_NATURAL, "F": 1, "C": 1, "G": 1, "D": 1},
    "B":  {**_NATURAL, "F": 1, "C": 1, "G": 1, "D": 1, "A": 1},
    "F#": {**_NATURAL, "F": 1, "C": 1, "G": 1, "D": 1, "A": 1, "E": 1},
    "C#": {**_NATURAL, "F": 1, "C": 1, "G": 1, "D": 1, "A": 1, "E": 1, "B": 1},
    "F":  {**_NATURAL, "B": -1},
    "Bb": {**_NATURAL, "B": -1, "E": -1},
    "Eb": {**_NATURAL, "B": -1, "E": -1, "A": -1},
    "Ab": {**_NATURAL, "B": -1, "E": -1, "A": -1, "D": -1},
    "Db": {**_NATURAL, "B": -1, "E": -1, "A": -1, "D": -1, "G": -1},
    "Gb": {**_NATURAL, "B": -1, "E": -1, "A": -1, "D": -1, "G": -1, "C": -1},
}

# Relative-major lookup: Aeolian i → relative Ionian (minor_root → major_root).
_AEOLIAN_RELATIVE_MAJOR = {
    "A": "C",  "E": "G",  "B": "D",  "F#": "A", "C#": "E", "G#": "B",
    "D#": "F#","D": "F",  "G": "Bb", "C": "Eb", "F": "Ab", "Bb": "Db",
    "Eb": "Gb","Ab": "B",
}

# Dorian i → relative Ionian (up a minor seventh). A Dorian = G major.
_DORIAN_RELATIVE_MAJOR = {
    "A": "G", "E": "D", "B": "A", "F#": "E", "C#": "B",
    "D": "C", "G": "F", "C": "Bb", "F": "Eb", "Bb": "Ab",
    "Eb": "Db", "Ab": "Gb",
}


def _lever_state_for(root: str, mode: str) -> dict[str, int]:
    """Return per-letter lever alter dict for a hymn's starting mode.

    For "ionian" we use the major key sig for ``root``.
    For "aeolian" we use the relative-major key sig.
    For "dorian" we use the relative-major key sig one-down.
    Unknown roots fall back to C major naturals.
    """
    if mode == "ionian":
        return dict(_MAJOR_KEY_SIG.get(root, _NATURAL))
    if mode == "aeolian":
        rel = _AEOLIAN_RELATIVE_MAJOR.get(root, "C")
        return dict(_MAJOR_KEY_SIG.get(rel, _NATURAL))
    if mode == "dorian":
        rel = _DORIAN_RELATIVE_MAJOR.get(root, "C")
        return dict(_MAJOR_KEY_SIG.get(rel, _NATURAL))
    return dict(_NATURAL)


# --------------------------------------------------------------------------- #
# HarpistState                                                                #
# --------------------------------------------------------------------------- #

@dataclass
class HarpistState:
    """Selector-side running context for one variation over one hymn.

    Fields (per Phase 4 spec):

    * ``lever_state``  — per-letter alter (0/+1/-1), current pedal state
    * ``prev_lh``/``prev_rh`` — last bar's voicing as list of (degree, octave)
    * ``prev_bass``/``prev_top`` — last bar's extreme strings
    * ``prev_shape_id`` — id of the shape picked last bar (for connect_from)
    * ``density_window``/``spread_window`` — rolling last-4-bars stats
    * ``coverage`` — tactic-id → count-so-far for coverage-targeted bias
    * ``bar_num`` — 1-indexed current bar
    * ``phrase_idx`` — 0-indexed which phrase we're in
    * ``phrase_bar_idx``/``phrase_len`` — position within phrase and length
    """

    lever_state: dict[str, int] = field(default_factory=dict)
    prev_lh: list[tuple[int, int]] = field(default_factory=list)
    prev_rh: list[tuple[int, int]] = field(default_factory=list)
    prev_bass: Optional[tuple[int, int]] = None
    prev_top: Optional[tuple[int, int]] = None
    prev_shape_id: Optional[str] = None
    density_window: list[int] = field(default_factory=list)
    spread_window: list[int] = field(default_factory=list)
    coverage: dict[str, int] = field(default_factory=dict)
    bar_num: int = 1
    phrase_idx: int = 0
    phrase_bar_idx: int = 0
    phrase_len: int = 0

    # ------------------------------------------------------------------ #
    # Constructors                                                       #
    # ------------------------------------------------------------------ #

    @classmethod
    def initial(cls, hymn_json: dict, mode: str) -> "HarpistState":
        """Build starting state for a hymn + chosen mode.

        Pulls the key root from ``hymn_json["key"]["root"]`` and seeds the
        lever state from the mode's natural collection.  Phrase bookkeeping
        starts at the first phrase if present, else a synthetic 1-bar
        phrase (so selector code can still index ``phrase_len``).
        """
        root = (hymn_json.get("key") or {}).get("root", "C")
        lever = _lever_state_for(root, mode)

        phrases = hymn_json.get("phrases") or []
        if phrases:
            phrase_len = len(phrases[0].get("ibars") or [1])
        else:
            phrase_len = 1

        return cls(
            lever_state=lever,
            prev_lh=[],
            prev_rh=[],
            prev_bass=None,
            prev_top=None,
            prev_shape_id=None,
            density_window=[],
            spread_window=[],
            coverage={},
            bar_num=1,
            phrase_idx=0,
            phrase_bar_idx=0,
            phrase_len=phrase_len,
        )

    # ------------------------------------------------------------------ #
    # Rolling-window bookkeeping                                         #
    # ------------------------------------------------------------------ #

    def push_density(self, attacks: int, window: int = 4) -> None:
        self.density_window.append(attacks)
        if len(self.density_window) > window:
            self.density_window = self.density_window[-window:]

    def push_spread(self, octaves: int, window: int = 4) -> None:
        self.spread_window.append(octaves)
        if len(self.spread_window) > window:
            self.spread_window = self.spread_window[-window:]

    def bump_coverage(self, tactic_id: str) -> None:
        self.coverage[tactic_id] = self.coverage.get(tactic_id, 0) + 1


__all__ = ["HarpistState"]
