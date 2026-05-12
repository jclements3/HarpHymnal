"""Per-beat hand routing.

Decides which hand (LH or RH) plays each pitch on each beat. Replaces the
old static `LH_VOICES`/`RH_VOICES` slot routing in types.py.

Algorithm: voice-preference + greedy repair.
  1. For each VOICE, compute its average pitch across the piece. Voices
     averaging at or above middle C tend RH; below tend LH.
  2. For each beat, place every active pitch in its voice's preferred hand.
  3. Repair under hard constraints:
       - ≤ 4 attacks per hand
       - hand span ≤ 16 semitones (10-string limit)
       - no note in C1–B1 unless it's the Dr drone slot
     Each repair moves one pitch to the other hand (preferring the more
     marginal note relative to the other hand's register); if no other
     hand has room, the pitch is dropped and reported.
  4. Voice continuity: when both hands have room, keep a voice in the
     same hand it occupied on the previous beat.

Public API:
    route(ledger, extra_lh_per_beat=None) -> RoutingResult
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .types import Beat, BeatLedger, VoiceName


MAX_ATTACKS_PER_HAND = 4
MAX_SPAN_ST = 16              # 10-string comfort limit
MIDDLE_C = 60                 # MIDI
DRONE_ZONE_TOP = 35           # C1=24, B1=35 (drone zone)
HARP_LOW = 24                 # C1
HARP_HIGH = 103               # G7


# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class RoutedNote:
    midi: int
    voice: str       # source voice ('S1', 'B', 'pattern:Alberti', etc.)
    kind: str        # 'attack' or 'sustain'
    hand: str        # 'LH' or 'RH'


@dataclass
class BeatRouting:
    rh: list[RoutedNote] = field(default_factory=list)
    lh: list[RoutedNote] = field(default_factory=list)
    dropped: list[RoutedNote] = field(default_factory=list)


@dataclass
class RoutingResult:
    beats: list[BeatRouting]
    voice_avg: dict[str, float]
    audits: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
def _compute_voice_averages(ledger: BeatLedger) -> dict[VoiceName, float]:
    sums: dict[VoiceName, list[int]] = {}
    for beat in ledger.beats:
        for vname, ev in beat.voices.items():
            if ev.kind == 'attack' and ev.pitch_midi is not None:
                sums.setdefault(vname, []).append(ev.pitch_midi)
    return {v: sum(m) / len(m) for v, m in sums.items() if m}


def _preferred_hand(voice: str, midi: int, voice_avg: dict[str, float]) -> str:
    """Default hand: by voice avg if known, fallback by pitch."""
    if voice == 'Dr':
        return 'LH'  # drone always LH
    avg = voice_avg.get(voice)
    if avg is not None:
        return 'LH' if avg < MIDDLE_C else 'RH'
    return 'LH' if midi < MIDDLE_C else 'RH'


def _span(notes: list[RoutedNote]) -> int:
    if not notes:
        return 0
    return max(n.midi for n in notes) - min(n.midi for n in notes)


def _check(rh: list[RoutedNote], lh: list[RoutedNote]) -> Optional[str]:
    """Return first violation name or None."""
    if sum(1 for n in rh if n.kind == 'attack') > MAX_ATTACKS_PER_HAND:
        return 'rh_attacks'
    if sum(1 for n in lh if n.kind == 'attack') > MAX_ATTACKS_PER_HAND:
        return 'lh_attacks'
    if _span(rh) > MAX_SPAN_ST:
        return 'rh_span'
    if _span(lh) > MAX_SPAN_ST:
        return 'lh_span'
    # Drone-zone: any non-Dr note in C1-B1
    for n in lh:
        if n.midi <= DRONE_ZONE_TOP and n.voice != 'Dr':
            return 'lh_drone_zone'
    return None


def _move(notes: list[RoutedNote], note: RoutedNote, new_hand: str) -> RoutedNote:
    """Return a copy of `note` with hand=new_hand."""
    return RoutedNote(midi=note.midi, voice=note.voice, kind=note.kind, hand=new_hand)


def _repair(rh: list[RoutedNote], lh: list[RoutedNote], violation: str
            ) -> tuple[list[RoutedNote], list[RoutedNote], list[RoutedNote]]:
    """One repair iteration. Returns (new_rh, new_lh, dropped_this_step)."""
    rh_attacks = [n for n in rh if n.kind == 'attack']
    lh_attacks = [n for n in lh if n.kind == 'attack']

    if violation == 'rh_attacks':
        # Move lowest RH attack down to LH.
        target = min(rh_attacks, key=lambda n: n.midi)
        new_rh = [n for n in rh if n is not target]
        new_lh = lh + [_move(target, target, 'LH')]
        return new_rh, new_lh, []

    if violation == 'lh_attacks':
        # Move highest LH attack up to RH.
        target = max(lh_attacks, key=lambda n: n.midi)
        new_lh = [n for n in lh if n is not target]
        new_rh = rh + [_move(target, target, 'RH')]
        return new_rh, new_lh, []

    if violation == 'rh_span':
        # Drop the lowest RH note; move to LH if it fits there.
        target = min(rh, key=lambda n: n.midi)
        new_rh = [n for n in rh if n is not target]
        # Try LH
        moved = _move(target, target, 'LH')
        cand_lh = lh + [moved]
        if (sum(1 for n in cand_lh if n.kind == 'attack') <= MAX_ATTACKS_PER_HAND
                and _span(cand_lh) <= MAX_SPAN_ST):
            return new_rh, cand_lh, []
        return new_rh, lh, [target]

    if violation == 'lh_span':
        target = max(lh, key=lambda n: n.midi)
        new_lh = [n for n in lh if n is not target]
        moved = _move(target, target, 'RH')
        cand_rh = rh + [moved]
        if (sum(1 for n in cand_rh if n.kind == 'attack') <= MAX_ATTACKS_PER_HAND
                and _span(cand_rh) <= MAX_SPAN_ST):
            return cand_rh, new_lh, []
        return rh, new_lh, [target]

    if violation == 'lh_drone_zone':
        # Octave-up the offending pitch (or drop if it still doesn't fit).
        target = next(n for n in lh if n.midi <= DRONE_ZONE_TOP and n.voice != 'Dr')
        new_lh = [n for n in lh if n is not target]
        bumped = RoutedNote(target.midi + 12, target.voice, target.kind, 'LH')
        cand_lh = new_lh + [bumped]
        if _check(rh, cand_lh) is None:
            return rh, cand_lh, []
        # Can't fit even after bumping — drop.
        return rh, new_lh, [target]

    return rh, lh, []


# ─────────────────────────────────────────────────────────────────────────────
def route(
    ledger: BeatLedger,
    extra_per_beat: Optional[list[list[RoutedNote]]] = None,
    exclude_voices: tuple[str, ...] = (),
) -> RoutingResult:
    """Route each beat's active pitches into LH/RH.

    Args:
        ledger: 8-voice composition (per-beat events).
        extra_per_beat: optional pre-routed notes per beat (e.g. somerset
            pattern). Each item is a list[RoutedNote] for that beat.
        exclude_voices: voices to skip entirely (e.g. ('B',) when a pattern
            takes over the bass).
    """
    voice_avg = _compute_voice_averages(ledger)
    n = len(ledger.beats)

    out: list[BeatRouting] = []
    prev_voice_hand: dict[str, str] = {}

    for i, beat in enumerate(ledger.beats):
        notes: list[RoutedNote] = []

        for vname, ev in beat.voices.items():
            if vname in exclude_voices:
                continue
            if ev.kind not in ('attack', 'sustain') or ev.pitch_midi is None:
                continue
            # Voice continuity: stay where we were last beat if defined.
            hand = prev_voice_hand.get(vname) or _preferred_hand(vname, ev.pitch_midi, voice_avg)
            notes.append(RoutedNote(ev.pitch_midi, vname, ev.kind, hand))

        if extra_per_beat and i < len(extra_per_beat):
            notes.extend(extra_per_beat[i])

        rh = [n for n in notes if n.hand == 'RH']
        lh = [n for n in notes if n.hand == 'LH']
        dropped: list[RoutedNote] = []

        for _ in range(20):  # bail after N repair iterations
            v = _check(rh, lh)
            if v is None:
                break
            rh, lh, d = _repair(rh, lh, v)
            dropped.extend(d)

        out.append(BeatRouting(rh=rh, lh=lh, dropped=dropped))
        # Remember each voice's final hand for next-beat continuity.
        for n in rh + lh:
            prev_voice_hand[n.voice] = n.hand

    return RoutingResult(beats=out, voice_avg=voice_avg)


# ─────────────────────────────────────────────────────────────────────────────
#   Slots derivation (for hand-off into the consolidator's chord-cell render)
# ─────────────────────────────────────────────────────────────────────────────
def slots_for_hand(routing: RoutingResult, hand: str) -> list[tuple[str, int, int, int]]:
    """Convert per-beat routing into (voice, midi, start_beat, length) runs.

    A run is the maximal stretch of consecutive beats where the same
    (midi, voice) pair is present in `hand`. Sustain kind extends a run;
    a new attack of the same pair starts a new run.
    """
    n = len(routing.beats)
    runs: list[tuple[str, int, int, int]] = []
    active: dict[tuple[int, str], int] = {}  # (midi, voice) -> start_beat

    for i in range(n):
        notes = routing.beats[i].rh if hand == 'RH' else routing.beats[i].lh
        present: dict[tuple[int, str], str] = {(n.midi, n.voice): n.kind for n in notes}
        ended_keys = [k for k in active if k not in present]
        for key in ended_keys:
            start = active.pop(key)
            length = i - start
            if length > 0:
                runs.append((key[1], key[0], start, length))
        for key, kind in present.items():
            if kind == 'attack':
                if key in active:
                    start = active.pop(key)
                    length = i - start
                    if length > 0:
                        runs.append((key[1], key[0], start, length))
                active[key] = i
            elif kind == 'sustain' and key not in active:
                active[key] = i
    for key, start in active.items():
        length = n - start
        if length > 0:
            runs.append((key[1], key[0], start, length))
    return runs

