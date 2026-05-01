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
        ((1, 3, 5), "1̂"), ((2, 4, 6), "2̂m"),
        ((3, 5, 7), "3̂m"), ((4, 6, 1), "4̂"),
        ((5, 7, 2), "5̂"), ((6, 1, 3), "6̂m"),
        ((7, 2, 4), "7̂°"),
    ]),
    ("Triads, 1st inv", [
        ((3, 5, 1), "1̂/3̂"), ((4, 6, 2), "2̂m/4̂"),
        ((5, 7, 3), "3̂m/5̂"), ((6, 1, 4), "4̂/6̂"),
        ((7, 2, 5), "5̂/7̂"), ((1, 3, 6), "6̂m/1̂"),
        ((2, 4, 7), "7̂°/2̂"),
    ]),
    ("Triads, 2nd inv", [
        ((5, 1, 3), "1̂/5̂"), ((6, 2, 4), "2̂m/6̂"),
        ((7, 3, 5), "3̂m/7̂"), ((1, 4, 6), "4̂/1̂"),
        ((2, 5, 7), "5̂/2̂"), ((3, 6, 1), "6̂m/3̂"),
        ((4, 7, 2), "7̂°/4̂"),
    ]),
    ("7ths root", [
        ((1, 3, 5, 7), "1̂Δ"), ((2, 4, 6, 1), "2̂m7"),
        ((3, 5, 7, 2), "3̂m7"), ((4, 6, 1, 3), "4̂Δ"),
        ((5, 7, 2, 4), "5̂7"), ((6, 1, 3, 5), "6̂m7"),
        ((7, 2, 4, 6), "7̂⌀"),
    ]),
    ("7ths 1st inv", [
        ((3, 5, 7, 1), "1̂Δ/3̂"),
        ((4, 6, 1, 2), "2̂m7/4̂"),
        ((6, 1, 3, 4), "4̂Δ/6̂"),
        ((7, 2, 4, 5), "5̂7/7̂"),
        ((1, 3, 5, 6), "6̂m7/1̂"),
    ]),
    ("7ths 2nd/3rd inv", [
        ((5, 7, 1, 3), "1̂Δ/5̂"),
        ((7, 1, 3, 5), "1̂Δ/7̂"),
        ((2, 4, 5, 7), "5̂7/2̂"),
        ((4, 5, 7, 2), "5̂7/4̂"),
        ((1, 2, 4, 6), "2̂m7/1̂"),
    ]),
    ("6 chords", [
        ((1, 3, 5, 6), "1̂6"), ((4, 6, 1, 2), "4̂6"),
        ((5, 7, 2, 3), "5̂6"),
    ]),
    ("m6", [
        ((2, 4, 6, 7), "2̂m6"),
    ]),
    ("sus2", [
        ((1, 2, 5), "1̂sus2"), ((2, 3, 6), "2̂sus2"),
        ((4, 5, 1), "4̂sus2"), ((5, 6, 2), "5̂sus2"),
        ((6, 7, 3), "6̂sus2"),
    ]),
    ("sus4", [
        ((1, 4, 5), "1̂sus"), ((2, 5, 6), "2̂sus"),
        ((3, 6, 7), "3̂sus"), ((5, 1, 2), "5̂sus"),
        ((6, 2, 3), "6̂sus"),
    ]),
    ("Power", [
        ((1, 5), "1̂5"), ((2, 6), "2̂5"), ((3, 7), "3̂5"),
        ((4, 1), "4̂5"), ((5, 2), "5̂5"), ((6, 3), "6̂5"),
    ]),
    ("add9", [
        ((1, 3, 5, 2), "1̂add9"), ((2, 4, 6, 3), "2̂madd9"),
        ((4, 6, 1, 5), "4̂add9"), ((5, 7, 2, 6), "5̂add9"),
        ((6, 1, 3, 7), "6̂madd9"),
    ]),
    ("add11", [
        ((1, 3, 5, 4), "1̂add11"), ((2, 4, 6, 5), "2̂madd11"),
        ((3, 5, 7, 6), "3̂madd11"), ((5, 7, 2, 1), "5̂add11"),
        ((6, 1, 3, 2), "6̂madd11"), ((7, 2, 4, 3), "7̂°add11"),
        ((4, 6, 1, 7), "4̂add♯11"),
    ]),
    ("6/9", [
        ((1, 3, 5, 6, 2), "1̂6/9"), ((4, 6, 1, 2, 5), "4̂6/9"),
        ((5, 7, 2, 3, 6), "5̂6/9"),
    ]),
    ("m6/9", [
        ((2, 4, 6, 7, 3), "2̂m6/9"),
    ]),
    ("9th", [
        ((1, 3, 5, 7, 2), "1̂Δ9"), ((2, 4, 6, 1, 3), "2̂m9"),
        ((3, 5, 7, 2, 4), "3̂m♭9"), ((4, 6, 1, 3, 5), "4̂Δ9"),
        ((5, 7, 2, 4, 6), "5̂9"), ((6, 1, 3, 5, 7), "6̂m9"),
        ((7, 2, 4, 6, 1), "7̂⌀♭9"),
    ]),
    ("11th", [
        ((2, 4, 6, 1, 3, 5), "2̂m11"), ((3, 5, 7, 2, 4, 6), "3̂m11"),
        ((4, 6, 1, 3, 5, 7), "4̂Δ♯11"),
        ((5, 7, 2, 4, 6, 1), "5̂11"), ((6, 1, 3, 5, 7, 2), "6̂m11"),
        ((7, 2, 4, 6, 1, 3), "7̂⌀11"),
    ]),
    ("13th", [
        ((1, 3, 5, 7, 2, 6), "1̂Δ13"),
        ((2, 4, 6, 1, 3, 5, 7), "2̂m13"),
        ((4, 6, 1, 3, 5, 7, 2), "4̂Δ13"),
        ((5, 7, 2, 4, 6, 3), "5̂13"),
        ((6, 1, 3, 5, 7, 2, 4), "6̂m♭13"),
    ]),
    ("7sus", [
        ((5, 1, 2, 4), "5̂7sus"), ((1, 4, 5, 7), "1̂Δsus"),
        ((2, 5, 6, 1), "2̂m7sus"), ((6, 2, 3, 5), "6̂m7sus"),
    ]),
    ("Pedal slash", [
        ((1, 4, 6, 1), "4̂/1̂"), ((5, 4, 6, 1), "4̂/5̂"),
        ((5, 1, 3, 5), "1̂/5̂"), ((1, 2, 4, 6), "2̂m/1̂"),
        ((5, 2, 4, 6), "2̂m/5̂"), ((1, 6, 1, 3), "6̂m/1̂"),
        ((1, 3, 5, 7), "3̂m/1̂"),
        ((1, 5, 7, 2, 4), "5̂7/1̂"),
    ]),
    ("Quartal 3", [
        ((1, 4, 7), "1̂q"), ((2, 5, 1), "2̂q"), ((3, 6, 2), "3̂q"),
        ((4, 7, 3), "4̂q"), ((5, 1, 4), "5̂q"), ((6, 2, 5), "6̂q"),
        ((7, 3, 6), "7̂q"),
    ]),
    ("Quartal 4", [
        ((1, 4, 7, 3), "1̂q4"), ((2, 5, 1, 4), "2̂q4"),
        ((3, 6, 2, 5), "3̂q4"), ((5, 1, 4, 7), "5̂q4"),
        ((6, 2, 5, 1), "6̂q4"),
    ]),
    ("Quartal 5", [
        ((2, 5, 1, 4, 7), "2̂q5"), ((3, 6, 2, 5, 1), "3̂q5"),
        ((5, 1, 4, 7, 3), "5̂q5"), ((6, 2, 5, 1, 4), "6̂q5"),
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


def poly_symbol(lh: int, rh: int) -> str:
    return f"{rh}̂~{lh}̂"


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
        roster = ", ".join(latex_escape(sym) for sym in by_shape[sh])
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
