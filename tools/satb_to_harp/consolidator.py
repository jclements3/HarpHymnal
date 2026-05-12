"""8-voice ledger → 2-voice (RH/LH) ABC consolidator.

Public API: ``consolidate(ledger: BeatLedger) -> ArrangementResult``.

CLI: ``python -m tools.satb_to_harp.consolidator <ledger.json>`` loads the
ledger JSON written by analyzer.py, emits ABC under
``data/harp_arranged/<slug>.abc``, prints an audit summary, and runs
``abc2midi`` to verify parseability.

When no ledger argument is given, runs against a synthetic one-bar C-major
SATB fixture so that the module can be smoke-tested end-to-end.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .types import (
    ArrangementResult,
    Audit,
    Beat,
    BeatLedger,
    LH_VOICES,
    RH_VOICES,
    VoiceEvent,
    VoiceName,
    VOICE_ORDER,
)


HAND_VOICE_ORDER: dict[str, tuple[VoiceName, ...]] = {
    'LH': ('Dr', 'B', 'T2', 'T1'),
    'RH': ('A2', 'A1', 'S2', 'S1', 'Gl'),
}

PITCH_LETTERS = ('C', 'D', 'E', 'F', 'G', 'A', 'B')
SEMITONES_FROM_C = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------

def midi_to_letter_octave(midi: int) -> tuple[str, int, int]:
    """Return (letter, accidental_semitones, octave) for a MIDI pitch.

    Prefers sharps over flats by default; spelling is refined per key by the
    caller via ``midi_to_abc``. ``accidental_semitones`` is -1/0/+1.
    """
    pc = midi % 12
    sharp_map = [
        ('C', 0), ('C', 1), ('D', 0), ('D', 1), ('E', 0), ('F', 0),
        ('F', 1), ('G', 0), ('G', 1), ('A', 0), ('A', 1), ('B', 0),
    ]
    letter, acc = sharp_map[pc]
    octave = midi // 12 - 1
    return letter, acc, octave


# Standard major-key signatures: which pitch classes are sharp/flat.
KEY_ACCIDENTALS: dict[str, dict[str, int]] = {
    # major key root -> {letter: -1|0|+1} (only altered letters)
    'C':  {},
    'G':  {'F': 1},
    'D':  {'F': 1, 'C': 1},
    'A':  {'F': 1, 'C': 1, 'G': 1},
    'E':  {'F': 1, 'C': 1, 'G': 1, 'D': 1},
    'B':  {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1},
    'F#': {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1, 'E': 1},
    'C#': {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1, 'E': 1, 'B': 1},
    'F':  {'B': -1},
    'Bb': {'B': -1, 'E': -1},
    'Eb': {'B': -1, 'E': -1, 'A': -1},
    'Ab': {'B': -1, 'E': -1, 'A': -1, 'D': -1},
    'Db': {'B': -1, 'E': -1, 'A': -1, 'D': -1, 'G': -1},
    'Gb': {'B': -1, 'E': -1, 'A': -1, 'D': -1, 'G': -1, 'C': -1},
    'Cb': {'B': -1, 'E': -1, 'A': -1, 'D': -1, 'G': -1, 'C': -1, 'F': -1},
}

MINOR_TO_RELATIVE_MAJOR = {
    'A':  'C',  'E':  'G',  'B':  'D',  'F#': 'A',  'C#': 'E',  'G#': 'B',
    'D#': 'F#','A#': 'C#','D':  'F',  'G':  'Bb','C':  'Eb','F':  'Ab',
    'Bb': 'Db','Eb': 'Gb','Ab': 'Cb',
}


def key_signature_for(ledger: BeatLedger) -> dict[str, int]:
    root = ledger.key_root
    if ledger.key_mode == 'minor':
        root = MINOR_TO_RELATIVE_MAJOR.get(root, root)
    return KEY_ACCIDENTALS.get(root, {})


def midi_to_abc(midi: int, key_sig: dict[str, int]) -> str:
    """MIDI → ABC pitch token (no duration).

    Uses scientific octave numbering: middle C = MIDI 60 = ``C`` (ABC C4).
    Adds ``^``/``_``/``=`` accidentals only when the spelling differs from
    the key signature.
    """
    letter, acc, octave = midi_to_letter_octave(midi)
    # Respell to match flat-keys (avoid unsuppressible naturals on the next bar)
    flat_key = any(v < 0 for v in key_sig.values())
    if acc == 1 and flat_key:
        # Use enharmonic flat (e.g., F# -> Gb)
        idx = PITCH_LETTERS.index(letter)
        new_letter = PITCH_LETTERS[(idx + 1) % 7]
        acc = -1
        letter = new_letter
        # octave correction: B# -> C of next octave doesn't apply here; only
        # F#->Gb / C#->Db / G#->Ab / D#->Eb / A#->Bb -- octave unchanged.

    key_acc = key_sig.get(letter, 0)
    if acc == key_acc:
        accidental_tok = ''
    else:
        accidental_tok = {-1: '_', 0: '=', 1: '^'}[acc]

    # ABC octave conventions:
    #   C  = C4 (middle C)
    #   c  = C5
    #   C, = C3, C,, = C2, C,,, = C1
    #   c' = C6, c'' = C7
    if octave <= 4:
        token = letter.upper()
        commas = 4 - octave
        suffix = ',' * commas
    else:
        token = letter.lower()
        apos = octave - 5
        suffix = "'" * apos
    return accidental_tok + token + suffix


def duration_token(beats: int) -> str:
    """Render a duration multiplier given L: 1/4. Whole numbers only."""
    if beats <= 1:
        return ''
    return str(beats)


# ---------------------------------------------------------------------------
# Per-voice attack/sustain run collection
# ---------------------------------------------------------------------------

def collect_voice_runs(
    beats: list[Beat], voice: VoiceName
) -> list[tuple[int, int, Optional[int]]]:
    """For one voice across all beats, return a list of (start_beat, length, midi).

    Each element covers one "slot" of the beat grid:
      - attack runs: midi is set, length includes following sustains of that pitch.
      - rest runs: midi is None, length is the contiguous rest span.
    A voice's events thus tile its beat row exactly.
    """
    runs: list[tuple[int, int, Optional[int]]] = []
    i = 0
    n = len(beats)
    while i < n:
        ev = beats[i].voices.get(voice)
        if ev is None or ev.kind == 'rest':
            j = i
            while j < n:
                e = beats[j].voices.get(voice)
                if e is None or e.kind == 'rest':
                    j += 1
                else:
                    break
            runs.append((i, j - i, None))
            i = j
            continue
        if ev.kind == 'attack':
            start_midi = ev.pitch_midi
            j = i + 1
            while j < n:
                e = beats[j].voices.get(voice)
                if e is not None and e.kind == 'sustain' and e.pitch_midi == start_midi:
                    j += 1
                else:
                    break
            runs.append((i, j - i, start_midi))
            i = j
            continue
        # Stray sustain with no preceding attack — treat as a single attack.
        runs.append((i, 1, ev.pitch_midi))
        i += 1
    return runs


# ---------------------------------------------------------------------------
# Per-hand, per-beat slot layout
# ---------------------------------------------------------------------------

class HandSlot:
    """A scheduled note in one hand: starts at ``start``, lasts ``length`` beats."""

    __slots__ = ('voice', 'midi', 'start', 'length')

    def __init__(self, voice: VoiceName, midi: int, start: int, length: int):
        self.voice = voice
        self.midi = midi
        self.start = start
        self.length = length


def build_hand_slots(
    beats: list[Beat],
    voices: tuple[VoiceName, ...],
    voice_transpose: Optional[dict[str, int]] = None,
) -> list[HandSlot]:
    """voice_transpose: optional {voice_name: semitones} added to each note in
    that voice. Used to fit SAT into RH range when patterns are active."""
    slots: list[HandSlot] = []
    vt = voice_transpose or {}
    for v in voices:
        shift = vt.get(v, 0)
        for start, length, midi in collect_voice_runs(beats, v):
            if midi is None:
                continue
            slots.append(HandSlot(v, midi + shift, start, length))
    return slots


# ---------------------------------------------------------------------------
# Beat-cell rendering
# ---------------------------------------------------------------------------

def _split_at_barlines(beats: list[Beat], start: int, length: int):
    """Yield (segment_length, is_last) so a note crossing bars emits as
    tied segments separated by barlines."""
    end = start + length
    cur = start
    while cur < end:
        cur_bar = beats[cur].bar
        nxt = cur + 1
        while nxt < end and beats[nxt].bar == cur_bar:
            nxt += 1
        seg_len = nxt - cur
        yield seg_len, (nxt >= end)
        cur = nxt


def _emit_cell(chord_token: str, beats: list[Beat], start: int, length: int) -> list[str]:
    """chord_token is e.g. 'C' or '[CE]'. Returns tokens including any internal
    barlines + tie markers."""
    out: list[str] = []
    segments = list(_split_at_barlines(beats, start, length))
    for i, (seg_len, is_last) in enumerate(segments):
        out.append(chord_token + duration_token(seg_len) + ('' if is_last else '-'))
        if not is_last:
            out.append('|')
    return out


def render_hand(
    beats: list[Beat],
    hand_voices: tuple[VoiceName, ...],
    key_sig: dict[str, int],
    meter_beats: int,
    chord_symbols: Optional[dict[int, str]] = None,
    exclude: tuple[VoiceName, ...] = (),
    voice_transpose: Optional[dict[str, int]] = None,
    pre_built_slots: Optional[list[HandSlot]] = None,
) -> tuple[str, list[Audit]]:
    """Render one hand to a single ABC voice string.

    Walks beat-by-beat. At each beat the chord includes every currently-active
    slot (newly-attacking + still-ringing from earlier). Cell length caps at
    the next attack boundary so inner-voice attacks during a long sustain
    aren't swallowed; the outer tie '-' carries continuing voices forward.

    chord_symbols: optional bar→RN map. When set, prepend `"<RN>"` to the
    first cell of each bar where the chord changes.
    exclude: voices to skip entirely (used to render Dr as a separate overlay).
    """
    audits: list[Audit] = []
    if pre_built_slots is not None:
        slots = pre_built_slots
    else:
        slots = build_hand_slots(beats, hand_voices, voice_transpose)
        slots = [s for s in slots if s.voice not in exclude]
    if not slots:
        return '', audits

    n = len(beats)
    attack_starts = sorted({s.start for s in slots})
    prev_chord_label: Optional[str] = None
    pending_chord_symbol: Optional[str] = None

    def active_at(b: int) -> list[HandSlot]:
        return [s for s in slots if s.start <= b < s.start + s.length]

    tokens: list[str] = []
    beat_idx = 0
    audited_attack_beats: set[int] = set()

    while beat_idx < n:
        # Chord-symbol decision: when we enter a new bar where the RN differs
        # from the previous emitted one, queue a "RN" annotation before the
        # next cell.
        if chord_symbols is not None:
            cur_bar = beats[beat_idx].bar
            label = chord_symbols.get(cur_bar)
            if label and label != prev_chord_label:
                pending_chord_symbol = label
                prev_chord_label = label

        active = active_at(beat_idx)
        if not active:
            if pending_chord_symbol is not None:
                tokens.append(f'"^{pending_chord_symbol}"')
                pending_chord_symbol = None
            tokens.append('z')
            beat_idx += 1
        else:
            future = [a for a in attack_starts if a > beat_idx]
            next_attack = future[0] if future else n
            next_release = min(s.start + s.length for s in active)
            cell_len = min(next_attack - beat_idx, next_release - beat_idx)

            active_sorted = sorted(active, key=lambda s: s.midi)
            seen_midis: set[int] = set()
            active_sorted = [
                s for s in active_sorted
                if not (s.midi in seen_midis or seen_midis.add(s.midi))
            ]
            pitch_tokens = [midi_to_abc(s.midi, key_sig) for s in active_sorted]
            plain_chord = (
                pitch_tokens[0] if len(pitch_tokens) == 1
                else '[' + ''.join(pitch_tokens) + ']'
            )

            if beat_idx not in audited_attack_beats:
                attacks_here = [s for s in active if s.start == beat_idx]
                if attacks_here:
                    if len(attacks_here) > 4:
                        audits.append(Audit(
                            beat=beat_idx,
                            message=f"{len(attacks_here)} attacks on one hand at beat {beat_idx}",
                            severity='warn',
                        ))
                    for s in attacks_here:
                        if s.voice != 'Dr' and s.voice in LH_VOICES and s.midi < 36:
                            audits.append(Audit(
                                beat=beat_idx,
                                message=f"{s.voice} pitch midi={s.midi} below C2 at beat {beat_idx}",
                                severity='warn',
                            ))
                span = active_sorted[-1].midi - active_sorted[0].midi
                if span > 17:
                    audits.append(Audit(
                        beat=beat_idx,
                        message=f"hand span {span} semitones exceeds 17 at beat {beat_idx}",
                        severity='warn',
                    ))
                audited_attack_beats.add(beat_idx)

            cell_end = beat_idx + cell_len
            # Per-pitch ties for the FINAL segment: only the pitches that keep
            # ringing past cell_end get an inner '-'. abc2midi errors out if a
            # chord-wide tie targets a next chord that drops one of the pitches,
            # so we tie per pitch instead.
            if len(active_sorted) == 1:
                s = active_sorted[0]
                tie = '-' if s.start + s.length > cell_end else ''
                final_chord_base = pitch_tokens[0] + (tie if tie else '')
            else:
                parts = []
                for s, pt in zip(active_sorted, pitch_tokens):
                    parts.append(pt + ('-' if s.start + s.length > cell_end else ''))
                final_chord_base = '[' + ''.join(parts) + ']'

            if pending_chord_symbol is not None:
                tokens.append(f'"^{pending_chord_symbol}"')
                pending_chord_symbol = None

            segments = list(_split_at_barlines(beats, beat_idx, cell_len))
            for i, (seg_len, is_last) in enumerate(segments):
                if is_last:
                    if len(active_sorted) == 1 and final_chord_base.endswith('-'):
                        # Single-pitch tie: 'C2-' (tie after duration).
                        base = final_chord_base[:-1]
                        tokens.append(base + duration_token(seg_len) + '-')
                    else:
                        tokens.append(final_chord_base + duration_token(seg_len))
                else:
                    # Internal segment of the same chord → outer tie is always
                    # safe because the next chord is identical.
                    tokens.append(plain_chord + duration_token(seg_len) + '-')
                    tokens.append('|')
            beat_idx += cell_len

        if beat_idx < n:
            prev_bar = beats[beat_idx - 1].bar
            cur_bar = beats[beat_idx].bar
            if cur_bar != prev_bar and tokens and tokens[-1] != '|':
                tokens.append('|')
        else:
            if tokens and tokens[-1] == '|':
                tokens[-1] = '|]'
            else:
                tokens.append('|]')

    # Insert newlines every 4 bars for readability.
    text_parts: list[str] = []
    bars_seen = 0
    buf: list[str] = []
    for tok in tokens:
        buf.append(tok)
        if tok == '|':
            bars_seen += 1
            if bars_seen % 4 == 0:
                text_parts.append(' '.join(buf))
                buf = []
    if buf:
        text_parts.append(' '.join(buf))
    return ('\n'.join(text_parts), audits)


# ---------------------------------------------------------------------------
# Top-level consolidate()
# ---------------------------------------------------------------------------

def _abc_key(ledger: BeatLedger) -> str:
    root = ledger.key_root
    # ABC convention: 'Bb' -> 'Bb', 'F#' -> 'F#', minor -> 'm' suffix.
    suffix = 'm' if ledger.key_mode == 'minor' else ''
    return root + suffix


def _has_dr(ledger: BeatLedger) -> bool:
    return any(
        b.voices.get('Dr') and b.voices['Dr'].kind == 'attack'
        for b in ledger.beats
    )


def _has_pattern_voices(ledger: BeatLedger) -> bool:
    """True iff the LH pattern slots (T1 or T2) have any attacks."""
    return any(
        (b.voices.get(v) and b.voices[v].kind == 'attack')
        for b in ledger.beats for v in ('T1', 'T2')
    )


def _pattern_to_router_events(
    pattern: str,
    ledger: BeatLedger,
    key_sig: dict[str, int],
) -> list[list]:
    """Convert a Somerset pattern into per-beat RoutedNote lists (hand='LH').

    Pattern attacks happen at sub-beat positions; for the router (which is
    beat-quantized) we approximate by treating each pattern attack as
    starting on the beat it falls in. Sustains carry through subsequent
    beats that the pattern's note duration covers.
    """
    from .hand_router import RoutedNote
    from .somerset import (PATTERNS, _root_midi, _RN_DEGREE, _rn_head,
                            _is_diminished, _clamp_lh)
    from music21 import key as m21key

    p_map = PATTERNS.get(pattern)
    if p_map is None:
        return [[] for _ in ledger.beats]

    K = m21key.Key(ledger.key_root + ('m' if ledger.key_mode == 'minor' else ''))
    meter = ledger.meter_beats
    n = len(ledger.beats)
    per_beat: list[list] = [[] for _ in range(n)]

    for bar in range(1, max(ledger.bar_chords.keys(), default=0) + 1):
        rn = ledger.bar_chords.get(bar, "")
        head = _rn_head(rn)
        degree = _RN_DEGREE.get(head) if head else None
        if degree is None:
            continue
        is_min = head and head[0].islower()
        is_dim = _is_diminished(rn)
        third_st = 3 if (is_min or is_dim) else 4
        fifth_st = 6 if is_dim else 7
        root_midi = _root_midi(K, degree)
        events_fn = p_map.get(meter) or next(iter(p_map.values()))
        events = events_fn(third_st, fifth_st)
        bar_start_beat = (bar - 1) * meter

        cur = 0.0
        for dur, offsets in events:
            beat_pos = bar_start_beat + int(cur)
            beats_covered = max(1, int(round(dur)))
            for off in offsets:
                # Voice slot by pattern role: root and octave-below in T2
                # (LH lower inner), upper chord-tones in T1 (LH upper inner).
                voice = 'T2' if off <= 0 else 'T1'
                midi = _clamp_lh(root_midi + off)
                if 0 <= beat_pos < n:
                    per_beat[beat_pos].append(
                        RoutedNote(midi, voice, 'attack', 'LH')
                    )
                for k in range(1, beats_covered):
                    bp = bar_start_beat + int(cur) + k
                    if 0 <= bp < n:
                        per_beat[bp].append(
                            RoutedNote(midi, voice, 'sustain', 'LH')
                        )
            cur += dur

    return per_beat


def consolidate(
    ledger: BeatLedger,
    pattern: Optional[str] = None,
) -> ArrangementResult:
    """Build ABC from the 8-voice ledger.

    When `pattern` is set, LH is replaced by the Somerset accompaniment figure
    (sourced from somerset.PATTERNS), and RH is the merged SAT — tenor + alto
    + soprano played by the right hand. Dr keeps its low chord-root pluck.

    When `pattern` is None, the default routing applies (LH = bass voices,
    RH = upper voices) — i.e. straight SATB rendering.
    """
    key_sig = key_signature_for(ledger)

    # Static voice-slot hand routing (per docs/harprules.md):
    #   LH = {Dr, B, T2, T1}        (HAND_VOICE_ORDER['LH'])
    #   RH = {A2, A1, S2, S1, Gl}   (HAND_VOICE_ORDER['RH'])
    rh_text, rh_audits = render_hand(
        ledger.beats, HAND_VOICE_ORDER['RH'], key_sig, ledger.meter_beats,
        chord_symbols=ledger.bar_chords or None,
    )

    if pattern:
        # Pattern occupies T1+T2 slots. We bypass the ledger for the pattern
        # (it has sub-beat rhythm that the beat-quantized ledger can't hold)
        # and render somerset directly to ABC. SATB bass + tenor are dropped
        # from LH in pattern mode; the pattern provides the bass figure.
        from .somerset import render_lh_voice
        lh_text = render_lh_voice(
            pattern, ledger.bar_chords, ledger.key_root, ledger.key_mode,
            ledger.meter_beats, key_sig,
        )
        lh_audits = []
    else:
        # Default LH: B (SATB bass) + T1 (SATB tenor) + T2 (empty unless filled).
        lh_text, lh_audits = render_hand(
            ledger.beats, HAND_VOICE_ORDER['LH'], key_sig, ledger.meter_beats,
            exclude=('Dr',),
        )

    # Bs voice: Dr drone in C1-B1. In pattern mode we also stack B (chord-
    # root one octave above Dr in C2-B2) as a synthesized parallel pluck —
    # the "echo of Dr" the user asked for, since pattern mode took B's slot
    # for the somerset figure.
    bs_text: Optional[str] = None
    if _has_dr(ledger):
        if pattern:
            synthetic_slots: list[HandSlot] = []
            # Walk Dr runs and synthesize a parallel B-octave run for each.
            from .consolidator import collect_voice_runs  # type: ignore
            for start, length, midi in collect_voice_runs(ledger.beats, 'Dr'):
                if midi is None:
                    continue
                synthetic_slots.append(HandSlot('Dr', midi, start, length))
                synthetic_slots.append(HandSlot('B', midi + 12, start, length))
            bs_text, _ = render_hand(
                ledger.beats, (), key_sig, ledger.meter_beats,
                pre_built_slots=synthetic_slots,
            )
        else:
            bs_text, _ = render_hand(
                ledger.beats, ('Dr',), key_sig, ledger.meter_beats,
            )

    # Assemble staves directive + voice declarations based on what's active.
    staves_parts: list[str] = ["RH"]
    voice_decls_parts: list[str] = [
        "V: RH clef=treble",
        "%%MIDI program 46",
    ]
    if lh_text:
        staves_parts.append("LH")
        voice_decls_parts += ["V: LH clef=bass", "%%MIDI program 46"]
    if bs_text:
        staves_parts.append("Bs")
        voice_decls_parts += ["V: Bs clef=bass", "%%MIDI program 46"]
    staves = "{" + " ".join(staves_parts) + "}"
    voice_decls = "\n".join(voice_decls_parts) + "\n"

    header = (
        f"X: 1\n"
        f"T: {ledger.title}\n"
        f"M: {ledger.meter_beats}/{ledger.meter_unit}\n"
        f"L: 1/4\n"
        f"Q: 1/4={ledger.tempo_bpm}\n"
        f"%%staves {staves}\n"
        f"{voice_decls}"
        f"K: {_abc_key(ledger)}\n"
    )
    body = "[V: RH]\n" + rh_text + "\n"
    if lh_text:
        body += "[V: LH]\n" + lh_text + "\n"
    if bs_text:
        body += "[V: Bs]\n" + bs_text + "\n"
    abc = header + body
    audits = list(ledger.audits) + rh_audits + lh_audits
    return ArrangementResult(ledger=ledger, abc=abc, audits=audits)


# ---------------------------------------------------------------------------
# JSON ↔ BeatLedger
# ---------------------------------------------------------------------------

def ledger_from_dict(data: dict) -> BeatLedger:
    beats: list[Beat] = []
    for b in data['beats']:
        voices: dict[VoiceName, VoiceEvent] = {}
        for vname, ev in b['voices'].items():
            voices[vname] = VoiceEvent(
                kind=ev['kind'],
                pitch_midi=ev.get('pitch_midi'),
                source=ev.get('source', 'satb'),
            )
        beats.append(Beat(
            index=b['index'],
            bar=b['bar'],
            beat_in_bar=b['beat_in_bar'],
            voices=voices,
        ))
    audits = [Audit(**a) for a in data.get('audits', [])]
    bar_chords = {int(k): v for k, v in data.get('bar_chords', {}).items()}
    return BeatLedger(
        title=data['title'],
        key_root=data['key_root'],
        key_mode=data['key_mode'],
        modal_name=data.get('modal_name', 'ionian'),
        meter_beats=data['meter_beats'],
        meter_unit=data['meter_unit'],
        beats_per_bar=data.get('beats_per_bar', data['meter_beats']),
        tempo_bpm=data.get('tempo_bpm', 90),
        beats=beats,
        bar_chords=bar_chords,
        audits=audits,
    )


# ---------------------------------------------------------------------------
# Synthetic fixture (used when no ledger is supplied or one isn't on disk)
# ---------------------------------------------------------------------------

def synthetic_fixture() -> BeatLedger:
    """One bar of C major SATB: I — V — vi — IV — back to I (5 beats of 4/4 won't fit).

    Compact: 4 beats of 4/4. SATB on each beat, no fills.
       Beat 1: C major (C3 / G3 / E4 / C5)
       Beat 2: G major (B2 / G3 / D4 / B4)  — soprano repeats? no, distinct
       Beat 3: A minor (A2 / E3 / E4 / C5)
       Beat 4: F major (F2 / C3 / A3 / C5)  (S1 = C5 sustains from beat 3)
    """
    # SATB pitches per beat (B, T1, A1, S1):
    seq = [
        (48, 55, 64, 72),  # I
        (47, 55, 62, 71),  # V
        (45, 52, 64, 72),  # vi  -- S1 attacks new note
        (41, 48, 57, 72),  # IV  -- S1 (72) sustained from beat 3
    ]
    beats: list[Beat] = []
    prev = None
    for i, (b, t, a, s) in enumerate(seq):
        voices: dict[VoiceName, VoiceEvent] = {}
        for vname, midi in (('B', b), ('T1', t), ('A1', a), ('S1', s)):
            if prev is not None and prev.get(vname) == midi:
                voices[vname] = VoiceEvent(kind='sustain', pitch_midi=midi, source='satb')
            else:
                voices[vname] = VoiceEvent(kind='attack', pitch_midi=midi, source='satb')
        # Fill remaining voices with rests.
        for vname in VOICE_ORDER:
            if vname not in voices:
                voices[vname] = VoiceEvent(kind='rest', pitch_midi=None, source='idle')
        beats.append(Beat(
            index=i, bar=1, beat_in_bar=i + 1, voices=voices,
        ))
        prev = {'B': b, 'T1': t, 'A1': a, 'S1': s}
    return BeatLedger(
        title='Synthetic C-major fixture',
        key_root='C',
        key_mode='major',
        modal_name='ionian',
        meter_beats=4,
        meter_unit=4,
        beats_per_bar=4,
        tempo_bpm=90,
        beats=beats,
        audits=[],
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _slugify(title: str) -> str:
    s = re.sub(r'[^A-Za-z0-9]+', '_', title).strip('_').lower()
    return s or 'untitled'


def main(argv: list[str]) -> int:
    if len(argv) >= 2:
        path = Path(argv[1])
        if not path.exists():
            print(f"ledger file not found: {path}", file=sys.stderr)
            return 2
        with open(path) as fh:
            data = json.load(fh)
        ledger = ledger_from_dict(data)
    else:
        print("No ledger argument; using synthetic C-major fixture.")
        ledger = synthetic_fixture()

    result = consolidate(ledger)
    out_dir = Path('data/harp_arranged')
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(ledger.title)
    abc_path = out_dir / f"{slug}.abc"
    abc_path.write_text(result.abc)
    print(f"wrote {abc_path}")

    # Audit summary.
    counts: dict[str, int] = {}
    for a in result.audits:
        counts[a.severity] = counts.get(a.severity, 0) + 1
    print(f"audits: {dict(counts) if counts else 'none'}")
    for a in result.audits:
        print(f"  [{a.severity}] beat={a.beat}: {a.message}")

    # Verify via abc2midi.
    mid_out = Path('/tmp') / f"{slug}.mid"
    try:
        proc = subprocess.run(
            ['abc2midi', str(abc_path), '-o', str(mid_out)],
            capture_output=True, text=True, check=False,
        )
        ok = proc.returncode == 0 and mid_out.exists()
        if proc.stdout:
            for line in proc.stdout.splitlines():
                print(f"  abc2midi: {line}")
        if proc.stderr:
            for line in proc.stderr.splitlines():
                print(f"  abc2midi(stderr): {line}")
        print(f"abc2midi: {'OK' if ok else 'FAILED'}")
        return 0 if ok else 1
    except FileNotFoundError:
        print("abc2midi not on PATH; skipping verification.")
        return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
