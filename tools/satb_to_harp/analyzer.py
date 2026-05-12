"""SATB → 8-voice BeatLedger analyzer.

Pipeline (see docs/harprules.md §Procedure):

    extract_tune       → ABC block for one hymn
    split_voices       → per-voice ABC lines (S1V1/S1V2/S2V1/S2V2)
    music21 parse      → music21 Note streams per voice
    sample_satb        → (t, S1, A1, T1, B) per beat
    Pass 1: seed       → SATB voices populated, others REST_EVENT
    Pass 2: collapse   → consecutive same-pitch attacks → sustain
    Pass 3: fill       → freed fingers receive chord-tone / octave-fill / idle
    Pass 4: audit      → range, drone-zone, same-letter, parallel checks

CLI: python -m tools.satb_to_harp.analyzer "Silent Night"
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from music21 import (
    chord as m21chord,
    converter,
    key as m21key,
    note as m21note,
    pitch as m21pitch,
)

from parsers.abc import (
    _key_root_normalized,
    aggregate_regions,
    analyze_beats,
    build_voice_abc,
    detect_cadence_bars,
    detect_fermata_bars,
    detect_mode,
    detect_true_tonic,
    downsample_per_bar,
    extract_tune,
    hymn_slug,
    sample_satb,
    split_into_phrases,
    split_voices,
)

from tools.satb_to_harp.types import (
    Audit,
    Beat,
    BeatLedger,
    EventSource,
    LH_VOICES,
    REST_EVENT,
    RH_VOICES,
    SATB_TO_VOICE,
    VOICE_ORDER,
    VOICE_RANGE,
    VoiceEvent,
    VoiceName,
)


import re

# Roman-numeral letter heads we recognize when picking chord tones.
# Inversions/qualities are stripped before lookup.
_RN_TO_DEGREES: dict[str, tuple[int, ...]] = {
    # Major-key diatonic triads (degrees from tonic, in semitones is built
    # from a scale degree list).
    "I":   (1, 3, 5),
    "ii":  (2, 4, 6),
    "iii": (3, 5, 7),
    "IV":  (4, 6, 1),
    "V":   (5, 7, 2),
    "vi":  (6, 1, 3),
    "vii": (7, 2, 4),
    # Minor-key diatonics
    "i":   (1, 3, 5),
    "iv":  (4, 6, 1),
    "v":   (5, 7, 2),
    "VI":  (6, 1, 3),
    "VII": (7, 2, 4),
    "III": (3, 5, 7),
}


def _rn_head(rn: str) -> Optional[str]:
    """Pull the bare numeral letters off a (possibly figured/inverted) RN."""
    if not rn or rn == "—":
        return None
    m = re.match(r"^[#b]?([ivIV]+)", rn.strip())
    if not m:
        return None
    return m.group(1)


def _scale_degree_to_midi(K: m21key.Key, degree: int, octave: int) -> int:
    """Return MIDI for a given scale degree of K at the requested octave."""
    pcs = [p.pitchClass for p in K.pitches[:7]]  # 7 distinct pcs in order
    pc = pcs[(degree - 1) % 7]
    tonic_pc = K.tonic.pitchClass
    # Build a MIDI in `octave` (scientific) whose pc matches.
    # MIDI octave conventions: C4 == 60, so MIDI for pc p in scientific oct o is
    # 12 * (o + 1) + p.
    cand = 12 * (octave + 1) + pc
    # If the resulting pitch is below the tonic-of-that-octave for non-tonic
    # degrees, bump up to keep ordering (so V in C4 sits at G4, not G3).
    tonic_midi = 12 * (octave + 1) + tonic_pc
    if degree != 1 and cand < tonic_midi:
        cand += 12
    return cand


def _voice_range_octaves(voice: VoiceName) -> range:
    lo, hi = VOICE_RANGE[voice]
    # Scientific octave for a midi m is m // 12 - 1
    return range((lo // 12) - 1, (hi // 12) - 1 + 1)


def _in_range(voice: VoiceName, midi: int) -> bool:
    lo, hi = VOICE_RANGE[voice]
    return lo <= midi <= hi


def _pitch_class(midi: int) -> int:
    return midi % 12


def _letter_of(midi: int) -> str:
    """Diatonic letter name (no accidental) for a MIDI value."""
    return m21pitch.Pitch(midi=midi).step


def _collect_sounding_midis(voices: dict[VoiceName, VoiceEvent]) -> list[int]:
    out = []
    for ev in voices.values():
        if ev.pitch_midi is not None and ev.kind in ("attack", "sustain"):
            out.append(ev.pitch_midi)
    return out


def _bar_chord_lookup(bar_regions: list[dict]) -> dict[int, str]:
    """Map bar number → RN figure (bar-level downsample, one chord per bar)."""
    out: dict[int, str] = {}
    for r in bar_regions:
        for b in range(r["start_bar"], r["end_bar"] + 1):
            out[b] = r["rn"]
    return out


def _pick_chord_tone(
    K: m21key.Key,
    rn_head_str: str,
    target_voice: VoiceName,
    forbidden_midis: list[int],
) -> Optional[int]:
    """Pick a chord-tone MIDI value for target_voice's range that isn't
    already sounding.

    Preference order: 3rd, 5th, then root. Empty list → None.
    """
    degrees = _RN_TO_DEGREES.get(rn_head_str)
    if not degrees:
        return None
    root, third, fifth = degrees
    forbidden_pcs = {_pitch_class(m) for m in forbidden_midis}
    forbidden_letters = {_letter_of(m) for m in forbidden_midis}

    lo, hi = VOICE_RANGE[target_voice]
    # Try preferred order: 3rd, 5th, root.
    for deg in (third, fifth, root):
        for octave in _voice_range_octaves(target_voice):
            cand = _scale_degree_to_midi(K, deg, octave)
            if not (lo <= cand <= hi):
                continue
            if _pitch_class(cand) in forbidden_pcs:
                continue
            if _letter_of(cand) in forbidden_letters:
                continue
            return cand
    return None


def _pick_octave_fill(
    target_voice: VoiceName,
    source_midi: int,
    forbidden_midis: list[int],
) -> Optional[int]:
    """Double `source_midi` at the nearest octave inside target_voice's range."""
    forbidden_pcs = {_pitch_class(m) for m in forbidden_midis}
    forbidden_letters = {_letter_of(m) for m in forbidden_midis}

    lo, hi = VOICE_RANGE[target_voice]
    candidates = [source_midi - 12, source_midi + 12, source_midi - 24, source_midi + 24]
    for cand in candidates:
        if not (lo <= cand <= hi):
            continue
        # Octave-doubling intentionally shares a letter with the source; the
        # forbidden-letter check only rejects clashes with *other* voices.
        other_letters = forbidden_letters - {_letter_of(source_midi)}
        other_pcs = forbidden_pcs - {_pitch_class(source_midi)}
        if _letter_of(cand) in other_letters:
            continue
        if _pitch_class(cand) in other_pcs:
            continue
        return cand
    return None


