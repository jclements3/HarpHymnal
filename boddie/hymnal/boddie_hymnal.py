#!/usr/bin/env python3
"""Boddie Hymnal -- arrange a hymn in the Brook Boddie style.

Reads a HarpHymnal per-bar JSON (data/hymns/<slug>.json) and emits a
grand-staff ABC file. Single output style -- no level argument.

Style fingerprints (see BODDIE.md):
  - Q=72 "Slowly, with great expression"
  - LH: bass note on beat 1 + ascending eighth-note arpeggio of chord
    tones for the rest of the bar
  - LH opening bar: drone octave (C1-C2 range) + arpeggio
  - LH cadence bar: wide-spread rolled chord, held full bar
  - LH final bar: wide-spread rolled chord with C1-C2 drone octave below
  - RH: melody passed through, octave-doubled on cadence bars
  - RH final note: rolled (!arpeggio!) and fermata
  - !breath! at the last note of every non-final phrase
  - Harmony: triads lifted to diatonic 7ths (Reharm L2 pool)

Reuses pitch/duration utilities from reharm_hymnal.py without importing
to avoid a hard cross-project dep -- duplicated like Retab/Reharm do.
"""
from __future__ import annotations
import copy
import json
import re
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Diatonic scale utilities (duplicated from reharm/retab; stays in sync by hand)

LETTERS = ["C", "D", "E", "F", "G", "A", "B"]

KEY_SIG = {
    "C":  ([], []),
    "G":  (["F"], []),
    "D":  (["F", "C"], []),
    "A":  (["F", "C", "G"], []),
    "E":  (["F", "C", "G", "D"], []),
    "B":  (["F", "C", "G", "D", "A"], []),
    "F#": (["F", "C", "G", "D", "A", "E"], []),
    "F":  ([], ["B"]),
    "Bb": ([], ["B", "E"]),
    "Eb": ([], ["B", "E", "A"]),
    "Ab": ([], ["B", "E", "A", "D"]),
    "Db": ([], ["B", "E", "A", "D", "G"]),
    "Gb": ([], ["B", "E", "A", "D", "G", "C"]),
}

ROMAN_TO_DEGREE = {
    "I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5, "vii": 6,
    "i": 0, "II": 1, "III": 2, "iv": 3, "v": 4, "VI": 5, "VII": 6,
}

AEOLIAN_TO_IONIAN = {
    "i":   "vi",
    "ii":  "vii",
    "III": "I",
    "iv":  "ii",
    "v":   "iii", "V": "iii",
    "VI":  "IV",  "bVI":  "IV",
    "VII": "V",   "bVII": "V",
}

DIATONIC_QUALITY = {
    "I":   "maj7",
    "ii":  "m7",
    "iii": "m7",
    "IV":  "maj7",
    "V":   "7",
    "vi":  "m7",
    "vii": "half_dim7",
}


def bare_numeral(numeral):
    if not numeral:
        return "I"
    n = numeral.split("/", 1)[0]
    n = n.lstrip("b#")
    n = re.split(r"[o°○0-9+\-]", n)[0]
    return n or "I"


def parse_roman(numeral):
    if numeral is None:
        return 0
    return ROMAN_TO_DEGREE.get(bare_numeral(numeral), 0)


def relative_major(key_root, mode):
    if mode in ("major", "ionian"):
        return key_root
    overrides = {"A": "C", "E": "G", "B": "D", "D": "F", "G": "Bb", "C": "Eb",
                 "F": "Ab", "Bb": "Db", "Eb": "Gb"}
    return overrides.get(key_root, LETTERS[(LETTERS.index(key_root[0]) + 2) % 7])


# -----------------------------------------------------------------------------
# ABC pitch rendering

def scale_degree_to_abc(degree, key_root, abs_octave):
    """Render scale degree (0=tonic) at given absolute octave to ABC.

    ABC octave convention: octave 4 = C..B uppercase, octave 5 = c..b
    lowercase, then `'` for higher and `,` on uppercase for lower.
    """
    tonic_idx = LETTERS.index(key_root[0])
    letter = LETTERS[(tonic_idx + degree) % 7]
    oct_add = (tonic_idx + degree) // 7
    real_oct = abs_octave + oct_add
    if real_oct >= 5:
        s = letter.lower() + "'" * (real_oct - 5)
    else:
        s = letter.upper() + "," * (4 - real_oct)
    return s


