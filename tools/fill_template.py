#!/usr/bin/env python3
"""
fill_template.py — render a reharm JSON into a LaTeX lead sheet.

Usage:
    python3 fill_template.py reharm.json > LeadSheet.tex

Reharm JSON structure:
    {
        "title": "Silent Night",
        "key": "B- major",
        "key_root": "B-",
        "mode": "major",
        "meter": "3/4",      # optional
        "bpm": 80,           # optional
        "words": "Joseph Mohr, 1818",
        "music": "Franz Gruber, 1818",
        "tune": "Stille Nacht",
        "lyrics": {"v1": ["phrase A lyrics", "phrase B lyrics", ...], "v2": [...]},
        "phrases": [
            {
                "label": "A",
                "bars": [1,2,3,4],
                "strategy": "melody rocks — tonic at rest",
                "cycle": "stacked",          # stacked / 4ths CW / 4ths CCW / 3rds CW / etc
                "cycle_color": "leafyellow",  # leafyellow / leafred / leafcyan / accent
            },
            ...
        ],
        "assignments": [
            {"bar":1, "rn":"I", "mel":"F4", "lh_rom":"I", "lh_qual":"",
             "lh_fig":"133", "rh_rom":"iii", "rh_qual":"i", "rh_fig":"743",
             "mood":"Soft", "source":"stacked_chords"},
            ...
        ]
    }
"""
import json
import re
import sys
import argparse

# ═════════════════════════════════════════════════════════════════════════════
#   Convert the mapper's LH/RH roman strings into the \rn{}{} macro format.
# The macro takes: \rn{root}{quality}. Splitting an entry like "V7" → ("V","7"),
# "iii¹" → ("iii","i"), "IV²+8" → ("IV","2+8") ... the macro's switch table
# handles quality codes: m, m7, m6, q, q7, s2, s4, s4+8, +8, D, o7, o, 7, 6,
# m7i, m7ii, m7iii, o7i, o7ii, 7i, 7ii, 7iii, oi, oii, and bare digits.
# ═════════════════════════════════════════════════════════════════════════════

# Superscript character to quality-code translations
SUP_TO_CODE = {
    '¹': 'i', '²': 'ii', '³': 'iii',
    'Δ': 'D', '°': 'o', 'ø': 'o',   # halfdim → o (template macro maps 'o7' → halfdim7)
    '⁷': '7',
}

def split_rn(rn):
    """Split '%V7' or 'iii¹' etc. into (numerals, quality_code) for \rn{}{}."""
    # Strip leading accidental (#, b)
    lead = ''
    if rn and rn[0] in '#b':
        lead = rn[0]
        rn = rn[1:]
    m = re.match(r'^([ivIV]+)(.*)$', rn)
    if not m:
        return rn, ''
    numerals, rest = m.groups()
    # Translate any unicode/super characters in `rest`
    code = ''
    # Handle half-dim (ø) specially: ø7 → o7
    rest = rest.replace('ø7', 'o7').replace('ø', 'o')
    for ch in rest:
        if ch in SUP_TO_CODE:
            code += SUP_TO_CODE[ch]
        elif ch in 'mbqs+D°':
            code += ch.replace('°', 'o')
        elif ch.isdigit():
            code += ch
        else:
            code += ch
    return lead + numerals, code

# ═════════════════════════════════════════════════════════════════════════════
#   Render a \fracA call
# ═════════════════════════════════════════════════════════════════════════════
def render_frac(assignment):
    lh_num, lh_q = split_rn(assignment['lh_rom'])
    rh_num, rh_q = split_rn(assignment['rh_rom'])
    return f"\\fracA{{{lh_num}}}{{{lh_q}}}{{{assignment['lh_fig']}}}"\
           f"{{{rh_num}}}{{{rh_q}}}{{{assignment['rh_fig']}}}"

# ═════════════════════════════════════════════════════════════════════════════
#   Edge-label macro picker by source
# ═════════════════════════════════════════════════════════════════════════════
def edge_label(assignment):
    mood = assignment.get('mood', '')
    if not mood:
        return ''
    if assignment.get('source') == 'stacked_chords':
        return f"\\edgeS{{SC:\\,{mood}}}"
    # For jazz_progressions, the mood is actually cw_label or ccw_label
    # We don't distinguish here without more metadata; use edgeY for 4ths etc
    # In practice the cycle should be tracked via the phrase context
    return f"\\edgeS{{{mood}}}"

# ═════════════════════════════════════════════════════════════════════════════
#   Melody pitch formatter for display
# ═════════════════════════════════════════════════════════════════════════════
def fmt_melody(p):
    """Convert music21-style pitch like 'B-4', 'F#5', 'D3' to LaTeX-safe form."""
    if not p:
        return '—'
    # music21 uses 'B-' for flat. Use LaTeX math mode for accidentals.
    result = p.replace('-', r'$\flat$').replace('#', r'$\sharp$')
    return result

