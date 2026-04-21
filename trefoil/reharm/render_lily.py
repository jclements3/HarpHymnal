"""Render a reharm-selector variation to a LilyPond source file.

Phase 7 companion to :mod:`trefoil.reharm.render_midi`: produces a
``.ly`` file with a GrandStaff (treble RH / bass LH), a tactic-manifest
markup line above the score, and per-bar chord labels.

The LilyPond output is deliberately *honest about rhythm* — the same
density / texture decisions that shape the MIDI attack grid also shape
the notated rhythm — but simplified.  A render-quality score is a
non-goal here; what the harpist wants is a **chart** they can skim in
parallel with the MIDI playback.

Decisions for v1 rendering
--------------------------

* **Density** drives note duration on the RH staff:
  - ``density.one_attack``    → whole-bar chord (or melody held).
  - ``density.per_beat``      → one event per beat.
  - ``density.two_per_beat``  → two per beat.
  - ``density.syncopated``    → offbeat-only events (rests on beats).
  - ``density.front_loaded``  → first half filled, second half rests.
  - ``density.back_loaded``   → first half rests, second half filled.

* **Texture** only adds annotations:
  - ``texture.rolled``        → ``\arpeggio`` on the chord.
  - ``texture.bisbigliando``  → ``:32`` tremolo on the RH.
  - ``texture.staggered``     → LH shifted by half-beat in notation.
  - ``texture.arp_both``      → LH broken, RH broken, beamed together.
  - ``texture.single_line``   → melody on RH only, LH empty.

* **LH activity** is honored by pattern choice (sustain = whole-note
  chord, bass_chord_chord = dotted bass + chord blocks, etc.).

* **RH activity** is honored by adding chord tones under the melody as
  chord stacks (``<... ...>``) or melody-alone single pitches.

* **Substitution / connect_from / connect_to / phrase_role / lever** —
  annotated in the markup above the bar only (no rhythmic impact in the
  simplified chart).

Stdlib only.  Usage::

    from trefoil.reharm.render_lily import render_variation_lily
    render_variation_lily(variation_json, hymn_json, Path("v28.ly"))
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional


# --------------------------------------------------------------------------- #
# Pitch math (kept local — don't import renderers.lilypond to preserve        #
# module independence per the Phase 7 deliverable list)                       #
# --------------------------------------------------------------------------- #

_PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
_MINOR_STEPS = [0, 2, 3, 5, 7, 8, 10]


def _parse_key_root(s: str) -> int:
    s = (s or "C").strip()
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
    steps = _scale_steps(mode)
    tonic_pc = _parse_key_root(key_root)
    zero = (octv - 1) * 7 + (deg - 1)
    octave_offset = zero // 7
    degree_idx = zero % 7
    return 24 + tonic_pc + steps[degree_idx] + 12 * octave_offset


_LY_CHROMATIC = {
    0: "c", 1: "cis", 2: "d", 3: "ees", 4: "e", 5: "f",
    6: "fis", 7: "g", 8: "aes", 9: "a", 10: "bes", 11: "b",
}


def _midi_to_ly(midi: int) -> str:
    """MIDI → LilyPond absolute pitch (C4 = ``c'``)."""
    pc = midi % 12
    letter = _LY_CHROMATIC[pc]
    # LilyPond absolute: c = MIDI 48 (C3), c' = MIDI 60 (C4).
    octave_of_c = midi // 12 - 4  # MIDI 48 → 0, 60 → 1 (one apostrophe)
    if octave_of_c > 0:
        return letter + "'" * octave_of_c
    if octave_of_c < 0:
        return letter + "," * (-octave_of_c)
    return letter


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
    return 12 * (octv + 1) + pc


# --------------------------------------------------------------------------- #
# Key signature                                                               #
# --------------------------------------------------------------------------- #

def _ly_keysig(root: str, mode: str) -> str:
    letter = root[0].lower()
    accid = ""
    for ch in root[1:]:
        if ch == "#":
            accid = "is"
        elif ch in ("b", "-"):
            accid = "es"
    m = "\\minor" if mode == "minor" else "\\major"
    return f"{letter}{accid} {m}"


# --------------------------------------------------------------------------- #
# Duration formatting                                                         #
# --------------------------------------------------------------------------- #

def _ql_to_ly_dur(ql: float) -> str:
    """Quarter-length → LilyPond duration token (approximate)."""
    table = [
        (4.0, "1"), (3.0, "2."), (2.0, "2"), (1.5, "4."),
        (1.0, "4"), (0.75, "8."), (0.5, "8"),
        (0.375, "16."), (0.25, "16"), (0.125, "32"), (0.0625, "64"),
    ]
    for v, tok in table:
        if abs(ql - v) < 1e-3:
            return tok
    # closest
    return min(table, key=lambda p: abs(p[0] - ql))[1]


def _beats_to_ly_dur(beat_fraction: float, meter_unit: int) -> str:
    """Given a beat fraction (of the bar) and the meter unit, return the LilyPond
    duration token for a single note of that length.

    Example: 4/4 meter, beat_fraction=0.25 (one beat) → quarter → "4".
    """
    # beat_fraction of bar * bar length (in quarters) = note length in quarters
    # bar length in quarters = 4 / meter_unit * beats_per_bar (but for LilyPond
    # we want note length = beat_fraction * meter_beats * (4/meter_unit) quarters
    # The caller passes the fraction already correctly.
    ql = beat_fraction
    return _ql_to_ly_dur(ql)


# --------------------------------------------------------------------------- #
# Main render                                                                 #
# --------------------------------------------------------------------------- #

_LY_TEMPLATE = r"""\version "2.22.1"

\paper {
  left-margin = 4\mm
  right-margin = 4\mm
  top-margin = 8\mm
  bottom-margin = 8\mm
  indent = 0
  ragged-right = ##t
}

\header {
  title = "__TITLE__"
  subtitle = "__SUBTITLE__"
  tagline = ##f
}

global = {
  \key __KEYSIG__
  \time __METER__
  \tempo 4=__BPM__
}

__TOP_MARKUP__

upper = {
  \set Staff.midiInstrument = "orchestral harp"
  \global
__UPPER_BODY__
}

lower = {
  \clef bass
  \set Staff.midiInstrument = "orchestral harp"
  \global
__LOWER_BODY__
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
}
"""


def _attack_schedule(density: str, n_beats: int) -> list[tuple[float, float]]:
    """Return a list of (start_fraction_of_bar, duration_fraction_of_bar) slots.

    Matches the MIDI side's density map but here we produce *note slots* that
    fill the bar exactly.  A rest-only slot is represented as (start, dur, True).
    """
    if n_beats <= 0:
        n_beats = 1
    if density == "density.one_attack":
        return [(0.0, 1.0)]
    if density == "density.per_beat":
        return [(i / n_beats, 1 / n_beats) for i in range(n_beats)]
    if density == "density.two_per_beat":
        return [(i / (2 * n_beats), 1 / (2 * n_beats)) for i in range(2 * n_beats)]
    if density == "density.syncopated":
        # rests on beats, notes on offbeats; we express as alternating half-beat slots
        slots = []
        for i in range(n_beats):
            slots.append((i / n_beats, 0.5 / n_beats))       # rest half
            slots.append(((i + 0.5) / n_beats, 0.5 / n_beats))  # note half
        return slots
    if density == "density.front_loaded":
        return [(i / (2 * n_beats), 1 / (2 * n_beats)) for i in range(n_beats)] + [(0.5, 0.5)]
    if density == "density.back_loaded":
        return [(0.0, 0.5)] + [(0.5 + i / (2 * n_beats), 1 / (2 * n_beats)) for i in range(n_beats)]
    return [(i / n_beats, 1 / n_beats) for i in range(n_beats)]


def _ly_escape(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace('"', r"\"")


def _manifest_line(manifest: dict) -> str:
    """Compact tactic-manifest string for top-of-page markup."""
    # Order preserved from REHARM_TACTICS.md
    order = [
        "substitution", "shape", "register", "density", "texture",
        "lh_activity", "rh_activity", "connect_from", "connect_to",
        "lever", "range", "phrase_role",
    ]
    parts = []
    for dim in order:
        v = manifest.get(dim, "")
        if not v:
            continue
        short = v.split(".", 1)[1] if "." in v else v
        parts.append(short)
    return " / ".join(parts)


def _voicing_to_midis(voicing: list, key_root: str, mode: str) -> list[int]:
    out = []
    for pair in voicing or []:
        if not pair or len(pair) < 2:
            continue
        try:
            out.append(_deg_oct_to_midi(int(pair[0]), int(pair[1]), key_root, mode))
        except (TypeError, ValueError):
            continue
    return out


def _ly_chord(midis: list[int]) -> str:
    if not midis:
        return "r"
    if len(midis) == 1:
        return _midi_to_ly(midis[0])
    return "<" + " ".join(_midi_to_ly(m) for m in sorted(midis)) + ">"


def render_variation_lily(variation: dict, hymn_json: dict, out_path: Path) -> Path:
    """Render one variation to LilyPond source.

    Parameters
    ----------
    variation
        Parsed ``data/reharm/variations/<slug>/v##.json`` dict.
    hymn_json
        Parsed ``data/hymns/<slug>.json`` dict.
    out_path
        Destination ``.ly`` path.

    Returns
    -------
    Path
        The ``out_path``.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    key = hymn_json.get("key") or {}
    key_root = key.get("root", "C")
    key_mode = key.get("mode", "major")
    meter = hymn_json.get("meter") or {"beats": 4, "unit": 4}
    m_beats = int(meter.get("beats") or 4)
    m_unit = int(meter.get("unit") or 4)
    bpm = 72
    t = hymn_json.get("tempo") or {}
    if t.get("value"):
        try:
            bpm = int(round(float(t["value"])))
        except (TypeError, ValueError):
            bpm = 72

    title = hymn_json.get("title") or variation.get("title") or variation.get("slug", "Untitled")
    subtitle = f"Variation {variation.get('variation_index', '?')} — reharm tactics draft"

    bars = variation.get("bars") or []
    hymn_bars = hymn_json.get("bars") or []

    # Per-bar rendered bodies for upper and lower staves
    upper_chunks: list[str] = []
    lower_chunks: list[str] = []

    # Bar length in quarters, for duration math
    bar_ql = m_beats * (4.0 / m_unit)

    for ibar, bar in enumerate(bars):
        manifest = bar.get("tactic_manifest") or {}
        density = manifest.get("density", "density.per_beat")
        texture = manifest.get("texture", "texture.block")
        lh_activity = manifest.get("lh_activity", "lh_activity.sustain")
        rh_activity = manifest.get("rh_activity", "rh_activity.melody_alone")

        lh_midis = _voicing_to_midis(bar.get("lh") or [], key_root, key_mode)
        rh_midis = _voicing_to_midis(bar.get("rh") or [], key_root, key_mode)

        # ---- Per-bar markup (tactic summary) above upper staff ----
        mfline = _manifest_line(manifest)
        chord = bar.get("chord_used") or {}
        ch_str = (chord.get("translated") or chord.get("numeral") or "")
        if chord.get("quality"):
            ch_str += chord.get("quality")
        bar_mark = (
            f"  \\once \\override TextScript.font-size = #-3 "
            f"s1*0^\\markup {{ \\column {{ "
            f"\\line {{ \\bold \"{_ly_escape(ch_str)}\" }} "
            f"\\line {{ \\italic \"{_ly_escape(mfline)}\" }} }} }}\n"
        )

        # ---- UPPER staff (RH) ----
        # single_line: just melody
        # bisbigliando: tremolo ``:32`` on a chord; LH sustains
        # otherwise: slot-based chord events using density schedule
        h_bar = hymn_bars[ibar] if ibar < len(hymn_bars) else {}
        mel_events = h_bar.get("melody") or []

        if texture == "texture.single_line":
            # render melody with its native rhythm
            tokens = []
            for e in mel_events:
                dur = float(e.get("duration") or 0)
                if e.get("kind") == "note":
                    m = _melody_event_to_midi(e)
                    if m is None:
                        tokens.append(f"r{_ql_to_ly_dur(dur)}")
                    else:
                        tokens.append(f"{_midi_to_ly(m)}{_ql_to_ly_dur(dur)}")
                else:
                    tokens.append(f"r{_ql_to_ly_dur(dur)}")
            upper_body = "  " + " ".join(tokens) + " |\n"
            # LH: silent rest for the bar
            lower_body = f"  R1*{bar_ql}/4 |\n"
            upper_chunks.append(bar_mark + upper_body)
            lower_chunks.append(lower_body)
            continue

        # --- Use density schedule to slot-align melody events ---
        slots = _attack_schedule(density, m_beats)

        # Resolve melody pitches per-slot: pick the melody note that sounds at
        # the slot's start tick (nearest onset ≤ slot start).
        mel_onsets: list[tuple[float, Optional[int]]] = []  # (fraction_of_bar, midi)
        mel_total = sum(float(e.get("duration") or 0) for e in mel_events) or bar_ql
        cur = 0.0
        for e in mel_events:
            dur = float(e.get("duration") or 0)
            m = _melody_event_to_midi(e) if e.get("kind") == "note" else None
            frac = cur / mel_total
            mel_onsets.append((frac, m))
            cur += dur
        if not mel_onsets:
            mel_onsets = [(0.0, None)]

        def _mel_at(frac: float) -> Optional[int]:
            chosen = None
            for f, m in mel_onsets:
                if f <= frac + 1e-6:
                    chosen = m
                else:
                    break
            return chosen

        def _rh_stack(mel_m: Optional[int]) -> list[int]:
            if mel_m is None:
                return []
            if rh_activity == "rh_activity.melody_alone":
                return [mel_m]
            if rh_activity == "rh_activity.melody_oct":
                return [mel_m - 12, mel_m]
            below = sorted([p for p in (lh_midis + rh_midis) if p < mel_m], reverse=True)
            if rh_activity == "rh_activity.melody_plus_1":
                if below:
                    return sorted([mel_m, below[0]])
                return [mel_m]
            if rh_activity == "rh_activity.melody_plus_2":
                picks = below[:2]
                return sorted([mel_m] + picks)
            return [mel_m]

        upper_tokens: list[str] = []
        # Syncopated: slots alternate (rest_half, note_half)
        sync = (density == "density.syncopated")
        front = (density == "density.front_loaded")
        back = (density == "density.back_loaded")

        if texture == "texture.bisbigliando" and rh_midis:
            # single whole-bar chord with :32 tremolo mark
            stack = _rh_stack(_mel_at(0.0)) or rh_midis[:1]
            tok = _ly_chord(stack) + "1:32"
            upper_tokens.append(tok)
        else:
            for i, (start, dur_f) in enumerate(slots):
                dur_ql = dur_f * bar_ql
                is_rest = False
                if sync and i % 2 == 0:
                    is_rest = True
                if back and start < 0.5 - 1e-6 and dur_f >= 0.5 - 1e-6:
                    # first-half slot is a rest
                    is_rest = True
                if front and start >= 0.5 - 1e-6 and dur_f >= 0.5 - 1e-6:
                    is_rest = True
                if is_rest:
                    upper_tokens.append(f"r{_ql_to_ly_dur(dur_ql)}")
                    continue
                mel_m = _mel_at(start)
                stack = _rh_stack(mel_m)
                if not stack:
                    upper_tokens.append(f"r{_ql_to_ly_dur(dur_ql)}")
                else:
                    tok = _ly_chord(stack) + _ql_to_ly_dur(dur_ql)
                    if i == 0 and texture == "texture.rolled":
                        tok += "\\arpeggio"
                    upper_tokens.append(tok)

        upper_body = "  " + " ".join(upper_tokens) + " |\n"

        # ---- LOWER staff (LH) ----
        if not lh_midis or lh_activity == "lh_activity.none":
            lower_body = f"  R1*{m_beats}/{m_unit} |\n"
        elif lh_activity in ("lh_activity.sustain", "lh_activity.strike_and_ring"):
            tok = _ly_chord(lh_midis) + _ql_to_ly_dur(bar_ql)
            if texture == "texture.rolled":
                tok += "\\arpeggio"
            lower_body = f"  {tok} |\n"
        elif lh_activity == "lh_activity.bass_chord_chord":
            # bass on 1, chord on remaining beats
            bass_tok = _ly_chord([min(lh_midis)]) + _ql_to_ly_dur(bar_ql / m_beats)
            upper_pcs = sorted(lh_midis)[1:] or lh_midis
            chord_tok = _ly_chord(upper_pcs) + _ql_to_ly_dur(bar_ql / m_beats)
            lower_body = "  " + bass_tok + " " + " ".join([chord_tok] * (m_beats - 1)) + " |\n"
        elif lh_activity == "lh_activity.chord_offbeat":
            # rest-on, chord-off per beat
            half = _ql_to_ly_dur((bar_ql / m_beats) / 2)
            chord_tok = _ly_chord(lh_midis) + half
            rest_tok = f"r{half}"
            toks = []
            for _ in range(m_beats):
                toks.extend([rest_tok, chord_tok])
            lower_body = "  " + " ".join(toks) + " |\n"
        elif lh_activity == "lh_activity.arp_up":
            tones = sorted(lh_midis)
            k = max(2, min(8, 2 * m_beats))
            dur_tok = _ql_to_ly_dur(bar_ql / k)
            toks = [_midi_to_ly(tones[i % len(tones)]) + dur_tok for i in range(k)]
            lower_body = "  " + " ".join(toks) + " |\n"
        elif lh_activity == "lh_activity.arp_down":
            tones = sorted(lh_midis, reverse=True)
            k = max(2, min(8, 2 * m_beats))
            dur_tok = _ql_to_ly_dur(bar_ql / k)
            toks = [_midi_to_ly(tones[i % len(tones)]) + dur_tok for i in range(k)]
            lower_body = "  " + " ".join(toks) + " |\n"
        elif lh_activity == "lh_activity.tremolo":
            # render as one tremolo chord
            tok = _ly_chord(lh_midis) + _ql_to_ly_dur(bar_ql) + ":32"
            lower_body = f"  {tok} |\n"
        elif lh_activity == "lh_activity.partial_silence":
            if m_beats >= 4:
                beat = _ql_to_ly_dur(bar_ql / m_beats)
                toks = [f"r{beat}", _ly_chord(lh_midis) + beat,
                        f"r{beat}", _ly_chord(lh_midis) + beat]
                lower_body = "  " + " ".join(toks) + " |\n"
            elif m_beats == 3:
                beat = _ql_to_ly_dur(bar_ql / m_beats)
                toks = [f"r{beat}", _ly_chord(lh_midis) + beat, f"r{beat}"]
                lower_body = "  " + " ".join(toks) + " |\n"
            else:
                half = _ql_to_ly_dur(bar_ql / 2)
                toks = [f"r{half}", _ly_chord(lh_midis) + half]
                lower_body = "  " + " ".join(toks) + " |\n"
        elif lh_activity == "lh_activity.low_bass_grab":
            # grace note to bass octave below, then chord
            grace = _midi_to_ly(min(lh_midis) - 12) + "16"
            tok = _ly_chord(lh_midis) + _ql_to_ly_dur(bar_ql - 0.25)
            lower_body = f"  \\grace {{ {grace} }} {tok} |\n"
        elif lh_activity == "lh_activity.countermelody":
            # 4 stepwise notes within the shape
            tones = sorted(lh_midis)
            dur_tok = _ql_to_ly_dur(bar_ql / 4)
            toks = [_midi_to_ly(tones[i % len(tones)]) + dur_tok for i in range(4)]
            lower_body = "  " + " ".join(toks) + " |\n"
        else:
            tok = _ly_chord(lh_midis) + _ql_to_ly_dur(bar_ql)
            lower_body = f"  {tok} |\n"

        upper_chunks.append(bar_mark + upper_body)
        lower_chunks.append(lower_body)

    top_markup = (
        "\\markup { \\fill-line { \\italic \\small \""
        + _ly_escape(f"Tactic manifest (per-bar above each measure). "
                     f"Seed: {variation.get('seed', '?')}, "
                     f"hash: {str(variation.get('tactics_hash', ''))[:12]}")
        + "\" } }\n"
    )

    ly = _LY_TEMPLATE
    ly = ly.replace("__TITLE__", _ly_escape(title))
    ly = ly.replace("__SUBTITLE__", _ly_escape(subtitle))
    ly = ly.replace("__KEYSIG__", _ly_keysig(key_root, key_mode))
    ly = ly.replace("__METER__", f"{m_beats}/{m_unit}")
    ly = ly.replace("__BPM__", str(bpm))
    ly = ly.replace("__TOP_MARKUP__", top_markup)
    ly = ly.replace("__UPPER_BODY__", "".join(upper_chunks) or "  R1 |\n")
    ly = ly.replace("__LOWER_BODY__", "".join(lower_chunks) or "  R1 |\n")

    out_path.write_text(ly, encoding="utf-8")
    return out_path


__all__ = ["render_variation_lily"]
