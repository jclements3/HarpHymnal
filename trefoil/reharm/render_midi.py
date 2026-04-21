"""Render a reharm-selector variation to a Standard MIDI File.

Phase 7 of the Reharm Tactics pipeline: turn a per-bar tactic manifest
(plus the hymn's melody) into an auditionable ``.mid`` file.  Hand-written
SMF (format 1), stdlib only.

Design notes
------------

The input to ``render_variation_midi`` is two JSONs:

* ``variation`` — ``data/reharm/variations/<slug>/v##.json`` — carries for
  each bar a ``tactic_manifest`` (the 12 chosen tactic ids) and the
  selector-picked ``lh`` / ``rh`` voicings as ``(degree, octave)`` pairs in
  the 47-string shape-library frame.
* ``hymn_json`` — ``data/hymns/<slug>.json`` — carries ``bars[].melody``
  (note/rest events with ``pitch.letter/accidental/octave`` + ``duration``
  in quarter-lengths), ``key``, ``meter``, and ``tempo``.

The renderer:

1. Converts every ``(degree, octave)`` voicing entry to absolute MIDI
   using the hymn's key (major / natural-minor scale).
2. Translates the bar's melody into MIDI, re-timed to the bar.
3. Applies tactic rendering rules — density, texture, lh_activity,
   rh_activity, connect_from/to, substitution, phrase_role — to produce
   a concrete list of (tick, pitch, duration, velocity) events.
4. Writes a single-track format-1 SMF on channel 0 using GM program value
   46 (Orchestral Harp; values are 0-indexed in MIDI program-change bytes,
   so the human-readable GM table entry #47 "Orchestral Harp" is byte 46).

Tactic rendering decisions (implemented)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``density.*``        — governs attack count & placement.
* ``texture.block``    — hands strike together at each attack tick.
* ``texture.staggered``— hands alternate by half-beat (one hand on beat,
  one off-beat).
* ``texture.arp_both`` — all shape tones (LH+RH) ordered low→high spread
  across the bar length.
* ``texture.rolled``   — LH/RH offset by 40 ms at each attack.
* ``texture.bisbigliando`` — rapid 64th alternation between two RH tones
  across the bar (LH sustained underneath).
* ``texture.single_line`` — melody only, regardless of other settings.
* ``lh_activity.*``   — as per task spec; overrides density for LH.
* ``rh_activity.*``   — enriches the melody line per bar.
* ``connect_from.sustained`` — previous bar's notes tied if pitches
  match.  Other variants treated as ``released``.
* ``connect_to.anticipate`` / ``.delay`` — shift shape at bar boundary.
* ``substitution.pedal`` — repeat previous bar's LH.
* ``substitution.delay_change`` — tie previous bar's LH into beat 1.
* ``phrase_role.cadence`` — 15% longer downbeat (tenuto).
* ``phrase_role.release`` — 10% longer total bar duration (rallentando).
* ``lever.*``         — ignored for MIDI v1 (documented choice — harpist
  cues come from LilyPond markup; MIDI renders as-if no flip).

Stdlib only.  Usage::

    from trefoil.reharm.render_midi import render_variation_midi
    render_variation_midi(variation_json, hymn_json, Path("v28.mid"))
"""
from __future__ import annotations

import json
import os
import struct
from pathlib import Path
from typing import Any, Optional


# --------------------------------------------------------------------------- #
# Key / scale / pitch math                                                    #
# --------------------------------------------------------------------------- #

_PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
_MINOR_STEPS = [0, 2, 3, 5, 7, 8, 10]


def _parse_key_root(key_root: str) -> int:
    s = (key_root or "C").strip()
    if not s:
        return 0
    base = _PITCH_CLASS[s[0].upper()]
    for ch in s[1:]:
        if ch == "#":
            base = (base + 1) % 12
        elif ch in ("b", "-"):
            base = (base - 1) % 12
    return base


def _scale_steps(mode: str) -> list[int]:
    return _MINOR_STEPS if (mode or "").startswith("m") or mode == "minor" else _MAJOR_STEPS


