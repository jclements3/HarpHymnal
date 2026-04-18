#!/usr/bin/env python3
"""
build_piano_book.py — reharm-sheet style PDF with per-bar chord fractions
(using HymnReharmTemplate.tex macros) + per-bar LilyPond piano snippets
below each fraction.

Pipeline:
  <export>.json + <reharm>.json
    → per-bar LilyPond files  (bars/bar01.ly, bar02.ly, ...)
    → main .lytex             (uses \\fracA + \\lilypondfile per cell)
    → lilypond-book  → .tex
    → pdflatex       → .pdf

Usage:
  python3 tools/build_piano_book.py --title "Silent_Night"
      -o hymnal_html/book/silent_night_book.lytex
  # runs lilypond-book and pdflatex automatically unless --no-compile
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_piano_score import (  # noqa: E402
    music21_key_to_ly, key_pc_to_ly_spelling,
    events_to_lilypond_bar,
    bar_melody_notes, bar_assignment, layout_bar_grand,
)


# ─────────────────────────────────────────────────────────────────────────────
# Per-bar LilyPond snippet
# ─────────────────────────────────────────────────────────────────────────────
_BAR_LY_TEMPLATE = r"""\version "2.22.1"
\header { tagline = ##f }
\paper {
  indent = 0\mm
  line-width = 42\mm
  ragged-right = ##f
  oddHeaderMarkup = ""
  evenHeaderMarkup = ""
  oddFooterMarkup = ""
  evenFooterMarkup = ""
  page-breaking = #ly:one-line-breaking
  system-system-spacing.basic-distance = #0
}

\score {
  \new PianoStaff \with { \remove "Bar_number_engraver" } <<
    \new Staff \with {
      \remove "Time_signature_engraver"
      instrumentName = ""
    } <<
      \new Voice { \voiceOne \clef treble \key __KEYSIG__ __MELODY__ }
      \new Voice { \voiceTwo \key __KEYSIG__ __RHFILL__ }
    >>
    \new Staff \with {
      \remove "Time_signature_engraver"
    } { \clef bass \key __KEYSIG__ __LH__ }
  >>
  \layout {
    \context { \Score \remove "Bar_number_engraver" }
  }
}
"""


def emit_bar_ly(bar_data, key_root, mode, meter_num, meter_den):
    keysig = music21_key_to_ly(key_root, mode)
    pc_spelling = key_pc_to_ly_spelling(key_root, mode)
    full_bar_ql = meter_num * (4.0 / meter_den)
    mel = events_to_lilypond_bar(bar_data.get('melody_events', []),
                                 full_bar_ql, pc_spelling)
    rhf = events_to_lilypond_bar(bar_data.get('rh_events', []),
                                 full_bar_ql, pc_spelling, arpeggiate=True)
    lh = events_to_lilypond_bar(bar_data.get('lh_events', []),
                                 full_bar_ql, pc_spelling, arpeggiate=True)
    return (_BAR_LY_TEMPLATE
            .replace('__KEYSIG__', keysig)
            .replace('__MELODY__', mel)
            .replace('__RHFILL__', rhf)
            .replace('__LH__', lh))


# ─────────────────────────────────────────────────────────────────────────────
# \fracA call generation — matches HymnReharmTemplate.tex macro signature
# ─────────────────────────────────────────────────────────────────────────────
_SUP_TO_CODE = {'¹': 'i', '²': 'ii', '³': 'iii', 'Δ': 'D',
                '°': 'o', 'ø': 'o', '⁷': '7'}


def split_rn(rn_str):
    """'V7' → ('V','7'); 'iii¹' → ('iii','i'); 'IΔii' → ('I','Dii')."""
    if not rn_str:
        return ('I', '')
    rn = rn_str.lstrip('b#\u266d\u266f')
    m = re.match(r'^([ivIV]+)(.*)$', rn)
    if not m:
        return (rn_str, '')
    roman, tail = m.group(1), m.group(2)
    qual = ''.join(_SUP_TO_CODE.get(c, c) for c in tail)
    return (roman, qual)


def fracA_call(assignment):
    """Build '\\fracA{lh_rom}{lh_qual}{lh_fig}{rh_rom}{rh_qual}{rh_fig}'."""
    lh_rom = assignment.get('lh_rom') or assignment.get('rn') or 'I'
    rh_rom = assignment.get('rh_rom') or assignment.get('rn') or 'I'
    lh_qual_raw = assignment.get('lh_qual') or ''
    rh_qual_raw = assignment.get('rh_qual') or ''
    # lh_rom might already contain inversion markers; split to extract
    lh_rom_s, lh_qual_split = split_rn(lh_rom)
    rh_rom_s, rh_qual_split = split_rn(rh_rom)
    # Prefer explicit qual over split-derived
    lh_qual = lh_qual_raw or lh_qual_split
    rh_qual = rh_qual_raw or rh_qual_split
    lh_fig = assignment.get('lh_fig', '')
    rh_fig = assignment.get('rh_fig', '')
    return (f'\\fracA{{{lh_rom_s}}}{{{lh_qual}}}{{{lh_fig}}}'
            f'{{{rh_rom_s}}}{{{rh_qual}}}{{{rh_fig}}}')


# ─────────────────────────────────────────────────────────────────────────────
# Main .lytex assembly
# ─────────────────────────────────────────────────────────────────────────────
# Minimal preamble: just the macros + colors needed for \fracA.
# Copied from HymnReharmTemplate.tex preamble (verbatim).
_LYTEX_PREAMBLE = r"""\documentclass[letterpaper,10pt]{article}
\usepackage[T1]{fontenc}
\usepackage[letterpaper, margin=0.45in]{geometry}
\usepackage{array}
\usepackage[table]{xcolor}
\usepackage{graphicx}
\usepackage{mathptmx}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

\definecolor{rhcol}{HTML}{1F4E79}
\definecolor{lhcol}{HTML}{7B2B2B}
\definecolor{desccol}{HTML}{2A3342}
\definecolor{flavcol}{HTML}{6B7A8F}
\definecolor{bandcol}{HTML}{F0F4F8}
\definecolor{leafred}{RGB}{220,75,75}
\definecolor{leafyellow}{RGB}{190,155,30}
\definecolor{leafcyan}{RGB}{40,180,190}
\definecolor{paper}{HTML}{F4ECD8}
\definecolor{ink}{HTML}{1A1612}
\definecolor{accent}{HTML}{8B6F47}

\newcommand{\osf}[1]{{\fontfamily{pplj}\selectfont #1}}
\newcommand{\Ro}[1]{{\fontfamily{ppl}\fontseries{b}\selectfont #1}}
\newcommand{\rp}{{\raisebox{0.55ex}{\footnotesize$+$}}}
\newcommand{\halfdim}{$^{\scriptstyle\varnothing}$}
\newcommand{\inv}[1]{$^{\osf{#1}}$}
\newcommand{\nd}{\rule[0.42ex]{4.5mm}{0.55pt}}

\newcommand{\rn}[2]{\Ro{#1}\rndq{#2}}
\newcommand{\rndq}[1]{\rndqparse{#1}}
\newcommand{\rndqparse}[1]{%
\def\tmp{#1}%
\def\tmpA{m7}\def\tmpB{m6}\def\tmpC{m}%
\def\tmpD{q7}\def\tmpE{q}%
\def\tmpF{s4+8}\def\tmpG{s4}\def\tmpH{s2}%
\def\tmpI{+8}%
\def\tmpJ{D}\def\tmpK{o7}\def\tmpL{o}%
\def\tmpM{7}\def\tmpN{6}%
\def\tmpO{m7i}\def\tmpP{m7ii}\def\tmpQ{m7iii}%
\def\tmpR{o7i}\def\tmpS{o7ii}%
\def\tmpT{7i}\def\tmpU{7ii}\def\tmpV{7iii}%
\def\tmpW{oi}\def\tmpX{oii}%
\ifx\tmp\tmpA $m$\osf{7}\else
\ifx\tmp\tmpB $m$\osf{6}\else
\ifx\tmp\tmpC $m$\else
\ifx\tmp\tmpD $q$\osf{7}\else
\ifx\tmp\tmpE $q$\else
\ifx\tmp\tmpF $s$\osf{4}\rp\osf{8}\else
\ifx\tmp\tmpG $s$\osf{4}\else
\ifx\tmp\tmpH $s$\osf{2}\else
\ifx\tmp\tmpI \rp\osf{8}\else
\ifx\tmp\tmpJ $\Delta$\else
\ifx\tmp\tmpK \halfdim\osf{7}\else
\ifx\tmp\tmpL $^\circ$\else
\ifx\tmp\tmpM \osf{7}\else
\ifx\tmp\tmpN \osf{6}\else
\ifx\tmp\tmpO $m$\osf{7}\inv{1}\else
\ifx\tmp\tmpP $m$\osf{7}\inv{2}\else
\ifx\tmp\tmpQ $m$\osf{7}\inv{3}\else
\ifx\tmp\tmpR \halfdim\osf{7}\inv{1}\else
\ifx\tmp\tmpS \halfdim\osf{7}\inv{2}\else
\ifx\tmp\tmpT \osf{7}\inv{1}\else
\ifx\tmp\tmpU \osf{7}\inv{2}\else
\ifx\tmp\tmpV \osf{7}\inv{3}\else
\ifx\tmp\tmpW $^\circ$\inv{1}\else
\ifx\tmp\tmpX $^\circ$\inv{2}\else
#1%
\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi
}

\newcommand{\fracA}[6]{%
\renewcommand{\arraystretch}{0.7}%
\begin{tabular}{@{}c@{}}
{\color{rhcol}\fontsize{9.5}{10}\selectfont\rn{#4}{#5}}\\[-0.5ex]
{\color{ink}\rule{9mm}{0.4pt}}\\[-0.5ex]
{\color{lhcol}\fontsize{9.5}{10}\selectfont\rn{#1}{#2}}\\[-0.2ex]
{\color{flavcol}\fontsize{5.5}{6.5}\selectfont\ttfamily #3\,/\,#6}
\end{tabular}%
}

\newcommand{\barn}[1]{{\color{accent}\fontsize{6}{7}\selectfont\bfseries #1}}

\pagestyle{empty}
\pagecolor{paper}
"""


def build_lytex(title, key_str, meter_str, bpm, bar_cells, bars_per_row=4):
    """bar_cells = [(bar_num, fracA_call_str, bar_ly_relpath), ...]"""
    col_spec = '|' + 'c|' * bars_per_row
    col_width = f'{0.96 / bars_per_row:.3f}'

    rows_html = []
    for i in range(0, len(bar_cells), bars_per_row):
        chunk = bar_cells[i:i + bars_per_row]
        # Pad short last row with empty cells
        while len(chunk) < bars_per_row:
            chunk.append(None)
        # Row 1: bar number
        row1 = ' & '.join(f'\\barn{{bar {c[0]}}}' if c else '' for c in chunk) + r' \\'
        # Row 2: chord fraction
        row2 = ' & '.join(c[1] if c else '' for c in chunk) + r' \\'
        # Row 3: music — each \lilypondfile on its own line so lilypond-book
        # processes each one (it only substitutes the first per input line).
        row3_cells = [
            (f'\\lilypondfile[noindent]{{{c[2]}}}' if c else '')
            for c in chunk
        ]
        row3 = ' &\n'.join(row3_cells) + r' \\'
        rows_html.append('\\hline\n' + row1 + '\n' + row2 + '\n' + row3)
    grid = '\n\\hline\n'.join(rows_html) + '\n\\hline'

    body = rf"""
\begin{{document}}

\noindent
\begin{{minipage}}[b]{{0.5\linewidth}}
\fontsize{{7}}{{9}}\selectfont\ttfamily\color{{desccol}}
\textbf{{Tune:}} {title}\\
\textbf{{Meter:}} {meter_str} \quad\raisebox{{0.2ex}}{{$\bullet$}}\quad
\textbf{{Key:}} {key_str} \quad\raisebox{{0.2ex}}{{$\bullet$}}\quad
$q$={bpm}
\end{{minipage}}\hfill
\begin{{minipage}}[b]{{0.48\linewidth}}
\raggedleft
{{\fontsize{{18}}{{22}}\selectfont\itshape\rmfamily\bfseries {title}}}
\end{{minipage}}

\vspace{{1mm}}
\noindent{{\color{{ink}}\rule{{\linewidth}}{{0.6pt}}}}
\vspace{{2mm}}

\setlength{{\tabcolsep}}{{2pt}}
\renewcommand{{\arraystretch}}{{0.95}}
\noindent\begin{{tabular}}{{@{{}}{col_spec}@{{}}}}
{grid}
\end{{tabular}}

\end{{document}}
"""
    return _LYTEX_PREAMBLE + body


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────
def resolve_title(title):
    slug = re.sub(r'[^A-Za-z0-9]+', '_', title).strip('_')
    export = glob.glob(f'hymnal_export/*{slug}*.json')
    reharm = glob.glob(f'hymnal_html/reharms/*{slug}*.json')
    return (export[0] if export else None, reharm[0] if reharm else None)


def run(cmd, cwd=None):
    print('$ ' + ' '.join(cmd), file=sys.stderr)
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-2000:], file=sys.stderr)
        print(result.stdout[-1000:], file=sys.stderr)
    return result.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('export_json', nargs='?')
    ap.add_argument('reharm_json', nargs='?')
    ap.add_argument('-o', '--output', required=True,
                     help='Output .lytex path (output dir will hold bars/ subfolder)')
    ap.add_argument('--title', help='Resolve JSON paths by title substring')
    ap.add_argument('--no-compile', action='store_true')
    ap.add_argument('--bars-per-row', type=int, default=4)
    args = ap.parse_args()

    if args.title:
        args.export_json, args.reharm_json = resolve_title(args.title)
        if not args.export_json or not args.reharm_json:
            print(f'Could not resolve {args.title!r}', file=sys.stderr)
            sys.exit(2)

    if not args.export_json or not args.reharm_json:
        ap.error('Need both JSONs or --title')

    with open(args.export_json) as f:
        export = json.load(f)
    with open(args.reharm_json) as f:
        reharm = json.load(f)

    title = export.get('title', 'Untitled')
    music = export.get('music', {})
    key_root = music.get('key_root', 'C')
    mode = music.get('mode', 'major')
    meter = music.get('meter', '4/4')
    meter_num, meter_den = map(int, meter.split('/'))
    bpm = music.get('bpm') or 80
    total_bars = music.get('total_bars', 0)
    s1v1 = export.get('voices', {}).get('S1V1', [])
    assignments = reharm.get('assignments', [])
    key_display = (export.get('music', {}).get('modal_name')
                    or f"{key_root} {mode}").replace('-', '♭')

    out_dir = os.path.dirname(os.path.abspath(args.output)) or '.'
    bars_dir = os.path.join(out_dir, 'bars')
    os.makedirs(bars_dir, exist_ok=True)

    # 1. Emit per-bar .ly files + collect \fracA calls
    bar_cells = []
    for bar_num in range(1, total_bars + 1):
        melody_notes = bar_melody_notes(s1v1, bar_num)
        assignment = bar_assignment(assignments, bar_num)
        if assignment is None:
            # No chord data — just melody with empty voices
            bar_data = {
                'melody_events': [{'offset_ql': n['offset_ql'] % (meter_num * 4.0 / meter_den),
                                     'duration_ql': n['duration_ql'],
                                     'midis': [n['midi']]} for n in melody_notes],
                'rh_events': [],
                'lh_events': [],
            }
            frac = r'\textit{\small (no chord)}'
        else:
            bar_data = layout_bar_grand(assignment, melody_notes,
                                         key_root, mode, meter_num, meter_den)
            frac = fracA_call(assignment)

        ly = emit_bar_ly(bar_data, key_root, mode, meter_num, meter_den)
        bar_ly_name = f'bars/bar{bar_num:02d}.ly'
        bar_ly_path = os.path.join(out_dir, bar_ly_name)
        with open(bar_ly_path, 'w') as f:
            f.write(ly)
        bar_cells.append((bar_num, frac, bar_ly_name))

    # 2. Assemble the main .lytex
    lytex = build_lytex(title, key_display, meter, int(bpm), bar_cells,
                         bars_per_row=args.bars_per_row)
    with open(args.output, 'w') as f:
        f.write(lytex)
    print(f'Wrote {args.output} ({len(bar_cells)} bars, {len(lytex)} chars)', file=sys.stderr)

    if args.no_compile:
        return

    if not shutil.which('lilypond-book') or not shutil.which('pdflatex'):
        print('lilypond-book or pdflatex not in PATH — skipping compile', file=sys.stderr)
        return

    # 3. lilypond-book → .tex, then pdflatex → .pdf
    build_dir = os.path.join(out_dir, 'build')
    os.makedirs(build_dir, exist_ok=True)
    ly_name = os.path.basename(args.output)
    rc = run(['lilypond-book', '--output=build', ly_name], cwd=out_dir)
    if rc != 0:
        sys.exit(rc)
    tex_name = os.path.splitext(ly_name)[0] + '.tex'
    rc = run(['pdflatex', '-interaction=nonstopmode', tex_name], cwd=build_dir)
    if rc != 0:
        sys.exit(rc)

    pdf_name = os.path.splitext(ly_name)[0] + '.pdf'
    final_pdf = os.path.join(out_dir, pdf_name)
    shutil.copy(os.path.join(build_dir, pdf_name), final_pdf)
    print(f'→ {final_pdf}', file=sys.stderr)


if __name__ == '__main__':
    main()
