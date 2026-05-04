#!/usr/bin/env python3
"""Generate a chord + polychord handout PDF.

Mirrors the *Catalog* mode of ``shapedrills.html``: a 30-string lever-harp
layout (C2-D6, key of C major) with every chord rendered as an inline
string-row, plus the chord symbol, the letter name, and a brief comment.
Single-hand voicings render in black on a faint dot-grid; polychord rows
use LH (blue) / RH (red) coloring like the HTML view.

XeLaTeX with JuliaMono-Medium / SemiBold for the string layout and chord
notation; DejaVu Serif for descriptions.

Output: ``tablet_app/app/src/main/assets/handout.pdf``.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Catalogs (kept in sync with shapedrills.html)
# ---------------------------------------------------------------------------

def deg_to_roman(d: int) -> str:
    """Scale degree (1..7) -> diatonic-quality Roman numeral in C major.
    2/3/6 are minors (lowercase). 7 is diminished (lowercase + °). Others
    are major (uppercase)."""
    upper = ["", "I", "II", "III", "IV", "V", "VI", "VII"][d]
    if d in (2, 3, 6):
        return upper.lower()
    if d == 7:
        return upper.lower() + "°"
    return upper


SECTIONS_SINGLE: list[tuple[str, list[tuple[tuple[int, ...], str, str]]]] = [
    ("Diatonic triads (root position)", [
        ((1, 3, 5), "I", "tonic, the home chord ({1} {3} {5})"),
        ((2, 4, 6), "ii", "supertonic minor ({2} {4} {6})"),
        ((3, 5, 7), "iii", "mediant minor, tonic substitute ({3} {5} {7})"),
        ((4, 6, 1), "IV", "subdominant ({4} {6} {1})"),
        ((5, 7, 2), "V", "dominant ({5} {7} {2})"),
        ((6, 1, 3), "vi", "submediant minor, relative minor ({6} {1} {3})"),
        ((7, 2, 4), "vii°", "leading-tone diminished ({7} {2} {4})"),
    ]),
    ("Triad inversions (1st inv = 3rd in bass)", [
        ((3, 5, 1), "I/III", "tonic, 3rd in bass"),
        ((4, 6, 2), "ii/IV", "supertonic minor, 3rd in bass"),
        ((5, 7, 3), "iii/V", "mediant minor, 3rd in bass"),
        ((6, 1, 4), "IV/VI", "subdominant, 3rd in bass"),
        ((7, 2, 5), "V/VII", "dominant in first inversion (smooth approach to I)"),
        ((1, 3, 6), "vi/I", "submediant minor, 3rd in bass"),
        ((2, 4, 7), "vii°/II", "leading-tone diminished, 3rd in bass"),
    ]),
    ("Triad inversions (2nd inv = 5th in bass)", [
        ((5, 1, 3), "I/V", "tonic, 5th in bass (cadential 6/4)"),
        ((6, 2, 4), "ii/VI", "supertonic minor, 5th in bass"),
        ((7, 3, 5), "iii/VII", "mediant minor, 5th in bass"),
        ((1, 4, 6), "IV/I", "subdominant over tonic pedal"),
        ((2, 5, 7), "V/II", "dominant, 5th in bass"),
        ((3, 6, 1), "vi/III", "submediant minor, 5th in bass"),
        ((4, 7, 2), "vii°/IV", "leading-tone diminished, 5th in bass"),
    ]),
    ("Diatonic seventh chords (root position)", [
        ((1, 3, 5, 7), "IΔ", "tonic major 7"),
        ((2, 4, 6, 1), "ii7", "ii7, the most common predominant"),
        ((3, 5, 7, 2), "iii7", "iii7, tonic substitute"),
        ((4, 6, 1, 3), "IVΔ", "IV major 7"),
        ((5, 7, 2, 4), "V7", "dominant 7"),
        ((6, 1, 3, 5), "vi7", "vi7, relative minor 7"),
        ((7, 2, 4, 6), "VII⌀", "half-diminished, rootless dominant"),
    ]),
    ("Seventh chord inversions (3rd in bass)", [
        ((3, 5, 7, 1), "IΔ/III", "tonic major 7, 3rd in bass"),
        ((4, 6, 1, 2), "ii7/IV", "ii7, 3rd in bass"),
        ((6, 1, 3, 4), "IVΔ/VI", "IV major 7, 3rd in bass"),
        ((7, 2, 4, 5), "V7/VII", "dominant 7, 3rd in bass — common voice-leading to I"),
        ((1, 3, 5, 6), "vi7/I", "vi7, 3rd in bass (same notes as I6)"),
    ]),
    ("Seventh chord inversions (5th and 7th in bass)", [
        ((5, 7, 1, 3), "IΔ/V", "tonic major 7, 5th in bass"),
        ((7, 1, 3, 5), "IΔ/VII", "tonic major 7, 7th in bass — moody"),
        ((2, 4, 5, 7), "V7/II", "dominant 7, 5th in bass"),
        ((4, 5, 7, 2), "V7/IV", "dominant 7, 7th in bass — leans hard to III"),
        ((1, 2, 4, 6), "ii7/I", "ii7, 7th in bass"),
    ]),
    ("Sixth chords (major triad + major 6th)", [
        ((1, 3, 5, 6), "I6", "tonic 6 (same notes as vi7)"),
        ((4, 6, 1, 2), "IV6", "IV6 (same notes as ii7)"),
        ((5, 7, 2, 3), "V6", "V6 — uncommon but playable"),
    ]),
    ("Minor sixth chord", [
        ((2, 4, 6, 7), "ii6", "ii minor 6 (Dorian flavor)"),
    ]),
    ("Suspended 2nd chords (sus2)", [
        ((1, 2, 5), "Isus2", "tonic with 2 replacing 3"),
        ((2, 3, 6), "IIsus2", "supertonic sus2"),
        ((4, 5, 1), "IVsus2", "subdominant sus2"),
        ((5, 6, 2), "Vsus2", "dominant sus2"),
        ((6, 7, 3), "VIsus2", "submediant sus2"),
    ]),
    ("Suspended 4th chords (sus4)", [
        ((1, 4, 5), "Isus", "tonic with 4 replacing 3"),
        ((2, 5, 6), "IIsus", "supertonic sus4"),
        ((3, 6, 7), "IIIsus", "mediant sus4"),
        ((5, 1, 2), "Vsus", "dominant sus, delays resolution"),
        ((6, 2, 3), "VIsus", "submediant sus4"),
    ]),
    ("Power chords (root + 5th, no 3rd)", [
        ((1, 5), "I5", "tonic power chord"),
        ((2, 6), "II5", "supertonic power chord"),
        ((3, 7), "III5", "mediant power chord"),
        ((4, 1), "IV5", "subdominant power chord"),
        ((5, 2), "V5", "dominant power chord"),
        ((6, 3), "VI5", "submediant power chord"),
    ]),
    ("add9 chords (triad + 9, no 7)", [
        ((1, 3, 5, 2), "Iadd9", "tonic add 9"),
        ((2, 4, 6, 3), "iiadd9", "ii minor add 9"),
        ((4, 6, 1, 5), "IVadd9", "IV add 9"),
        ((5, 7, 2, 6), "Vadd9", "V add 9"),
        ((6, 1, 3, 7), "viadd9", "vi minor add 9"),
    ]),
    ("add11 chords (triad + 11, no 7)", [
        ((1, 3, 5, 4), "Iadd11", "tonic add 11 (rare — 3-4 clash)"),
        ((2, 4, 6, 5), "iiadd11", "ii minor add 11"),
        ((3, 5, 7, 6), "iiiadd11", "iii minor add 11"),
        ((5, 7, 2, 1), "Vadd11", "V add 11 (clash — usually voiced sus)"),
        ((6, 1, 3, 2), "viadd11", "vi minor add 11"),
        ((7, 2, 4, 3), "vii°add11", "vii° add 11"),
        ((4, 6, 1, 7), "IVadd11", "IV Lydian add 11 (the diatonic VII — chord-theory ♯11)"),
    ]),
    ("6/9 chords (major triad + 6 + 9)", [
        ((1, 3, 5, 6, 2), "I6/9", "tonic 6/9, very harp-friendly"),
        ((4, 6, 1, 2, 5), "IV6/9", "IV 6/9"),
        ((5, 7, 2, 3, 6), "V6/9", "V 6/9"),
    ]),
    ("Minor 6/9", [
        ((2, 4, 6, 7, 3), "ii6/9", "ii minor 6/9 — Dorian-flavored"),
    ]),
    ("9th chords (7th + 9)", [
        ((1, 3, 5, 7, 2), "IΔ9", "tonic major 9"),
        ((2, 4, 6, 1, 3), "ii9", "ii minor 9"),
        ((3, 5, 7, 2, 4), "iii9", "iii minor 9 — the diatonic 9 here is the half-step above I, so it's dissonant"),
        ((4, 6, 1, 3, 5), "IVΔ9", "IV major 9"),
        ((5, 7, 2, 4, 6), "V9", "dominant 9"),
        ((6, 1, 3, 5, 7), "vi9", "vi minor 9"),
        ((7, 2, 4, 6, 1), "VII⌀9", "half-dim 9 — the diatonic 9 here is the half-step above VII"),
    ]),
    ("11th chords", [
        ((2, 4, 6, 1, 3, 5), "ii11", "ii minor 11"),
        ((3, 5, 7, 2, 4, 6), "iii11", "iii minor 11 (the half-step 9 is still in the stack)"),
        ((4, 6, 1, 3, 5, 7), "IVΔ11", "IV Lydian — all-diatonic 11 (chord-theory ♯11)"),
        ((5, 7, 2, 4, 6, 1), "V11", "dominant 11 — clashes; usually voiced as V9sus"),
        ((6, 1, 3, 5, 7, 2), "vi11", "vi minor 11"),
        ((7, 2, 4, 6, 1, 3), "VII⌀11", "half-dim 11"),
    ]),
    ("13th chords", [
        ((1, 3, 5, 7, 2, 6), "IΔ13_B", "tonic major 13 (skip 11 — would clash)"),
        ((2, 4, 6, 1, 3, 5, 7), "ii13", "ii minor 13 — full diatonic Dorian stack"),
        ((4, 6, 1, 3, 5, 7, 2), "IVΔ13", "IV Lydian 13 — all 7 scale degrees"),
        ((5, 7, 2, 4, 6, 3), "V13_B", "dominant 13 (skip the 11)"),
        ((6, 1, 3, 5, 7, 2, 4), "vi13", "vi minor 13 — the 13 here is the diatonic 6, a half-step from VII"),
    ]),
    ("Seventh chord suspensions", [
        ((5, 1, 2, 4), "V7sus", "dominant 7 sus — classic delayed-resolution"),
        ((1, 4, 5, 7), "IΔsus", "tonic major 7 sus"),
        ((2, 5, 6, 1), "ii7sus", "ii sus 7"),
        ((6, 2, 3, 5), "vi7sus", "vi sus 7"),
    ]),
    ("Pedal-tone slash chords", [
        ((1, 4, 6, 1), "IV/I", "subdominant over tonic pedal"),
        ((5, 4, 6, 1), "IV/V", "subdominant over dominant pedal"),
        ((5, 1, 3, 5), "I/V", "tonic over dominant pedal — opening sound"),
        ((1, 2, 4, 6), "ii/I", "ii minor over tonic pedal — moody"),
        ((5, 2, 4, 6), "ii/V", "ii minor over dominant pedal — pre-cadential"),
        ((1, 6, 1, 3), "vi/I", "relative minor over tonic pedal"),
        ((1, 3, 5, 7), "iii/I", "mediant minor over tonic pedal (same notes as IΔ)"),
        ((1, 5, 7, 2, 4), "V7/I", "dominant 7 over tonic pedal — V over I drone"),
    ]),
    ("Quartal three-note voicings (stacked 4ths)", [
        ((1, 4, 7), "Iq", "tonic quartal — contains tritone"),
        ((2, 5, 1), "IIq", "supertonic quartal — open sound"),
        ((3, 6, 2), "IIIq", "mediant quartal"),
        ((4, 7, 3), "IVq", "subdominant quartal — contains tritone"),
        ((5, 1, 4), "Vq", "dominant quartal"),
        ((6, 2, 5), "VIq", "submediant quartal"),
        ((7, 3, 6), "VIIq", "leading-tone quartal"),
    ]),
    ("Quartal four-note voicings", [
        ((1, 4, 7, 3), "Iq4", "tonic quartal, 4 notes"),
        ((2, 5, 1, 4), "IIq4", "supertonic quartal — Dorian flavor"),
        ((3, 6, 2, 5), "IIIq4", "mediant quartal, 4 notes"),
        ((5, 1, 4, 7), "Vq4", "dominant quartal, 4 notes"),
        ((6, 2, 5, 1), "VIq4", "submediant quartal, 4 notes"),
    ]),
    ("Quartal five-note voicings (“So What” style)", [
        ((2, 5, 1, 4, 7), "IIq5", "five-note quartal — Dorian vamp voicing"),
        ((3, 6, 2, 5, 1), "IIIq5", "five-note quartal on III"),
        ((5, 1, 4, 7, 3), "Vq5", "five-note quartal on V"),
        ((6, 2, 5, 1, 4), "VIq5", "five-note quartal on VI"),
    ]),
]

SECTIONS_POLY: list[tuple[str, str, list[tuple[int, int, str, str]]]] = [
    ("Triads stacked over I  (tonic colors)",
     "Lower hand holds the tonic. The upper hand selects the extension flavor — major 9, 11, 13, or 6 — depending on which triad sits above.", [
        (1, 5, "IΔ9", "dominant over tonic — the open, suspended-tonic sound (1 3 5 / 5 7 2)"),
        (1, 6, "I6", "submediant over tonic — the classic shimmering 6 (1 3 5 / 6 1 3)"),
        (1, 2, "I13_7", "supertonic over tonic — 9, 11, 13 stacked above the triad, no 7 (1 3 5 / 2 4 6)"),
        (1, 3, "IΔ", "mediant over tonic — same notes as IΔ7 (1 3 5 / 3 5 7)"),
        (1, 7, "IΔ11", "leading-tone diminished over tonic — Δ11 with all upper extensions (1 3 5 / 7 2 4)"),
    ]),
    ("Triads stacked over ii  (Dorian / supertonic colors)",
     "Lower hand holds the supertonic minor. Upper triads add 9, 11, 13 — the Dorian palette.", [
        (2, 4, "ii7", "subdominant over supertonic — basic m7 voicing (2 4 6 / 4 6 1)"),
        (2, 1, "ii11", "tonic over supertonic — m11, full Dorian stack (2 4 6 / 1 3 5)"),
        (2, 5, "ii13_7", "dominant over supertonic — m13 voicing, no 7; floats between Vsus and m11 (2 4 6 / 5 7 2)"),
        (2, 3, "ii13_7", "mediant over supertonic — m13 voicing, no 7; layered 9 and 11 below (2 4 6 / 3 5 7)"),
        (2, 6, "ii9", "submediant over supertonic — m9, no 7-9 clash above (2 4 6 / 6 1 3)"),
    ]),
    ("Triads stacked over IV  (subdominant / Lydian colors)",
     "Lower hand holds the subdominant. Upper triads naturally produce Lydian-flavored 11 and major 13 voicings — the diatonic 11 from IV is what chord theory calls ♯11.", [
        (4, 5, "IVΔ13_7", "dominant over subdominant — the bright Lydian 13 (4 6 1 / 5 7 2)"),
        (4, 1, "IVΔ9", "tonic over subdominant — I/IV sound, gospel-flavored (4 6 1 / 1 3 5)"),
        (4, 2, "IV6", "supertonic over subdominant — IV6 (4 6 1 / 2 4 6)"),
        (4, 3, "IVΔ11", "mediant over subdominant — the floating Lydian sound (4 6 1 / 3 5 7)"),
        (4, 6, "IVΔ", "submediant over subdominant — same notes as IVΔ7 (4 6 1 / 6 1 3)"),
    ]),
    ("Triads stacked over V  (dominant colors, fully diatonic)",
     "Lower hand holds the dominant. Upper triads give 9, 11, 13 and sus colors. The classic jazz move ii~V7 lives here as IV~V.", [
        (5, 1, "V13_7", "tonic over dominant — the iconic suspended-dominant sound (no 7); resolves to I (5 7 2 / 1 3 5)"),
        (5, 2, "V9", "supertonic over dominant — dominant 9, avoids the 11 clash (5 7 2 / 2 4 6)"),
        (5, 4, "V11", "subdominant over dominant — full dominant-11 pre-cadential tension (5 7 2 / 4 6 1)"),
        (5, 6, "V13_7", "submediant over dominant — vi7 over V = dominant-13 sound, no 7 (5 7 2 / 6 1 3)"),
        (5, 3, "V6", "mediant over dominant — triad + 13 only; the 11 (=IV) is absent (5 7 2 / 3 5 7)"),
        (5, 7, "V7", "leading-tone over dominant — basic dominant 7 voicing (5 7 2 / 7 2 4)"),
    ]),
    ("Triads stacked over vi  (relative-minor colors)",
     "Lower hand holds the submediant minor. Upper triads color the relative minor with 9s and 11s.", [
        (6, 1, "vi7", "tonic over submediant — basic m7 voicing (6 1 3 / 1 3 5)"),
        (6, 2, "vi13_7", "supertonic over submediant — m13 with no 7 (6 1 3 / 2 4 6)"),
        (6, 5, "vi11", "dominant over submediant — full Aeolian m11 (6 1 3 / 5 7 2)"),
        (6, 4, "vi13_7", "subdominant over submediant — same notes as IVΔ rooted lower (6 1 3 / 4 6 1)"),
        (6, 3, "vi9", "mediant over submediant — dense, contains all of IΔ (6 1 3 / 3 5 7)"),
    ]),
    ("Triads stacked over iii  (mediant / Phrygian colors)",
     "Lower hand holds the mediant minor. Upper triads add 9, 11, 13 — diatonic 9 from III is the half-step above III (Phrygian flavor); diatonic 13 from III is the half-step above V.", [
        (3, 4, "iii11", "subdominant over mediant — Phrygian m11 with diatonic 9 and 13 (3 5 7 / 4 6 1)"),
        (3, 1, "iii13_7", "tonic over mediant — m13 with no 7, Phrygian flavor (3 5 7 / 1 3 5)"),
        (3, 2, "iii11", "supertonic over mediant — Phrygian m11 with stacked extensions (3 5 7 / 2 4 6)"),
        (3, 6, "iii13_7", "submediant over mediant — m13 with no 7; same notes as IΔ9 rooted lower (3 5 7 / 6 1 3)"),
        (3, 5, "iii7", "rare; dominant over mediant — basic m7 (3 5 7 / 5 7 2)"),
    ]),
    ("Triads stacked over vii°  (leading-tone colors)",
     "Lower hand holds the leading-tone diminished. A tonic triad above gives the rootless dominant 9 sound.", [
        (7, 1, "V9_1", "tonic over leading-tone — the classic rootless V9 (7 2 4 / 1 3 5)"),
        (7, 2, "VII⌀", "supertonic over leading-tone — basic half-dim 7 voicing (7 2 4 / 2 4 6)"),
        (7, 4, "VII⌀9", "subdominant over leading-tone — half-dim 9, Locrian flavor (7 2 4 / 4 6 1)"),
        (7, 5, "VII⌀13_7", "variant; dominant over leading-tone — strong pull to I (7 2 4 / 5 7 2)"),
    ]),
]

# ---------------------------------------------------------------------------
# Music-theory helpers (port of shapedrills.html's JS)
# ---------------------------------------------------------------------------

LETTERS = ["C", "D", "E", "F", "G", "A", "B"]


def build_strings_lever_c() -> list[dict]:
    """30 strings in C major, lowest C2 (lever-30 layout)."""
    out = []
    for i in range(30):
        letter = LETTERS[i % 7]
        deg = (i % 7) + 1
        octave = 2 + (i // 7)
        out.append({"idx": i, "letter": letter, "degree": deg, "octave": octave})
    return out


def render_voicing(stack: tuple[int, ...], strings: list[dict]) -> list[int] | None:
    """Walk the stack up the harp; return list of placed string indices."""
    bass = next((s["idx"] for s in strings if s["degree"] == stack[0]), None)
    if bass is None:
        return None
    placements = [bass]
    pos = 1
    while True:
        target = stack[pos % len(stack)]
        prev = placements[-1]
        nxt = next((s["idx"] for s in strings if s["idx"] > prev and s["degree"] == target), None)
        if nxt is None:
            break
        placements.append(nxt)
        pos += 1
    return placements


def place_triad(root: int, after_idx: int, strings: list[dict]) -> list[int] | None:
    third = ((root - 1 + 2) % 7) + 1
    fifth = ((root - 1 + 4) % 7) + 1
    positions: list[int] = []
    search = after_idx + 1
    for want in (root, third, fifth):
        found = next((i for i in range(search, len(strings)) if strings[i]["degree"] == want), None)
        if found is None:
            return None
        positions.append(found)
        search = found + 1
    return positions


def render_polychord(lh: int, rh: int, strings: list[dict]) -> tuple[set[int], set[int]] | None:
    lh_pos = place_triad(lh, -1, strings)
    if lh_pos is None:
        return None
    rh_pos = place_triad(rh, lh_pos[-1], strings)
    if rh_pos is None:
        return None
    return set(lh_pos), set(rh_pos)


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------

def latex_escape_serif(s: str) -> str:
    """Escape for DejaVu Serif (description text). Substitutes ⌀ → ø since
    DejaVu Serif lacks the half-dim glyph."""
    s = s.replace("⌀", "ø")
    repl = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
        ("_", "\\_"), ("{", "\\{"), ("}", "\\}"),
        ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"),
    ]
    for a, b in repl:
        s = s.replace(a, b)
    return s


def latex_escape_juliamono(s: str) -> str:
    """Escape for JuliaMono (chord notation). Keeps ⌀ — JuliaMono has it."""
    repl = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
        ("_", "\\_"), ("{", "\\{"), ("}", "\\}"),
        ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"),
    ]
    for a, b in repl:
        s = s.replace(a, b)
    return s


# (the _<hex> subscript convention for missing chord tones was retired
#  with the move back to traditional Roman-numeral notation.)


_ROMAN_RE = __import__("re").compile(
    r"^([♭♯])?(VII|III|VI|IV|II|V|I|vii|iii|vi|iv|ii|v|i)(°?)(.*)$"
)


def _escape_latex_chord(s: str) -> str:
    out: list[str] = []
    for ch in s:
        if ch == "\\":   out.append(r"\textbackslash{}")
        elif ch == "&":  out.append(r"\&")
        elif ch == "%":  out.append(r"\%")
        elif ch == "$":  out.append(r"\$")
        elif ch == "#":  out.append(r"\#")
        elif ch == "_":  out.append(r"\_")
        elif ch == "{":  out.append(r"\{")
        elif ch == "}":  out.append(r"\}")
        elif ch == "~":  out.append(r"\textasciitilde{}")
        elif ch == "^":  out.append(r"\textasciicircum{}")
        else:            out.append(ch)
    return "".join(out)


def _bold_roman_piece(piece: str) -> str:
    """Wrap the leading Roman-numeral (+ optional ° dim mark) of a chord
    piece in \\textbf{} so the Roman renders bold and the suffix renders
    regular weight. If the piece doesn't parse as a chord, it is escaped
    and returned as-is."""
    m = _ROMAN_RE.match(piece)
    if not m:
        return _escape_latex_chord(piece)
    acc, roman, dim, suffix = m.group(1) or "", m.group(2), m.group(3) or "", m.group(4) or ""
    return (_escape_latex_chord(acc)
            + r"\textbf{" + roman + dim + r"}"
            + _escape_latex_chord(suffix))


def _split_slash(piece: str) -> str:
    """Bold Roman on each side of a slash-bass (`V/I`)."""
    if "/" in piece:
        chord, _, bass = piece.partition("/")
        return _bold_roman_piece(chord) + "/" + _bold_roman_piece(bass)
    return _bold_roman_piece(piece)


def render_chord_latex(sym: str) -> str:
    """Render a chord label or polychord stack as LaTeX. The Roman
    numeral portion (and any trailing ° dim mark) is bold; the suffix is
    regular weight. Polychord stacks (``IV~iii``) split on tilde and
    bold each piece; slash-bass (``V/I``) bolds both sides."""
    if "~" in sym:
        return r"\textasciitilde{}".join(_split_slash(p) for p in sym.split("~"))
    return _split_slash(sym)


def format_comment(template: str, scale_letters: list[str]) -> str:
    """Substitute {1}..{7} placeholders with C-major scale letters."""
    out = template
    for d in range(1, 8):
        out = out.replace("{" + str(d) + "}", scale_letters[d - 1])
    return out


def render_single_row(stack: tuple[int, ...], strings: list[dict]) -> str:
    """Latex chunk: one chord rendered as 30 colored chars (played + unplayed)."""
    placed = set(render_voicing(stack, strings) or [])
    parts: list[str] = []
    for s in strings:
        if s["idx"] in placed:
            parts.append(r"\played{" + s["letter"] + r"}")
        else:
            parts.append(r"\unplay")
    return "".join(parts)


def render_poly_row(lh: int, rh: int, strings: list[dict]) -> str | None:
    placement = render_polychord(lh, rh, strings)
    if placement is None:
        return None
    lh_set, rh_set = placement
    parts: list[str] = []
    for s in strings:
        if s["idx"] in lh_set:
            # Project convention: lowercase = LH, UPPERCASE = RH (B&W friendly).
            parts.append(r"\plLH{" + s["letter"].lower() + r"}")
        elif s["idx"] in rh_set:
            parts.append(r"\plRH{" + s["letter"] + r"}")
        else:
            parts.append(r"\unplay")
    return "".join(parts)


def visual_width(s: str) -> int:
    """Char count ignoring combining marks (U+0300-U+036F)."""
    n = 0
    for ch in s:
        cp = ord(ch)
        if 0x0300 <= cp <= 0x036F:
            continue
        n += 1
    return n


def pad_visual(s: str, width: int) -> str:
    vw = visual_width(s)
    return s + (" " * (width - vw)) if vw < width else s


def build_tex(font_dir: Path) -> str:
    strings = build_strings_lever_c()
    scale_letters = ["C", "D", "E", "F", "G", "A", "B"]
    font_path = str(font_dir).rstrip("/") + "/"

    lines: list[str] = [
        r"\documentclass[10pt]{article}",
        r"\usepackage[letterpaper,top=0.45in,bottom=0.5in,left=0.4in,right=0.4in]{geometry}",
        r"\usepackage{fontspec}",
        r"\usepackage{xcolor}",
        r"\usepackage{longtable}",
        r"\usepackage{array}",
        r"\setmainfont{DejaVu Serif}",
        # JuliaMono for the harp string layout + chord notation.
        # No FakeBold — synthetic stroking distorts combining marks (the
        # caret on I, II, etc.). SemiBold alone gives the weight we need.
        r"\newfontfamily\juliamono[",
        r"  Path=" + font_path + ",",
        r"  Extension=.ttf,",
        r"  UprightFont=JuliaMono-Medium,",
        r"  BoldFont=JuliaMono-SemiBold,",
        r"  Scale=0.82,",
        r"]{JuliaMono-Medium}",
        # Black & white: keep a single light-gray for unplayed dots so played
        # notes pop, but no color anywhere else. LH/RH distinguished by case
        # (lowercase = LH, UPPERCASE = RH) per the project convention.
        r"\definecolor{ink}{HTML}{000000}",
        r"\definecolor{inksoft}{HTML}{555555}",
        r"\definecolor{unplayed}{HTML}{B5B0A6}",
        r"\newcommand{\played}[1]{\textbf{#1}}",
        r"\newcommand{\unplay}{\textcolor{unplayed}{\textperiodcentered}}",
        r"\newcommand{\plLH}[1]{\textbf{#1}}",
        r"\newcommand{\plRH}[1]{\textbf{#1}}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\parskip}{0pt}",
        r"\renewcommand{\arraystretch}{1.05}",
        r"\setlength{\LTpre}{0pt}",
        r"\setlength{\LTpost}{0pt}",
        r"\pagestyle{plain}",
        r"\begin{document}",
        r"\noindent{\LARGE\bfseries Harp Chord Handout}\\[0.2em]",
        r"\noindent{\small Catalog mirror of \texttt{shapedrills.html} \textemdash{} 30-string lever harp, key of C major}\\[0.05em]",
        r"\noindent{\small \textit{Strings low \textrightarrow{} high; played notes in bold, dots are unplayed.\quad "
        r"Polychords:} \textbf{lower-case} \textit{= LH triad,} \textbf{UPPER-CASE} \textit{= RH triad}\par",
        r"\vspace{0.6em}",
    ]

    # Column widths for the master table (4 columns).
    # Total usable width on A4 with 0.4in margins ≈ 540pt.
    #   col1 (string grid, JuliaMono 30 chars @ Scale=0.78): ~145pt → 150pt
    #   col2 (symbol):                                       55pt
    #   col3 (equivalent / extra info, polychord only):      75pt
    #   col4 (description):                                  rest = ~245pt
    col_spec = (
        r"@{}>{\juliamono}l"     # col 1: string row, mono, no leading space
        r"@{\hspace{8pt}}>{\juliamono\bfseries}l"                # col 2: symbol
        r"@{\hspace{8pt}}>{\juliamono\bfseries}l"                # col 3: extra info
        r"@{\hspace{8pt}}>{\raggedright\arraybackslash}p{3.5in}@{}"  # col 4: desc, ragged
    )

    lines += [
        r"\begin{longtable}{" + col_spec + r"}",
    ]

    # Header rows
    header_letters = "".join(r"\played{" + s["letter"] + r"}" for s in strings)
    header_degrees = "".join(r"{\textbf{" + str(s["degree"]) + r"}}" for s in strings)
    # Header letters use the macros, so suppress the column's own \juliamono via {} group
    lines += [
        r"\multicolumn{1}{@{}l@{}}{{\juliamono " + header_letters + r"}} & "
        r"\multicolumn{3}{@{\hspace{8pt}}l@{}}{\small\textit{string layout, lowest is C2 / scale degrees below}} \\",
        r"\multicolumn{1}{@{}l@{}}{{\juliamono " + header_degrees + r"}} & "
        r"\multicolumn{3}{@{\hspace{8pt}}l@{}}{} \\[0.4em]",
    ]

    def section_row(title: str) -> str:
        return (
            r"\multicolumn{4}{@{}l@{}}{\rule{0pt}{1.4em}"
            r"\textbf{\normalsize " + latex_escape_serif(title) + r"}}\\[0.1em]"
        )

    def blurb_row(blurb: str) -> str:
        return (
            r"\multicolumn{4}{@{}>{\raggedright\arraybackslash}p{\linewidth}@{}}"
            r"{\itshape\small\color{inksoft} "
            + latex_escape_serif(blurb) + r"}\\[0.1em]"
        )

    # Single-hand sections
    for title, items in SECTIONS_SINGLE:
        lines.append(section_row(title))
        for stack, sym, comment_template in items:
            row = render_single_row(stack, strings)
            comment = format_comment(comment_template, scale_letters)
            sym_esc = render_chord_latex(sym)
            lines.append(
                r"{" + row + r"} & "
                r"" + sym_esc + r" & "
                r" & "
                r"{\small " + latex_escape_serif(comment) + r"} \\"
            )

    # Polychord sections
    for title, blurb, items in SECTIONS_POLY:
        lines.append(section_row(title))
        lines.append(blurb_row(blurb))
        for lh, rh, equiv, comment in items:
            row = render_poly_row(lh, rh, strings)
            if row is None:
                continue
            sym = f"{deg_to_roman(rh)}~{deg_to_roman(lh)}"
            sym_esc = render_chord_latex(sym)
            equiv_esc = render_chord_latex(equiv)
            lines.append(
                r"{" + row + r"} & "
                r"" + sym_esc + r" & "
                r"{= " + equiv_esc + r"} & "
                r"{\small " + latex_escape_serif(comment) + r"} \\"
            )

    lines += [
        r"\end{longtable}",
        r"\end{document}",
    ]
    return "\n".join(lines)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    assets = repo_root / "tablet_app" / "app" / "src" / "main" / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    font_dir = repo_root / "viewer" / "font"
    if not (font_dir / "JuliaMono-Medium.ttf").exists():
        print(f"error: JuliaMono-Medium.ttf not found in {font_dir}")
        return 1

    tex_path = assets / "handout.tex"
    pdf_path = assets / "handout.pdf"
    aux_path = assets / "handout.aux"
    log_path = assets / "handout.log"

    tex_path.write_text(build_tex(font_dir), encoding="utf-8")

    if not shutil.which("xelatex"):
        print("error: xelatex not found in PATH")
        return 1

    result = subprocess.run(
        ["xelatex", "-interaction=nonstopmode",
         "-output-directory", str(assets), str(tex_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not pdf_path.exists():
        print("xelatex failed:")
        print((result.stdout or "")[-2500:])
        return 1

    for stray in (aux_path, log_path):
        if stray.exists():
            stray.unlink()

    print(f"wrote {pdf_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