def _last_beat_of_phrase(beat_idx: int, beats_per_bar: int, phrase_dicts: list[dict]) -> bool:
    """True iff `beat_idx` (0-based) is the final beat of a phrase."""
    bar = beat_idx // beats_per_bar + 1
    beat_in_bar = beat_idx % beats_per_bar + 1
    if beat_in_bar != beats_per_bar:
        return False
    for p in phrase_dicts:
        if p["bars"] and p["bars"][-1] == bar:
            return True
    return False


def analyze(title: str, abc_path: Path = Path("source/OpenHymnal.abc")) -> BeatLedger:
    abc_text = Path(abc_path).read_text()
    block = extract_tune(abc_text, title)
    headers, body, extras = split_voices(block, return_extras=True)

    # --- headers: key, meter, tempo (mirrors parse_hymn) ---
    real_title = title
    for h in headers:
        if h.startswith("T:"):
            real_title = h[2:].strip()
            break

    key_line = next((h for h in headers if h.startswith("K:")), "K: C")
    meter_line = next((h for h in headers if h.startswith("M:")), "M: 4/4")
    tempo_line = next((h for h in headers if h.startswith("Q:")), None)

    key_match = re.match(r"K:\s*([A-G][b#]?m?(?:aj|in)?)", key_line)
    key_str = key_match.group(1) if key_match else "C"
    K_header = m21key.Key(key_str.rstrip("maj").rstrip("in"))

    meter_match = re.search(r"M:\s*(\d+)/(\d+)", meter_line)
    meter_num = int(meter_match.group(1)) if meter_match else 4
    meter_den = int(meter_match.group(2)) if meter_match else 4

    tempo_value = 90
    if tempo_line:
        m_q = re.search(r"(\d+)/(\d+)\s*=\s*(\d+)", tempo_line)
        if m_q:
            tempo_value = int(m_q.group(3))
        else:
            m_q2 = re.search(r"=?\s*(\d+)", tempo_line)
            if m_q2:
                tempo_value = int(m_q2.group(1))

    # --- parse voices through music21 (same as parse_hymn lines 1045-1070) ---
    voices_raw: dict[str, list] = {}
    for v in ("S1V1", "S1V2", "S2V1", "S2V2"):
        if not body[v]:
            voices_raw[v] = []
            continue
        abc = build_voice_abc(headers, body, v)
        s = converter.parseData(abc, format="abc")
        voices_raw[v] = list(s.flatten().notesAndRests)

    voices_parsed: dict[str, list] = {}
    for v_name, nl in voices_raw.items():
        is_upper = v_name in ("S1V1", "S1V2")
        fixed = []
        for n in nl:
            if isinstance(n, m21chord.Chord):
                rep = (max if is_upper else min)(n.pitches, key=lambda p: p.midi)
                repl = m21note.Note(rep)
                repl.offset = n.offset
                repl.duration = n.duration
                repl.tie = n.tie
                repl.expressions = n.expressions
                fixed.append(repl)
            else:
                fixed.append(n)
        voices_parsed[v_name] = fixed

    # --- tonic + mode ---
    K = detect_true_tonic(voices_parsed, K_header)
    key_mode: str = "minor" if K.mode == "minor" else "major"
    header_scale_pcs = {p.pitchClass for p in K_header.pitches}
    modal_name = detect_mode(K.tonic.pitchClass, header_scale_pcs)

    # --- beat samples + region analysis ---
    samples, total_ql = sample_satb(voices_parsed, beat_unit_ql=1.0)
    beats_analyzed = analyze_beats(samples, K, key_mode, meter_num)
    bar_regions = downsample_per_bar(beats_analyzed, meter_num, slots_per_bar=1)
    halfbar_regions = downsample_per_bar(beats_analyzed, meter_num, slots_per_bar=2)
    total_bars = max((b["bar"] for b in beats_analyzed), default=0)

    fermata_bars = detect_fermata_bars(body, total_bars=total_bars)
    cadence_bars = detect_cadence_bars(bar_regions, key_mode, halfbar_regions)
    phrase_dicts = split_into_phrases(bar_regions, fermata_bars, cadence_bars)

    bar_chord = _bar_chord_lookup(bar_regions)

    # ────────────────────────────────────────────────────────────────────
    # Pass 1 — seed beats with SATB into S1/A1/T1/B; everything else rests.
    # ────────────────────────────────────────────────────────────────────
    beats: list[Beat] = []
    for i, (t, n_s1v1, n_s1v2, n_s2v1, n_s2v2) in enumerate(samples):
        bar = i // meter_num + 1
        beat_in_bar = i % meter_num + 1
        voices: dict[VoiceName, VoiceEvent] = {v: REST_EVENT for v in VOICE_ORDER}

        for src_key, src_note in (
            ("S1V1", n_s1v1),
            ("S1V2", n_s1v2),
            ("S2V1", n_s2v1),
            ("S2V2", n_s2v2),
        ):
            target = SATB_TO_VOICE[src_key]
            if src_note is None or isinstance(src_note, m21note.Rest):
                continue
            try:
                midi = int(src_note.pitch.midi)
            except AttributeError:
                continue
            voices[target] = VoiceEvent(kind="attack", pitch_midi=midi, source="satb")

        beats.append(Beat(index=i, bar=bar, beat_in_bar=beat_in_bar, voices=voices))

    # ────────────────────────────────────────────────────────────────────
    # Pass 2 — collapse re-pluck attacks of the same pitch to sustains.
    # ────────────────────────────────────────────────────────────────────
    for v in ("S1", "A1", "T1", "B"):
        held_pitch: Optional[int] = None
        for beat in beats:
            ev = beat.voices[v]
            if ev.kind == "attack" and ev.pitch_midi is not None:
                if held_pitch is not None and ev.pitch_midi == held_pitch:
                    beat.voices[v] = VoiceEvent(
                        kind="sustain", pitch_midi=ev.pitch_midi, source=ev.source,
                    )
                else:
                    held_pitch = ev.pitch_midi
            elif ev.kind == "sustain" and ev.pitch_midi is not None:
                held_pitch = ev.pitch_midi
            else:
                held_pitch = None

    # Pass 3 — chord-root open-octave bass.
    #   Dr = chord root in C1-B1 (one pluck per chord change)
    #   B  = chord root one octave above Dr, in C2-B2 (overrides SATB bass)
    # This is an open-octave harp bass that follows the harmony directly. The
    # SATB inner voices (A1 alto, T1 tenor) and S1 melody are unchanged.
    # Pass 3 — Dr drone only. B keeps its SATB-bass content; the hand router
    # decides per beat which hand actually plays it. In pattern mode the
    # consolidator excludes B from the router and synthesizes a chord-root
    # octave-above-Dr as a separate router input.
    if beats and bar_chord:
        last_root_pc: Optional[int] = None
        for beat in beats:
            rn_str = bar_chord.get(beat.bar, "")
            head = _rn_head(rn_str)
            degrees = _RN_TO_DEGREES.get(head) if head else None
            if not degrees or not (1 <= degrees[0] <= 7):
                if last_root_pc is not None:
                    beat.voices["Dr"] = VoiceEvent(
                        kind="sustain", pitch_midi=24 + last_root_pc, source="drone",
                    )
                continue
            root_pc = K.pitches[degrees[0] - 1].pitchClass
            kind = "attack" if root_pc != last_root_pc else "sustain"
            beat.voices["Dr"] = VoiceEvent(
                kind=kind, pitch_midi=24 + root_pc, source="drone",
            )
            last_root_pc = root_pc

    # ────────────────────────────────────────────────────────────────────
    # Pass 4 — musical audit (voice-leading). Playability concerns
    # (range, hand span, pedal conflicts) live in the consolidator.
    # ────────────────────────────────────────────────────────────────────
    audits: list[Audit] = []

    # Parallel 5ths/8ves between any fill voice and any SATB voice.
    fill_voices: tuple[VoiceName, ...] = ("T1", "T2")  # pattern slots
    satb_voices: tuple[VoiceName, ...] = ("S1", "S2", "A1", "A2")
    for i in range(1, len(beats)):
        prev, cur = beats[i - 1], beats[i]
        for fv in fill_voices:
            pv = prev.voices[fv]
            cv = cur.voices[fv]
            if pv.kind != "attack" or cv.kind != "attack":
                continue
            if pv.pitch_midi is None or cv.pitch_midi is None:
                continue
            if pv.pitch_midi == cv.pitch_midi:
                continue
            for sv in satb_voices:
                ps = prev.voices[sv]
                cs = cur.voices[sv]
                if ps.kind not in ("attack", "sustain") or cs.kind not in ("attack", "sustain"):
                    continue
                if ps.pitch_midi is None or cs.pitch_midi is None:
                    continue
                if ps.pitch_midi == cs.pitch_midi:
                    continue
                prev_intvl = abs(pv.pitch_midi - ps.pitch_midi) % 12
                cur_intvl = abs(cv.pitch_midi - cs.pitch_midi) % 12
                if prev_intvl == cur_intvl and prev_intvl in (0, 7):
                    name = "octave" if prev_intvl == 0 else "fifth"
                    audits.append(Audit(
                        beat=cur.index,
                        message=f"parallel {name}: fill {fv} ↔ SATB {sv}",
                        severity="warn",
                    ))

    return BeatLedger(
        title=real_title,
        key_root=_key_root_normalized(K),
        key_mode=key_mode,  # type: ignore[arg-type]
        modal_name=modal_name,
        meter_beats=meter_num,
        meter_unit=meter_den,
        beats_per_bar=meter_num,
        tempo_bpm=tempo_value,
        beats=beats,
        bar_chords=bar_chord,
        audits=audits,
    )


