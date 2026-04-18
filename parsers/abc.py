"""ABC → typed Song/Piece (grammar/types).

Port of legacy hymn_parser.py + the parser-facing half of legacy export_hymn.py.
Produces grammar-native Song objects and grammar-conformant JSON.

Top-level API:
    parse_hymn(abc_text: str, title: str) -> Song
    parse_hymnal(abc_path: Path) -> Iterator[Song]
    hymn_slug(title: str) -> str
    song_to_json(song: Song) -> dict
    write_song_json(song: Song, out_dir: Path) -> Path

Patterns (NOT modules) are copied from legacy; this module never imports
from legacy.*.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Iterator, Optional

from music21 import (
    chord as m21chord,
    converter,
    key as m21key,
    note as m21note,
    roman as m21roman,
)

from grammar.parse import parse_roman
from grammar.types import (
    Bar,
    Key,
    Meter,
    Note,
    Phrase,
    Pitch,
    Rest,
    Roman,
    Song,
    Syllable,
    Tempo,
    Verse,
)


# ─────────────────────────────────────────────────────────────────────────────
#   Slug helper (lower-case, collapse non-alnum runs to '_')
# ─────────────────────────────────────────────────────────────────────────────
def hymn_slug(title: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_").lower()


# ─────────────────────────────────────────────────────────────────────────────
#   ABC tune extraction
# ─────────────────────────────────────────────────────────────────────────────
def extract_tune(abc_text: str, title_query: str) -> list[str]:
    """Return the ABC block (as lines) for the hymn matching title_query."""
    lines = abc_text.split("\n")
    t_line = None
    for i, line in enumerate(lines):
        if line.startswith("T:") and title_query.lower() in line.lower():
            t_line = i
            break
    if t_line is None:
        raise ValueError(f"Hymn not found: {title_query!r}")
    start = t_line
    for j in range(t_line, -1, -1):
        if lines[j].startswith("X:"):
            start = j
            break
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("X:"):
            end = j
            break
    return lines[start:end]


def iter_tunes(abc_text: str) -> Iterator[tuple[str, list[str]]]:
    """Yield (title, block_lines) for each tune in the ABC text."""
    lines = abc_text.split("\n")
    # Find X: positions
    x_positions = [i for i, line in enumerate(lines) if line.startswith("X:")]
    for idx, start in enumerate(x_positions):
        end = x_positions[idx + 1] if idx + 1 < len(x_positions) else len(lines)
        block = lines[start:end]
        title = None
        for h in block:
            if h.startswith("T:"):
                t = h[2:].strip()
                if t and not t.startswith("(also"):
                    title = t
                    break
        if title:
            yield title, block


# ─────────────────────────────────────────────────────────────────────────────
#   Voice splitting (3 ABC conventions)
# ─────────────────────────────────────────────────────────────────────────────
def split_voices(block: list[str], return_extras: bool = False):
    """Split ABC block into S1V1/S1V2/S2V1/S2V2 voices.

    Handles:
      (1) Standard 4-voice SATB — direct label mapping.
      (2) 2-staff piano reduction (S1+S2) with packed chords like [Ac] — splits
          each chord into top/bottom pitches for upper/lower voices.
      (3) 3-staff arrangement (S1 + S2V1/S2V2 + S3V*) — remap.
      (4) 3-voice with S1V1/S1V2 top divisi + single S2 bass.
    """
    headers = [l for l in block if re.match(r"^[XTMLKQ]:", l)]

    raw_voices: dict[str, list[str]] = {}
    current_voice: Optional[str] = None
    for line in block:
        m = re.match(r"^\[V:\s*(\S+)\]\s*(.*)$", line.rstrip())
        if m:
            current_voice = m.group(1)
            inline_content = m.group(2).strip()
            if inline_content:
                raw_voices.setdefault(current_voice, []).append(inline_content)
            continue
        if current_voice is not None:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("%"):
                if "%%endtext" in stripped or "%%begintext" in stripped:
                    current_voice = None
                continue
            if stripped.startswith("V:"):
                current_voice = None
                continue
            if stripped.startswith("w:"):
                continue
            if stripped.startswith('"'):
                continue
            if "|" not in stripped and not re.search(r"[A-Ga-gz][\d,',/]", stripped):
                continue
            raw_voices.setdefault(current_voice, []).append(line.strip())

    body = {"S1V1": [], "S1V2": [], "S2V1": [], "S2V2": []}
    extras: dict[str, list[str]] = {}

    present = set(raw_voices.keys())
    has_top_standard = "S1V1" in present or "S1V2" in present

    if has_top_standard:
        for v in body:
            if v in raw_voices:
                body[v] = raw_voices[v]
        if "S2" in present and "S2V1" not in present and "S2V2" not in present:
            body["S2V2"] = raw_voices["S2"]
    elif ({"S1", "S2"} <= present and not has_top_standard
          and not any(v.startswith("S3") for v in present)):
        body["S1V1"] = _split_chord_voice(raw_voices["S1"], which="top")
        body["S1V2"] = _split_chord_voice(raw_voices["S1"], which="bottom")
        body["S2V1"] = _split_chord_voice(raw_voices["S2"], which="top")
        body["S2V2"] = _split_chord_voice(raw_voices["S2"], which="bottom")
    elif "S1" in present and (
        "S2V1" in present or "S2V2" in present
        or any(v.startswith("S3") for v in present)
    ):
        body["S1V1"] = raw_voices.get("S1", [])
        body["S1V2"] = raw_voices.get("S2V1", [])
        body["S2V1"] = raw_voices.get("S2V2", [])
        body["S2V2"] = raw_voices.get("S3V1", [])
        for extra in ("S3V2", "S3V3"):
            if extra in raw_voices:
                extras[extra] = raw_voices[extra]
    else:
        for v in body:
            if v in raw_voices:
                body[v] = raw_voices[v]

    if return_extras:
        return headers, body, extras
    return headers, body


def _split_chord_voice(abc_lines, which="top"):
    result = []
    for line in abc_lines:
        def replace_chord(m):
            inner = m.group(1)
            duration = m.group(2)
            pitches = re.findall(r"[_^=]?[A-Ga-g][,']*\d*/?\d*", inner)
            if not pitches:
                return inner + duration

            def height(p):
                mm = re.match(r"[_^=]?([A-Ga-g])([,']*)", p)
                if not mm:
                    return 0
                letter, octave_marks = mm.groups()
                base = 4 if letter.isupper() else 5
                for c in octave_marks:
                    if c == ",":
                        base -= 1
                    elif c == "'":
                        base += 1
                pc = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11,
                      "c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}.get(letter, 0)
                return base * 12 + pc

            pitches_sorted = sorted(pitches, key=height)
            pick = pitches_sorted[-1] if which == "top" else pitches_sorted[0]
            pitch_clean = re.sub(r"\d.*$", "", pick)
            return pitch_clean + duration

        new_line = re.sub(
            r"\[(?![A-Z]:)([^\]]+)\](\d*/?\d*)", replace_chord, line
        )
        result.append(new_line)
    return result


def build_voice_abc(headers, body, voice):
    lines = []
    for pfx in ("X:", "T:", "M:", "L:", "K:"):
        lines += [h for h in headers if h.startswith(pfx)]
    lines += body[voice]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#   Fermata detection from raw ABC text (music21 drops !fermata!)
# ─────────────────────────────────────────────────────────────────────────────
def detect_fermata_bars(body, voice="S1V1", total_bars=None):
    if voice not in body or not body[voice]:
        return set()
    joined = " ".join(body[voice])
    joined = re.sub(r"\|[:\|\]]*", "|", joined)
    bars = joined.split("|")
    fermata_bars = set()
    for i, bar_content in enumerate(bars, start=1):
        if not bar_content.strip():
            continue
        if "!fermata!" in bar_content:
            fermata_bars.add(i)
    if total_bars is not None and fermata_bars:
        clamped = set()
        for b in fermata_bars:
            if b <= total_bars:
                clamped.add(b)
            else:
                clamped.add(total_bars)
        fermata_bars = clamped
    return fermata_bars


# ─────────────────────────────────────────────────────────────────────────────
#   Cadence detection
# ─────────────────────────────────────────────────────────────────────────────
def detect_cadence_bars(bar_regions, key_mode="major", halfbar_regions=None):
    if not bar_regions:
        return set()
    regions_to_use = halfbar_regions if halfbar_regions else bar_regions

    bar_rns: dict[int, list[tuple[int, str]]] = {}
    for r in regions_to_use:
        for b in range(r["start_bar"], r["end_bar"] + 1):
            bar_rns.setdefault(b, []).append(
                (r["start_beat"] if b == r["start_bar"] else 1, r["rn"])
            )

    bars_sorted = sorted(bar_rns.keys())
    if not bars_sorted:
        return set()

    def rn_letters_only(rn):
        m = re.match(r"^(b?[ivIV]+[°ø]?)", rn)
        return m.group(1) if m else rn

    def is_tonic(rn):
        return rn_letters_only(rn) in ("i", "I")

    def is_leading(rn, mode):
        base = rn_letters_only(rn)
        major_set = {"V", "IV", "iv", "ii", "vii", "vii°", "viiø"}
        minor_set = major_set | {"VII", "bVII", "III", "v"}
        return base in (minor_set if mode == "minor" else major_set)

    cadence_bars = set()
    for i, b in enumerate(bars_sorted):
        rns_in_bar = [rn for _, rn in bar_rns[b]]
        for j in range(1, len(rns_in_bar)):
            prev = rns_in_bar[j - 1]
            cur = rns_in_bar[j]
            if is_tonic(cur) and is_leading(prev, key_mode):
                cadence_bars.add(b)
                break
        if b in cadence_bars:
            continue
        if rns_in_bar and is_tonic(rns_in_bar[0]):
            if i > 0:
                prev_bar_rns = [rn for _, rn in bar_rns[bars_sorted[i - 1]]]
                if prev_bar_rns and is_leading(prev_bar_rns[-1], key_mode):
                    cadence_bars.add(b)

    # Half cadences
    bar_level_rn = {}
    for r in bar_regions:
        for b in range(r["start_bar"], r["end_bar"] + 1):
            bar_level_rn[b] = r["rn"]

    def is_dominant(rn):
        return rn_letters_only(rn) == "V"

    def is_predominant(rn, mode):
        base = rn_letters_only(rn)
        major_set = {"I", "ii", "IV", "vi"}
        minor_set = {"i", "ii°", "iv", "VI", "III"}
        return base in (minor_set if mode == "minor" else major_set)

    half_cad = []
    sorted_bars = sorted(bar_level_rn.keys())
    for i, b in enumerate(sorted_bars):
        if i == 0:
            continue
        cur = bar_level_rn[b]
        prev = bar_level_rn[sorted_bars[i - 1]]
        if is_dominant(cur) and is_predominant(prev, key_mode):
            half_cad.append(b)

    min_spacing = 3
    for cand in half_cad:
        if any(abs(cand - e) < min_spacing for e in cadence_bars):
            continue
        cadence_bars.add(cand)

    cadence_bars.add(bars_sorted[-1])
    return cadence_bars


def split_into_phrases(bar_regions, fermata_bars, cadence_bars, min_phrase_length=2):
    if not bar_regions:
        return []
    all_bars = sorted(
        {b for r in bar_regions
         for b in range(r["start_bar"], r["end_bar"] + 1)}
    )
    if not all_bars:
        return []
    boundaries = set(fermata_bars or set()) | set(cadence_bars or set())
    if not boundaries:
        boundaries = set(all_bars[3::4]) | {all_bars[-1]}
    boundaries = boundaries | {all_bars[-1]}

    phrases = []
    cur_bars = []
    label_idx = 0
    for b in all_bars:
        cur_bars.append(b)
        if b in boundaries and len(cur_bars) >= min_phrase_length:
            label = chr(ord("A") + label_idx)
            marker = (
                "fermata" if b in fermata_bars
                else ("cadence" if b in cadence_bars else "auto")
            )
            phrases.append({
                "label": label,
                "bars": list(cur_bars),
                "ending_marker": marker,
            })
            cur_bars = []
            label_idx += 1
    if cur_bars:
        if phrases and len(cur_bars) < min_phrase_length:
            phrases[-1]["bars"] += cur_bars
        else:
            label = chr(ord("A") + label_idx)
            phrases.append({
                "label": label,
                "bars": list(cur_bars),
                "ending_marker": "end",
            })
    return phrases


# ─────────────────────────────────────────────────────────────────────────────
#   Beat-by-beat SATB sampling
# ─────────────────────────────────────────────────────────────────────────────
def sample_satb(voices_parsed, beat_unit_ql=1.0):
    mel = voices_parsed["S1V1"]
    if not mel:
        return [], 0.0
    total_ql = float(mel[-1].offset) + float(mel[-1].duration.quarterLength)

    def pitch_at(voice, t):
        for n in voices_parsed.get(voice, []):
            start = float(n.offset)
            end = start + float(n.duration.quarterLength)
            if start <= t < end:
                if isinstance(n, m21note.Rest):
                    return None
                return n
        return None

    samples = []
    n_beats = int(total_ql / beat_unit_ql)
    for i in range(n_beats):
        t = i * beat_unit_ql
        samples.append((
            t,
            pitch_at("S1V1", t),
            pitch_at("S1V2", t),
            pitch_at("S2V1", t),
            pitch_at("S2V2", t),
        ))
    return samples, total_ql


# ─────────────────────────────────────────────────────────────────────────────
#   Non-chord-tone detection
# ─────────────────────────────────────────────────────────────────────────────
def _is_passing_tone(p0, p1, p2):
    from music21 import interval as m21interval
    if p0 is None or p1 is None or p2 is None:
        return False
    i1 = m21interval.Interval(p0, p1).semitones
    i2 = m21interval.Interval(p1, p2).semitones
    return abs(i1) in (1, 2) and abs(i2) in (1, 2) and (i1 > 0) == (i2 > 0)


def _is_neighbor_tone(p0, p1, p2):
    from music21 import interval as m21interval
    if p0 is None or p1 is None or p2 is None:
        return False
    if p0.nameWithOctave != p2.nameWithOctave:
        return False
    return abs(m21interval.Interval(p0, p1).semitones) in (1, 2)


# ─────────────────────────────────────────────────────────────────────────────
#   Clean music21's roman-numeral output
# ─────────────────────────────────────────────────────────────────────────────
CLEAN_RN = {
    "V752": "V7",
    "V542": "V7",
    "V432": "V7",
    "ii542": "V",
    "ii752": "V7",
    "I753": "I7",
    "I64": "I64",
    "IV64": "IV64",
    "iii6": "V7",
}

MAJOR_DIATONIC = {"I": "I", "II": "ii", "III": "iii", "IV": "IV",
                  "V": "V", "VI": "vi", "VII": "vii°"}
MINOR_DIATONIC = {"I": "i", "II": "ii°", "III": "III", "IV": "iv",
                  "V": "V", "VI": "VI", "VII": "VII"}


def _enforce_diatonic_quality(rn_figure, key_mode="major"):
    m = re.match(r"^([#b]?)([ivIV]+)([oø°Δ]?)(\d*)(.*)$", rn_figure)
    if not m:
        return rn_figure
    acc, numerals, quality, ext, rest = m.groups()
    upper = numerals.upper()
    diatonic = MAJOR_DIATONIC if key_mode == "major" else MINOR_DIATONIC
    if upper not in diatonic:
        return rn_figure
    correct = diatonic[upper]
    cm = re.match(r"^([ivIV]+)([oø°Δ]?)$", correct)
    if cm:
        correct_num, correct_qual = cm.groups()
        final_qual = quality if quality else correct_qual
        return f"{acc}{correct_num}{final_qual}{ext}"
    return rn_figure


def clean_rn(rn_figure, key_mode="major"):
    if rn_figure in CLEAN_RN:
        result = CLEAN_RN[rn_figure]
    else:
        m = re.match(r"^([#b]?[ivIV]+[oø°Δ]?)(\d*)(.*)$", rn_figure)
        if m:
            base, ext, rest = m.groups()
            if len(ext) > 2:
                ext = ext[:1]
            result = base + ext
        else:
            result = rn_figure
    return _enforce_diatonic_quality(result, key_mode)


# ─────────────────────────────────────────────────────────────────────────────
#   Normalize a cleaned RN so grammar.parse_roman accepts it.
# ─────────────────────────────────────────────────────────────────────────────
# Figured-bass inversion codes (music21 style) → grammar inversion superscript.
_FIGURED_INVERSION = {
    # Triads
    "6":   ("",   "¹"),    # V6 → V¹
    "64":  ("",   "²"),    # V64 → V²
    # Seventh chords (attached to base triad root; music21 omits the '7'):
    # V65 = V7 first inversion, V43 = V7 second, V42 = V7 third.
    "65":  ("7",  "¹"),
    "43":  ("7",  "²"),
    "42":  ("7",  "³"),
    "7":   ("7",  None),   # V7 plain
    # '753' etc. normalized already via CLEAN_RN; leave others raw
}


def normalize_for_grammar(rn: str) -> str:
    """Translate a cleaned music21-style RN string into the grammar-compatible
    form accepted by grammar.parse.parse_roman.

    Examples:
        'V65'   -> 'V7¹'
        'V43'   -> 'V7²'
        'V42'   -> 'V7³'
        'I6'    -> 'I¹'
        'I64'   -> 'I²'
        'vii°'  -> 'vii○'
        'viio'  -> 'vii○'
        'ii°'   -> ValueError-safe: dropped to 'ii' (diatonic ii° lives under
                    grammar 'ii○' only in the 7-chord family; triad ii° has
                    no grammar spelling beyond 'ii○' either, so we map it).
        'bVII'  -> 'VII' (flat marker not in grammar vocabulary; this keeps
                    parse_roman from failing; in practice minor-mode bVII is
                    just the diatonic VII of aeolian)

    The goal is a best-effort lossless mapping where possible and a graceful
    degradation where the grammar doesn't support the symbol.
    """
    if not rn or rn == "—":
        return "I"  # placeholder tonic; empty/unknown → neutral fallback

    s = rn.strip()

    # Strip leading '#' / 'b' chromatic accidentals (grammar is strictly diatonic).
    if s and s[0] in "#b":
        s = s[1:]

    # Normalize diminished glyphs: music21 emits 'o' or '°'; grammar uses '○'.
    s = s.replace("°", "○").replace("ø", "ø")  # ø already matches grammar
    # Replace 'o' (letter) after a numeral with '○' (diminished circle).
    # Only do this when it's the diminished marker (i.e. directly after 'vii' / 'ii').
    s = re.sub(r"(vii|ii|VII|II)o(?=\d|$)", r"\1○", s)

    # Map figured-bass digits to grammar inversion.
    # Find numeral prefix (with optional ○/ø).
    m = re.match(r"^([ivIV]+[○ø]?)(\d+)(.*)$", s)
    if m:
        head, digits, tail = m.group(1), m.group(2), m.group(3)
        if digits in _FIGURED_INVERSION:
            qual, inv = _FIGURED_INVERSION[digits]
            out = head + qual
            if inv:
                out += inv
            return out + tail
        # Unknown digit pattern — truncate to first digit and hope it's a 7
        if digits[0] == "7":
            return head + "7" + tail
        # Fall through: strip extra digits
        return head + tail

    return s


def safe_parse_roman(rn_str: str) -> Roman:
    """Parse a cleaned RN via grammar.parse.parse_roman, normalizing first.

    Guaranteed never to raise: unparseable symbols fall back to Roman('I')
    so downstream code always gets a typed object. The fallback is the same
    tonic-placeholder convention used by the legacy `—` sentinel.
    """
    try:
        return parse_roman(normalize_for_grammar(rn_str))
    except Exception:
        return Roman(numeral="I", quality=None, inversion=None)


# ─────────────────────────────────────────────────────────────────────────────
#   Mode detection
# ─────────────────────────────────────────────────────────────────────────────
def detect_mode(new_tonic_pc: int, header_scale_pcs: set[int]) -> str:
    intervals = sorted((p - new_tonic_pc) % 12 for p in header_scale_pcs)
    patterns = {
        (0, 2, 4, 5, 7, 9, 11): "ionian",
        (0, 2, 3, 5, 7, 9, 10): "dorian",
        (0, 1, 3, 5, 7, 8, 10): "phrygian",
        (0, 2, 4, 6, 7, 9, 11): "lydian",
        (0, 2, 4, 5, 7, 9, 10): "mixolydian",
        (0, 2, 3, 5, 7, 8, 10): "aeolian",
        (0, 1, 3, 5, 6, 8, 10): "locrian",
    }
    return patterns.get(tuple(intervals), "unknown")


# ─────────────────────────────────────────────────────────────────────────────
#   Tonic detection: weighted vote across 6 signals (legacy algorithm).
# ─────────────────────────────────────────────────────────────────────────────
def detect_true_tonic(voices_parsed, K_header):
    bass_voice = None
    bass_lowest = 999
    for v_name, notes_list in voices_parsed.items():
        nn = [n for n in notes_list if isinstance(n, m21note.Note)]
        if not nn:
            continue
        avg = sum(n.pitch.midi for n in nn) / len(nn)
        if avg < bass_lowest:
            bass_lowest = avg
            bass_voice = v_name
    if not bass_voice:
        return K_header

    bass_notes = [n for n in voices_parsed[bass_voice]
                  if isinstance(n, m21note.Note)]
    if not bass_notes:
        return K_header

    mel_notes = []
    if "S1V1" in voices_parsed:
        mel_notes = [n for n in voices_parsed["S1V1"]
                     if isinstance(n, m21note.Note)]

    votes: dict[int, int] = {}

    def vote(pc, weight):
        if pc is not None:
            votes[pc] = votes.get(pc, 0) + weight

    vote(bass_notes[0].pitch.pitchClass, 1)
    vote(bass_notes[-1].pitch.pitchClass, 3)
    if mel_notes:
        vote(mel_notes[0].pitch.pitchClass, 1)
        vote(mel_notes[-1].pitch.pitchClass, 3)
    pc_count: dict[int, int] = {}
    for n in bass_notes:
        pc = n.pitch.pitchClass
        pc_count[pc] = pc_count.get(pc, 0) + 1
    most_common = max(pc_count, key=pc_count.get)
    vote(most_common, 1)
    header_pc = K_header.tonic.pitchClass
    vote(header_pc, 1)

    winner_pc = max(votes, key=votes.get)
    if winner_pc == header_pc:
        return K_header

    new_tonic_pitch = None
    for n in bass_notes + mel_notes:
        if n.pitch.pitchClass == winner_pc:
            new_tonic_pitch = n.pitch
            break
    if new_tonic_pitch is None:
        return K_header

    header_scale_pcs = {p.pitchClass for p in K_header.pitches}
    major_third_pc = (winner_pc + 4) % 12
    minor_third_pc = (winner_pc + 3) % 12
    has_M3 = major_third_pc in header_scale_pcs
    has_m3 = minor_third_pc in header_scale_pcs
    new_name = new_tonic_pitch.name
    if has_M3 and not has_m3:
        return m21key.Key(new_name, "major")
    elif has_m3 and not has_M3:
        return m21key.Key(new_name, "minor")
    elif has_m3 and has_M3:
        return m21key.Key(new_name, "minor")
    else:
        return K_header


# ─────────────────────────────────────────────────────────────────────────────
#   Beat-level analysis
# ─────────────────────────────────────────────────────────────────────────────
def analyze_beats(samples, K, key_mode="major", beats_per_bar=2):
    results = []
    mel_pitches = [s[1].pitch if s[1] else None for s in samples]
    for i, (t, m, a, tn, b) in enumerate(samples):
        bar = i // beats_per_bar + 1
        beat = i % beats_per_bar + 1
        nct = False
        if 0 < i < len(samples) - 1 and mel_pitches[i]:
            if _is_passing_tone(mel_pitches[i - 1], mel_pitches[i], mel_pitches[i + 1]):
                nct = True
            elif _is_neighbor_tone(mel_pitches[i - 1], mel_pitches[i], mel_pitches[i + 1]):
                nct = True
        chord_pitches = [p for p in (b, tn, a) if p is not None]
        if not nct and m is not None:
            chord_pitches.append(m)
        rn_raw = "—"
        rn_clean = "—"
        if chord_pitches:
            c = m21chord.Chord([p.pitch for p in chord_pitches])
            try:
                rn = m21roman.romanNumeralFromChord(c, K)
                rn_raw = rn.figure
                rn_clean = clean_rn(rn_raw, key_mode)
            except Exception:
                pass
        results.append({
            "bar": bar, "beat": beat, "offset": t,
            "rn_raw": rn_raw, "rn_clean": rn_clean, "nct": nct,
        })
    return results


def aggregate_regions(beats):
    if not beats:
        return []
    regions = []
    cur = {
        "start_bar": beats[0]["bar"], "start_beat": beats[0]["beat"],
        "end_bar": beats[0]["bar"], "end_beat": beats[0]["beat"],
        "rn": beats[0]["rn_clean"], "length": 1,
    }
    for b in beats[1:]:
        if b["rn_clean"] == cur["rn"]:
            cur["end_bar"] = b["bar"]
            cur["end_beat"] = b["beat"]
            cur["length"] += 1
        else:
            regions.append(cur)
            cur = {
                "start_bar": b["bar"], "start_beat": b["beat"],
                "end_bar": b["bar"], "end_beat": b["beat"],
                "rn": b["rn_clean"], "length": 1,
            }
    regions.append(cur)
    return regions


SIMPLE_FUNCS = {
    "I", "IV", "V", "V7", "vi", "ii", "iii", "I6", "IV6",
    "V6", "vi6", "ii6", "I64", "IV64", "V65", "V43", "V42",
    "i", "iv", "v", "III", "VI", "VII",
}
NOISE_PATTERNS = (
    r"#", r"^b(?!vii°$)", r"\d{2,}(?!$)", r"42$", r"54$",
    r"65$", r"5$", r"\(no", r"incomplete",
)


def is_noise(rn):
    if rn in SIMPLE_FUNCS:
        return False
    for pat in NOISE_PATTERNS:
        if re.search(pat, rn):
            return True
    return False


def smooth_regions(regions, min_kept_length=2):
    if len(regions) < 3:
        return regions
    result = [regions[0]]
    i = 1
    while i < len(regions) - 1:
        prev, cur, nxt = result[-1], regions[i], regions[i + 1]
        if (cur["length"] == 1 and is_noise(cur["rn"])
                and prev["rn"] == nxt["rn"]):
            prev["end_bar"] = nxt["end_bar"]
            prev["end_beat"] = nxt["end_beat"]
            prev["length"] += cur["length"] + nxt["length"]
            i += 2
            continue
        result.append(cur)
        i += 1
    if i == len(regions) - 1:
        result.append(regions[-1])
    result2 = []
    for r in result:
        if (r["length"] == 1 and is_noise(r["rn"]) and result2
                and not is_noise(result2[-1]["rn"])):
            result2[-1]["end_bar"] = r["end_bar"]
            result2[-1]["end_beat"] = r["end_beat"]
            result2[-1]["length"] += 1
        else:
            result2.append(r)
    return result2


def downsample_per_bar(beats, beats_per_bar, slots_per_bar=1):
    if not beats:
        return []
    bars: dict[int, list] = {}
    for b in beats:
        bars.setdefault(b["bar"], []).append(b)

    regions = []
    slot_size = beats_per_bar // slots_per_bar
    if slot_size < 1:
        slot_size = 1

    for bar_num in sorted(bars.keys()):
        bar_beats = bars[bar_num]
        for slot_idx in range(slots_per_bar):
            slot_start_beat = slot_idx * slot_size + 1
            slot_end_beat = min((slot_idx + 1) * slot_size, beats_per_bar)
            slot_beats = [b for b in bar_beats
                          if slot_start_beat <= b["beat"] <= slot_end_beat]
            if not slot_beats:
                continue
            vote: dict[str, float] = {}
            for b in slot_beats:
                weight = 2 if b["beat"] == slot_start_beat else 1
                if is_noise(b["rn_clean"]):
                    weight = 0.3
                vote[b["rn_clean"]] = vote.get(b["rn_clean"], 0) + weight
            if not vote:
                continue
            winner = max(vote, key=vote.get)
            regions.append({
                "start_bar": bar_num,
                "start_beat": slot_start_beat,
                "end_bar": bar_num,
                "end_beat": slot_end_beat,
                "rn": winner,
                "length": len(slot_beats),
            })
    collapsed = [regions[0]] if regions else []
    for r in regions[1:]:
        if r["rn"] == collapsed[-1]["rn"]:
            collapsed[-1]["end_bar"] = r["end_bar"]
            collapsed[-1]["end_beat"] = r["end_beat"]
            collapsed[-1]["length"] += r["length"]
        else:
            collapsed.append(r)
    return collapsed


# ─────────────────────────────────────────────────────────────────────────────
#   Pitch / Note / Rest conversion (music21 → grammar types)
# ─────────────────────────────────────────────────────────────────────────────
_ACCIDENTAL_MAP = {"sharp": "♯", "flat": "♭", "double-sharp": "♯",
                   "double-flat": "♭", "natural": None}


def _m21_pitch_to_grammar(p) -> Pitch:
    letter = p.step  # 'A'..'G'
    acc = None
    if p.accidental is not None:
        acc = _ACCIDENTAL_MAP.get(p.accidental.name)
    return Pitch(letter=letter, accidental=acc, octave=int(p.octave))


def _event_to_melody(n) -> Note | Rest:
    dur = float(n.duration.quarterLength)
    if isinstance(n, m21note.Rest):
        return Rest(duration=dur)
    if isinstance(n, m21chord.Chord):
        top = max(n.pitches, key=lambda p: p.midi)
        return Note(pitch=_m21_pitch_to_grammar(top), duration=dur, ornaments=())
    return Note(pitch=_m21_pitch_to_grammar(n.pitch), duration=dur, ornaments=())


# ─────────────────────────────────────────────────────────────────────────────
#   Lyric alignment (per-bar/note syllable references)
# ─────────────────────────────────────────────────────────────────────────────
def _detect_melody_voice_label(block):
    current_voice = None
    w_counts: dict[str, int] = {}
    for line in block:
        m = re.match(r"^\[V:\s*(\S+)\]", line)
        if m:
            current_voice = m.group(1)
            continue
        if line.startswith("w:") and current_voice:
            w_counts[current_voice] = w_counts.get(current_voice, 0) + 1
    if w_counts:
        return max(w_counts, key=w_counts.get)
    seen = []
    for line in block:
        m = re.match(r"^\[V:\s*(\S+)\]", line)
        if m and m.group(1) not in seen:
            seen.append(m.group(1))
    if "S1V1" in seen:
        return "S1V1"
    if "S1" in seen:
        return "S1"
    return seen[0] if seen else "S1V1"


def _tokenize_syllables(raw: str):
    raw = raw.replace("~", "\u00a0")
    parts = raw.split()
    tokens = []
    for p in parts:
        if p in ("*", "_"):
            tokens.append({"text": "", "continues_previous": True})
        elif p == "|":
            pass
        else:
            has_trailing_hyphen = p.endswith("-")
            text = p.rstrip("-").replace("\u00a0", " ")
            tokens.append({
                "text": text,
                "continues_previous": False,
                "joins_next": has_trailing_hyphen,
            })
    return tokens


def _extract_verses(block, melody_voice_raw_events, melody_label="S1V1") -> list[Verse]:
    """Extract lyrics and align to melody Note/Chord events. Returns a list
    of grammar-typed Verse objects with per-syllable (ibar, inote, text, melisma).
    """
    melody_marker = f"[V: {melody_label}]"
    line_groups = []
    cur_mel_idx = -1
    collecting = False
    cur_wlines: list[str] = []

    for line in block:
        if line.startswith(melody_marker) or line.rstrip() == f"[V:{melody_label}]":
            if cur_wlines:
                line_groups.append((cur_mel_idx, cur_wlines))
            cur_mel_idx += 1
            cur_wlines = []
            collecting = True
        elif line.startswith("[V:"):
            if cur_wlines:
                line_groups.append((cur_mel_idx, cur_wlines))
                cur_wlines = []
            collecting = False
        elif line.startswith("w:") and collecting:
            cur_wlines.append(line[2:].strip())
        elif line.startswith("%") and cur_wlines:
            line_groups.append((cur_mel_idx, cur_wlines))
            cur_wlines = []
            collecting = False
    if cur_wlines:
        line_groups.append((cur_mel_idx, cur_wlines))

    max_verses = max((len(wl) for _, wl in line_groups), default=0)
    if max_verses == 0:
        return []
    verses_syl_lists: dict[int, list[list[dict]]] = {
        v: [] for v in range(1, max_verses + 1)
    }

    for mel_idx, wlines in line_groups:
        if not wlines:
            continue
        if len(wlines) == 1 and max_verses > 1:
            raw = wlines[0]
            stripped = re.sub(r"^\d+\.?[~\s]+", "", raw)
            syllables = _tokenize_syllables(stripped)
            for v in range(1, max_verses + 1):
                verses_syl_lists[v].append(syllables)
        else:
            for v_idx, raw in enumerate(wlines):
                v = v_idx + 1
                stripped = re.sub(r"^\d+\.?[~\s]+", "", raw)
                syllables = _tokenize_syllables(stripped)
                verses_syl_lists.setdefault(v, []).append(syllables)

    # Align to melody notes/chords (skip rests). For tied-continuation notes,
    # emit a melisma syllable with empty text.
    melody_events = [
        n for n in melody_voice_raw_events
        if isinstance(n, (m21note.Note, m21chord.Chord))
    ]
    is_tie_continuation = []
    for n in melody_events:
        t = n.tie
        is_tie_continuation.append(
            t is not None and getattr(t, "type", None) in ("continue", "stop")
        )

    verses: list[Verse] = []
    for v in range(1, max_verses + 1):
        all_syl: list[dict] = []
        for lst in verses_syl_lists[v]:
            all_syl.extend(lst)
        syls: list[Syllable] = []
        syl_idx = 0
        inote_in_bar: dict[int, int] = {}
        for note_idx, n in enumerate(melody_events):
            offset = float(n.offset)
            bar_1based = int(offset // _BEATS_PER_BAR_GLOBAL.get("bpb", 4)) + 1
            ino = inote_in_bar.get(bar_1based, 0)
            inote_in_bar[bar_1based] = ino + 1

            if is_tie_continuation[note_idx]:
                syls.append(Syllable(ibar=bar_1based, inote=ino, text="", melisma=True))
                continue
            if syl_idx >= len(all_syl):
                syls.append(Syllable(ibar=bar_1based, inote=ino, text="", melisma=False))
                continue
            tok = all_syl[syl_idx]
            melisma = bool(tok.get("continues_previous"))
            syls.append(Syllable(
                ibar=bar_1based, inote=ino,
                text=tok["text"], melisma=melisma,
            ))
            syl_idx += 1

        verses.append(Verse(syllables=tuple(syls)))
    return verses


# Mutable side-channel so the lyric extractor gets the right beats-per-bar
# without threading it through every helper. Set by parse_hymn before use.
_BEATS_PER_BAR_GLOBAL: dict[str, int] = {"bpb": 4}


# ─────────────────────────────────────────────────────────────────────────────
#   Top-level parse API
# ─────────────────────────────────────────────────────────────────────────────
def _key_root_normalized(k: m21key.Key) -> str:
    """Return key root as 'Bb' / 'F#' / 'C' (human form)."""
    name = k.tonic.name  # e.g. 'B-', 'F#', 'C'
    return name.replace("-", "b")


def parse_hymn(abc_text: str, title: str) -> Song:
    """Parse one hymn from ABC text → typed Song.

    abc_text may be the full hymnal (extract_tune will locate the title) or
    a single-tune block.
    """
    block = extract_tune(abc_text, title)
    headers, body, extras = split_voices(block, return_extras=True)

    # Title
    real_title = title
    for h in headers:
        if h.startswith("T:"):
            real_title = h[2:].strip()
            break

    # Key / meter headers
    key_line = next((h for h in headers if h.startswith("K:")), "K: C")
    meter_line = next((h for h in headers if h.startswith("M:")), "M: 4/4")
    tempo_line = next((h for h in headers if h.startswith("Q:")), None)

    key_match = re.match(r"K:\s*([A-G][b#]?m?(?:aj|in)?)", key_line)
    key_str = key_match.group(1) if key_match else "C"
    K_header = m21key.Key(key_str.rstrip("maj").rstrip("in"))

    meter_match = re.search(r"M:\s*(\d+)/(\d+)", meter_line)
    meter_num = int(meter_match.group(1)) if meter_match else 4
    meter_den = int(meter_match.group(2)) if meter_match else 4

    # Parse voices through music21. Normalize Chord→Note (upper/lower).
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

    # Tempo — best-effort parse (Q: tag forms vary widely).
    tempo_value = 90
    tempo_unit = 4
    if tempo_line:
        m_q = re.search(r"(\d+)/(\d+)\s*=\s*(\d+)", tempo_line)
        if m_q:
            tempo_unit = int(m_q.group(2))
            tempo_value = int(m_q.group(3))
        else:
            m_q2 = re.search(r"=?\s*(\d+)", tempo_line)
            if m_q2:
                tempo_value = int(m_q2.group(1))

    # Empty-melody fallback: nothing to analyze.
    if not voices_parsed.get("S1V1"):
        return Song(
            title=real_title,
            key=Key(root=_key_root_normalized(K_header),
                    mode="minor" if K_header.mode == "minor" else "major"),
            meter=Meter(beats=meter_num, unit=meter_den),  # type: ignore[arg-type]
            tempo=Tempo(value=tempo_value, unit=tempo_unit),  # type: ignore[arg-type]
            bars=(),
            phrases=(),
            verses=(),
        )

    # True tonic (weighted vote).
    K = detect_true_tonic(voices_parsed, K_header)
    key_mode = "minor" if K.mode == "minor" else "major"
    header_scale_pcs = {p.pitchClass for p in K_header.pitches}
    modal_name = detect_mode(K.tonic.pitchClass, header_scale_pcs)

    # Beat-level + per-bar RN regions (music21-based).
    samples, total_ql = sample_satb(voices_parsed)
    beats = analyze_beats(samples, K, key_mode, meter_num)
    bar_regions = downsample_per_bar(beats, meter_num, slots_per_bar=1)
    halfbar_regions = downsample_per_bar(beats, meter_num, slots_per_bar=2)
    total_bars = max((b["bar"] for b in beats), default=0)

    # Phrases.
    fermata_bars = detect_fermata_bars(body, total_bars=total_bars)
    cadence_bars = detect_cadence_bars(bar_regions, key_mode, halfbar_regions)
    phrase_dicts = split_into_phrases(bar_regions, fermata_bars, cadence_bars)

    # Build grammar-typed Bars from S1V1 melody events, one per bar index.
    # Note offsets are quarter-lengths. `bar_index = int(offset // meter_num) + 1`.
    melody_raw_events = voices_raw["S1V1"]
    bar_to_events: dict[int, list] = {}
    for n in melody_raw_events:
        offset = float(n.offset)
        bar = int(offset // meter_num) + 1
        bar_to_events.setdefault(bar, []).append(n)

    # bar → Roman assignment from per-bar regions
    bar_to_rn_str: dict[int, str] = {r["start_bar"]: r["rn"] for r in bar_regions}

    n_bars = max(total_bars, max(bar_to_events.keys(), default=0))
    bars_tuple: list[Bar] = []
    for ibar in range(1, n_bars + 1):
        events = bar_to_events.get(ibar, [])
        melody = tuple(_event_to_melody(n) for n in events)
        rn_str = bar_to_rn_str.get(ibar, "I")
        chord = safe_parse_roman(rn_str)
        bars_tuple.append(Bar(
            melody=melody,
            chord=chord,
            voicing=None,
            technique=None,
        ))

    # Phrases → typed Phrase objects (path inferred later by mapper).
    phrases = tuple(
        Phrase(ibars=tuple(p["bars"]), path=None)
        for p in phrase_dicts
    )

    # Lyrics — need beats-per-bar in the helper (offset → bar index).
    _BEATS_PER_BAR_GLOBAL["bpb"] = meter_num
    melody_label = _detect_melody_voice_label(block)
    verses = tuple(_extract_verses(block, voices_raw["S1V1"], melody_label))

    # Stash the raw ABC source and modal_name on the Song via a sidecar dict
    # (grammar.types.Song doesn't carry arbitrary kv; we attach attrs).
    song = Song(
        title=real_title,
        key=Key(root=_key_root_normalized(K),
                mode="minor" if K.mode == "minor" else "major"),
        meter=Meter(beats=meter_num, unit=meter_den),  # type: ignore[arg-type]
        tempo=Tempo(value=tempo_value, unit=tempo_unit),  # type: ignore[arg-type]
        bars=tuple(bars_tuple),
        phrases=phrases,
        verses=verses,
    )
    # Attach non-grammar metadata (so song_to_json can surface it).
    setattr(song, "_abc_source", "\n".join(block))
    setattr(song, "_modal_name", modal_name)
    return song


def parse_hymnal(abc_path: Path) -> Iterator[Song]:
    """Yield a Song for every hymn in the ABC file. Failures are skipped
    with a warning printed to stderr."""
    import sys
    text = Path(abc_path).read_text()
    for title, block in iter_tunes(text):
        try:
            yield parse_hymn(text, title)
        except Exception as e:
            print(f"  ! skip {title!r}: {e}", file=sys.stderr)


# ─────────────────────────────────────────────────────────────────────────────
#   Serialization (Song → JSON-safe dict)
# ─────────────────────────────────────────────────────────────────────────────
def _dict_of_pitch(p: Pitch) -> dict:
    return {"letter": p.letter, "accidental": p.accidental, "octave": p.octave}


def _dict_of_melody_event(e) -> dict:
    if isinstance(e, Rest):
        return {"kind": "rest", "duration": e.duration, "ornaments": []}
    return {
        "kind": "note",
        "pitch": _dict_of_pitch(e.pitch),
        "duration": e.duration,
        "ornaments": list(e.ornaments),
    }


def _dict_of_roman(r: Roman) -> dict:
    return {
        "numeral": r.numeral,
        "quality": r.quality,
        "inversion": r.inversion,
    }


def _dict_of_bar(b: Bar) -> dict:
    d = {
        "melody": [_dict_of_melody_event(e) for e in b.melody],
        "chord": _dict_of_roman(b.chord),
        "voicing": None,
        "technique": b.technique,
    }
    return d


def _dict_of_phrase(p: Phrase) -> dict:
    return {"ibars": list(p.ibars), "path": p.path}


def _dict_of_verse(v: Verse) -> dict:
    return {
        "syllables": [
            {"ibar": s.ibar, "inote": s.inote,
             "text": s.text, "melisma": s.melisma}
            for s in v.syllables
        ],
    }


def song_to_json(song: Song) -> dict:
    """Grammar-conformant JSON dict for one hymn."""
    d: dict = {
        "title": song.title,
        "key": {"root": song.key.root, "mode": song.key.mode},
        "meter": {"beats": song.meter.beats, "unit": song.meter.unit},
        "tempo": {"value": song.tempo.value, "unit": song.tempo.unit},
        "bars": [_dict_of_bar(b) for b in song.bars],
        "phrases": [_dict_of_phrase(p) for p in song.phrases],
        "verses": [_dict_of_verse(v) for v in song.verses],
    }
    abc = getattr(song, "_abc_source", None)
    if abc is not None:
        d["_abc_source"] = abc
    modal = getattr(song, "_modal_name", None)
    if modal and modal != "unknown":
        d["_modal_name"] = modal
    return d


def write_song_json(song: Song, out_dir: Path) -> Path:
    """Write song JSON to out_dir/<slug>.json and return the path."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{hymn_slug(song.title)}.json"
    with path.open("w") as f:
        json.dump(song_to_json(song), f, indent=2, default=str)
    return path