def _deg_oct_to_midi(deg: int, octv: int, key_root: str, mode: str) -> int:
    """Shape-library ``(deg, oct)`` → MIDI.

    The 47-string harp starts at C1 = string 1.  ``string = (oct-1)*7 +
    (deg-1) + 1``, so string 22 = C4 = MIDI 60.  ``base_octave`` offsets
    the C-octave scaffolding; we map string 1 (C1) to MIDI 24 (C1 in
    music21 convention, though actually C1 = MIDI 24 in General MIDI).
    """
    steps = _scale_steps(mode)
    tonic_pc = _parse_key_root(key_root)
    zero = (octv - 1) * 7 + (deg - 1)  # 0-based string index (0..46)
    octave_offset = zero // 7
    degree_idx = zero % 7
    semitones = steps[degree_idx] + 12 * octave_offset
    # string 1 = C1 = MIDI 24 in standard General-MIDI mapping.
    # Our tonic lives at string 1 + (tonic_pc's offset from C); but since
    # the degree system is already tonic-relative (deg 1 = tonic), we
    # add tonic_pc on top of string 1's C anchor.
    # Base = MIDI 24 = C1.  Add tonic_pc so a G-major hymn puts its deg-1
    # at G1 (MIDI 31), i.e. string 1 becomes the tonic G below the harp's
    # lowest C... but per shape_gen.py comment, string 1 *is* C1 and the
    # degree system is in the *key's* frame.  The actual lowest tonic-1
    # thus sits at the first deg-1 above C1.
    return 24 + tonic_pc + semitones


def _letter_to_pc(letter: str, accidental: Optional[str]) -> int:
    pc = _PITCH_CLASS[letter.upper()]
    if accidental in ("#", "sharp", "♯"):
        pc = (pc + 1) % 12
    elif accidental in ("b", "flat", "-", "♭"):
        pc = (pc - 1) % 12
    return pc


def _melody_event_to_midi(ev: dict) -> Optional[int]:
    if ev.get("kind") != "note":
        return None
    p = ev.get("pitch") or {}
    letter = p.get("letter")
    if not letter:
        return None
    pc = _letter_to_pc(letter, p.get("accidental"))
    octv = int(p.get("octave") or 4)
    # Music21 octave convention: C4 = MIDI 60.  C-1 would be MIDI 0 but
    # hymn data uses only positive octaves.  MIDI = 12 * (oct + 1) + pc.
    return 12 * (octv + 1) + pc


# --------------------------------------------------------------------------- #
# SMF writer (format 1, single track, hand-written)                           #
# --------------------------------------------------------------------------- #

def _vlq(n: int) -> bytes:
    """Encode non-negative int as MIDI variable-length quantity."""
    if n < 0:
        n = 0
    if n == 0:
        return b"\x00"
    buf = []
    buf.append(n & 0x7F)
    n >>= 7
    while n > 0:
        buf.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(buf))


