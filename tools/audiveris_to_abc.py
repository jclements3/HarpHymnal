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


def quarter_to_abc_len(qlen: Fraction, unit: Fraction = Fraction(1, 1)) -> str:
    """Convert quarter-length to ABC length suffix.
    With unit=1 quarter (L:1/4): 1 -> '' (default), 2 -> '2', 1/2 -> '/',
    1/4 -> '//', 3/4 -> '3/4', etc."""
    qlen = Fraction(qlen).limit_denominator(48)
    n = qlen / unit
    if n == 1:
        return ""
    if n.denominator == 1:
        return str(n.numerator)
    if n.numerator == 1 and n.denominator == 2:
        return "/"
    if n.numerator == 1:
        return f"/{n.denominator}"
    return f"{n.numerator}/{n.denominator}"


def emit_element(el, unit, qlen_override=None) -> str:
    """One note/rest/chord -> ABC token. qlen_override sets displayed length
    (used when emitting inside an (N tuplet bracket so the visual length
    becomes a power of 2 instead of e.g. 2/3)."""
    qlen = qlen_override if qlen_override is not None else el.quarterLength
    if isinstance(el, note.Rest):
        return f"z{quarter_to_abc_len(qlen, unit)}"
    if isinstance(el, chord.Chord) and not isinstance(el, note.Note):
        ps = sorted(el.pitches, key=lambda p: p.ps)
        body = "".join(m21_pitch_to_abc(p) for p in ps)
        return f"[{body}]{quarter_to_abc_len(qlen, unit)}"
    if isinstance(el, note.Note):
        return f"{m21_pitch_to_abc(el.pitch)}{quarter_to_abc_len(qlen, unit)}"
    return ""


def tuplet_of(el):
    if hasattr(el, "duration") and el.duration.tuplets:
        return el.duration.tuplets[0]
    return None


def voice_bars(part, unit) -> list[str]:
    """Emit one ABC content string per measure (no '|' separators yet)."""
    bars = []
    measures = part.getElementsByClass(stream.Measure)
    for m in measures:
        toks = []
        try:
            elements = list(m.flatten().notesAndRests)
        except Exception:
            bars.append("z4")
            continue
        i = 0
        while i < len(elements):
            el = elements[i]
            tup = tuplet_of(el)
            if tup is not None:
                actual = tup.numberNotesActual or 3
                normal = tup.numberNotesNormal or 2
                ratio = Fraction(actual, normal)
                group = []
                j = i
                while j < len(elements) and len(group) < actual:
                    if tuplet_of(elements[j]) is not None:
                        group.append(elements[j])
                        j += 1
                    else:
                        break
                if len(group) == actual:
                    inner_toks = []
                    for g in group:
                        try:
                            displayed = Fraction(g.quarterLength) * ratio
                            t = emit_element(g, unit, qlen_override=displayed)
                        except Exception:
                            t = ""
                        if t:
                            inner_toks.append(t)
                    toks.append(f"({actual}" + " ".join(inner_toks))
                    i = j
                    continue
                for g in group:
                    try:
                        displayed = Fraction(g.quarterLength) * ratio
                        t = emit_element(g, unit, qlen_override=displayed)
                    except Exception:
                        t = ""
                    if t:
                        toks.append(t)
                i = j
                continue
            try:
                t = emit_element(el, unit)
            except Exception:
                t = ""
            if t:
                toks.append(t)
            i += 1
        bars.append(" ".join(toks) if toks else "z4")
    return bars


def count_bars(part) -> int:
    return len(list(part.getElementsByClass(stream.Measure)))


def synth_bass_bars(num_bars: int) -> list[str]:
    """At L:1/4 the bass walks D->F (bar n) then G->A (bar n+1), repeating.
    Octava-bassa clef so written D, sounds D2."""
    if num_bars <= 0:
        num_bars = 4
    pattern = ["D,2 F,,2", "G,,2 A,,2"]
    return [pattern[i % 2] for i in range(num_bars)]


def align_voices(treble_bars: list[str], bass_bars: list[str],
                 v1_header: str, v2_header: str) -> tuple[str, str]:
    """Pad both voices so bar separators line up vertically and the [V:N ...]
    headers are equal-width."""
    n = max(len(treble_bars), len(bass_bars))
    treble_bars = treble_bars + [""] * (n - len(treble_bars))
    bass_bars = bass_bars + [""] * (n - len(bass_bars))
    padded_t, padded_b = [], []
    for tb, bb in zip(treble_bars, bass_bars):
        w = max(len(tb), len(bb))
        padded_t.append(tb.ljust(w))
        padded_b.append(bb.ljust(w))
    head_w = max(len(v1_header), len(v2_header))
    v1 = f"[{v1_header.ljust(head_w)}] " + " | ".join(padded_t) + " |]"
    v2 = f"[{v2_header.ljust(head_w)}] " + " | ".join(padded_b) + " |]"
    return v1, v2


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

    key_str = detect_key(score)
    unit = Fraction(1, 1)  # L:1/4

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

    treble_bars = voice_bars(treble_part, unit)
    n_bars = count_bars(treble_part)
    bass_bars = synth_bass_bars(n_bars)
    v1, v2 = align_voices(treble_bars, bass_bars, "V:1", "V:2 clef=bass-8")

    abc = []
    abc.append(f"X:1")
    abc.append(f"T:Lick {lick_num} (D natural minor)")
    abc.append(f"M:C")
    abc.append(f"L:1/4")
    abc.append(f"Q:1/4=80")
    abc.append(f"%%pagewidth 8.5in")
    abc.append(f"%%barsperstaff 4")
    abc.append(f"K:{key_str}")
    abc.append(f"% Audiveris OMR; level={level}; scale={scale}; bars={n_bars}")
    abc.append(f"% Bass: synthesized D-F-G-A walk (octava bassa)")
    abc.append(v1)
    abc.append(v2)
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
