"""Harp pedal diagram helpers — shared by SATB SVG annotation, compare pages,
and (later) jazz score rendering.

A pedal state is a dict {letter: -1 (flat) | 0 (nat) | +1 (sharp)} for each of
the seven pedal letters D C B E F G A.

The braille diagram packs seven pedals into four cells:
    cell 1: (D | C)      left dot = D alter, right dot = C alter
    cell 2: (B | divider) left dot = B alter, right = dots 4-5-6 (foot bar)
    cell 3: (E | F)
    cell 4: (G | A)
Position → dot:  flat=1/4, nat=2/5, sharp=3/6 (left/right side of the cell).

The per-bar planner pulls each pedal's *first* change in a bar to the bar's
first beat when no earlier beat in the bar uses that pedal at its previous
alter. Later changes (intra-bar toggles) keep their native beat.
"""
from __future__ import annotations


PEDAL_ORDER = ["D", "C", "B", "E", "F", "G", "A"]
SHARP_ORDER = ["F", "C", "G", "D", "A", "E", "B"]
FLAT_ORDER = ["B", "E", "A", "D", "G", "C", "F"]

LEFT_DOT = {-1: 1, 0: 2, 1: 3}
RIGHT_DOT = {-1: 4, 0: 5, 1: 6}
DIVIDER_DOTS = {4, 5, 6}

PEDAL_CELLS = 4  # width of a full diagram, in braille characters


def braille_cell(dots: set[int]) -> str:
    code = 0x2800
    for d in dots:
        code |= 1 << (d - 1)
    return chr(code)


def pedals_to_braille(state: dict[str, int]) -> str:
    D, C, B, E, F, G, A = (state[l] for l in PEDAL_ORDER)
    c1 = braille_cell({LEFT_DOT[D], RIGHT_DOT[C]})
    c2 = braille_cell({LEFT_DOT[B]} | DIVIDER_DOTS)
    c3 = braille_cell({LEFT_DOT[E], RIGHT_DOT[F]})
    c4 = braille_cell({LEFT_DOT[G], RIGHT_DOT[A]})
    return c1 + c2 + c3 + c4


def initial_pedal_state(key_root: str, mode: str) -> dict[str, int]:
    from music21 import key as m21key
    try:
        n = m21key.Key(key_root, mode).sharps
    except Exception:
        n = 0
    state = {l: 0 for l in PEDAL_ORDER}
    if n > 0:
        for l in SHARP_ORDER[:n]:
            state[l] = 1
    elif n < 0:
        for l in FLAT_ORDER[:-n]:
            state[l] = -1
    return state


def pitch_letter_alter(p_str: str) -> tuple[str, int] | None:
    """Return (letter, alter) from a music21-style pitch string (e.g. 'F#4',
    'Bb3', 'D4'). Returns None if the string doesn't start with a pedal letter."""
    if not p_str:
        return None
    letter = p_str[0].upper()
    if letter not in set(PEDAL_ORDER):
        return None
    alter = 0
    for ch in p_str[1:]:
        if ch in "#♯":
            alter = 1
        elif ch in "b♭":
            alter = -1
        elif ch in "n♮":
            alter = 0
        else:
            break
    return letter, alter


def plan_bar_pedal_events(bar_beats: list[dict],
                          state_in: dict[str, int]
                          ) -> dict[int, dict[str, int]]:
    """Plan pedal changes for one bar, pulling each pedal's first change to
    the bar's first beat when no earlier beat in the bar uses that pedal at
    its previous alter.

    `bar_beats`: list of beat dicts (legacy export format with S/A/T/B keys).
    `state_in`:  pedal state entering this bar (mutated *out* via return).

    Returns: {beat_num: {letter: new_alter}} — one entry per (beat, pedal)
    change event. Empty if no changes are needed in this bar.
    """
    if not bar_beats:
        return {}
    bar_start_beat = bar_beats[0].get("beat", 1)

    timeline_by_L: dict[str, list[tuple[int, int]]] = {}
    for b in bar_beats:
        beat_num = b.get("beat", 0)
        seen_L: dict[str, int] = {}
        for v in ("S", "A", "T", "B"):
            la = pitch_letter_alter(b.get(v) or "")
            if not la:
                continue
            L, a = la
            if L not in seen_L:
                seen_L[L] = a
        for L, a in seen_L.items():
            timeline_by_L.setdefault(L, []).append((beat_num, a))

    events: dict[int, dict[str, int]] = {}
    for L, timeline in timeline_by_L.items():
        prev = state_in[L]
        first_change = True
        for beat, alter in timeline:
            if alter == prev:
                continue
            if first_change:
                earlier_prev_use = any(
                    b < beat and a == prev for b, a in timeline
                )
                target = beat if earlier_prev_use else bar_start_beat
                first_change = False
            else:
                target = beat
            events.setdefault(target, {})[L] = alter
            prev = alter
    return events