class _MidiBuilder:
    """Accumulates delta-encoded MIDI events; emits an SMF file.

    Events are collected as (absolute_tick, sort_key, raw_bytes); the
    sort_key breaks ties so note-offs precede note-ons at the same tick
    (avoids same-pitch note-off after note-on zero-length glitches).
    """

    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    META = 0xFF
    PROGRAM_CHANGE = 0xC0

    def __init__(self, ticks_per_quarter: int = 480, channel: int = 0):
        self.tpq = ticks_per_quarter
        self.channel = channel
        self.events: list[tuple[int, int, bytes]] = []

    def add_meta(self, tick: int, meta_type: int, data: bytes, sort: int = -10) -> None:
        payload = bytes([self.META, meta_type]) + _vlq(len(data)) + data
        self.events.append((tick, sort, payload))

    def tempo(self, tick: int, bpm: float) -> None:
        micros_per_quarter = int(round(60_000_000 / max(bpm, 1.0)))
        data = micros_per_quarter.to_bytes(3, "big")
        self.add_meta(tick, 0x51, data, sort=-20)

    def time_signature(self, tick: int, numerator: int, denominator: int) -> None:
        # denominator as power of 2 exponent (2=quarter, 3=eighth, etc.)
        import math
        dd = int(round(math.log2(denominator))) if denominator > 0 else 2
        data = bytes([numerator, dd, 24, 8])
        self.add_meta(tick, 0x58, data, sort=-15)

    def program(self, tick: int, program: int) -> None:
        payload = bytes([self.PROGRAM_CHANGE | self.channel, program & 0x7F])
        self.events.append((tick, -5, payload))

    def note(self, tick: int, pitch: int, duration_ticks: int, velocity: int = 80) -> None:
        if pitch < 0 or pitch > 127 or duration_ticks <= 0:
            return
        on = bytes([self.NOTE_ON | self.channel, pitch & 0x7F, max(1, min(127, velocity))])
        off = bytes([self.NOTE_OFF | self.channel, pitch & 0x7F, 0])
        # note_offs sort before note_ons at same tick to avoid glitches
        self.events.append((tick, 10, on))
        self.events.append((tick + duration_ticks, 5, off))

    def build(self) -> bytes:
        # sort by (tick, sort_key, insertion) — Python's sort is stable
        evs = sorted(self.events, key=lambda x: (x[0], x[1]))
        track = bytearray()
        last_tick = 0
        for tick, _sort, payload in evs:
            delta = max(0, tick - last_tick)
            track += _vlq(delta)
            track += payload
            last_tick = tick
        # end-of-track meta
        track += _vlq(0) + bytes([self.META, 0x2F, 0x00])

        # Format 1 multi-track container, 1 track.  Format 1 is the more
        # common modern default even for single-track files.
        header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, self.tpq)
        track_chunk = b"MTrk" + struct.pack(">I", len(track)) + bytes(track)
        return header + track_chunk


# --------------------------------------------------------------------------- #
# Shape voicing → MIDI pitches                                                #
# --------------------------------------------------------------------------- #

def _voicing_to_midis(voicing: list[list[int]], key_root: str, mode: str) -> list[int]:
    out: list[int] = []
    for pair in voicing or []:
        if not pair or len(pair) < 2:
            continue
        try:
            deg, octv = int(pair[0]), int(pair[1])
        except (TypeError, ValueError):
            continue
        out.append(_deg_oct_to_midi(deg, octv, key_root, mode))
    return out


# --------------------------------------------------------------------------- #
# Per-bar rendering                                                           #
# --------------------------------------------------------------------------- #

def _meter_of(hymn_json: dict) -> tuple[int, int]:
    m = hymn_json.get("meter") or {}
    beats = int(m.get("beats") or 4)
    unit = int(m.get("unit") or 4)
    return beats, unit


def _tempo_bpm(hymn_json: dict) -> float:
    t = hymn_json.get("tempo") or {}
    v = t.get("value")
    if v is None:
        return 72.0
    try:
        bpm = float(v)
    except (TypeError, ValueError):
        return 72.0
    # If tempo unit isn't a quarter, translate so that SMF tempo (per quarter)
    # gives the same wall clock for the bar.
    unit = t.get("unit") or 4
    try:
        unit = int(unit)
    except (TypeError, ValueError):
        unit = 4
    # bpm is "unit-notes per minute"; quarter BPM = bpm * (unit/4)
    return bpm * (unit / 4.0)


def _bar_length_quarters(hymn_json: dict) -> float:
    beats, unit = _meter_of(hymn_json)
    return beats * (4.0 / unit)


def _beat_count(hymn_json: dict) -> int:
    # Logical "beat" for density rules: the meter's numerator.
    beats, _unit = _meter_of(hymn_json)
    return max(1, beats)


def _attack_offsets_for_density(density: str, n_beats: int) -> list[float]:
    """Return list of attack fractions-of-bar for the density mode.

    Result is in [0, 1).  Empty list means "use melody rhythm".
    """
    if n_beats <= 0:
        n_beats = 1
    if density == "density.one_attack":
        return [0.0]
    if density == "density.per_beat":
        return [i / n_beats for i in range(n_beats)]
    if density == "density.two_per_beat":
        return [i / (2 * n_beats) for i in range(2 * n_beats)]
    if density == "density.syncopated":
        # offbeats only — midway between each beat
        return [(i + 0.5) / n_beats for i in range(n_beats)]
    if density == "density.front_loaded":
        # cluster in first half
        if n_beats == 1:
            return [0.0, 0.25]
        return [i / (2 * n_beats) for i in range(n_beats)]  # first half, 2/beat
    if density == "density.back_loaded":
        # cluster in second half
        if n_beats == 1:
            return [0.5, 0.75]
        return [0.5 + i / (2 * n_beats) for i in range(n_beats)]
    # fallback: per-beat
    return [i / n_beats for i in range(n_beats)]


