"""Render a hymn's four voice streams into a SATB MIDI baseline.

Part of the pedagogical testing rig (parallel track to the reharm-selector
renderer). The baseline is literally "the 4-voice chorale as written":
real rhythms (halves, quarters, eighths), real ties, four independent
voice lines. No reharmonization, no added voicings — the control file
against which every one-tactic demo is compared.

Input: ``legacy/hymnal_export/<Title>.json`` which carries a ``voices``
dict with keys ``S1V1`` (soprano), ``S1V2`` (alto), ``S2V1`` (tenor),
``S2V2`` (bass). Each voice is a list of note events with ``offset_ql``,
``duration_ql``, ``pitch``, ``is_rest``, and ``tied_next`` fields.

Tempo + meter come from ``data/hymns/<slug>.json`` (the modern pipeline's
hymn record), since the legacy JSON records them as ``None``.

Stdlib only.  Reuses ``_MidiBuilder`` from ``render_midi``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from trefoil.reharm.render_midi import _MidiBuilder


# Pitch string like "F#3" or "Bb4" or "G2" → MIDI number.
_PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_PITCH_RE = re.compile(r"^([A-Ga-g])([#b-]*)(-?\d+)$")


def _pitch_to_midi(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    m = _PITCH_RE.match(s.strip())
    if not m:
        return None
    letter, acc, octv = m.group(1), m.group(2), m.group(3)
    pc = _PITCH_CLASS[letter.upper()]
    for ch in acc:
        if ch == "#":
            pc = (pc + 1) % 12
        elif ch in ("b", "-"):
            pc = (pc - 1) % 12
    try:
        o = int(octv)
    except ValueError:
        return None
    # music21 convention: C4 = MIDI 60.
    return 12 * (o + 1) + pc


# Repo root — this file lives at trefoil/reharm/satb_baseline.py.
_ROOT = Path(__file__).resolve().parents[2]


# Voice → velocity. Soprano and bass bracket the texture; inner voices sit
# slightly behind so the top-and-bottom line is audible.
_VOICE_VEL = {"S1V1": 90, "S1V2": 75, "S2V1": 70, "S2V2": 80}
# Friendly aliases for use by other modules.
_VOICE_ROLE = {"S1V1": "S", "S1V2": "A", "S2V1": "T", "S2V2": "B"}


def _find_legacy_export(hymn_slug: str) -> Path:
    """Map slug (e.g. 'amazing_grace') → legacy/hymnal_export/*.json path."""
    legacy_dir = _ROOT / "legacy" / "hymnal_export"

    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

    target = _norm(hymn_slug)
    for p in sorted(legacy_dir.glob("*.json")):
        if _norm(p.stem) == target:
            return p
    guess = legacy_dir / ("_".join(w.capitalize() for w in hymn_slug.split("_")) + ".json")
    if guess.exists():
        return guess
    raise FileNotFoundError(f"no legacy export for slug {hymn_slug!r} in {legacy_dir}")


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


def _clamp_midi(midi: int, lo: int = 24, hi: int = 103) -> int:
    while midi > hi:
        midi -= 12
    while midi < lo:
        midi += 12
    return midi


def _voice_events_to_notes(
    voice_events: list[dict],
    vel: int,
    tpq: int = 480,
) -> list[tuple[int, int, int, int, str]]:
    """Walk one voice stream, merge ties, skip rests, clamp range.

    Returns a list of ``(tick, pitch, dur_ticks, velocity, source_voice)``.
    ``source_voice`` is left empty here — the caller fills it so dedup
    across voices knows who wrote each event.

    Ties: when an event has ``tied_next=True`` AND the next event's
    pitch matches, the next event is consumed into the current event's
    duration and no re-attack is emitted.
    """
    out: list[tuple[int, int, int, int, str]] = []
    i = 0
    n = len(voice_events)
    while i < n:
        e = voice_events[i]
        if e.get("is_rest"):
            i += 1
            continue
        midi = _pitch_to_midi(e.get("pitch"))
        if midi is None:
            i += 1
            continue
        try:
            onset_q = float(e.get("offset_ql") or 0.0)
            dur_q = float(e.get("duration_ql") or 0.0)
        except (TypeError, ValueError):
            i += 1
            continue
        total_dur_q = dur_q
        # Consume chain of tied_next events with matching pitch.
        j = i
        while (
            voice_events[j].get("tied_next")
            and j + 1 < n
            and not voice_events[j + 1].get("is_rest")
            and _pitch_to_midi(voice_events[j + 1].get("pitch")) == midi
        ):
            try:
                total_dur_q += float(voice_events[j + 1].get("duration_ql") or 0.0)
            except (TypeError, ValueError):
                pass
            j += 1
        # Advance past any consumed tied-notes (j may equal i if no ties).
        midi_clamped = _clamp_midi(midi)
        tick = int(round(onset_q * tpq))
        dur_ticks = max(1, int(round(total_dur_q * tpq)))
        out.append((tick, midi_clamped, dur_ticks, vel, ""))
        i = j + 1
    return out


def _dedup_events(
    events: list[tuple[int, int, int, int, str]],
    tick_window: int = 10,
) -> list[tuple[int, int, int, int, str]]:
    """Collapse near-simultaneous unisons across voices.

    If two events share a pitch and their ticks differ by less than
    ``tick_window`` (default 10 ticks ≈ 5 ms at 480 tpq / 120 bpm), keep
    the louder one; merge durations to the longer of the two.
    """
    # Sort by (pitch, tick) so duplicates land adjacent.
    events_sorted = sorted(events, key=lambda ev: (ev[1], ev[0]))
    kept: list[tuple[int, int, int, int, str]] = []
    for ev in events_sorted:
        tick, pitch, dur, vel, src = ev
        if kept:
            p_tick, p_pitch, p_dur, p_vel, p_src = kept[-1]
            if p_pitch == pitch and abs(tick - p_tick) < tick_window:
                new_vel = max(p_vel, vel)
                # Span the full sustain of both events.
                end = max(p_tick + p_dur, tick + dur)
                new_tick = min(p_tick, tick)
                kept[-1] = (new_tick, pitch, end - new_tick, new_vel, p_src or src)
                continue
        kept.append(ev)
    # Re-sort by tick for stable downstream behaviour.
    kept.sort(key=lambda ev: (ev[0], ev[1]))
    return kept


def build_baseline_events(
    hymn_slug: str,
    tpq: int = 480,
) -> tuple[list[tuple[int, int, int, int, str]], dict]:
    """Build the voice-driven SATB event list for ``hymn_slug``.

    Returns ``(events, hymn_json)`` where ``events`` is a deduped list of
    ``(tick, pitch, dur_ticks, velocity, source_voice)`` tuples ready for
    emission by ``_MidiBuilder.note`` and ``hymn_json`` is the parsed
    ``data/hymns/<slug>.json`` (so callers avoid re-reading it).
    """
    hymn_json_path = _ROOT / "data" / "hymns" / f"{hymn_slug}.json"
    hymn_json = json.loads(hymn_json_path.read_text())

    legacy_path = _find_legacy_export(hymn_slug)
    legacy = json.loads(legacy_path.read_text())
    voices = legacy.get("voices") or {}

    all_events: list[tuple[int, int, int, int, str]] = []
    for voice_name in ("S1V1", "S1V2", "S2V1", "S2V2"):
        evs = voices.get(voice_name) or []
        vel = _VOICE_VEL[voice_name]
        raw = _voice_events_to_notes(evs, vel, tpq=tpq)
        # Tag with source voice.
        all_events.extend((t, p, d, v, voice_name) for (t, p, d, v, _) in raw)

    deduped = _dedup_events(all_events, tick_window=10)
    return deduped, hymn_json


def bar_tick_windows(
    hymn_slug: str,
    tpq: int = 480,
) -> dict[int, tuple[int, int]]:
    """Compute ``{bar_number: (start_tick, end_tick_exclusive)}`` from
    the legacy voices streams.

    The window is ``[min(offset_ql), max(offset_ql + duration_ql))`` over
    every non-rest event assigned to that bar (by the legacy ``bar``
    field). For a standard hymn this matches the meter-grid, and it
    degrades gracefully for pickup bars or unusual meters.
    """
    legacy_path = _find_legacy_export(hymn_slug)
    legacy = json.loads(legacy_path.read_text())
    voices = legacy.get("voices") or {}

    per_bar_start: dict[int, float] = {}
    per_bar_end: dict[int, float] = {}
    for voice_name in ("S1V1", "S1V2", "S2V1", "S2V2"):
        for e in voices.get(voice_name) or []:
            if e.get("is_rest"):
                continue
            try:
                bar = int(e.get("bar") or 0)
                on = float(e.get("offset_ql") or 0.0)
                dur = float(e.get("duration_ql") or 0.0)
            except (TypeError, ValueError):
                continue
            # For a tied note, its own duration may exceed the bar — use
            # the onset's bar but cap end at the next bar's onset later.
            if bar not in per_bar_start or on < per_bar_start[bar]:
                per_bar_start[bar] = on
            if bar not in per_bar_end or (on + dur) > per_bar_end[bar]:
                per_bar_end[bar] = on + dur

    # Collapse ties: a bar's end shouldn't exceed the next bar's start, so
    # we use the following bar's start as the hard boundary when present.
    bars = sorted(per_bar_start)
    windows: dict[int, tuple[int, int]] = {}
    for idx, bar in enumerate(bars):
        start_q = per_bar_start[bar]
        if idx + 1 < len(bars):
            end_q = per_bar_start[bars[idx + 1]]
        else:
            end_q = per_bar_end[bar]
        windows[bar] = (int(round(start_q * tpq)), int(round(end_q * tpq)))
    return windows


def render_satb_baseline(
    hymn_slug: str,
    out_path: Path,
    bar_range: Optional[tuple[int, int]] = None,
) -> Path:
    """Render a hymn's SATB voices to a MIDI baseline.

    Parameters
    ----------
    hymn_slug
        e.g. ``"amazing_grace"``.  Used to locate both the modern
        ``data/hymns/<slug>.json`` (tempo/meter/key) and the legacy
        ``legacy/hymnal_export/*.json`` (voices).
    out_path
        Destination ``.mid``.
    bar_range
        Optional ``(first_bar, last_bar)`` inclusive window.  Bars are
        identified by the legacy JSON's 1-indexed ``bar`` field.

    Returns
    -------
    Path
        ``out_path``.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tpq = 480
    events, hymn_json = build_baseline_events(hymn_slug, tpq=tpq)

    bpm = _tempo_bpm(hymn_json)
    beats_num, unit = _meter(hymn_json)

    mb = _MidiBuilder(ticks_per_quarter=tpq, channel=0)
    mb.time_signature(0, beats_num, unit)
    mb.tempo(0, bpm)
    mb.program(0, 46)  # GM Orchestral Harp

    shift = 0
    if bar_range is not None:
        lo, hi = bar_range
        windows = bar_tick_windows(hymn_slug, tpq=tpq)
        lo_tick = windows.get(lo, (0, 0))[0]
        hi_tick = windows.get(hi, (0, 0))[1]
        events = [ev for ev in events if lo_tick <= ev[0] < hi_tick]
        shift = lo_tick

    for tick, pitch, dur_ticks, vel, _src in events:
        mb.note(tick - shift, pitch, dur_ticks, vel)

    out_path.write_bytes(mb.build())
    return out_path


__all__ = [
    "render_satb_baseline",
    "build_baseline_events",
    "bar_tick_windows",
    "_pitch_to_midi",
    "_clamp_midi",
    "_VOICE_VEL",
    "_VOICE_ROLE",
]
