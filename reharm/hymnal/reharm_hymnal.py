#!/usr/bin/env python3
"""Reharm Hymnal -- substitute diatonic jazz chords under a hymn melody.

Reads a HarpHymnal per-bar JSON (../HarpHymnal/data/hymns/<slug>.json) and
emits a grand-staff ABC file. V1 = melody (as given, passed through from
retab's renderer). V2 = reharm-ed chord, voiced on the harp with the same
"no piano stomp" rule that retab uses.

The reharm transformation is level-parameterised. Every level stays
strictly within the hymn's diatonic collection -- zero lever flips.
Levels 1-7 match the ladder in REHARM.md:

    L1  straight triads                 (baseline)
    L2  diatonic 7ths                   (tonic->maj7, V->7, ii->m7, ...)
    L3  functional substitution         (I->vi7, IV<->ii7, V->iii7, ...)
    L4  relative-minor reharm           (vi-centred, natural-minor v)
    L5  modal reharm                    (Dorian / Mix / Lydian / Phrygian)
    L6  non-functional + slash chords   (chromatic mediants, F/G, C/D)
    L7  voice-leading-first             (inner-voice contour search)

Levels L2-L7 are stubs in this bootstrap -- L1 is implemented.
"""

from __future__ import annotations
import copy
import json
import re
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Diatonic scale utilities (duplicated from retab; stays in sync by hand)

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
    "i": "vi",
    "ii": "vii", "ii": "vii",
    "III": "I",
    "iv": "ii",
    "v": "iii", "V": "iii",
    "VI": "IV", "bVI": "IV",
    "VII": "V", "bVII": "V",
}


def bare_numeral(numeral: str | None) -> str:
    """Strip accidental prefix and diminished/aug/digit suffix.

    'ii^o' -> 'ii', 'bVII7' -> 'VII', 'V/V' -> 'V'. Handles both ASCII
    'o' and the unicode degree symbols used in the hymn JSONs.
    """
    if not numeral:
        return "I"
    n = numeral.split("/", 1)[0]
    n = n.lstrip("b#")
    n = re.split(r"[o°○0-9+\-]", n)[0]
    return n or "I"


def parse_roman(numeral: str) -> int:
    if numeral is None:
        return 0
    return ROMAN_TO_DEGREE.get(bare_numeral(numeral), 0)


def relative_major(key_root: str, mode: str) -> str:
    if mode in ("major", "ionian"):
        return key_root
    overrides = {"A": "C", "E": "G", "B": "D", "D": "F", "G": "Bb", "C": "Eb",
                 "F": "Ab", "Bb": "Db", "Eb": "Gb"}
    return overrides.get(key_root, LETTERS[(LETTERS.index(key_root[0]) + 2) % 7])


# -----------------------------------------------------------------------------
# ABC pitch rendering

def scale_degree_to_abc(degree: int, key_root: str, abs_octave: int) -> str:
    tonic_idx = LETTERS.index(key_root[0])
    letter = LETTERS[(tonic_idx + degree) % 7]
    oct_add = (tonic_idx + degree) // 7
    real_oct = abs_octave + oct_add
    if real_oct >= 5:
        s = letter.lower() + "'" * (real_oct - 5)
    else:
        s = letter.upper() + "," * (4 - real_oct)
    return s


def pitch_to_abc(pitch: dict) -> str:
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
# Duration handling (duplicated from retab)

_SAFE_DURS = {1, 2, 3, 4, 6, 7, 8, 12, 14, 16, 24, 28, 32}


def _safe_note_dur(token: str, n: int) -> str:
    if n <= 0:
        return ""
    if n in _SAFE_DURS:
        return token if n == 1 else f"{token}{n}"
    for cand in sorted(_SAFE_DURS, reverse=True):
        if cand < n:
            return f"{token}{cand}-{_safe_note_dur(token, n - cand)}"
    return f"{token}{n}"


_safe_chord = _safe_note_dur


def detect_duration_multiplier(hymn: dict) -> int:
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