# ═════════════════════════════════════════════════════════════════════════════
#   Render a phrase table (4-column, 3-column, etc. based on phrase length)
# ═════════════════════════════════════════════════════════════════════════════
def render_phrase_table(phrase, assignments_by_bar):
    nbars = len(phrase['bars'])
    # Column width — equal division of \linewidth minus a hair
    col_pct = 0.97 / nbars
    col_spec = '|'.join([f">{{\\centering\\arraybackslash}}p{{{col_pct:.4f}\\linewidth}}"
                          for _ in range(nbars)])
    col_spec = f"@{{}}|{col_spec}|@{{}}"

    lines = []
    # Bar-number row
    lines.append(' & '.join(f"\\barn{{bar {b}}}" for b in phrase['bars']) + ' \\\\')

    # Edge-label row
    edges = []
    for b in phrase['bars']:
        a = assignments_by_bar.get(b)
        edges.append(edge_label(a) if a else '')
    lines.append(' & '.join(edges) + ' \\\\')

    # Fraction row
    fracs = []
    for b in phrase['bars']:
        a = assignments_by_bar.get(b)
        fracs.append(render_frac(a) if a else '')
    lines.append(' & '.join(fracs) + ' \\\\')

    # Melody row
    mels = []
    for b in phrase['bars']:
        a = assignments_by_bar.get(b)
        mels.append(f"\\mel{{{fmt_melody(a.get('mel', '') if a else '')}}}")
    lines.append(' & '.join(mels) + ' \\\\')

    return f"""\\noindent\\begin{{tabular}}{{{col_spec}}}
\\hline
{chr(10).join(lines)}
\\hline
\\end{{tabular}}"""

# ═════════════════════════════════════════════════════════════════════════════
#   Full document assembly
# ═════════════════════════════════════════════════════════════════════════════
DOC_PREAMBLE = r"""\documentclass[letterpaper,10pt]{article}
\usepackage[T1]{fontenc}
\usepackage[letterpaper, margin=0.35in]{geometry}
\usepackage{array}
\usepackage[table]{xcolor}
\usepackage{microtype}
\usepackage{amssymb}
\usepackage{helvet}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{mathptmx}
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
\def\tmpYa{i}\def\tmpYb{ii}\def\tmpYc{iii}%
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
\ifx\tmp\tmpYa \inv{1}\else
\ifx\tmp\tmpYb \inv{2}\else
\ifx\tmp\tmpYc \inv{3}\else
#1%
\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi\fi
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

\newcommand{\edgeY}[1]{{\color{leafyellow!70!black}\fontsize{6}{7}\selectfont\itshape #1}}
\newcommand{\edgeR}[1]{{\color{leafred}\fontsize{6}{7}\selectfont\itshape #1}}
\newcommand{\edgeC}[1]{{\color{leafcyan!70!black}\fontsize{6}{7}\selectfont\itshape #1}}
\newcommand{\edgeS}[1]{{\color{accent}\fontsize{6}{7}\selectfont\itshape #1}}

\newcommand{\mel}[1]{{\color{ink}\fontsize{7.5}{8.5}\selectfont\ttfamily\bfseries #1}}
\newcommand{\barn}[1]{{\color{accent}\fontsize{6}{7}\selectfont\bfseries #1}}

\newcommand{\phrasebanner}[4]{%
\par\vspace{0.8mm}%
\noindent\colorbox{#1!18}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{%
\hspace{1mm}{\color{#1!60!black}\fontsize{8.5}{10}\selectfont\bfseries\scshape #2}%
\hspace{2.5mm}{\color{desccol}\fontsize{8.5}{10}\selectfont\itshape #3}%
\hfill%
\colorbox{#1!80!black}{\color{white}\hspace{1mm}\fontsize{6.5}{8}\selectfont\bfseries #4\hspace{1mm}}%
\hspace{1mm}%
}}%
\par\vspace{0.3mm}%
}

\newcommand{\lyricsrow}[2]{%
\vspace{-0.3mm}%
\noindent\colorbox{white!60!paper}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{%
\fontsize{9}{10.5}\selectfont\itshape\color{ink}%
\hspace{2mm}\makebox[7mm][l]{\color{accent}\ttfamily\upshape\bfseries v.1}%
#1\hfill%
\makebox[7mm][r]{\color{accent}\ttfamily\upshape\bfseries v.2}%
#2\hspace{2mm}%
}}%
}

\pagestyle{empty}
\pagecolor{paper}

\begin{document}
"""