def pitch_to_abc(pitch):
    letter = pitch["letter"]
    acc = pitch.get("accidental")
    octv = pitch["octave"]
    prefix = {"sharp": "^", "flat": "_", "natural": "="}.get(acc, "")
    if octv >= 5:
        s = letter.lower() + "'" * (octv - 5)
    else:
        s = letter.upper() + "," * (4 - octv)
    return prefix + s


# -----------------------------------------------------------------------------
# Duration handling (duplicated from reharm)

_SAFE_DURS = {1, 2, 3, 4, 6, 7, 8, 12, 14, 16, 24, 28, 32}


def _safe_note_dur(token, n):
    if n <= 0:
        return ""
    if n in _SAFE_DURS:
        return token if n == 1 else f"{token}{n}"
    for cand in sorted(_SAFE_DURS, reverse=True):
        if cand < n:
            return f"{token}{cand}-{_safe_note_dur(token, n - cand)}"
    return f"{token}{n}"


_safe_chord = _safe_note_dur


def detect_duration_multiplier(hymn):
    from collections import Counter
    beats = hymn["meter"]["beats"]
    unit = hymn["meter"]["unit"]
    expected_16ths = beats * 16 // unit
    sums = []
    for b in hymn["bars"]:
        s = sum(e["duration"] for e in b["melody"])
        if s > 0:
            sums.append(s)
    if not sums:
        return 4
    typical = Counter(sums).most_common(1)[0][0]
    mult = expected_16ths / typical
    for candidate in (1, 2, 4, 8, 16):
        if abs(mult - candidate) < 0.1:
            return candidate
    return max(1, int(round(mult)))


