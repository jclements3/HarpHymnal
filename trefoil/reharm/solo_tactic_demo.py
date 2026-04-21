"""Render a SATB baseline with ONE tactic applied to ONE spotlight bar.

Pedagogical testing rig — pairs with ``satb_baseline.py``.  The listener
hears the hymn as-sung, with a single audible manifestation of one tactic
in one clearly-identifiable bar, so they can train their ear on what each
tactic sounds like before we integrate many tactics at once.

The rendering of each tactic in the spotlight bar is deliberately concrete
and opinionated — it is NOT the same as how ``render_midi.py`` would render
a full selector-picked variation. A "solo demo" is a simplified audition
aimed at a single didactic effect:

* ``shape.*``            : ADD the named LH voicing under SATB in the bar.
* ``register.*``         : shift LH voices per rule (down_oct/up_oct/etc).
* ``lh_activity.*``      : re-shape the LH rhythm for the bar.
* ``rh_activity.*``      : enrich the melody (top voice).
* ``texture.*``          : coordinate hands (block/staggered/arp/rolled/
  bisbigliando/single_line).
* ``density.*``          : attack-count shaping (one_attack, per_beat, etc).
* ``phrase_role.*``      : role-specific micro-treatment (cadence tenuto,
  release stretch, opening clean entrance, …).
* ``connect_from.*``     : entry character into spotlight bar.
* ``connect_to.*``       : PRIOR bar telegraphs the change.
* ``lever.*``            : add an audible chromatic note (skip if doesn't fit).
* ``range.*``            : move the spotlight bar's pitch band.
* ``substitution.*``     : swap the bar's chord per rule.

All tactics not classified above emit the plain baseline for that bar.
Every demo clamps MIDI to 24..103 and dedupes (tick, pitch) to avoid
Magenta-player phantom envelopes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from trefoil.reharm.render_midi import _MidiBuilder, _deg_oct_to_midi
from trefoil.reharm.satb_baseline import (
    _pitch_to_midi,
    bar_tick_windows,
    build_baseline_events,
)


_ROOT = Path(__file__).resolve().parents[2]

_PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


# --------------------------------------------------------------------------- #
# Shape lookup                                                                #
# --------------------------------------------------------------------------- #

_SHAPES_CACHE: Optional[list[dict]] = None


def _shapes() -> list[dict]:
    global _SHAPES_CACHE
    if _SHAPES_CACHE is None:
        _SHAPES_CACHE = json.loads(
            (_ROOT / "data" / "reharm" / "shape_library.json").read_text()
        )["shapes"]
    return _SHAPES_CACHE


def _pick_shape(tactic_id: str, chord_numeral: str) -> Optional[dict]:
    """Pick a non-alias shape that supports ``tactic_id`` for the given numeral."""
    for s in _shapes():
        if s.get("is_alias"):
            continue
        ch = s.get("chord") or {}
        if (ch.get("numeral") or "").split("[")[0] != chord_numeral:
            continue
        if tactic_id in (s.get("supports") or []):
            return s
    # fallback: any numeral
    for s in _shapes():
        if s.get("is_alias"):
            continue
        if tactic_id in (s.get("supports") or []):
            return s
    return None


# --------------------------------------------------------------------------- #
# Hymn data helpers                                                           #
# --------------------------------------------------------------------------- #

def _tempo_bpm(hymn_json: dict) -> float:
    t = hymn_json.get("tempo") or {}
    v = t.get("value")
    try:
        bpm = float(v) if v is not None else 72.0
    except (TypeError, ValueError):
        bpm = 72.0
    unit = t.get("unit") or 4
    try:
        unit = int(unit)
    except (TypeError, ValueError):
        unit = 4
    return bpm * (unit / 4.0)


def _meter(hymn_json: dict) -> tuple[int, int]:
    m = hymn_json.get("meter") or {}
    return int(m.get("beats") or 4), int(m.get("unit") or 4)


def _load_legacy_beats(hymn_slug: str) -> list[dict]:
    legacy_dir = _ROOT / "legacy" / "hymnal_export"

    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

    target = _norm(hymn_slug)
    for p in sorted(legacy_dir.glob("*.json")):
        if _norm(p.stem) == target:
            return json.loads(p.read_text()).get("beats") or []
    raise FileNotFoundError(f"no legacy export for slug {hymn_slug!r}")


def _load_tactics() -> dict:
    return json.loads((_ROOT / "data" / "reharm" / "tactics.json").read_text())


# --------------------------------------------------------------------------- #
# Voice math                                                                  #
# --------------------------------------------------------------------------- #

def _clamp(midi: int, lo: int = 24, hi: int = 103) -> int:
    while midi > hi:
        midi -= 12
    while midi < lo:
        midi += 12
    return midi


def _beat_midis(beat: dict) -> dict[str, Optional[int]]:
    return {v: _pitch_to_midi(beat.get(v)) for v in "SATB"}


# --------------------------------------------------------------------------- #
# Diatonic neighbor helper (scale-degree math)                                #
# --------------------------------------------------------------------------- #

_MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
_MINOR_STEPS = [0, 2, 3, 5, 7, 8, 10]


def _diatonic_step(midi: int, key_root: str, mode: str, direction: int) -> int:
    steps = _MINOR_STEPS if (mode or "").startswith("m") else _MAJOR_STEPS
    tonic_pc = _PITCH_CLASS.get((key_root or "C")[0].upper(), 0)
    for ch in (key_root or "C")[1:]:
        if ch == "#":
            tonic_pc = (tonic_pc + 1) % 12
        elif ch in ("b", "-"):
            tonic_pc = (tonic_pc - 1) % 12
    rel = (midi - tonic_pc) % 12
    anchor = midi - rel
    if rel in steps:
        idx = steps.index(rel)
    else:
        below = [s for s in steps if s <= rel]
        idx = steps.index(below[-1]) if below else 0
    new_idx = idx + direction
    octv = 0
    if new_idx < 0:
        new_idx += 7
        octv = -1
    elif new_idx >= 7:
        new_idx -= 7
        octv = 1
    return anchor + 12 * octv + steps[new_idx]


# --------------------------------------------------------------------------- #
# Chord tone lookup for substitution.diatonic                                 #
# --------------------------------------------------------------------------- #

# For G major (our only test hymn) we just hard-code the vi chord tones.
# Extending to other keys is a straightforward diatonic-triad walk but out
# of scope for the v1 audition rig.
def _vi_chord_pitches(key_root: str, mode: str) -> list[int]:
    tonic_pc = _PITCH_CLASS.get((key_root or "C")[0].upper(), 0)
    for ch in (key_root or "C")[1:]:
        if ch == "#":
            tonic_pc = (tonic_pc + 1) % 12
        elif ch in ("b", "-"):
            tonic_pc = (tonic_pc - 1) % 12
    # vi in major = tonic + 9 semitones (e.g. G→E), triad is (vi, i, iii of major)
    # For G major: E minor triad = E, G, B
    vi_pc = (tonic_pc + 9) % 12
    triad_pcs = [vi_pc, (vi_pc + 3) % 12, (vi_pc + 7) % 12]
    # Place in 3rd octave (MIDI ~48..60)
    out = []
    for pc in triad_pcs:
        # pick midi in [48, 60)
        m = 48 + ((pc - 48) % 12)
        out.append(m)
    return sorted(out)


# --------------------------------------------------------------------------- #
# Main rendering                                                              #
# --------------------------------------------------------------------------- #

def _emit_bar_baseline(mb: _MidiBuilder, beats: list[dict], tpq: int,
                       bar_start_tick: int, beat_quarters: float,
                       emitted: set[tuple[int, int]]) -> None:
    """Emit a straight SATB block-chord baseline for the given beats."""
    for i, b in enumerate(beats):
        tick = bar_start_tick + int(round(i * beat_quarters * tpq))
        dur_ticks = max(1, int(round(beat_quarters * tpq)))
        midis = _beat_midis(b)
        for voice in "SATB":
            midi = midis[voice]
            if midi is None:
                continue
            midi = _clamp(midi)
            key = (tick, midi)
            if key in emitted:
                continue
            emitted.add(key)
            vel = 85 if voice == "S" else (75 if voice == "B" else 70)
            mb.note(tick, midi, dur_ticks, vel)


def _apply_tactic_to_bar(
    mb: _MidiBuilder,
    tactic_id: str,
    bar_beats: list[dict],          # beats of the spotlight bar
    prev_bar_beats: Optional[list[dict]],  # beats of the bar before (for connect_from / pedal)
    next_bar_beats: Optional[list[dict]],  # beats of the bar after (for connect_to, anticipation)
    tpq: int,
    bar_start_tick: int,
    beat_quarters: float,
    bpm: float,
    key_root: str,
    key_mode: str,
    chord_numeral: str,
    emitted: set[tuple[int, int]],
) -> str:
    """Render the spotlight bar with ``tactic_id`` applied. Returns a human
    ambiguity note or ``""`` if the tactic has a clear realization."""
    dim = tactic_id.split(".", 1)[0]
    bar_ticks = int(round(beat_quarters * tpq * len(bar_beats)))

    def emit(tick: int, midi: int, dur: int, vel: int = 75) -> None:
        midi = _clamp(midi)
        key = (tick, midi)
        if key in emitted:
            return
        emitted.add(key)
        mb.note(tick, midi, dur, vel)

    def emit_baseline_voices(voices_to_skip: set[str] = frozenset(),
                              voices_only: Optional[set[str]] = None) -> None:
        for i, b in enumerate(bar_beats):
            tick = bar_start_tick + int(round(i * beat_quarters * tpq))
            dur_ticks = max(1, int(round(beat_quarters * tpq)))
            midis = _beat_midis(b)
            for voice in "SATB":
                if voice in voices_to_skip:
                    continue
                if voices_only is not None and voice not in voices_only:
                    continue
                midi = midis[voice]
                if midi is None:
                    continue
                vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                emit(tick, midi, dur_ticks, vel)

    # --------------- shape.* ---------------
    if dim == "shape":
        if tactic_id == "shape.no_lh":
            # Drop bass+tenor in spotlight bar — melody + alto only.
            emit_baseline_voices(voices_only={"S", "A"})
            return ""
        # ADD the named LH voicing under SATB.
        shape = _pick_shape(tactic_id, chord_numeral)
        emit_baseline_voices()
        if not shape:
            return f"no library shape supporting {tactic_id} for {chord_numeral}"
        voicing = (shape.get("lh") or []) + (shape.get("rh") or [])
        for pair in voicing:
            try:
                deg, octv = int(pair[0]), int(pair[1])
            except (TypeError, ValueError, IndexError):
                continue
            midi = _deg_oct_to_midi(deg, octv, key_root, key_mode)
            # Place LH voicing in lower register (drop octave if overlaps SATB)
            # Shape lib is tonic-anchored; we just clamp into harp range.
            emit(bar_start_tick, midi, bar_ticks, 65)
        return ""

    # --------------- register.* ---------------
    if dim == "register":
        if tactic_id == "register.same":
            emit_baseline_voices()
            return ""
        # Apply per-rule shift to LH voices (T + B).
        def shift_tb(b_beats):
            for i, b in enumerate(b_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                midis = _beat_midis(b)
                for voice in "SATB":
                    midi = midis[voice]
                    if midi is None:
                        continue
                    if voice == "B":
                        if tactic_id == "register.down_oct":
                            midi -= 12
                        elif tactic_id == "register.up_oct":
                            midi += 12
                        elif tactic_id == "register.sub_bass":
                            midi -= 24
                        elif tactic_id == "register.wide":
                            midi -= 12
                        elif tactic_id == "register.compressed":
                            midi += 12
                    elif voice == "T":
                        if tactic_id == "register.down_oct":
                            midi -= 12
                        elif tactic_id == "register.up_oct":
                            midi += 12
                        elif tactic_id == "register.sub_bass":
                            pass
                        elif tactic_id == "register.wide":
                            pass  # tenor stays to keep middle empty-ish
                        elif tactic_id == "register.compressed":
                            midi += 12
                    elif voice == "S":
                        if tactic_id == "register.wide":
                            midi += 12
                    vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                    emit(tick, midi, dur_ticks, vel)
        shift_tb(bar_beats)
        return ""

    # --------------- lh_activity.* ---------------
    if dim == "lh_activity":
        # keep SA (melody+alto); reshape B (bass) + T (tenor) per rule.
        emit_baseline_voices(voices_only={"S", "A"})
        # Gather LH pitches (T+B) across the bar — use bar downbeat as the
        # canonical LH chord, plus the per-beat pitches when they change.
        lh_per_beat = []
        for b in bar_beats:
            m = _beat_midis(b)
            lh_per_beat.append([p for p in (m.get("T"), m.get("B")) if p is not None])
        lh_pitches = lh_per_beat[0] if lh_per_beat and lh_per_beat[0] else [48, 60]
        n_beats = len(bar_beats) or 1
        beat_ticks = int(round(beat_quarters * tpq))

        if tactic_id == "lh_activity.sustain":
            for p in lh_pitches:
                emit(bar_start_tick, p, bar_ticks, 70)
        elif tactic_id == "lh_activity.strike_and_ring":
            for p in lh_pitches:
                emit(bar_start_tick, p, bar_ticks, 78)
        elif tactic_id == "lh_activity.none":
            pass
        elif tactic_id == "lh_activity.arp_up":
            k = max(2, 2 * n_beats)
            tones = sorted(lh_pitches) or [48]
            for i in range(k):
                t = bar_start_tick + int(round(i * bar_ticks / k))
                dur = max(1, bar_ticks // k)
                emit(t, tones[i % len(tones)], dur, 70)
        elif tactic_id == "lh_activity.arp_down":
            k = max(2, 2 * n_beats)
            tones = sorted(lh_pitches, reverse=True) or [60]
            for i in range(k):
                t = bar_start_tick + int(round(i * bar_ticks / k))
                dur = max(1, bar_ticks // k)
                emit(t, tones[i % len(tones)], dur, 70)
        elif tactic_id == "lh_activity.bass_chord_chord":
            # beat 1 = bass; beats 2..n = upper LH (tenor)
            t0 = bar_start_tick
            bass = min(lh_pitches) if lh_pitches else 36
            emit(t0, bass, beat_ticks, 82)
            uppers = [p for p in lh_pitches if p != bass] or lh_pitches
            for i in range(1, n_beats):
                t = bar_start_tick + i * beat_ticks
                for p in uppers:
                    emit(t, p, beat_ticks, 65)
        elif tactic_id == "lh_activity.chord_offbeat":
            for i in range(n_beats):
                t = bar_start_tick + int(round((i + 0.5) * beat_ticks))
                for p in lh_pitches:
                    emit(t, p, beat_ticks // 2, 65)
        elif tactic_id == "lh_activity.tremolo":
            k = max(4, 4 * n_beats)
            tones = sorted(lh_pitches) or [48]
            if len(tones) < 2:
                tones = [tones[0], tones[0] + 4]
            for i in range(k):
                t = bar_start_tick + int(round(i * bar_ticks / k))
                dur = max(1, bar_ticks // k)
                emit(t, tones[i % 2], dur, 55)
        elif tactic_id == "lh_activity.partial_silence":
            # hit beat 2 only (3/4 meter); for 4/4 this'd be beat 2+4
            if n_beats == 3:
                t = bar_start_tick + beat_ticks
                for p in lh_pitches:
                    emit(t, p, beat_ticks, 70)
            else:
                for bi in (1, 3):
                    if bi < n_beats:
                        t = bar_start_tick + bi * beat_ticks
                        for p in lh_pitches:
                            emit(t, p, beat_ticks, 70)
        elif tactic_id == "lh_activity.low_bass_grab":
            # grace note ~80 ms before downbeat, octave below bass
            bass = min(lh_pitches) if lh_pitches else 36
            grace_pitch = bass - 12
            grace_ticks = int(round(tpq * bpm * 0.08 / 60))
            gt = max(0, bar_start_tick - grace_ticks)
            emit(gt, grace_pitch, max(1, grace_ticks), 78)
            # then normal LH strum on downbeat, sustained
            for p in lh_pitches:
                emit(bar_start_tick, p, bar_ticks, 78)
        elif tactic_id == "lh_activity.countermelody":
            tones = sorted(lh_pitches) or [48, 55]
            if len(tones) < 2:
                tones = [tones[0], tones[0] + 4]
            # 4 stepwise notes across bar (up then down)
            walk = [tones[0], tones[-1], tones[0] + 2, tones[-1] - 1]
            k = 4
            dur = max(1, bar_ticks // k)
            for i, p in enumerate(walk):
                t = bar_start_tick + int(round(i * bar_ticks / k))
                emit(t, p, dur, 68)
        else:
            # unknown — fall back to baseline LH
            emit_baseline_voices(voices_only={"T", "B"})
        return ""

    # --------------- rh_activity.* ---------------
    if dim == "rh_activity":
        emit_baseline_voices(voices_to_skip={"S"})  # keep ATB, reshape S
        for i, b in enumerate(bar_beats):
            tick = bar_start_tick + int(round(i * beat_quarters * tpq))
            dur_ticks = max(1, int(round(beat_quarters * tpq)))
            midis = _beat_midis(b)
            s_midi = midis.get("S")
            if s_midi is None:
                continue
            if tactic_id == "rh_activity.melody_alone":
                emit(tick, s_midi, dur_ticks, 88)
            elif tactic_id == "rh_activity.melody_plus_1":
                # add alto underneath
                a = midis.get("A")
                if a:
                    emit(tick, a, dur_ticks, 70)
                emit(tick, s_midi, dur_ticks, 88)
            elif tactic_id == "rh_activity.melody_plus_2":
                for voice in ("A", "T"):
                    m = midis.get(voice)
                    if m:
                        emit(tick, m, dur_ticks, 68)
                emit(tick, s_midi, dur_ticks, 88)
            elif tactic_id == "rh_activity.melody_oct":
                emit(tick, s_midi - 12, dur_ticks, 75)
                emit(tick, s_midi, dur_ticks, 88)
            elif tactic_id == "rh_activity.neighbor":
                # upper neighbor 16th before the beat
                nb = _diatonic_step(s_midi, key_root, key_mode, +1)
                ng_dur = max(1, tpq // 4)
                gt = max(bar_start_tick, tick - ng_dur)
                emit(gt, nb, ng_dur, 60)
                emit(tick, s_midi, dur_ticks, 88)
            elif tactic_id == "rh_activity.anticipation":
                # last beat borrows next bar's downbeat pitch
                if i == len(bar_beats) - 1 and next_bar_beats:
                    next_s = _pitch_to_midi(next_bar_beats[0].get("S"))
                    if next_s is not None:
                        emit(tick, next_s, dur_ticks, 88)
                        continue
                emit(tick, s_midi, dur_ticks, 88)
            elif tactic_id == "rh_activity.passing_tone":
                emit(tick, s_midi, dur_ticks, 88)
                # passing tone mid-beat (diatonic step below)
                pt = _diatonic_step(s_midi, key_root, key_mode, -1)
                pt_t = tick + dur_ticks // 2
                pt_dur = max(1, dur_ticks // 4)
                emit(pt_t, pt, pt_dur, 55)
            else:
                emit(tick, s_midi, dur_ticks, 88)
        return ""

    # --------------- texture.* ---------------
    if dim == "texture":
        midis_flat = []
        for b in bar_beats:
            for v in "SATB":
                m = _pitch_to_midi(b.get(v))
                if m is not None:
                    midis_flat.append((v, m))
        # downbeat pitches
        db_midis = _beat_midis(bar_beats[0]) if bar_beats else {}

        if tactic_id == "texture.block":
            # hands together at each beat — default block (same as baseline)
            emit_baseline_voices()
            return ""
        if tactic_id == "texture.single_line":
            # melody only
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                s = _pitch_to_midi(b.get("S"))
                if s is not None:
                    emit(tick, s, dur_ticks, 90)
            return ""
        if tactic_id == "texture.staggered":
            # RH on beat, LH on half-beat offset
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                midis = _beat_midis(b)
                for voice in ("S", "A"):
                    if midis.get(voice) is not None:
                        emit(tick, midis[voice], dur_ticks, 80)
                lh_tick = tick + int(round(beat_quarters * tpq / 2))
                for voice in ("T", "B"):
                    if midis.get(voice) is not None:
                        emit(lh_tick, midis[voice], dur_ticks, 70)
            return ""
        if tactic_id == "texture.arp_both":
            # spread all downbeat pitches ascending across the bar
            tones = sorted({m for v, m in midis_flat if db_midis.get(v) is not None
                             and m == db_midis[v]}) or sorted({m for v, m in midis_flat})
            if not tones:
                return ""
            k = len(tones)
            dur = max(1, bar_ticks // k)
            for i, p in enumerate(tones):
                t = bar_start_tick + int(round(i * bar_ticks / k))
                emit(t, p, dur, 70)
            # melody on top for clarity
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                s = _pitch_to_midi(b.get("S"))
                if s is not None:
                    emit(tick, s, dur_ticks, 88)
            return ""
        if tactic_id == "texture.rolled":
            # ~40 ms stagger between B→T→A→S at each beat
            roll_ticks = max(1, int(round(tpq * bpm * 0.04 / 60)))
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                midis = _beat_midis(b)
                for k, voice in enumerate(("B", "T", "A", "S")):
                    m = midis.get(voice)
                    if m is None:
                        continue
                    emit(tick + k * roll_ticks, m, dur_ticks, 78 if voice == "S" else 70)
            return ""
        if tactic_id == "texture.bisbigliando":
            # rapid alternation between two RH tones — cap at 4 attacks per quarter
            rh_pitches = []
            db = _beat_midis(bar_beats[0]) if bar_beats else {}
            for voice in ("A", "S"):
                m = db.get(voice)
                if m is not None:
                    rh_pitches.append(m)
            if len(rh_pitches) < 2:
                rh_pitches = [60, 64]
            # attacks per quarter = 4
            attacks_per_quarter = 4
            total_attacks = int(round(beat_quarters * len(bar_beats) * attacks_per_quarter))
            dur = max(1, bar_ticks // total_attacks) if total_attacks else bar_ticks
            for i in range(total_attacks):
                t = bar_start_tick + int(round(i * bar_ticks / total_attacks))
                emit(t, rh_pitches[i % 2], dur, 55)
            # LH sustained
            for voice in ("T", "B"):
                m = db.get(voice)
                if m is not None:
                    emit(bar_start_tick, m, bar_ticks, 70)
            return ""

    # --------------- density.* ---------------
    if dim == "density":
        midis = _beat_midis(bar_beats[0]) if bar_beats else {}
        all_pitches = [midis[v] for v in "SATB" if midis.get(v) is not None]
        n_beats = len(bar_beats) or 1
        beat_ticks = int(round(beat_quarters * tpq))

        def stamp(fracs: list[float], vel: int = 70) -> None:
            for frac in fracs:
                t = bar_start_tick + int(round(frac * bar_ticks))
                dur = max(1, int(round(bar_ticks / max(1, len(fracs)))))
                for p in all_pitches:
                    emit(t, p, dur, vel)

        if tactic_id == "density.one_attack":
            for p in all_pitches:
                emit(bar_start_tick, p, bar_ticks, 80)
        elif tactic_id == "density.per_beat":
            # same as baseline; render it.
            emit_baseline_voices()
        elif tactic_id == "density.two_per_beat":
            fracs = [i / (2 * n_beats) for i in range(2 * n_beats)]
            stamp(fracs, vel=65)
            # plus melody line so rhythm is audible
            emit_baseline_voices(voices_only={"S"})
        elif tactic_id == "density.syncopated":
            fracs = [(i + 0.5) / n_beats for i in range(n_beats)]
            stamp(fracs, vel=70)
            emit_baseline_voices(voices_only={"S"})
        elif tactic_id == "density.front_loaded":
            if n_beats == 1:
                fracs = [0.0, 0.25]
            else:
                fracs = [i / (2 * n_beats) for i in range(n_beats)]
            stamp(fracs, vel=75)
            emit_baseline_voices(voices_only={"S"})
        elif tactic_id == "density.back_loaded":
            if n_beats == 1:
                fracs = [0.5, 0.75]
            else:
                fracs = [0.5 + i / (2 * n_beats) for i in range(n_beats)]
            stamp(fracs, vel=75)
            emit_baseline_voices(voices_only={"S"})
        return ""

    # --------------- phrase_role.* ---------------
    if dim == "phrase_role":
        if tactic_id == "phrase_role.cadence":
            # 15% tenuto on downbeat — lengthen beat 1 events slightly
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                base_dur = int(round(beat_quarters * tpq))
                dur_ticks = int(round(base_dur * (1.15 if i == 0 else 1.0)))
                midis = _beat_midis(b)
                for voice in "SATB":
                    m = midis.get(voice)
                    if m is not None:
                        vel = 95 if (voice == "S" and i == 0) else (85 if voice == "S" else 70)
                        emit(tick, m, dur_ticks, vel)
            return ""
        if tactic_id == "phrase_role.cadence_approach":
            # velocity ramp across the bar
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                ramp = 70 + int(round(20 * (i / max(1, len(bar_beats) - 1))))
                midis = _beat_midis(b)
                for voice in "SATB":
                    m = midis.get(voice)
                    if m is not None:
                        emit(tick, m, dur_ticks, ramp)
            return ""
        if tactic_id == "phrase_role.release":
            # 10% bar stretch
            stretched_beat_q = beat_quarters * 1.10
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * stretched_beat_q * tpq))
                dur_ticks = max(1, int(round(stretched_beat_q * tpq)))
                midis = _beat_midis(b)
                for voice in "SATB":
                    m = midis.get(voice)
                    if m is not None:
                        vel = 75 if voice == "S" else 65
                        emit(tick, m, dur_ticks, vel)
            return ""
        if tactic_id == "phrase_role.opening":
            # clean entrance — slightly softer beat-1 release, no grace notes
            emit_baseline_voices()
            return ""
        # phrase_role.middle = control
        emit_baseline_voices()
        return ""

    # --------------- connect_from.* ---------------
    if dim == "connect_from":
        if tactic_id == "connect_from.sustained" and prev_bar_beats:
            # tie pitches from end of prior bar into beat 1 (reattack only
            # those that change)
            prev_last = _beat_midis(prev_bar_beats[-1])
            midis = _beat_midis(bar_beats[0]) if bar_beats else {}
            # tie (skip re-attack) for voices that match
            tied_voices = {v for v in "SATB"
                           if prev_last.get(v) is not None and prev_last.get(v) == midis.get(v)}
            # emit beat 1 with tied voices' pitches sustained from prior bar:
            # We can't literally tie across files, so we just *omit* re-attack
            # for tied voices at beat 1 — they will have been struck by prior
            # bar's emission already, and since harp rings, the listener still
            # hears them.
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                bm = _beat_midis(b)
                for voice in "SATB":
                    m = bm.get(voice)
                    if m is None:
                        continue
                    if i == 0 and voice in tied_voices:
                        continue
                    vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                    emit(tick, m, dur_ticks, vel)
            return ""
        if tactic_id == "connect_from.released":
            # fresh attack on every voice at beat 1 (velocity bump)
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                bm = _beat_midis(b)
                for voice in "SATB":
                    m = bm.get(voice)
                    if m is None:
                        continue
                    base = 85 if voice == "S" else (75 if voice == "B" else 70)
                    vel = base + (10 if i == 0 else 0)
                    emit(tick, m, dur_ticks, vel)
            return ""
        if tactic_id == "connect_from.same":
            # repeat prior bar's shape — use prior bar's pitches for spotlight
            # beats (just stamp prev bar's pitches across).
            if prev_bar_beats:
                for i, b in enumerate(bar_beats):
                    src = prev_bar_beats[i] if i < len(prev_bar_beats) else prev_bar_beats[-1]
                    tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                    dur_ticks = max(1, int(round(beat_quarters * tpq)))
                    bm = _beat_midis(src)
                    for voice in "SATB":
                        m = bm.get(voice)
                        if m is not None:
                            vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                            emit(tick, m, dur_ticks, vel)
                return ""
        if tactic_id == "connect_from.same_inv":
            # same pitch-classes, bass moves to chord-tone above original
            emit_baseline_voices(voices_to_skip={"B"})
            # Re-voice bass up a third (diatonic step twice)
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                bm = _beat_midis(b)
                bass = bm.get("B")
                if bass is not None:
                    new_bass = _diatonic_step(
                        _diatonic_step(bass, key_root, key_mode, +1),
                        key_root, key_mode, +1
                    )
                    emit(tick, new_bass, dur_ticks, 75)
            return ""
        # step / third / larger — render as released with noted ambiguity
        emit_baseline_voices()
        return f"{tactic_id}: rendered as released (single-bar isolation can't convey shape-shift interval)"

    # --------------- connect_to.* ---------------
    # These modify the *prior* bar, not the spotlight bar. In solo-demo
    # isolation we render the spotlight bar normally and apply the effect
    # BEFORE it — handled in render_solo_tactic via prior-bar-hook.
    if dim == "connect_to":
        emit_baseline_voices()
        # Effects are applied to prior bar by the outer renderer; see
        # _apply_connect_to_to_prev.
        return ""

    # --------------- lever.* ---------------
    if dim == "lever":
        # Amazing Grace in G major — insert an F natural in the spotlight
        # bar (F is raised to F# by G-major levers; "flipping" it back gives
        # an F natural, an audible chromatic). We add it as a passing tone
        # against the tenor/alto in the middle of beat 2.
        emit_baseline_voices()
        if tactic_id == "lever.no_flip":
            return ""
        # Beat 2 has room in all 3 spotlight bars we use.
        if len(bar_beats) >= 2:
            beat2_tick = bar_start_tick + int(round(1 * beat_quarters * tpq))
            dur = max(1, int(round(beat_quarters * tpq * 0.4)))
            # F natural in octave 4 = MIDI 65
            emit(beat2_tick + dur // 2, 65, dur, 70)
        if tactic_id == "lever.prepare_next":
            return (
                "lever.prepare_next: a single-bar demo can only hint; listen "
                "for the F-natural leaking in over the I chord"
            )
        return ""

    # --------------- range.* ---------------
    if dim == "range":
        if tactic_id == "range.stay":
            emit_baseline_voices()
            return ""
        shift = 0
        shift_lh = 0
        shift_rh = 0
        if tactic_id == "range.migrate_up":
            shift = +12
        elif tactic_id == "range.migrate_down":
            shift = -12
        elif tactic_id == "range.split":
            shift_lh = -12
            shift_rh = +12
        elif tactic_id == "range.extreme":
            shift_lh = -24  # LH to bottom of harp
        for i, b in enumerate(bar_beats):
            tick = bar_start_tick + int(round(i * beat_quarters * tpq))
            dur_ticks = max(1, int(round(beat_quarters * tpq)))
            bm = _beat_midis(b)
            for voice in "SATB":
                m = bm.get(voice)
                if m is None:
                    continue
                if voice in ("T", "B"):
                    m += shift or shift_lh
                else:
                    m += shift or shift_rh
                vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                emit(tick, m, dur_ticks, vel)
        return ""

    # --------------- substitution.* ---------------
    if dim == "substitution":
        if tactic_id == "substitution.as_written":
            emit_baseline_voices()
            return ""
        if tactic_id == "substitution.diatonic":
            # vi for I: keep melody (S), replace ATB with vi-triad pitches
            emit_baseline_voices(voices_only={"S"})
            vi_pitches = _vi_chord_pitches(key_root, key_mode)
            # Place them in the middle/low register mapped to A/T/B lanes
            ordered = sorted(vi_pitches)  # low to high
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                # B lane = ordered[0] - 12
                emit(tick, ordered[0] - 12, dur_ticks, 75)
                emit(tick, ordered[0], dur_ticks, 68)  # T
                emit(tick, ordered[1], dur_ticks, 68)  # A
            return ""
        if tactic_id == "substitution.inversion":
            # bass moves to 3rd (diatonic step up twice from root)
            emit_baseline_voices(voices_to_skip={"B"})
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                bm = _beat_midis(b)
                bass = bm.get("B")
                if bass is not None:
                    new_bass = _diatonic_step(
                        _diatonic_step(bass, key_root, key_mode, +1),
                        key_root, key_mode, +1
                    )
                    emit(tick, new_bass, dur_ticks, 75)
            return ""
        if tactic_id == "substitution.pedal":
            # hold prior bar's chord throughout
            emit_baseline_voices(voices_only={"S"})  # keep melody fresh
            if prev_bar_beats:
                prev_db = _beat_midis(prev_bar_beats[0])
                for voice in ("A", "T", "B"):
                    m = prev_db.get(voice)
                    if m is not None:
                        vel = 75 if voice == "B" else 68
                        emit(bar_start_tick, m, int(round(beat_quarters * tpq * len(bar_beats))), vel)
            return ""
        if tactic_id == "substitution.sus":
            # 3rd → 4th in the alto line (raise by diatonic step)
            emit_baseline_voices(voices_to_skip={"A"})
            for i, b in enumerate(bar_beats):
                tick = bar_start_tick + int(round(i * beat_quarters * tpq))
                dur_ticks = max(1, int(round(beat_quarters * tpq)))
                bm = _beat_midis(b)
                alto = bm.get("A")
                if alto is not None:
                    new_alto = _diatonic_step(alto, key_root, key_mode, +1)
                    emit(tick, new_alto, dur_ticks, 70)
            return ""
        if tactic_id == "substitution.delay_change":
            # keep prior chord for whole bar (like pedal but including melody
            # anchor: bass ATB from prior)
            if prev_bar_beats:
                prev_db = _beat_midis(prev_bar_beats[0])
                for voice in "SATB":
                    m = prev_db.get(voice)
                    if m is not None:
                        vel = 85 if voice == "S" else (75 if voice == "B" else 68)
                        emit(bar_start_tick,
                             m,
                             int(round(beat_quarters * tpq * len(bar_beats))),
                             vel)
                return ""
            emit_baseline_voices()
            return ""

    # Default — just emit baseline.
    emit_baseline_voices()
    return ""


def _apply_connect_to_to_prev(
    mb: _MidiBuilder,
    tactic_id: str,
    prev_bar_beats: list[dict],
    target_bar_beats: list[dict],
    tpq: int,
    prev_bar_start_tick: int,
    beat_quarters: float,
    emitted: set[tuple[int, int]],
) -> None:
    """For connect_to.*, the *prior* bar telegraphs the upcoming change."""
    if not prev_bar_beats:
        return
    n = len(prev_bar_beats)
    bar_ticks = int(round(n * beat_quarters * tpq))

    def emit(tick, midi, dur, vel):
        midi = _clamp(midi)
        key = (tick, midi)
        if key in emitted:
            return
        emitted.add(key)
        mb.note(tick, midi, dur, vel)

    # default: baseline prev bar
    def emit_prev_baseline():
        for i, b in enumerate(prev_bar_beats):
            tick = prev_bar_start_tick + int(round(i * beat_quarters * tpq))
            dur_ticks = max(1, int(round(beat_quarters * tpq)))
            bm = _beat_midis(b)
            for voice in "SATB":
                m = bm.get(voice)
                if m is None:
                    continue
                vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                emit(tick, m, dur_ticks, vel)

    if tactic_id == "connect_to.anticipate":
        # last beat of prev bar takes target's downbeat ATB pitches
        tgt = _beat_midis(target_bar_beats[0]) if target_bar_beats else {}
        for i, b in enumerate(prev_bar_beats):
            tick = prev_bar_start_tick + int(round(i * beat_quarters * tpq))
            dur_ticks = max(1, int(round(beat_quarters * tpq)))
            bm = _beat_midis(b)
            if i == n - 1:
                # replace ATB with target chord tones
                src = tgt
            else:
                src = bm
            for voice in "SATB":
                if voice == "S":
                    m = bm.get("S")  # keep melody
                else:
                    m = src.get(voice)
                if m is None:
                    continue
                vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                emit(tick, m, dur_ticks, vel)
        return
    if tactic_id == "connect_to.delay":
        # no special effect on prior bar — handled in spotlight bar.
        emit_prev_baseline()
        return
    if tactic_id == "connect_to.step_bass":
        # replace last-beat bass with a stepwise approach to target's bass
        tgt = _beat_midis(target_bar_beats[0]) if target_bar_beats else {}
        tgt_bass = tgt.get("B")
        for i, b in enumerate(prev_bar_beats):
            tick = prev_bar_start_tick + int(round(i * beat_quarters * tpq))
            dur_ticks = max(1, int(round(beat_quarters * tpq)))
            bm = _beat_midis(b)
            for voice in "SATB":
                m = bm.get(voice)
                if m is None:
                    continue
                if voice == "B" and i == n - 1 and tgt_bass is not None:
                    # step toward target
                    direction = +1 if tgt_bass > m else -1
                    m = m + direction
                vel = 85 if voice == "S" else (75 if voice == "B" else 70)
                emit(tick, m, dur_ticks, vel)
        return
    if tactic_id == "connect_to.common_tone":
        # emphasise a pitch shared between prev last-beat ATB and target downbeat
        tgt = _beat_midis(target_bar_beats[0]) if target_bar_beats else {}
        last = _beat_midis(prev_bar_beats[-1])
        shared = None
        for voice in "ATB":
            if last.get(voice) is not None and last.get(voice) in tgt.values():
                shared = last[voice]
                break
        emit_prev_baseline()
        if shared is not None:
            t = prev_bar_start_tick + int(round((n - 1) * beat_quarters * tpq))
            emit(t, shared, int(round(beat_quarters * tpq)), 85)
        return
    # land_down / default → baseline
    emit_prev_baseline()


def render_solo_tactic(
    hymn_slug: str,
    tactic_id: str,
    out_path: Path,
    spotlight_bar: int = 5,
) -> tuple[Path, str]:
    """Render a SATB baseline with ONE tactic applied to ONE bar.

    The non-spotlight bars come from the hymn's per-voice streams (real
    rhythms, ties, eighth notes) via ``build_baseline_events``. The
    spotlight bar's baseline events are filtered out and replaced by the
    tactic-specific rendering. For ``connect_to.*`` the *prior* bar is
    the target instead of the spotlight bar.

    Returns
    -------
    (out_path, note)
        ``note`` is a short human ambiguity / skip explanation; empty when
        the tactic renders cleanly.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    hymn_json = json.loads((_ROOT / "data" / "hymns" / f"{hymn_slug}.json").read_text())
    all_beats = _load_legacy_beats(hymn_slug)

    key = hymn_json.get("key") or {}
    key_root = key.get("root", "C")
    key_mode = key.get("mode", "major")
    beats_num, unit = _meter(hymn_json)
    beat_quarters = 4.0 / unit
    bpm = _tempo_bpm(hymn_json)
    tpq = 480

    # Beats[] is still consulted for CHORD identification in the spotlight
    # bar (i.e. "what pitches voice this chord?"), not as a rhythm source.
    bars_beats: dict[int, list[dict]] = {}
    for b in all_beats:
        bars_beats.setdefault(int(b.get("bar") or 0), []).append(b)

    # Spotlight chord numeral (from modern hymn JSON)
    hjs_bars = hymn_json.get("bars") or []
    try:
        chord_numeral = (hjs_bars[spotlight_bar - 1].get("chord") or {}).get("numeral") or "I"
    except (IndexError, AttributeError, KeyError):
        chord_numeral = "I"

    # --- Build baseline from voices[] & compute bar windows ---
    baseline_events, _ = build_baseline_events(hymn_slug, tpq=tpq)
    windows = bar_tick_windows(hymn_slug, tpq=tpq)

    dim = tactic_id.split(".", 1)[0]
    note = ""

    # Which bar gets replaced with tactic-driven events? For connect_to
    # it's the bar BEFORE the spotlight (the one that "telegraphs"); for
    # every other dimension it's the spotlight bar itself.
    if dim == "connect_to":
        replaced_bar = spotlight_bar - 1
    else:
        replaced_bar = spotlight_bar

    replaced_window = windows.get(replaced_bar)
    if replaced_window is None:
        # Unknown spotlight bar — fall back to emitting straight baseline.
        replaced_window = (0, 0)

    mb = _MidiBuilder(ticks_per_quarter=tpq, channel=0)
    mb.time_signature(0, beats_num, unit)
    mb.tempo(0, bpm)
    mb.program(0, 46)

    emitted: set[tuple[int, int]] = set()

    # Emit the voices-driven baseline EXCEPT for events whose onset falls
    # inside the replaced bar's tick window. Those get filtered out and
    # the tactic dispatch supplies the replacement.
    lo_tick, hi_tick = replaced_window
    for tick, pitch, dur_ticks, vel, _src in baseline_events:
        if lo_tick <= tick < hi_tick:
            continue
        k = (tick, pitch)
        if k in emitted:
            continue
        emitted.add(k)
        mb.note(tick, pitch, dur_ticks, vel)

    # Spotlight / connect_to prior-bar dispatch. The tactic helpers use
    # beats[] purely as chord-tone lookup tables for the replaced bar —
    # rhythm-wise they stamp their own events per tactic semantics.
    spotlight_beats = bars_beats.get(spotlight_bar, [])
    prev_beats = bars_beats.get(spotlight_bar - 1)
    next_beats = bars_beats.get(spotlight_bar + 1)

    # Bar start tick from windows (not cumulative), so pickup/anomaly bars
    # are still placed correctly.
    spotlight_start_tick = windows.get(spotlight_bar, (0, 0))[0]

    if dim == "connect_to":
        prev_start_tick = windows.get(spotlight_bar - 1, (0, 0))[0]
        _apply_connect_to_to_prev(
            mb, tactic_id, prev_beats or [], spotlight_beats,
            tpq, prev_start_tick, beat_quarters, emitted,
        )
    else:
        n = _apply_tactic_to_bar(
            mb, tactic_id, spotlight_beats, prev_beats, next_beats,
            tpq, spotlight_start_tick, beat_quarters, bpm,
            key_root, key_mode, chord_numeral, emitted,
        )
        if n:
            note = n

    out_path.write_bytes(mb.build())
    return out_path, note


__all__ = ["render_solo_tactic"]