DOC_POSTAMBLE = r"""

\vspace{1mm}
\noindent{\color{ink}\rule{\linewidth}{0.6pt}}\\[0.3mm]
\noindent\begin{minipage}[t]{0.32\linewidth}
{\fontsize{6.5}{8}\selectfont\ttfamily\color{accent}\bfseries READING THE FRACTIONS}\\[-0.3mm]
{\fontsize{7.5}{9}\selectfont
Each beat shows {\color{rhcol}\textbf{\textit{RH}}} over {\color{lhcol}\textbf{\textit{LH}}} --- one stacked sonority. Figure pair below (e.g.\ \texttt{133\,/\,8333}) is {\color{lhcol}LH string+intervals} over {\color{rhcol}RH string+intervals}.}
\end{minipage}\hfill
\begin{minipage}[t]{0.32\linewidth}
{\fontsize{6.5}{8}\selectfont\ttfamily\color{accent}\bfseries PROCESS}\\[-0.3mm]
{\fontsize{7.5}{9}\selectfont
Auto-generated via hymn\_parser.py + harp\_mapper.py. Every fraction validated against the 118-chord Harp Chord System vocabulary.}
\end{minipage}\hfill
\begin{minipage}[t]{0.32\linewidth}
{\fontsize{6.5}{8}\selectfont\ttfamily\color{accent}\bfseries COLOR LEGEND}\\[-0.3mm]
{\fontsize{7.5}{9}\selectfont
\textcolor{rhcol}{\textbf{RH blue}}, \textcolor{lhcol}{\textbf{LH red}}. \textcolor{leafyellow!80!black}{\textbf{4ths yellow}}, \textcolor{leafred}{\textbf{3rds red}}, \textcolor{leafcyan!80!black}{\textbf{2nds cyan}}.}
\end{minipage}

\end{document}
"""

def render_document(data):
    """Render the full LaTeX document from reharm data."""
    header = render_header(data)
    body_parts = []
    assignments_by_bar = {a['bar']: a for a in data['assignments']}
    # If no phrases are defined, treat everything as one big phrase
    if 'phrases' not in data or not data['phrases']:
        all_bars = sorted(assignments_by_bar.keys())
        data['phrases'] = [{
            'label': 'A',
            'bars': all_bars,
            'strategy': 'auto-generated reharmonization',
            'cycle': 'stacked',
            'cycle_color': 'leafyellow',
        }]

    for phrase in data['phrases']:
        banner = f"\\phrasebanner{{{phrase.get('cycle_color','leafyellow')}}}"\
                 f"{{Phrase {phrase['label']} $\\cdot$ bars {phrase['bars'][0]}--{phrase['bars'][-1]}}}"\
                 f"{{{phrase.get('strategy','')}}}"\
                 f"{{{phrase.get('cycle','stacked')}}}"
        table = render_phrase_table(phrase, assignments_by_bar)
        lyrics = phrase.get('lyrics', {'v1':'', 'v2':''})
        lyrics_line = f"\\lyricsrow{{{lyrics.get('v1','')}}}{{{lyrics.get('v2','')}}}"
        body_parts.append(banner + "\n\n" + table + "\n\n" + lyrics_line)

    body = "\n\n".join(body_parts)
    return DOC_PREAMBLE + "\n" + header + "\n\n" + body + DOC_POSTAMBLE

def render_header(data):
    """Render the three-column document header."""
    title = data.get('title', 'Untitled Hymn')
    words = data.get('words', '—')
    music = data.get('music', '—')
    tune = data.get('tune', '—')
    key_str = data.get('key', '—')
    meter = data.get('meter', '—')
    bpm = data.get('bpm', 80)
    n_bars = max(a['bar'] for a in data['assignments']) if data['assignments'] else 0
    n_phrases = len(data.get('phrases', []))

    return fr"""\noindent
\begin{{minipage}}[b]{{0.28\linewidth}}
\fontsize{{7}}{{9}}\selectfont\ttfamily\color{{desccol}}
\textbf{{Words:}} {words}\\
\textbf{{Music:}} {music}\\
\textbf{{Tune:}} {tune} --- Key of {key_str}\\
\textbf{{Meter:}} {meter} \quad \raisebox{{0.2ex}}{{$\bullet$}} \quad $q$={bpm}
\end{{minipage}}\hfill
\begin{{minipage}}[b]{{0.44\linewidth}}
\centering
{{\color{{accent}}\fontsize{{7}}{{8.5}}\selectfont\ttfamily HARP CHORD SYSTEM $\cdot$ AUTO REHARM}}\\[0.2mm]
{{\fontsize{{22}}{{24}}\selectfont\itshape\rmfamily\bfseries {title}}}\\[0mm]
{{\color{{desccol}}\fontsize{{8.5}}{{10}}\selectfont\itshape stacked LH/RH fractions along cycle edges}}
\end{{minipage}}\hfill
\begin{{minipage}}[b]{{0.26\linewidth}}
\raggedleft
\fontsize{{7}}{{9}}\selectfont\ttfamily\color{{desccol}}
\textbf{{Reharm Sheet}}\\
{n_bars} bars \raisebox{{0.2ex}}{{$\bullet$}} {n_phrases} phrase{'s' if n_phrases != 1 else ''}\\
Strictly within the 118-chord vocabulary\\
Auto-generated
\end{{minipage}}

\vspace{{0.3mm}}
\noindent{{\color{{ink}}\rule{{\linewidth}}{{0.8pt}}}}"""

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('reharm_json')
    ap.add_argument('-o', '--output', default=None,
                    help='Output .tex file (default stdout)')
    args = ap.parse_args()
    with open(args.reharm_json) as f:
        data = json.load(f)
    doc = render_document(data)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(doc)
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(doc)
