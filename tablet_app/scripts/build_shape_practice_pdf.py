#!/usr/bin/env python3
"""Generate a one-page PDF practice list grouped by hand-shape.

Mirrors the "By Shape" mode of `shapedrills.html`: every chord in the combined
single-hand + polychord catalog is grouped by its interval-step shape signature
(e.g., `33` for root-position triads, `33~3~33` for a polychord with a 3rd
between hands). For each shape, the PDF lists the shape, a short description,
and every chord symbol that shares it.

Output: ``tablet_app/app/src/main/assets/shape-practice.pdf``.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Catalogs (kept in sync with shapedrills.html)
# ---------------------------------------------------------------------------

SECTIONS_SINGLE: list[tuple[str, list[tuple[tuple[int, ...], str]]]] = [
    ("Diatonic triads (root)", [
        ((1, 3, 5), "I"), ((2, 4, 6), "ii"),
        ((3, 5, 7), "iii"), ((4, 6, 1), "IV"),
        ((5, 7, 2), "V"), ((6, 1, 3), "vi"),
        ((7, 2, 4), "vii°"),
    ]),
    ("Triads, 1st inv", [
        ((3, 5, 1), "I/III"), ((4, 6, 2), "ii/IV"),
        ((5, 7, 3), "iii/V"), ((6, 1, 4), "IV/VI"),
        ((7, 2, 5), "V/VII"), ((1, 3, 6), "vi/I"),
        ((2, 4, 7), "vii°/II"),
    ]),
    ("Triads, 2nd inv", [
        ((5, 1, 3), "I/V"), ((6, 2, 4), "ii/VI"),
        ((7, 3, 5), "iii/VII"), ((1, 4, 6), "IV/I"),
        ((2, 5, 7), "V/II"), ((3, 6, 1), "vi/III"),
        ((4, 7, 2), "vii°/IV"),
    ]),
    ("7ths root", [
        ((1, 3, 5, 7), "IΔ"), ((2, 4, 6, 1), "ii7"),
        ((3, 5, 7, 2), "iii7"), ((4, 6, 1, 3), "IVΔ"),
        ((5, 7, 2, 4), "V7"), ((6, 1, 3, 5), "vi7"),
        ((7, 2, 4, 6), "VII⌀"),
    ]),
    ("7ths 1st inv", [
        ((3, 5, 7, 1), "IΔ/III"),
        ((4, 6, 1, 2), "ii7/IV"),
        ((6, 1, 3, 4), "IVΔ/VI"),
        ((7, 2, 4, 5), "V7/VII"),
        ((1, 3, 5, 6), "vi7/I"),
    ]),
    ("7ths 2nd/3rd inv", [
        ((5, 7, 1, 3), "IΔ/V"),
        ((7, 1, 3, 5), "IΔ/VII"),
        ((2, 4, 5, 7), "V7/II"),
        ((4, 5, 7, 2), "V7/IV"),
        ((1, 2, 4, 6), "ii7/I"),
    ]),
    ("6 chords", [
        ((1, 3, 5, 6), "I6"), ((4, 6, 1, 2), "IV6"),
        ((5, 7, 2, 3), "V6"),
    ]),
    ("m6", [
        ((2, 4, 6, 7), "ii6"),
    ]),
    ("sus2", [
        ((1, 2, 5), "Isus2"), ((2, 3, 6), "IIsus2"),
        ((4, 5, 1), "IVsus2"), ((5, 6, 2), "Vsus2"),
        ((6, 7, 3), "VIsus2"),
    ]),
    ("sus4", [
        ((1, 4, 5), "Isus"), ((2, 5, 6), "IIsus"),
        ((3, 6, 7), "IIIsus"), ((5, 1, 2), "Vsus"),
        ((6, 2, 3), "VIsus"),
    ]),
    ("Power", [
        ((1, 5), "I5"), ((2, 6), "II5"), ((3, 7), "III5"),
        ((4, 1), "IV5"), ((5, 2), "V5"), ((6, 3), "VI5"),
    ]),
    ("add9", [
        ((1, 3, 5, 2), "Iadd9"), ((2, 4, 6, 3), "iiadd9"),
        ((4, 6, 1, 5), "IVadd9"), ((5, 7, 2, 6), "Vadd9"),
        ((6, 1, 3, 7), "viadd9"),
    ]),
    ("add11", [
        ((1, 3, 5, 4), "Iadd11"), ((2, 4, 6, 5), "iiadd11"),
        ((3, 5, 7, 6), "iiiadd11"), ((5, 7, 2, 1), "Vadd11"),
        ((6, 1, 3, 2), "viadd11"), ((7, 2, 4, 3), "vii°add11"),
        ((4, 6, 1, 7), "IVadd♯11"),
    ]),
    ("6/9", [
        ((1, 3, 5, 6, 2), "I6/9"), ((4, 6, 1, 2, 5), "IV6/9"),
        ((5, 7, 2, 3, 6), "V6/9"),
    ]),
    ("m6/9", [
        ((2, 4, 6, 7, 3), "ii6/9"),
    ]),
    ("9th", [
        ((1, 3, 5, 7, 2), "IΔ9"), ((2, 4, 6, 1, 3), "ii9"),
        ((3, 5, 7, 2, 4), "iii♭9"), ((4, 6, 1, 3, 5), "IVΔ9"),
        ((5, 7, 2, 4, 6), "V9"), ((6, 1, 3, 5, 7), "vi9"),
        ((7, 2, 4, 6, 1), "VII⌀♭9"),
    ]),
    ("11th", [
        ((2, 4, 6, 1, 3, 5), "ii11"), ((3, 5, 7, 2, 4, 6), "iii11"),
        ((4, 6, 1, 3, 5, 7), "IVΔ♯11"),
        ((5, 7, 2, 4, 6, 1), "V11"), ((6, 1, 3, 5, 7, 2), "vi11"),
        ((7, 2, 4, 6, 1, 3), "VII⌀11"),
    ]),
    ("13th", [
        ((1, 3, 5, 7, 2, 6), "IΔ13"),
        ((2, 4, 6, 1, 3, 5, 7), "ii13"),
        ((4, 6, 1, 3, 5, 7, 2), "IVΔ13"),
        ((5, 7, 2, 4, 6, 3), "V13"),
        ((6, 1, 3, 5, 7, 2, 4), "vi♭13"),
    ]),
    ("7sus", [
        ((5, 1, 2, 4), "V7sus"), ((1, 4, 5, 7), "IΔsus"),
        ((2, 5, 6, 1), "ii7sus"), ((6, 2, 3, 5), "vi7sus"),
    ]),
    ("Pedal slash", [
        ((1, 4, 6, 1), "IV/I"), ((5, 4, 6, 1), "IV/V"),
        ((5, 1, 3, 5), "I/V"), ((1, 2, 4, 6), "ii/I"),
        ((5, 2, 4, 6), "ii/V"), ((1, 6, 1, 3), "vi/I"),
        ((1, 3, 5, 7), "iii/I"),
        ((1, 5, 7, 2, 4), "V7/I"),
    ]),
    ("Quartal 3", [
        ((1, 4, 7), "Iq"), ((2, 5, 1), "IIq"), ((3, 6, 2), "IIIq"),
        ((4, 7, 3), "IVq"), ((5, 1, 4), "Vq"), ((6, 2, 5), "VIq"),
        ((7, 3, 6), "VIIq"),
    ]),
    ("Quartal 4", [
        ((1, 4, 7, 3), "Iq4"), ((2, 5, 1, 4), "IIq4"),
        ((3, 6, 2, 5), "IIIq4"), ((5, 1, 4, 7), "Vq4"),
        ((6, 2, 5, 1), "VIq4"),
    ]),
    ("Quartal 5", [
        ((2, 5, 1, 4, 7), "IIq5"), ((3, 6, 2, 5, 1), "IIIq5"),
        ((5, 1, 4, 7, 3), "Vq5"), ((6, 2, 5, 1, 4), "VIq5"),
    ]),
]

SECTIONS_POLY: list[tuple[int, int]] = [
    (1, 5), (1, 6), (1, 2), (1, 3), (1, 7),
    (2, 4), (2, 1), (2, 5), (2, 3), (2, 6),
    (4, 5), (4, 1), (4, 2), (4, 3), (4, 6),
    (5, 1), (5, 2), (5, 4), (5, 6), (5, 3), (5, 7),
    (6, 1), (6, 2), (6, 5), (6, 4), (6, 3),
    (3, 4), (3, 1), (3, 2), (3, 6), (3, 5),
    (7, 1), (7, 2), (7, 4), (7, 5),
]

SHAPE_DESC: dict[str, str] = {
    "5":       "root + 5th (power chord)",
    "24":      "sus2 (3 replaced by 2)",
    "33":      "root-position triad",
    "34":      "first-inversion triad (3rd in bass)",
    "42":      "sus4 (3 replaced by 4)",
    "43":      "second-inversion triad (5th in bass)",
    "44":      "quartal three-note voicing",
    "233":     "7th chord, 3rd in bass",
    "323":     "7th chord, 5th in bass",
    "332":     "7th 1st inv (also 6 chord, m6)",
    "333":     "root-position 7th chord",
    "335":     "add9 (root + triad + 9 above)",
    "337":     "add11 (root + triad + 11 above)",
    "423":     "7th sus (delayed resolution)",
    "433":     "tonic triad over IV pedal (or 1/5 voicing)",
    "444":     "quartal four-note (Dorian / open)",
    "533":     "ii minor over V pedal (pre-cadential)",
    "633":     "relative minor over tonic pedal",
    "733":     "subdominant over dominant pedal",
    "3324":    "6/9 chord (triad + 6 + 9)",
    "3333":    "root-position 9th chord",
    "4444":    "quartal five-note (“So What” voicing)",
    "5333":    "V7 over tonic pedal (V/I drone)",
    "33333":   "root-position 11th chord",
    "33335":   "13th chord skipping the 11",
    "333333":  "full diatonic 13th chord (all 7 degrees)",
    "33~2~33": "LH triad, step up a 2nd, RH triad - tight stack",
    "33~3~33": "LH triad, up a 3rd, RH triad - layered diatonic stack",
    "33~5~33": "LH triad, up a 5th, RH triad - dominant-spaced",
    "33~6~33": "LH triad, up a 6th, RH triad - wide pre-octave gap",
    "33~7~33": "LH triad, up a 7th, RH triad - near-octave gap",
    "33~8~33": "LH triad, octave gap, RH triad - widest spacing",
}


def interval_up(a: int, b: int) -> int:
    """Diatonic interval name from degree a UP to next b. 1->3 = 3rd."""
    steps = ((b - a - 1) % 7 + 7) % 7 + 1
    return steps + 1


def single_shape(stack: tuple[int, ...]) -> str:
    return "".join(str(interval_up(stack[i], stack[i + 1])) for i in range(len(stack) - 1))


def poly_shape(lh: int, rh: int) -> str:
    top = ((lh - 1 + 4) % 7) + 1
    return f"33~{interval_up(top, rh)}~33"


def deg_to_roman(d: int) -> str:
    """Scale degree (1..7) -> diatonic-quality Roman numeral in C major."""
    upper = ["", "I", "II", "III", "IV", "V", "VI", "VII"][d]
    if d in (2, 3, 6):
        return upper.lower()
    if d == 7:
        return upper.lower() + "°"
    return upper


def poly_symbol(lh: int, rh: int) -> str:
    return f"{deg_to_roman(rh)}~{deg_to_roman(lh)}"


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------

def latex_escape(s: str) -> str:
    """Convert text to LaTeX-safe form. Used for descriptions and any text
    rendered in the main (non-mono) font. ⌀ kept as-is — JuliaMono has it."""
    repl = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    for a, b in repl:
        s = s.replace(a, b)
    return s


_ROMAN_RE = __import__("re").compile(
    r"^([♭♯])?(VII|III|VI|IV|II|V|I|vii|iii|vi|iv|ii|v|i)(°?)(.*)$"
)


def _bold_roman_piece(piece: str) -> str:
    """Bold the Roman numeral (+ optional °) of a chord piece, leave the
    suffix in regular weight. Non-chord pieces are LaTeX-escaped as-is."""
    m = _ROMAN_RE.match(piece)
    if not m:
        return latex_escape(piece)
    acc, roman, dim, suffix = m.group(1) or "", m.group(2), m.group(3) or "", m.group(4) or ""
    return latex_escape(acc) + r"\textbf{" + roman + dim + r"}" + latex_escape(suffix)


def _split_slash(piece: str) -> str:
    """Bold Roman on each side of slash-bass."""
    if "/" in piece:
        chord, _, bass = piece.partition("/")
        return _bold_roman_piece(chord) + "/" + _bold_roman_piece(bass)
    return _bold_roman_piece(piece)


def render_chord_latex(sym: str) -> str:
    """Bold-Roman LaTeX rendering. Polychord stacks (``IV~iii``) split on
    tilde and bold each piece; slash-bass (``V/I``) bolds both sides."""
    if "~" in sym:
        return r"\textasciitilde{}".join(_split_slash(p) for p in sym.split("~"))
    return _split_slash(sym)


def build_tex(font_dir: Path) -> str:
    by_shape: dict[str, list[str]] = {}
    for _, items in SECTIONS_SINGLE:
        for stack, sym in items:
            by_shape.setdefault(single_shape(stack), []).append(sym)
    for lh, rh in SECTIONS_POLY:
        by_shape.setdefault(poly_shape(lh, rh), []).append(poly_symbol(lh, rh))

    def sort_key(sh: str) -> tuple[int, int, str]:
        if "~" in sh:
            return (1, int(sh.split("~")[1]), sh)
        return (0, len(sh), sh)

    shapes = sorted(by_shape.keys(), key=sort_key)

    font_path = str(font_dir).rstrip("/") + "/"

    # Body size tuned to fill a single A4 page. Anything above 13.8pt overflows
    # to a second page; BODY_PT env var lets you experiment.
    body_pt = float(__import__("os").environ.get("BODY_PT", "13.7"))
    body_lh = body_pt * 1.18
    lines: list[str] = [
        r"\documentclass[12pt]{article}",
        r"\usepackage[a4paper,top=0.4in,bottom=0.4in,left=0.4in,right=0.4in]{geometry}",
        r"\usepackage{fontspec}",
        r"\setmainfont{DejaVu Serif}",
        r"\AtBeginDocument{\fontsize{" + f"{body_pt}" + r"}{" + f"{body_lh:.2f}" + r"}\selectfont}",
        # JuliaMono for chord notation: combining circumflex + music glyphs.
        # Only Medium + SemiBold ship in the repo; FakeBold synthesizes a
        # heavier weight so shape signatures read as truly bold.
        r"\newfontfamily\juliamono[",
        r"  Path=" + font_path + ",",
        r"  Extension=.ttf,",
        r"  UprightFont=JuliaMono-Medium,",
        r"  BoldFont=JuliaMono-SemiBold,",
        r"  BoldFeatures={FakeBold=2.5},",
        r"  Scale=0.92,",
        r"]{JuliaMono-Medium}",
        r"\usepackage{multicol}",
        r"\setlength{\columnsep}{0.35in}",
        r"\setlength{\columnseprule}{0.2pt}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\parskip}{0.35em}",
        r"\renewcommand{\baselinestretch}{0.95}",
        r"\pagestyle{empty}",
        r"\begin{document}",
        r"{\centering",
        r"{\Large\bfseries Shape Drills} \\",
        r"{\small Practice list grouped by hand-shape \textemdash{} combined single-hand + polychord catalog \\",
        r"\textit{Notation:} {\juliamono 33} = up a 3rd, then up another 3rd; {\juliamono 33\textasciitilde{}3\textasciitilde{}33} = LH triad, up a 3rd, RH triad}",
        r"\par}",
        r"\vspace{0.5em}",
        r"\begin{multicols}{2}",
        r"\raggedright",
    ]

    block: str | None = None
    for sh in shapes:
        is_poly = "~" in sh
        new_block = "poly" if is_poly else "single"
        if new_block != block:
            block = new_block
            label = "Polychord shapes" if is_poly else "Single-hand shapes"
            lines.append(r"\noindent\textbf{\large " + label + r"}\par\vspace{0.15em}")

        desc = SHAPE_DESC.get(sh, "")
        roster = ", ".join(render_chord_latex(sym) for sym in by_shape[sh])
        sh_disp = latex_escape(sh)
        # Hanging indent: shape signature flush left, wrapped chord roster
        # indented underneath. No line break between description and roster.
        lines.append(
            r"\noindent\hangindent=2.2em\hangafter=1 "
            r"{\juliamono\bfseries " + sh_disp + r"}\enspace\textemdash\enspace "
            + latex_escape(desc) + r".\enspace "
            r"{\juliamono " + roster + r"}\par"
        )

    lines.append(r"\end{multicols}")
    lines.append(r"\end{document}")
    return "\n".join(lines)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    assets = repo_root / "tablet_app" / "app" / "src" / "main" / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    tex_path = assets / "shape-practice.tex"
    pdf_path = assets / "shape-practice.pdf"
    aux_path = assets / "shape-practice.aux"
    log_path = assets / "shape-practice.log"

    font_dir = repo_root / "viewer" / "font"
    if not (font_dir / "JuliaMono-Medium.ttf").exists():
        print(f"error: JuliaMono-Medium.ttf not found in {font_dir}")
        return 1

    tex_path.write_text(build_tex(font_dir), encoding="utf-8")

    if not shutil.which("xelatex"):
        print("error: xelatex not found in PATH", flush=True)
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

    # Clean intermediates; keep .tex for inspection.
    for stray in (aux_path, log_path):
        if stray.exists():
            stray.unlink()

    print(f"wrote {pdf_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