def beat_group_sixteenths(beats, unit):
    if unit == 8 and beats % 3 == 0 and beats >= 6:
        return 6
    if unit <= 0:
        return 4
    return max(1, 16 // unit)


def bar_length_sixteenths(bar, mult):
    total = sum(ev["duration"] for ev in bar["melody"])
    return int(round(total * mult))


# -----------------------------------------------------------------------------
# Boddie harmonic transform: lift triads to diatonic 7ths (Reharm L2)
# Pool stays diatonic; nothing requires lever flips.

CHORD_POOL = {
    ("I",   None), ("ii",  None), ("iii", None), ("IV",  None),
    ("V",   None), ("vi",  None), ("vii", None),
    ("I",    "maj7"), ("ii",   "m7"), ("iii",  "m7"),
    ("IV",   "maj7"), ("V",    "7"),  ("vi",   "m7"),
    ("vii",  "half_dim7"),
}


def validate_chord_pool(chord):
    key = (chord.get("numeral"), chord.get("quality"))
    if key not in CHORD_POOL:
        raise ValueError(f"chord outside Boddie pool: {chord!r}")


def _normalize_to_ionian(hymn):
    out = copy.deepcopy(hymn)
    mode = out.get("key", {}).get("mode", "major")
    for bar in out["bars"]:
        ch = bar.get("chord")
        if not ch:
            continue
        num = bare_numeral(ch.get("numeral"))
        if mode == "minor":
            num = bare_numeral(AEOLIAN_TO_IONIAN.get(num, num))
        ch["numeral"] = num
    return out


def apply_boddie_harmony(hymn):
    """Lift every triad to its diatonic 7th. Single transform, no
    substitution -- Boddie doesn't reharmonize, just enriches.
    """
    out = _normalize_to_ionian(hymn)
    for bar in out["bars"]:
        ch = bar.get("chord")
        if not ch:
            continue
        ch["quality"] = DIATONIC_QUALITY.get(ch["numeral"])
    return out


# -----------------------------------------------------------------------------
# Phrase roles

def assign_phrase_roles(n_bars, phrases):
    """Tag each bar: opening / middle / cadence_approach / cadence."""
    roles = ["middle"] * n_bars
    for ph in phrases:
        ibars = ph.get("ibars") or []
        if not ibars:
            continue
        roles[ibars[0] - 1] = "opening"
        roles[ibars[-1] - 1] = "cadence"
        if len(ibars) >= 3:
            roles[ibars[-2] - 1] = "cadence_approach"
    return roles


def phrase_last_bar_indices(n_bars, phrases):
    """Return set of 0-indexed bar numbers that end a phrase."""
    out = set()
    for ph in phrases:
        ibars = ph.get("ibars") or []
        if ibars:
            out.add(ibars[-1] - 1)
    return out


# -----------------------------------------------------------------------------
# RH (melody) rendering

def chord_label(chord):
    if not chord:
        return ""
    num = chord.get("numeral") or ""
    if not num:
        return ""
    q = chord.get("quality")
    inv = chord.get("inversion")
    q_map = {
        "maj7": "Δ⁷", "M7": "Δ⁷", "7": "⁷",
        "m7": "m⁷", "dim7": "°⁷",
        "half_dim7": "ø⁷",
        "dim": "°", "aug": "+",
    }
    suffix = q_map.get(q, q or "")
    if inv is not None and inv != 0 and inv != "0":
        sup_map = str.maketrans("0123456789",
                                "⁰¹²³⁴"
                                "⁵⁶⁷⁸⁹")
        suffix += str(inv).translate(sup_map)
    if suffix:
        return f"$1{num}$2{suffix}$0"
    return f"$1{num}$0"


def render_melody_bar(bar, mult, octave_double=False, last_event_decoration=None,
                      last_event_breath=False):
    """Render one bar of melody. If `octave_double`, double each note up
    one octave. `last_event_decoration` is an ABC `!...!` tag prepended
    to the last note (e.g. `!arpeggio!`, `!fermata!`). `last_event_breath`
    appends `!breath!` after the last note token.
    """
    toks = []
    label = chord_label(bar.get("chord"))
    annotation = f'"^{label}"' if label else ""
    events = bar["melody"]
    # Find the LAST event that will actually emit a non-empty token --
    # i.e. a note or rest with non-zero duration after the mult scaling.
    last_voiced_idx = -1
    for i, ev in enumerate(events):
        n = int(round(ev["duration"] * mult))
        if n > 0:
            last_voiced_idx = i
    first = True
    for i, ev in enumerate(events):
        n = int(round(ev["duration"] * mult))
        if n <= 0:
            continue
        if ev["kind"] == "rest":
            tok = _safe_note_dur("z", n)
        else:
            p = pitch_to_abc(ev["pitch"])
            if octave_double:
                hi = pitch_to_abc({**ev["pitch"],
                                   "octave": ev["pitch"]["octave"] + 1})
                p = f"[{p}{hi}]"
            tok = _safe_note_dur(p, n)
            if i == last_voiced_idx and last_event_decoration and ev["kind"] == "note":
                tok = last_event_decoration + tok
        if first and annotation and tok:
            tok = annotation + tok
            first = False
        elif tok:
            first = False
        if i == last_voiced_idx and last_event_breath and tok:
            tok = tok + "!breath!"
        toks.append(tok)
    return " ".join(t for t in toks if t)


# -----------------------------------------------------------------------------
# LH (Boddie figuration) rendering

# Octave registers used by the LH writer.
LH_BASS_OCTAVE   = 2  # bass note on beat 1 (C2-B2)
LH_DRONE_OCTAVE  = 1  # drone-octave pluck below the staff (C1-B1)
LH_ARP_OCTAVE    = 3  # arpeggio chord-tone register (C3-B3 climbing into C4)


def chord_tone_pitches(numeral, quality, key_root, base_octave):
    """Return (root, third, fifth, [seventh]) ABC tokens at base_octave."""
    deg = parse_roman(numeral)
    r = scale_degree_to_abc(deg,     key_root, base_octave)
    t = scale_degree_to_abc(deg + 2, key_root, base_octave)
    f = scale_degree_to_abc(deg + 4, key_root, base_octave)
    s = None
    if quality in ("maj7", "m7", "7", "half_dim7", "dim7"):
        s = scale_degree_to_abc(deg + 6, key_root, base_octave)
    return r, t, f, s


def _arp_cells_for_eighths(numeral, quality, key_root, n_eighths):
    """Return a list of `n_eighths` ABC pitch tokens forming a Boddie
    rising arpeggio across the bar. Bass octave is used on beat 1 and
    the arpeggio rises through chord tones into the next octave.

    Spans roughly 1.5 octaves -- bass at C2-B2, arp climbing through
    C3-B3 into the lower part of C4-B4 register.
    """
    deg = parse_roman(numeral)
    bass = scale_degree_to_abc(deg, key_root, LH_BASS_OCTAVE)
    third = scale_degree_to_abc(deg + 2, key_root, LH_ARP_OCTAVE)
    fifth = scale_degree_to_abc(deg + 4, key_root, LH_ARP_OCTAVE)
    octv  = scale_degree_to_abc(deg + 7, key_root, LH_ARP_OCTAVE)  # +octave
    third_hi = scale_degree_to_abc(deg + 9, key_root, LH_ARP_OCTAVE)
    has_sev = quality in ("maj7", "m7", "7", "half_dim7", "dim7")
    seventh = scale_degree_to_abc(deg + 6, key_root, LH_ARP_OCTAVE) if has_sev else None

    # Climbing pattern; truncate or repeat to fill `n_eighths`.
    if has_sev:
        pattern = [bass, third, fifth, seventh, octv, third_hi]
    else:
        pattern = [bass, third, fifth, octv, third_hi, fifth]
    cells = []
    for i in range(n_eighths):
        cells.append(pattern[i % len(pattern)])
    return cells


def lh_pattern(chord, key_root, role, total_sixteenths, beats, unit,
               is_first_bar=False, is_final_bar=False):
    """Render one bar of Boddie-style LH. Returns ABC text filling
    exactly `total_sixteenths` 1/16 units.
    """
    if total_sixteenths <= 0:
        return ""
    numeral = chord.get("numeral") or "I"
    quality = chord.get("quality")
    deg = parse_roman(numeral)

    # FINAL bar of hymn -- wide-spread rolled chord with drone octave.
    if is_final_bar:
        drone = scale_degree_to_abc(deg, key_root, LH_DRONE_OCTAVE)
        r, t, f, s = chord_tone_pitches(numeral, quality, key_root,
                                         LH_BASS_OCTAVE)
        pitches = [drone, r, t, f] + ([s] if s else [])
        chord_blob = f"!fermata!!arpeggio![{''.join(pitches)}]"
        return _safe_chord(chord_blob, total_sixteenths)

    # CADENCE bar -- rolled wide-spread chord, full bar (no drone octave).
    if role == "cadence":
        r, t, f, s = chord_tone_pitches(numeral, quality, key_root,
                                         LH_BASS_OCTAVE)
        pitches = [r, t, f] + ([s] if s else [])
        chord_blob = f"!arpeggio![{''.join(pitches)}]"
        return _safe_chord(chord_blob, total_sixteenths)

    # Otherwise: bass + arpeggio in eighths.
    # `total_sixteenths` divided into eighth-cells = total_sixteenths/2.
    n_eighths = total_sixteenths // 2
    if n_eighths < 1:
        # Bar shorter than an eighth -- fall back to single block.
        r, t, f, s = chord_tone_pitches(numeral, quality, key_root,
                                         LH_BASS_OCTAVE)
        pitches = [r, t, f] + ([s] if s else [])
        return _safe_chord(f"[{''.join(pitches)}]", total_sixteenths)

    cells = _arp_cells_for_eighths(numeral, quality, key_root, n_eighths)

    # Opening bar of hymn or phrase: drone octave on the bass tone of
    # beat 1 (the first cell). Pluck = root at C1 + root at C2 stacked.
    if is_first_bar or role == "opening":
        drone = scale_degree_to_abc(deg, key_root, LH_DRONE_OCTAVE)
        bass_root = cells[0]
        cells[0] = f"[{drone}{bass_root}]"

    out = " ".join(_safe_chord(c, 2) for c in cells)
    # Handle odd 1/16 leftover (e.g. dotted bar): pad with a tied cell.
    rem = total_sixteenths - n_eighths * 2
    if rem > 0:
        out += " " + _safe_chord(cells[-1], rem)
    return out


# -----------------------------------------------------------------------------
# Build ABC

def build_abc(hymn, x_num=1, num_prefix=None, tempo_qpm=72):
    title = hymn["title"]
    if num_prefix:
        title = f"{num_prefix}. {title}"
    key_root = hymn["key"]["root"]
    mode = hymn["key"]["mode"]
    beats = hymn["meter"]["beats"]
    unit = hymn["meter"]["unit"]
    bars = hymn["bars"]
    phrases = hymn["phrases"]

    effective_key = relative_major(key_root, mode) if mode == "minor" else key_root

    roles = assign_phrase_roles(len(bars), phrases)
    last_phrase_bars = phrase_last_bar_indices(len(bars), phrases)
    mult = detect_duration_multiplier(hymn)
    final_idx = len(bars) - 1

    # Validate chords
    for b in bars:
        ch = b.get("chord") or {"numeral": "I"}
        validate_chord_pool({"numeral": ch.get("numeral") or "I",
                             "quality": ch.get("quality")})

    melody_bars = []
    for i, b in enumerate(bars):
        is_cadence = roles[i] == "cadence"
        deco = None
        breath = False
        if i == final_idx:
            deco = "!fermata!!arpeggio!"
        elif i in last_phrase_bars:
            breath = True
        melody_bars.append(render_melody_bar(
            b, mult,
            octave_double=is_cadence or i == final_idx,
            last_event_decoration=deco,
            last_event_breath=breath,
        ))

    lh_bars = []
    for i, b in enumerate(bars):
        ch = dict(b.get("chord") or {"numeral": "I"})
        bar_16 = bar_length_sixteenths(b, mult)
        lh_bars.append(lh_pattern(
            ch, effective_key, roles[i], bar_16, beats, unit,
            is_first_bar=(i == 0),
            is_final_bar=(i == final_idx),
        ))

    LINE_BUDGET = 70

    def bar_cost(v1, v2):
        return len(v1.split()) + len(v2.split()) + 3 * v1.count('"^') + 2

    def pack_lines(pairs):
        v1l, v2l = [], []
        cur1, cur2, cost = [], [], 0
        for v1, v2 in pairs:
            c = bar_cost(v1, v2)
            if cur1 and cost + c > LINE_BUDGET:
                v1l.append(" | ".join(cur1) + " |")
                v2l.append(" | ".join(cur2) + " |")
                cur1, cur2, cost = [], [], 0
            cur1.append(v1); cur2.append(v2); cost += c
        if cur1:
            v1l.append(" | ".join(cur1) + " |")
            v2l.append(" | ".join(cur2) + " |")
        return v1l, v2l

    abc = []
    abc.append(f"X:{x_num}")
    abc.append(f"T:{title}")
    abc.append(f"M:{beats}/{unit}")
    abc.append("L:1/16")
    abc.append(f'Q:1/4={tempo_qpm} "Slowly, with great expression"')
    abc.append(f"K:{effective_key}")
    abc.append("%%scale 0.75")
    abc.append("%%annotationfont Times-Italic 13")
    abc.append("%%setfont-1 Times-Bold 13")
    abc.append("%%setfont-2 Times-Italic 11")
    abc.append("%%score {V1 V2}")
    abc.append("V:V1 clef=treble")
    abc.append("V:V2 clef=bass")
    v1l, v2l = pack_lines(list(zip(melody_bars, lh_bars)))
    abc.append("[V:V1]"); abc.extend(v1l)
    abc.append("[V:V2]"); abc.extend(v2l)
    return "\n".join(abc) + "\n"


# -----------------------------------------------------------------------------
# Public entry point: hymn JSON dict -> ABC text

def render_boddie(hymn, x_num=1, num_prefix=None, tempo_qpm=72):
    """Apply Boddie harmonic transform + ABC rendering. One-shot, no levels."""
    transformed = apply_boddie_harmony(hymn)
    return build_abc(transformed, x_num=x_num, num_prefix=num_prefix,
                     tempo_qpm=tempo_qpm)


# -----------------------------------------------------------------------------
# CLI

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("hymn_json")
    ap.add_argument("-o", "--output")
    ap.add_argument("-x", "--xnum", type=int, default=1)
    ap.add_argument("--tempo", type=int, default=72,
                    help="Q:1/4= tempo (default 72)")
    args = ap.parse_args()

    hymn = json.loads(Path(args.hymn_json).read_text(encoding="utf-8"))
    abc = render_boddie(hymn, x_num=args.xnum, tempo_qpm=args.tempo)
    if args.output:
        Path(args.output).write_text(abc, encoding="utf-8")
    else:
        sys.stdout.write(abc)


if __name__ == "__main__":
    main()