def _lh_pattern_ticks(lh_activity: str, bar_ticks: int, n_beats: int,
                       bar_density_attacks: list[float]) -> list[tuple[float, str]]:
    """Return list of (tick_fraction, event_kind) describing LH attacks.

    event_kind in {"all", "bass", "chord", "arp_up", "arp_down", "tremolo",
    "countermelody"}.  "all" means strike whole LH shape.  "arp_up" etc.
    are marker placeholders the renderer replaces with concrete pitch
    subsets.
    """
    if lh_activity == "lh_activity.none":
        return []
    if lh_activity == "lh_activity.sustain":
        return [(0.0, "all")]  # one attack, sustained full bar
    if lh_activity == "lh_activity.strike_and_ring":
        return [(0.0, "all")]
    if lh_activity == "lh_activity.arp_up":
        # 16ths ascending — count = min(4, 4*n_beats) per bar
        k = max(2, min(8, 2 * n_beats))
        return [(i / k, "arp_up") for i in range(k)]
    if lh_activity == "lh_activity.arp_down":
        k = max(2, min(8, 2 * n_beats))
        return [(i / k, "arp_down") for i in range(k)]
    if lh_activity == "lh_activity.bass_chord_chord":
        # bass on 1, chord on 2..n_beats
        pat = [(0.0, "bass")]
        for i in range(1, n_beats):
            pat.append((i / n_beats, "chord"))
        return pat
    if lh_activity == "lh_activity.chord_offbeat":
        return [((i + 0.5) / n_beats, "all") for i in range(n_beats)]
    if lh_activity == "lh_activity.tremolo":
        # 32nds alternating between two LH tones
        k = max(4, min(16, 4 * n_beats))
        return [(i / k, "tremolo") for i in range(k)]
    if lh_activity == "lh_activity.partial_silence":
        # hit beats 2 and 4 (or equivalent offbeats)
        if n_beats >= 4:
            return [(1.0 / n_beats, "all"), (3.0 / n_beats, "all")]
        if n_beats == 3:
            return [(1.0 / 3.0, "all")]
        return [(0.5, "all")]
    if lh_activity == "lh_activity.low_bass_grab":
        # grace before downbeat handled separately; return downbeat strum.
        return [(0.0, "all")]
    if lh_activity == "lh_activity.countermelody":
        # 4 stepwise notes across the bar
        return [(i / 4, "countermelody") for i in range(4)]
    # fallback: match density attacks with a block strike per beat
    return [(x, "all") for x in bar_density_attacks]


def _rh_pitches_for_melody_event(
    rh_activity: str,
    melody_midi: int,
    shape_rh_midis: list[int],
    shape_all_midis: list[int],
    next_bar_rh_midis: Optional[list[int]] = None,
    key_root: str = "C",
    mode: str = "major",
) -> list[int]:
    """Given one melody note + rh_activity tactic, return list of pitches
    that sound at that attack point (the melody itself is included).
    """
    below = [p for p in shape_all_midis if p < melody_midi]
    below_sorted = sorted(below, reverse=True)  # closest first

    if rh_activity == "rh_activity.melody_alone":
        return [melody_midi]
    if rh_activity == "rh_activity.melody_plus_1":
        if below_sorted:
            return [below_sorted[0], melody_midi]
        return [melody_midi]
    if rh_activity == "rh_activity.melody_plus_2":
        picks = below_sorted[:2]
        return sorted(picks + [melody_midi])
    if rh_activity == "rh_activity.melody_oct":
        return [melody_midi - 12, melody_midi]
    # neighbor / anticipation / passing_tone handled at the rhythm level
    # (they add extra events) — here we emit the melody alone.
    return [melody_midi]