# ─────────────────────────────────────────────────────────────────────────────
# JSON serialization
# ─────────────────────────────────────────────────────────────────────────────
def _ledger_to_dict(ledger: BeatLedger) -> dict:
    return {
        "title": ledger.title,
        "key_root": ledger.key_root,
        "key_mode": ledger.key_mode,
        "modal_name": ledger.modal_name,
        "meter_beats": ledger.meter_beats,
        "meter_unit": ledger.meter_unit,
        "beats_per_bar": ledger.beats_per_bar,
        "tempo_bpm": ledger.tempo_bpm,
        "beats": [
            {
                "index": b.index,
                "bar": b.bar,
                "beat_in_bar": b.beat_in_bar,
                "voices": {
                    v: {
                        "kind": b.voices[v].kind,
                        "pitch_midi": b.voices[v].pitch_midi,
                        "source": b.voices[v].source,
                    }
                    for v in VOICE_ORDER
                },
            }
            for b in ledger.beats
        ],
        "bar_chords": {str(k): v for k, v in ledger.bar_chords.items()},
        "audits": [asdict(a) for a in ledger.audits],
    }


def write_ledger(ledger: BeatLedger, out_dir: Path = Path("data/harp_arranged")) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{hymn_slug(ledger.title)}.ledger.json"
    with path.open("w") as f:
        json.dump(_ledger_to_dict(ledger), f, indent=2)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python -m tools.satb_to_harp.analyzer <title> [<abc_path>]",
              file=sys.stderr)
        return 2
    title = argv[1]
    abc_path = Path(argv[2]) if len(argv) > 2 else Path("source/OpenHymnal.abc")
    ledger = analyze(title, abc_path)
    path = write_ledger(ledger)

    print(f"wrote {path}")
    print(f"beats: {len(ledger.beats)}")

    attack_counts: dict[str, int] = {v: 0 for v in VOICE_ORDER}
    for b in ledger.beats:
        for v in VOICE_ORDER:
            if b.voices[v].kind == "attack":
                attack_counts[v] += 1
    print("attack counts per voice:")
    for v in VOICE_ORDER:
        print(f"  {v}: {attack_counts[v]}")

    sev_counts: dict[str, int] = {}
    for a in ledger.audits:
        sev_counts[a.severity] = sev_counts.get(a.severity, 0) + 1
    print(f"audits: {len(ledger.audits)} total " + (
        ", ".join(f"{s}={c}" for s, c in sorted(sev_counts.items())) or "(none)"
    ))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
