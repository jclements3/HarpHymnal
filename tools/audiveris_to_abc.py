#!/usr/bin/env python3
"""
Convert an Audiveris-exported MusicXML (.mxl) of a single 101-licks strip
into the project's ABC format (two voices: V:1 treble, V:2 clef=bass).

Usage:
    python3 tools/audiveris_to_abc.py <in.mxl> <out.abc> --lick N \
        [--level "Easy"] [--scale "D natural minor"]
"""
from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

from music21 import converter, note, chord, meter, key, stream, clef


PITCH_TO_ABC = {0: "C", 1: "^C", 2: "D", 3: "^D", 4: "E", 5: "F",
                6: "^F", 7: "G", 8: "^G", 9: "A", 10: "^A", 11: "B"}


def m21_pitch_to_abc(p) -> str:
    """ABC pitch with octave marks. ABC's middle C is C, octave 5 (=C5) -> 'C'.
    C4 -> 'C,', B4 -> 'B,', C5 -> 'C', C6 -> 'c', C7 -> "c'"."""
    name = p.name.replace("-", "_").replace("#", "^")
    step = name[0]
    accidentals = name[1:]
    accs = accidentals.replace("^^", "^^").replace("__", "__")
    octave = p.octave if p.octave is not None else 4

    if octave >= 5:
        letter = step.lower()
        ticks = "'" * (octave - 5)
    else:
        letter = step.upper()
        ticks = "," * (4 - octave)
    pitch = f"{accs}{letter}{ticks}"
    return pitch


def quarter_to_abc_len(qlen: Fraction, unit: Fraction = Fraction(1, 2)) -> str:
    """Convert quarter-length to ABC length suffix relative to L=1/8 (unit=1/2 quarter).
    Returns the multiplier as a string ('' for 1, '2' for 2, etc.)."""
    qlen = Fraction(qlen).limit_denominator(48)
    n = qlen / unit
    if n == 1:
        return ""
    if n.denominator == 1:
        return str(n.numerator)
    if n.numerator == 1:
        return f"/{n.denominator}"
    return f"{n.numerator}/{n.denominator}"


def emit_element(el, unit) -> str:
    """One note/rest/chord -> ABC token."""
    if isinstance(el, note.Rest):
        return f"z{quarter_to_abc_len(el.quarterLength, unit)}"
    if isinstance(el, chord.Chord) and not isinstance(el, note.Note):
        ps = sorted(el.pitches, key=lambda p: p.ps)
        body = "".join(m21_pitch_to_abc(p) for p in ps)
        return f"[{body}]{quarter_to_abc_len(el.quarterLength, unit)}"
    if isinstance(el, note.Note):
        return f"{m21_pitch_to_abc(el.pitch)}{quarter_to_abc_len(el.quarterLength, unit)}"
    return ""


def voice_to_abc(part, unit) -> str:
    """Emit measures for one part: 'tok tok tok | tok tok |] '."""
    bars = []
    measures = part.getElementsByClass(stream.Measure)
    for m in measures:
        toks = []
        try:
            flat = m.flatten().notesAndRests
        except Exception:
            bars.append("z8")
            continue
        for el in flat:
            try:
                t = emit_element(el, unit)
            except Exception:
                t = ""
            if t:
                toks.append(t)
        bars.append(" ".join(toks) if toks else "z8")
    if not bars:
        return ""
    body = " | ".join(bars)
    return body + " |]"


def count_bars(part) -> int:
    return len(list(part.getElementsByClass(stream.Measure)))


def synth_bass(num_bars: int) -> str:
    """All 101 licks share a D-A half-note ostinato in cut time, octava bassa.
    With clef=bass-8 the written D, sounds an octave below D3 (= D2)."""
    if num_bars <= 0:
        num_bars = 4
    one = "D,2 A,,2"
    return " | ".join([one] * num_bars) + " |]"


def detect_meter(score) -> str:
    ts = score.flatten().getElementsByClass(meter.TimeSignature)
    if ts:
        t = ts[0]
        if t.symbol == "cut":
            return "C|"
        return f"{t.numerator}/{t.denominator}"
    return "4/4"


def detect_key(score) -> str:
    ks = score.flatten().getElementsByClass(key.KeySignature)
    if ks:
        sharps = ks[0].sharps
        if sharps == -1:
            return "Dm"   # 1 flat: F or Dm. Licks are all Dm.
        if sharps == 0:
            return "Am"
    return "Dm"


def convert(mxl_path: Path, lick_num: int, level: str, scale: str) -> str:
    score = converter.parse(str(mxl_path))
    parts = list(score.parts)

    if not parts:
        raise SystemExit(f"No parts in {mxl_path}")

    meter_str = detect_meter(score)
    key_str = detect_key(score)
    unit = Fraction(1, 2)  # L:1/8

    if len(parts) >= 2:
        treble_part, bass_part = parts[0], parts[1]
    else:
        only = parts[0]
        staffs = list(only.getElementsByClass(stream.PartStaff))
        if len(staffs) >= 2:
            treble_part, bass_part = staffs[0], staffs[1]
        else:
            voices = list(only.flatten().getElementsByClass(stream.Voice))
            if len(voices) >= 2:
                treble_part, bass_part = voices[0], voices[1]
            else:
                treble_part, bass_part = only, None

    treble_abc = voice_to_abc(treble_part, unit)
    n_bars = count_bars(treble_part)
    bass_abc = synth_bass(n_bars)

    abc = []
    abc.append(f"X:1")
    abc.append(f"T:Lick {lick_num} (D natural minor)")
    abc.append(f"M:{meter_str}")
    abc.append(f"L:1/8")
    abc.append(f"Q:1/4=80")
    abc.append(f"K:{key_str}")
    abc.append(f"% Audiveris OMR; level={level}; scale={scale}; bars={n_bars}")
    abc.append(f"% Bass: synthesized D-A ostinato (uniform across all 101 licks, octava bassa)")
    abc.append(f"[V:1] {treble_abc}")
    abc.append(f"[V:2 clef=bass-8] {bass_abc}")
    return "\n".join(abc) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mxl", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--lick", type=int, required=True)
    ap.add_argument("--level", default="?")
    ap.add_argument("--scale", default="D natural minor")
    args = ap.parse_args()

    abc = convert(args.mxl, args.lick, args.level, args.scale)
    args.out.write_text(abc)
    print(f"Wrote {args.out} ({len(abc)} bytes)")


if __name__ == "__main__":
    main()