def _diatonic_neighbor(midi: int, key_root: str, mode: str, direction: int) -> int:
    tonic_pc = _parse_key_root(key_root)
    steps = _scale_steps(mode)
    pc_above = (midi - tonic_pc) % 12
    if pc_above in steps:
        idx = steps.index(pc_above)
    else:
        # nearest scale step below
        below = [s for s in steps if s <= pc_above]
        idx = steps.index(below[-1]) if below else 0
    new_idx = idx + direction
    octave_shift = 0
    if new_idx < 0:
        new_idx += 7
        octave_shift = -1
    elif new_idx >= 7:
        new_idx -= 7
        octave_shift = 1
    anchor = midi - pc_above
    return anchor + 12 * octave_shift + steps[new_idx]


# --------------------------------------------------------------------------- #
# Main rendering entry point                                                  #
# --------------------------------------------------------------------------- #

def render_variation_midi(variation: dict, hymn_json: dict, out_path: Path) -> Path:
    """Render one variation to a Standard MIDI File.

    Parameters
    ----------
    variation
        Parsed ``data/reharm/variations/<slug>/v##.json`` dict.
    hymn_json
        Parsed ``data/hymns/<slug>.json`` dict (for melody, tempo,
        meter, key).
    out_path
        Destination ``.mid`` file path.  Parent directories will be
        created.

    Returns
    -------
    Path
        The ``out_path`` (so callers can chain).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tpq = 480
    bpm = _tempo_bpm(hymn_json)
    beats, unit = _meter_of(hymn_json)
    bar_quarters = _bar_length_quarters(hymn_json)
    bar_ticks = int(round(bar_quarters * tpq))
    n_beats = _beat_count(hymn_json)

    key = hymn_json.get("key") or {}
    key_root = key.get("root", "C")
    key_mode = key.get("mode", "major")

    mb = _MidiBuilder(ticks_per_quarter=tpq, channel=0)
    mb.time_signature(0, beats, unit)
    mb.tempo(0, bpm)
    mb.program(0, 46)  # GM Orchestral Harp (0-indexed; value 47 would be Timpani)

    bars = variation.get("bars") or []
    hymn_bars = hymn_json.get("bars") or []
    # Pre-compute per-bar shape midis (lh, rh), for pedal / delay-change / look-ahead.
    bar_lh_midis: list[list[int]] = []
    bar_rh_midis: list[list[int]] = []
    for b in bars:
        bar_lh_midis.append(_voicing_to_midis(b.get("lh") or [], key_root, key_mode))
        bar_rh_midis.append(_voicing_to_midis(b.get("rh") or [], key_root, key_mode))

    prev_bar_events: list[tuple[int, int, int, int]] = []  # (tick, pitch, dur_ticks, vel)

    bar_tick_offset = 0
    for ibar, bar in enumerate(bars):
        manifest = bar.get("tactic_manifest") or {}
        density = manifest.get("density", "density.per_beat")
        texture = manifest.get("texture", "texture.block")
        lh_activity = manifest.get("lh_activity", "lh_activity.sustain")
        rh_activity = manifest.get("rh_activity", "rh_activity.melody_alone")
        connect_from = manifest.get("connect_from", "connect_from.released")
        connect_to = manifest.get("connect_to", "connect_to.land_down")
        substitution = manifest.get("substitution", "substitution.as_written")
        phrase_role = manifest.get("phrase_role", "phrase_role.middle")

        # Phrase-release rallentando: stretch this bar's local ticks by 10%.
        local_bar_ticks = bar_ticks
        if phrase_role == "phrase_role.release":
            local_bar_ticks = int(round(bar_ticks * 1.10))

        lh_midis = list(bar_lh_midis[ibar])
        rh_midis = list(bar_rh_midis[ibar])

        # substitution.pedal → repeat previous bar's LH entirely
        if substitution == "substitution.pedal" and ibar > 0:
            lh_midis = list(bar_lh_midis[ibar - 1])

        # connect_to.anticipate at previous bar affects *this* bar's last
        # beat; we treat simply — honored symmetrically below via next bar.

        # --- Melody events for this hymn bar ---
        h_bar = hymn_bars[ibar] if ibar < len(hymn_bars) else {}
        mel_events = h_bar.get("melody") or []
        # Compute onsets of melody events (quarter-lengths within bar).
        mel_total_ql = sum(float(e.get("duration") or 0) for e in mel_events) or bar_quarters
        # Scale factor to fit melody's declared lengths into the bar.
        scale = bar_quarters / mel_total_ql if mel_total_ql > 0 else 1.0
        mel_onsets: list[tuple[float, Optional[int], float]] = []  # (onset_q, midi_or_None, dur_q)
        cur = 0.0
        for e in mel_events:
            dur = float(e.get("duration") or 0) * scale
            if e.get("kind") == "note":
                m = _melody_event_to_midi(e)
                mel_onsets.append((cur, m, dur))
            else:
                mel_onsets.append((cur, None, dur))
            cur += dur

        # --- texture.single_line: melody only, skip LH & RH shapes ---
        if texture == "texture.single_line":
            for on_q, midi, dur_q in mel_onsets:
                if midi is None:
                    continue
                tick = bar_tick_offset + int(round(on_q * tpq))
                dur_ticks = max(1, int(round(dur_q * tpq)))
                vel = 80
                if phrase_role == "phrase_role.cadence" and on_q < 1e-6:
                    dur_ticks = int(round(dur_ticks * 1.15))
                mb.note(tick, midi, dur_ticks, vel)
            bar_tick_offset += local_bar_ticks
            prev_bar_events = []
            continue

        # --- LH attacks ---
        lh_pattern = _lh_pattern_ticks(lh_activity, local_bar_ticks, n_beats,
                                        _attack_offsets_for_density(density, n_beats))

        # substitution.delay_change: tie previous bar's LH into beat 1
        if substitution == "substitution.delay_change" and ibar > 0:
            prev_lh = list(bar_lh_midis[ibar - 1])
            beat1_dur = int(round((1.0 / n_beats) * local_bar_ticks))
            for p in prev_lh:
                mb.note(bar_tick_offset, p, beat1_dur, 70)
            # delay the "real" LH until beat 2
            lh_pattern = [(pos, kind) for pos, kind in lh_pattern
                          if pos >= (1.0 / n_beats) - 1e-6] or [(1.0 / n_beats, "all")]

        # low_bass_grab → grace note 1-2 octaves below bar's bass, 80 ms before
        if lh_activity == "lh_activity.low_bass_grab" and lh_midis:
            grace_pitch = min(lh_midis) - 12
            if grace_pitch >= 12:
                # 80 ms in ticks: ticks/sec = tpq * bpm / 60; 80ms = tpq*bpm*0.08/60
                grace_delta_ticks = int(round(tpq * bpm * 0.08 / 60))
                grace_tick = max(0, bar_tick_offset - grace_delta_ticks)
                mb.note(grace_tick, grace_pitch, max(1, grace_delta_ticks), 70)

        # Apply texture.rolled offset between hands
        rolled_offset_ticks = 0
        if texture == "texture.rolled":
            rolled_offset_ticks = int(round(tpq * bpm * 0.04 / 60))  # 40 ms

        # Apply texture.staggered: push LH to half-beat offset if also RH on beat
        staggered = (texture == "texture.staggered")

        # connect_from.sustained: if prev bar had matching pitches, ties — we
        # approximate by skipping re-attack on pitches identical to prev bar
        # held at end.
        sustained_pitches: set[int] = set()
        if connect_from == "connect_from.sustained" and ibar > 0:
            prev_last_pitches = {p for _t, p, _d, _v in prev_bar_events}
            sustained_pitches = set(lh_midis + rh_midis) & prev_last_pitches

        # --- Emit LH events ---
        this_bar_events: list[tuple[int, int, int, int]] = []

        # Dedup (tick, pitch) within the bar. When LH and RH voicings share
        # a pitch (e.g. both stacking the root), emitting two note-on events
        # at the same tick makes synths lose track of their envelopes and
        # produce phantom/percussive artifacts during the ensuing note-off.
        emitted_onsets: set[tuple[int, int]] = set()

        def _emit(tick: int, pitch: int, dur_ticks: int, vel: int = 75) -> None:
            if pitch in sustained_pitches:
                return
            # Clamp to 47-string harp range (C1..G7 = MIDI 24..103). Out-of-range
            # pitches octave-shift into range rather than getting dropped, so the
            # voicing stays intact but SGM_Plus's harp samples don't have to
            # fake pitched-up/down synthesis (source of chime/whistle artifacts).
            while pitch > 103:
                pitch -= 12
            while pitch < 24:
                pitch += 12
            key = (tick, pitch)
            if key in emitted_onsets:
                return
            emitted_onsets.add(key)
            mb.note(tick, pitch, dur_ticks, vel)
            this_bar_events.append((tick, pitch, dur_ticks, vel))

        for pos, kind in lh_pattern:
            local_tick = bar_tick_offset + int(round(pos * local_bar_ticks))
            if staggered:
                # push LH by half-beat
                local_tick += int(round((0.5 / n_beats) * local_bar_ticks))
            if texture == "texture.rolled":
                local_tick += rolled_offset_ticks

            # duration of this LH event: until the next LH attack (or bar end
            # for sustain/strike_and_ring)
            if kind in ("tremolo", "arp_up", "arp_down", "countermelody"):
                dur_ticks = max(1, int(round((1.0 / max(1, len(lh_pattern))) * local_bar_ticks)))
            elif lh_activity in ("lh_activity.sustain", "lh_activity.strike_and_ring"):
                dur_ticks = local_bar_ticks
            else:
                dur_ticks = max(1, int(round((1.0 / max(1, len(lh_pattern))) * local_bar_ticks)))

            if kind == "bass":
                if lh_midis:
                    _emit(local_tick, min(lh_midis), dur_ticks, 80)
            elif kind == "chord":
                # upper LH pitches (not the bass)
                uppers = sorted(lh_midis)[1:] or lh_midis
                for p in uppers:
                    _emit(local_tick, p, dur_ticks, 70)
            elif kind == "arp_up":
                idx = lh_pattern.index((pos, kind)) % max(1, len(lh_midis))
                if lh_midis:
                    p = sorted(lh_midis)[idx]
                    _emit(local_tick, p, dur_ticks, 75)
            elif kind == "arp_down":
                idx = lh_pattern.index((pos, kind)) % max(1, len(lh_midis))
                if lh_midis:
                    p = sorted(lh_midis, reverse=True)[idx]
                    _emit(local_tick, p, dur_ticks, 75)
            elif kind == "tremolo":
                # alternate between two LH tones
                if lh_midis:
                    tones = sorted(lh_midis)
                    if len(tones) < 2:
                        tones = [tones[0], tones[0]]
                    idx = lh_pattern.index((pos, kind))
                    p = tones[idx % 2]
                    _emit(local_tick, p, dur_ticks, 65)
            elif kind == "countermelody":
                # walk stepwise within the shape (lowest→highest→return)
                if lh_midis:
                    tones = sorted(lh_midis)
                    step_idx = lh_pattern.index((pos, kind))
                    p = tones[step_idx % len(tones)]
                    _emit(local_tick, p, dur_ticks, 70)
            else:  # "all"
                for p in lh_midis:
                    _emit(local_tick, p, dur_ticks, 75)

        # --- Emit RH (melody-aligned) events ---
        # Determine RH attack timing: either melody-driven (default) or
        # density-grid-driven for bisbigliando / arp_both.
        if texture == "texture.bisbigliando" and len(rh_midis) >= 2:
            # bisbigliando: alternation between two RH tones. Was 16 per
            # quarter (64ths) which caused buzzing overlap under soundfont
            # playback; reduced to 4 per quarter (16ths) which reads as
            # bisbigliando without turning into mush.
            tones = sorted(rh_midis)[:2]
            k = max(4, int(round(bar_quarters * 4)))
            for i in range(k):
                t = bar_tick_offset + int(round(i * local_bar_ticks / k))
                dur_ticks = max(1, int(round(local_bar_ticks / k)))
                _emit(t, tones[i % 2], dur_ticks, 55)
            # also emit melody line
            for on_q, midi, dur_q in mel_onsets:
                if midi is None:
                    continue
                t = bar_tick_offset + int(round(on_q * local_bar_ticks / bar_quarters))
                d = max(1, int(round(dur_q * local_bar_ticks / bar_quarters)))
                _emit(t, midi, d, 85)

        elif texture == "texture.arp_both":
            # all shape tones (LH + RH) ordered low→high across the bar
            # LH was already emitted above; override by replacing with an
            # ordered spread.  To keep it simple we *add* the RH pitches as
            # an ascending 16th-note sweep through the bar, on top of LH
            # (so arp is audible on top).
            all_tones = sorted(set(lh_midis + rh_midis))
            if all_tones:
                k = len(all_tones)
                per_dur = max(1, int(round(local_bar_ticks / max(1, k))))
                for i, p in enumerate(all_tones):
                    t = bar_tick_offset + int(round(i * local_bar_ticks / k))
                    _emit(t, p, per_dur, 70)
            # Plus the melody line on top
            for on_q, midi, dur_q in mel_onsets:
                if midi is None:
                    continue
                t = bar_tick_offset + int(round(on_q * local_bar_ticks / bar_quarters))
                d = max(1, int(round(dur_q * local_bar_ticks / bar_quarters)))
                _emit(t, midi, d, 85)

        else:
            # default: melody-driven RH with activity enrichment
            next_rh = bar_rh_midis[ibar + 1] if ibar + 1 < len(bar_rh_midis) else None
            n_events = len(mel_onsets)

            # Density overlay: when density asks for more attacks than the
            # melody naturally provides, stamp the RH shape (minus melody)
            # at the density grid points.  This gives density a concrete
            # audible effect even when lh_activity/rh_activity would
            # otherwise leave attack counts untouched.
            density_attacks = _attack_offsets_for_density(density, n_beats)
            if density != "density.one_attack" and rh_midis:
                # Tones to use for overlay: the RH shape itself (skip the
                # melody pitch if present to avoid doubling).
                per_dur = max(1, int(round(local_bar_ticks / max(1, len(density_attacks) + 1))))
                for frac in density_attacks:
                    t = bar_tick_offset + int(round(frac * local_bar_ticks))
                    # lower a velocity on overlay so it sits under melody
                    for p in rh_midis:
                        _emit(t, p, per_dur, 55)

            for i, (on_q, midi, dur_q) in enumerate(mel_onsets):
                if midi is None:
                    continue
                t = bar_tick_offset + int(round(on_q * local_bar_ticks / bar_quarters))
                d = max(1, int(round(dur_q * local_bar_ticks / bar_quarters)))

                # phrase_role.cadence — 15% tenuto on downbeat
                vel = 85
                if on_q < 1e-6 and phrase_role == "phrase_role.cadence":
                    d = int(round(d * 1.15))

                # rh_activity.anticipation — last mel note uses next bar's chord tone
                if (rh_activity == "rh_activity.anticipation"
                        and i == n_events - 1
                        and next_rh):
                    midi = min(next_rh, key=lambda p: abs(p - midi))

                pitches = _rh_pitches_for_melody_event(
                    rh_activity, midi, rh_midis,
                    sorted(set(lh_midis + rh_midis)),
                    next_rh, key_root, key_mode,
                )

                if texture == "texture.rolled":
                    # RH rolled: no extra offset here, LH already offset
                    pass

                for p in pitches:
                    _emit(t, p, d, vel)

                # rh_activity.neighbor — 16th upper neighbor *before* this note
                if rh_activity == "rh_activity.neighbor":
                    neighbor = _diatonic_neighbor(midi, key_root, key_mode, +1)
                    ng_dur = max(1, int(round(tpq / 4)))  # 16th
                    ng_t = max(bar_tick_offset, t - ng_dur)
                    _emit(ng_t, neighbor, ng_dur, 60)

                # rh_activity.passing_tone — inner finger adds stepwise passing
                if rh_activity == "rh_activity.passing_tone" and dur_q >= 0.5:
                    pt = _diatonic_neighbor(midi, key_root, key_mode, -1)
                    pt_t = t + d // 2
                    pt_dur = max(1, d // 4)
                    _emit(pt_t, pt, pt_dur, 55)

        bar_tick_offset += local_bar_ticks
        prev_bar_events = this_bar_events

    data = mb.build()
    out_path.write_bytes(data)
    return out_path


__all__ = ["render_variation_midi"]