def beat_group_sixteenths(beats: int, unit: int) -> int:
    if unit == 8 and beats % 3 == 0 and beats >= 6:
        return 6
    if unit <= 0:
        return 4
    return max(1, 16 // unit)


def bar_length_sixteenths(bar: dict, mult: int) -> int:
    total = sum(ev["duration"] for ev in bar["melody"])
    return int(round(total * mult))


# -----------------------------------------------------------------------------
# Chord pool -- every chord reharm may produce. All pitches diatonic to the
# hymn's key. Zero lever flips.
#
# Any chord produced by apply_level_N must be in this pool. A chord outside
# the pool -- or any accidental outside the parent key signature -- is a
# hard failure. That's the flip-free guarantee.

CHORD_POOL = {
    # L1 baseline: bare diatonic triads
    ("I",   None), ("ii",  None), ("iii", None), ("IV",  None),
    ("V",   None), ("vi",  None), ("vii", None),
    # L2+: diatonic 7ths
    ("I",    "maj7"),
    ("ii",   "m7"),
    ("iii",  "m7"),
    ("IV",   "maj7"),
    ("V",    "7"),
    ("vi",   "m7"),
    ("vii",  "half_dim7"),
}


def validate_chord_pool(chord: dict) -> None:
    key = (chord.get("numeral"), chord.get("quality"))
    if key not in CHORD_POOL:
        raise ValueError(f"chord outside reharm pool: {chord!r}")


# -----------------------------------------------------------------------------
# Diatonic 7th quality map -- used by L2 and by every higher level that
# enriches a bare diatonic triad.

DIATONIC_QUALITY = {
    "I":   "maj7",
    "ii":  "m7",
    "iii": "m7",
    "IV":  "maj7",
    "V":   "7",
    "vi":  "m7",
    "vii": "half_dim7",
}


# -----------------------------------------------------------------------------
# Reharm levels -- each is a pass that transforms hymn["bars"][i]["chord"].

def _normalize_to_ionian(hymn: dict) -> dict:
    """Return a deep copy with all chord numerals translated to major-key
    Ionian labels. Minor-mode hymns store their chords in Aeolian (i, iv,
    V, bVII); every downstream level assumes Ionian labels, so we rewrite
    up front. Also bare-normalizes suffixes like 'ii^o' -> 'ii'.

    After this pass, the hymn's `key.mode` still reflects the original
    (major/minor) for key-signature calculation, but every chord numeral
    reads against the *parent major*.
    """
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


def apply_level_1(hymn: dict) -> dict:
    """L1 -- baseline. Every written chord kept as-is, quality stripped so
    the output renders as a plain diatonic triad. L1 establishes the
    baseline voicing against which higher levels are judged.
    """
    out = _normalize_to_ionian(hymn)
    for bar in out["bars"]:
        if bar.get("chord"):
            bar["chord"]["quality"] = None
    return out


def apply_level_2(hymn: dict) -> dict:
    """L2 -- diatonic 7ths. Lift every triad to its diatonic-7th form."""
    out = _normalize_to_ionian(hymn)
    for bar in out["bars"]:
        ch = bar.get("chord")
        if not ch:
            continue
        ch["quality"] = DIATONIC_QUALITY.get(ch["numeral"])
    return out


def apply_level_3(hymn: dict) -> dict:
    """L3 -- functional substitution within diatonic 7ths.

    Starts from L2 (diatonic 7ths) and rewrites chord numerals based on
    phrase role:

      - Deceptive tonic:   I -> vi7  at weak arrivals (opening-of-middle)
      - Plagal tonic:      I -> iii7 at phrase starts that need motion
      - Pre-dominant:      IV -> ii7 mid-phrase
      - Weak dominant:     V -> iii7 or V -> viiø7 in non-cadence bars

    The hymn's final cadence bar is sacred -- never substituted.
    """
    out = apply_level_2(hymn)
    roles = assign_phrase_roles(len(out["bars"]), out.get("phrases") or [])
    final_idx = len(out["bars"]) - 1

    # Deterministic but varied: substitutions keyed on bar index so the same
    # hymn substitutes the same way every build, but different bars get
    # different treatments within the functional rules.
    for i, bar in enumerate(out["bars"]):
        ch = bar.get("chord")
        if not ch or i == final_idx:
            continue
        role = roles[i]
        if role == "cadence" or role == "cadence_approach":
            continue
        num = ch["numeral"]  # already Ionian via _normalize_to_ionian

        # Tonic function: I at phrase openings -> iii7 for motion; I
        # mid-phrase at weak arrivals -> vi7 (deceptive).
        if num == "I":
            if role == "opening" and i != 0:
                ch["numeral"], ch["quality"] = "iii", "m7"
            elif role == "middle" and i % 3 == 2:
                ch["numeral"], ch["quality"] = "vi", "m7"
        # Pre-dominant: IV mid-phrase -> ii7 half the time.
        elif num == "IV" and role == "middle" and i % 2 == 0:
            ch["numeral"], ch["quality"] = "ii", "m7"
        # Weak dominant: V in non-cadence bars -> iii7 (tonic-leaning
        # substitute); keep V at cadences (handled by role filter above).
        elif num == "V" and role == "middle":
            ch["numeral"], ch["quality"] = "iii", "m7"

    return out


def apply_level_4(hymn: dict) -> dict:
    """L4 -- relative-minor reharm with natural-minor v.

    Start from L2 (diatonic 7ths). Scan phrases; for phrases that show
    relative-minor gravity in the written harmony (opening or cadence
    bar rooted on vi or iii), rewrite the phrase as an Andalusian-style
    minor progression:

        opening          -> vi7   (relative-minor tonic)
        cadence          -> vi7   (relative-minor tonic)
        cadence_approach -> iii7  (natural-minor v = iii in parent major)
        middle           -> IVmaj7 / ii7 alternating (relative-minor
                            pre-dominant area)

    The hymn's final phrase is sacred -- never rewritten.
    """
    out = apply_level_2(hymn)
    phrases = out.get("phrases") or []
    bars = out["bars"]
    final_idx = len(bars) - 1

    for phrase in phrases:
        ibars = phrase.get("ibars") or []
        if len(ibars) < 2:
            continue
        # Skip the hymn's final phrase entirely.
        if ibars[-1] - 1 == final_idx:
            continue
        first_ch = bars[ibars[0] - 1].get("chord") or {}
        last_ch = bars[ibars[-1] - 1].get("chord") or {}
        if first_ch.get("numeral") not in ("vi", "iii") and \
           last_ch.get("numeral") not in ("vi", "iii"):
            continue

        n = len(ibars)
        for local_i, bar_1idx in enumerate(ibars):
            ch = bars[bar_1idx - 1].get("chord")
            if not ch:
                continue
            if local_i == 0 or local_i == n - 1:
                ch["numeral"], ch["quality"] = "vi", "m7"
            elif local_i == n - 2:
                ch["numeral"], ch["quality"] = "iii", "m7"
            elif local_i % 2 == 0:
                ch["numeral"], ch["quality"] = "IV", "maj7"
            else:
                ch["numeral"], ch["quality"] = "ii", "m7"

    return out


def apply_level_5(hymn: dict) -> dict:
    """L5 -- modal reharm within parent key signature.

    Start from L2 and apply a single modal section to the middle of the
    hymn. The mode (Dorian / Mixolydian / Lydian / Phrygian) is chosen
    deterministically from the hymn slug so the same hymn always reads
    the same way, but different hymns distribute across modes.

    Per mode, the section is rewritten with the modal centre as tonic:

        Dorian     (centre = ii): i(ii)  iv(V)  bVII(I)  i(ii)
        Mixolydian (centre = V):  I(V)   bVII(IV) IV(I)  I(V)
        Lydian     (centre = IV): I(IV)  II(V)  V(I)    I(IV)
        Phrygian   (centre = iii): i(iii) bII(IV) bVII(ii) i(iii)

    Parent-major labels in parens. Each substitution stays pitch-diatonic
    because the key signature is preserved -- only the tonal gravity
    shifts. One section per hymn (phrase 2 of N, when N >= 3).
    """
    out = apply_level_2(hymn)
    phrases = out.get("phrases") or []
    bars = out["bars"]
    final_idx = len(bars) - 1
    if len(phrases) < 3:
        return out  # too short for a modal section

    # Pick the mode from a stable hash of the slug.
    slug = out.get("slug") or out.get("title") or ""
    modes = ["dorian", "mixolydian", "lydian", "phrygian"]
    mode_name = modes[sum(ord(c) for c in slug) % len(modes)]

    # Progression templates in parent-major labels. Each is a 4-bar cycle;
    # emitter wraps/truncates to the phrase length.
    templates = {
        "dorian":     [("ii", "m7"),   ("V", "7"),      ("I", "maj7"),  ("ii", "m7")],
        "mixolydian": [("V", "7"),     ("IV", "maj7"),  ("I", "maj7"),  ("V", "7")],
        "lydian":     [("IV", "maj7"), ("V", "7"),      ("I", "maj7"),  ("IV", "maj7")],
        "phrygian":   [("iii", "m7"),  ("IV", "maj7"),  ("ii", "m7"),   ("iii", "m7")],
    }
    prog = templates[mode_name]

    # Target the middle phrase (index N//2 -- not first, not last).
    target = phrases[len(phrases) // 2]
    ibars = target.get("ibars") or []
    if not ibars or ibars[-1] - 1 == final_idx:
        return out

    for local_i, bar_1idx in enumerate(ibars):
        ch = bars[bar_1idx - 1].get("chord")
        if not ch:
            continue
        num, qual = prog[local_i % len(prog)]
        ch["numeral"], ch["quality"] = num, qual

    return out


def apply_level_6(hymn: dict) -> dict:
    """L6 -- non-functional chromatic mediants within diatonic.

    Start from L2 and replace functional fifth-motion with chromatic-
    mediant pairings (root motion by a third between chords of different
    qualities). The three pairs:

        tonic pair:       I   <-> iii   (major <-> minor, third apart)
        pre-dominant:     IV  <-> vi    (major <-> minor, third apart)
        dominant pair:    V   <-> vii   (major <-> dim, third apart)

    Alternate each pair by bar index so the progression wanders by thirds
    instead of resolving by fifths. Final cadence stays sacred.
    """
    out = apply_level_2(hymn)
    bars = out["bars"]
    final_idx = len(bars) - 1
    roles = assign_phrase_roles(len(bars), out.get("phrases") or [])

    mediants = {
        "I":   ("iii", "m7"),
        "iii": ("I",   "maj7"),
        "IV":  ("vi",  "m7"),
        "vi":  ("IV",  "maj7"),
        "V":   ("vii", "half_dim7"),
        "vii": ("V",   "7"),
    }

    for i, bar in enumerate(bars):
        ch = bar.get("chord")
        if not ch or i == final_idx:
            continue
        # Preserve cadence and cadence_approach -- resolution feeling
        # still wants functional weight.
        if roles[i] in ("cadence", "cadence_approach"):
            continue
        # Flip on odd bars so the progression alternates mediant/original
        # rather than swapping everything uniformly.
        if i % 2 != 1:
            continue
        num = ch["numeral"]
        if num in mediants:
            ch["numeral"], ch["quality"] = mediants[num]

    return out


def apply_level_7(hymn: dict) -> dict:
    """L7 -- voice-leading-first: inner-voice contour drives chord choice.

    For each phrase (except the final), we pick an inner-voice line that
    descends stepwise from tonic (scale degree 1) at the phrase opening
    toward dominant (degree 5) at the cadence. For each bar, we emit the
    diatonic 7th chord whose 3rd equals the inner-voice pitch at that
    beat. The chord symbol falls out of the voice leading rather than
    being chosen first.

    The 7 diatonic 7ths indexed by "inner voice scale degree as chord 3rd":

        degree 1 (C in C)  -> vi7   (A-C-E-G, 1 is the 3rd)
        degree 2 (D)       -> viiø7 (B-D-F-A)
        degree 3 (E)       -> Imaj7 (C-E-G-B)
        degree 4 (F)       -> ii7   (D-F-A-C)
        degree 5 (G)       -> iii7  (E-G-B-D)
        degree 6 (A)       -> IVmaj7(F-A-C-E)
        degree 7 (B)       -> V7    (G-B-D-F)

    Under a 1 -> 7 -> 6 -> 5 inner-voice descent this yields the classic
    vi -> V -> IV -> iii bassline -- an Andalusian-shape, arrived at via
    voice leading rather than mode selection.
    """
    out = _normalize_to_ionian(hymn)
    phrases = out.get("phrases") or []
    bars = out["bars"]
    final_idx = len(bars) - 1

    INNER_TO_CHORD = {
        1: ("vi",  "m7"),
        2: ("vii", "half_dim7"),
        3: ("I",   "maj7"),
        4: ("ii",  "m7"),
        5: ("iii", "m7"),
        6: ("IV",  "maj7"),
        7: ("V",   "7"),
    }

    for phrase in phrases:
        ibars = phrase.get("ibars") or []
        if len(ibars) < 2:
            continue
        # Final phrase: lift to diatonic 7ths (L2 baseline) but don't
        # rewrite -- the hymn's resolution is sacred.
        if ibars[-1] - 1 == final_idx:
            for bar_1idx in ibars:
                ch = bars[bar_1idx - 1].get("chord")
                if ch:
                    ch["quality"] = DIATONIC_QUALITY.get(ch["numeral"])
            continue

        for local_i, bar_1idx in enumerate(ibars):
            ch = bars[bar_1idx - 1].get("chord")
            if not ch:
                continue
            # Stepwise descent from degree 1; wraps after 7 bars.
            degree = ((1 - local_i - 1) % 7) + 1
            ch["numeral"], ch["quality"] = INNER_TO_CHORD[degree]

    # Any bar not covered by a phrase gets the L2 treatment so every
    # chord still has a quality field.
    for bar in bars:
        ch = bar.get("chord")
        if ch and ch.get("quality") is None:
            ch["quality"] = DIATONIC_QUALITY.get(ch.get("numeral") or "I")

    return out


REHARM_LEVELS = {
    1: apply_level_1,
    2: apply_level_2,
    3: apply_level_3,
    4: apply_level_4,
    5: apply_level_5,
    6: apply_level_6,
    7: apply_level_7,
}


# -----------------------------------------------------------------------------
# Melody rendering (duplicated from retab). V1 is always the melody, passed
# through with optional octave-doubling on the final cadence bar.

def chord_label(chord: dict | None) -> str:
    if not chord:
        return ""
    num = chord.get("numeral") or ""
    if not num:
        return ""
    q = chord.get("quality")
    inv = chord.get("inversion")
    q_map = {
        "M7": "Δ⁷",
        "maj7": "Δ⁷",
        "7": "⁷",
        "m7": "m⁷",
        "dim7": "°⁷",
        "half_dim7": "ø⁷",
        "dim": "°",
        "aug": "+",
    }
    suffix = q_map.get(q, q or "")
    if inv is not None and inv != 0 and inv != "0":
        sup_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
        suffix += str(inv).translate(sup_map)
    if suffix:
        return f"$1{num}$2{suffix}$0"
    return f"$1{num}$0"


def render_melody_bar(bar: dict, mult: int, octave_double: bool = False) -> str:
    toks = []
    label = chord_label(bar.get("chord"))
    annotation = f'"^{label}"' if label else ""
    first = True
    for ev in bar["melody"]:
        n = int(round(ev["duration"] * mult))
        if ev["kind"] == "rest":
            tok = _safe_note_dur("z", n)
        else:
            p = pitch_to_abc(ev["pitch"])
            if octave_double:
                hi = pitch_to_abc({**ev["pitch"], "octave": ev["pitch"]["octave"] + 1})
                p = f"[{p}{hi}]"
            tok = _safe_note_dur(p, n)
        if first and annotation and tok:
            tok = annotation + tok
            first = False
        elif tok:
            first = False
        toks.append(tok)
    return " ".join(t for t in toks if t)


# -----------------------------------------------------------------------------
# LH voicing -- the reharm-ed chord, rendered on the harp.
#
# At L1 the chord is a plain triad; the voicing logic mirrors retab's L3
# block-135 walking pattern (no piano stomp). Higher levels will add the
# 7th, 9th, etc. into the voicing.

LH_TRIAD_OCTAVE = 2
LH_DITTO_OCTAVE = 1


def build_chord_voicing(numeral: str, quality: str | None,
                        key_root: str) -> tuple[str, str, str, str | None]:
    """Return (root, third, fifth, seventh?) ABC tokens at LH octave.

    For L1 seventh is None. Higher levels will drive this from `quality`.
    """
    deg = parse_roman(numeral)
    r = scale_degree_to_abc(deg, key_root, LH_TRIAD_OCTAVE)
    t = scale_degree_to_abc(deg + 2, key_root, LH_TRIAD_OCTAVE)
    f = scale_degree_to_abc(deg + 4, key_root, LH_TRIAD_OCTAVE)
    s = None
    if quality in ("maj7", "m7", "7", "half_dim7", "dim7"):
        s = scale_degree_to_abc(deg + 6, key_root, LH_TRIAD_OCTAVE)
    return r, t, f, s


def lh_pattern(chord: dict, key_root: str, phrase_role: str,
               total_sixteenths: int, beats: int, unit: int,
               next_chord: dict | None = None) -> str:
    """Emit bass-clef voicing filling exactly `total_sixteenths`.

    Harp-idiom rule (carried over from retab): never re-strike the same
    voicing on consecutive beats. Either strike once and let ring, or walk
    through chord tones so each beat hits a fresh string.
    """
    if total_sixteenths <= 0:
        return ""
    numeral = chord.get("numeral") or "I"
    quality = chord.get("quality")
    r, t, f, s = build_chord_voicing(numeral, quality, key_root)
    pitches = [r, t, f] + ([s] if s else [])
    block = f"[{''.join(pitches)}]"

    ditto_block = None
    if phrase_role in ("opening", "cadence"):
        deg = parse_roman(numeral)
        ditto = scale_degree_to_abc(deg, key_root, LH_DITTO_OCTAVE)
        ditto_block = f"!arpeggio![{ditto}{''.join(pitches)}]"

    beat_16 = beat_group_sixteenths(beats, unit)
    num_groups = total_sixteenths // beat_16 if (
        beat_16 > 0 and total_sixteenths % beat_16 == 0) else 0

    # Opening + cadence: single strike, let ring.
    if phrase_role in ("opening", "cadence"):
        return _safe_chord(ditto_block or block, total_sixteenths)

    # Middle: walk through chord tones (no stomp).
    if num_groups >= 2:
        cycle = pitches + pitches[1:-1][::-1]  # R T F [S] F T  (or R T F T)
        cells = [cycle[i % len(cycle)] for i in range(num_groups)]
        return " ".join(_safe_chord(c, beat_16) for c in cells)

    return _safe_chord(block, total_sixteenths)


# -----------------------------------------------------------------------------
# Phrase roles

def assign_phrase_roles(n_bars: int, phrases: list) -> list:
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


# -----------------------------------------------------------------------------
# Build ABC

def build_abc(hymn: dict, x_num: int = 1, num_prefix: str | None = None) -> str:
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
    mult = detect_duration_multiplier(hymn)
    final_bar_idx = len(bars) - 1

    melody_bars = [
        render_melody_bar(b, mult, octave_double=(i == final_bar_idx))
        for i, b in enumerate(bars)
    ]

    # Validate every chord is in the pool before rendering. By the time we
    # get here every level pass has run numerals through _normalize_to_ionian,
    # so numerals are already bare Ionian labels -- no further translation.
    for i, b in enumerate(bars):
        ch = b.get("chord") or {"numeral": "I"}
        validate_chord_pool({"numeral": ch.get("numeral") or "I",
                             "quality": ch.get("quality")})

    lh_bars = []
    for i, b in enumerate(bars):
        ch = dict(b.get("chord") or {"numeral": "I"})
        bar_16ths = bar_length_sixteenths(b, mult)
        nxt = bars[i + 1].get("chord") if i + 1 < len(bars) else None
        pat = lh_pattern(ch, effective_key, roles[i], bar_16ths, beats, unit, nxt)
        lh_bars.append(pat)

    LINE_BUDGET = 65

    def bar_cost(v1: str, v2: str) -> int:
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
# CLI

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("hymn_json")
    ap.add_argument("-o", "--output")
    ap.add_argument("-x", "--xnum", type=int, default=1)
    ap.add_argument("--level", type=int, default=1, choices=range(1, 8))
    args = ap.parse_args()

    hymn = json.loads(Path(args.hymn_json).read_text(encoding="utf-8"))
    reharmed = REHARM_LEVELS[args.level](hymn)
    abc = build_abc(reharmed, x_num=args.xnum)
    if args.output:
        Path(args.output).write_text(abc, encoding="utf-8")
    else:
        sys.stdout.write(abc)


if __name__ == "__main__":
    main()
