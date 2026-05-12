"""Per-phrase countermelodies for the inner harp voices (T2, A2, S2).

Why this exists: the v1 fill picker chose chord-tones per beat independently,
producing tight clusters like G3+A3+B3 because it had no concept of the inner
voice as a melody. This module composes a phrase-level line for each inner
voice so the result is a singable shape, not a chain of per-beat optima.

Default texture (v1): each inner voice tracks its SATB partner a diatonic 3rd
below — S2 below S1, A2 below A1, T2 below T1 — producing the conservative
"SSAATTBB hymn" sound. Pitches are kept in scientific midi space; we don't
clamp to per-voice preferred registers because the user is fine with crossings.

Public API:
    generate(beats, phrases, K, key_mode, bar_chord, meter_beats) -> None
        Modifies `beats` in place. Each Beat's T2/A2/S2 voice slot gets an
        attack/sustain/rest event sourced as 'countermelody'.
"""
from __future__ import annotations

from typing import Optional

from music21 import key as m21key

from .types import Beat, REST_EVENT, VoiceEvent, VoiceName


INNER_VOICES: tuple[VoiceName, ...] = ('T2', 'A2', 'S2')

# Each inner voice tracks its SATB partner one diatonic 3rd below.
PARALLEL_ANCHOR: dict[VoiceName, VoiceName] = {
    'T2': 'T1',
    'A2': 'A1',
    'S2': 'S1',
}


def _scale_pcs(K: m21key.Key) -> list[int]:
    return [p.pitchClass for p in K.pitches[:7]]


def _diatonic_step(midi: int, steps: int, pcs: list[int]) -> int:
    """Move `midi` by `steps` diatonic scale steps (negative = down).

    Snaps non-diatonic input to the nearest scale pitch class first.
    """
    cur_pc = midi % 12
    octv = midi // 12
    if cur_pc in pcs:
        i = pcs.index(cur_pc)
    else:
        i = min(
            range(7),
            key=lambda j: min((pcs[j] - cur_pc) % 12, (cur_pc - pcs[j]) % 12),
        )
    new_i = i + steps
    new_octv = octv + new_i // 7
    return new_octv * 12 + pcs[new_i % 7]


def _phrase_beat_indices(
    phrase: dict, meter_beats: int, total_beats: int
) -> list[int]:
    out = []
    for bar in phrase.get('bars', []):
        for b in range(meter_beats):
            idx = (bar - 1) * meter_beats + b
            if 0 <= idx < total_beats:
                out.append(idx)
    return out


def _parallel_third_line(
    voice: VoiceName,
    indices: list[int],
    beats: list[Beat],
    pcs: list[int],
) -> list[Optional[int]]:
    """For each beat in the phrase, emit (anchor pitch) - one diatonic 3rd.

    Anchor silent → this voice rests too.
    """
    anchor = PARALLEL_ANCHOR[voice]
    out: list[Optional[int]] = []
    for bi in indices:
        ev = beats[bi].voices[anchor]
        if ev.pitch_midi is None or ev.kind == 'rest':
            out.append(None)
            continue
        out.append(_diatonic_step(ev.pitch_midi, -2, pcs))
    return out


def _overlay(
    beats: list[Beat],
    voice: VoiceName,
    indices: list[int],
    pitches: list[Optional[int]],
) -> None:
    """Write pitches into the voice slot. Pitch changes → attack; identical
    consecutive pitches → sustain; None → rest."""
    held: Optional[int] = None
    for bi, p in zip(indices, pitches):
        if bi >= len(beats):
            continue
        if p is None:
            beats[bi].voices[voice] = REST_EVENT
            held = None
        elif p != held:
            beats[bi].voices[voice] = VoiceEvent(
                kind='attack', pitch_midi=p, source='countermelody',
            )
            held = p
        else:
            beats[bi].voices[voice] = VoiceEvent(
                kind='sustain', pitch_midi=p, source='countermelody',
            )


def generate(
    beats: list[Beat],
    phrases: list[dict],
    K: m21key.Key,
    key_mode: str,
    bar_chord: dict[int, str],
    meter_beats: int,
) -> None:
    """Populate T2/A2/S2 on `beats` in place with phrase-level countermelodies."""
    if not phrases or not beats:
        return
    pcs = _scale_pcs(K)
    n = len(beats)
    for phrase in phrases:
        indices = _phrase_beat_indices(phrase, meter_beats, n)
        if not indices:
            continue
        for voice in INNER_VOICES:
            pitches = _parallel_third_line(voice, indices, beats, pcs)
            _overlay(beats, voice, indices, pitches)
