#!/usr/bin/env python3
"""
build_chord_system_html.py — render HarpChordSystem.json as a single static
HTML reference page, to be cross-linked from hymnal_html/review.html.

Usage:
    python3 tools/build_chord_system_html.py \
        HarpChordSystem.json -o hymnal_html/chord_system.html
"""
import argparse
import html
import json
import os
import re


# Map quality suffix strings to small HTML fragments (mirrors
# fill_template.py::rndqparse and build_review_html.py::_render_qual)
def render_rn_inline(roman):
    """Render a bare roman-numeral-with-quality string as display HTML.

    Input format: e.g. 'ii', 'Iø7', 'V7', 'vi°', 'IΔ¹', 'iim7', 'Vs4+8'.
    """
    if not roman:
        return ''
    s = roman
    # Strip leading accidental
    accid = ''
    if s[0] in '#b':
        accid = '&#9839;' if s[0] == '#' else '&#9837;'
        s = s[1:]
    m = re.match(r'^([ivIV]+)(.*)$', s)
    if not m:
        return html.escape(roman)
    numerals, rest = m.groups()
    # Map the rest to superscripts/characters
    rest_html = ''
    # Map unicode-bearing rest
    # Quality handling
    tail = rest
    # Only ø (halfdim), ° (dim), and ¹²³ (inversions) are superscript.
    # Δ, digits, quality letters (m/q/s), +8 are all baseline.
    tail = (tail.replace('Δ', '&#916;')
                .replace('ø7', '<sup>&#248;</sup>7')
                .replace('ø', '<sup>&#248;</sup>')
                .replace('°', '<sup>&#176;</sup>'))
    # Inversion superscripts (¹²³)
    tail = (tail.replace('¹', '<sup class="inv">1</sup>')
                .replace('²', '<sup class="inv">2</sup>')
                .replace('³', '<sup class="inv">3</sup>'))
    # Quality letter groups: italic letter + baseline digit
    tail = re.sub(r'm7', '<i>m</i>7', tail)
    tail = re.sub(r'm6', '<i>m</i>6', tail)
    tail = re.sub(r'(?<![a-zA-Z])m(?![a-zA-Z0-9])', '<i>m</i>', tail)
    tail = re.sub(r'q7', '<i>q</i>7', tail)
    tail = re.sub(r'(?<![a-zA-Z])q(?![a-zA-Z0-9])', '<i>q</i>', tail)
    tail = re.sub(r's4\+8', '<i>s</i>4+8', tail)
    tail = re.sub(r's4', '<i>s</i>4', tail)
    tail = re.sub(r's2', '<i>s</i>2', tail)
    # +8 and bare 6/7 digits stay inline (baseline) — no super-tag
    return f'{accid}<span class="num">{html.escape(numerals)}</span>{tail}'


CSS = """
:root {
  --rhcol: #1F4E79;
  --lhcol: #7B2B2B;
  --paper: #F4ECD8;
  --ink: #1A1612;
  --accent: #8B6F47;
  --flavcol: #6B7A8F;
  --leafred: rgb(220,75,75);
  --leafyellow: rgb(190,155,30);
  --leafcyan: rgb(40,180,190);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #2b2722;
  font-family: -apple-system, "Segoe UI", Roboto, sans-serif; }
body { display: flex; min-height: 100vh; color: var(--ink); }

nav#sidebar {
  width: 220px; flex-shrink: 0;
  background: #1f1c19; color: #d8ccb0;
  position: sticky; top: 0; align-self: flex-start;
  height: 100vh; overflow-y: auto; padding: 14px 10px;
  border-right: 1px solid #000; font-size: 12px;
}
nav#sidebar h1 { font-size: 14px; margin: 0 0 10px 2px; color: #e8d8b4;
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
nav#sidebar .back { display: block; margin-bottom: 12px; padding: 4px 8px;
  color: #c8bc9c; text-decoration: none; border-radius: 3px;
  background: #2d2924; }
nav#sidebar .back:hover { background: #3a3429; color: #fff; }
nav#sidebar ol { list-style: none; margin: 0; padding: 0; }
nav#sidebar li { margin: 1px 0; }
nav#sidebar a { display: block; padding: 4px 8px; color: #c8bc9c;
  text-decoration: none; border-radius: 3px; }
nav#sidebar a:hover { background: #2d2924; color: #f0e4c4; }

main { flex: 1; padding: 24px; overflow-x: auto; }
.sheet { background: var(--paper); max-width: 1100px; margin: 0 auto 24px auto;
  padding: 20px 26px; border-radius: 4px; box-shadow: 0 3px 16px rgba(0,0,0,0.4); }
.sheet h2 { font-family: "Palatino", "Book Antiqua", Georgia, serif;
  font-style: italic; font-weight: 700; font-size: 22px; margin: 18px 0 6px 0;
  color: var(--ink); border-bottom: 1px solid var(--ink); padding-bottom: 3px; }
.sheet h2:first-child { margin-top: 0; }
.sheet h3 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.7px;
  color: var(--accent); margin: 14px 0 6px 0; }
.sheet p, .sheet li { font-size: 13px; line-height: 1.45; margin: 4px 0;
  color: var(--ink); }

.subtitle { color: var(--flavcol); font-style: italic; font-size: 13px;
  margin-top: -4px; margin-bottom: 6px; }

.kv { display: grid; grid-template-columns: 140px 1fr; gap: 3px 12px;
  font-size: 12px; margin: 6px 0; }
.kv dt { color: var(--accent); font-family: ui-monospace, monospace; }
.kv dd { margin: 0; }

table.data { border-collapse: collapse; width: 100%; font-size: 12px;
  margin: 6px 0 12px 0; }
table.data th, table.data td { padding: 3px 6px; text-align: left;
  border-bottom: 1px solid #d9cead; vertical-align: top; }
table.data th { color: var(--accent); font-weight: 700; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.5px;
  border-bottom: 1px solid var(--ink); }
table.data td.fig, table.data td.num { font-family: ui-monospace, monospace; }
table.data td.rn { font-family: "Palatino","Palatino Linotype","Book Antiqua",Georgia,serif;
  font-weight: 700; font-style: normal;
  font-feature-settings: "onum" 1; }
table.data td.rh { color: var(--rhcol); }
table.data td.lh { color: var(--lhcol); }
table.data td.rn .num { font-style: normal; }
table.data td.rn i { font-style: italic; font-weight: 700; }
table.data td.rn sup { font-feature-settings: "onum" 1; }

.cycle { border-left: 4px solid var(--cyc-color); padding-left: 10px;
  margin: 8px 0 16px 0; }
.cycle.twos   { --cyc-color: var(--leafcyan); }
.cycle.thirds { --cyc-color: var(--leafred); }
.cycle.fourths{ --cyc-color: var(--leafyellow); }
.cycle .traversal { font-family: "Palatino","Palatino Linotype",Georgia,serif;
  font-size: 12px; color: var(--flavcol); margin: 4px 0;
  font-feature-settings: "onum" 1; }

sup.inv { font-size: 65%; vertical-align: super; line-height: 0; }
"""


def escape_text(s):
    return html.escape(s or '')


def render_conventions(conv):
    out = ['<h2>Conventions</h2>']
    # Roman-numeral case
    rc = conv.get('roman_numeral_case', {})
    out.append('<h3>Roman-numeral case</h3>')
    out.append('<dl class="kv">')
    out.append(f'<dt>uppercase</dt><dd>{escape_text(rc.get("uppercase",""))}</dd>')
    out.append(f'<dt>lowercase</dt><dd>{escape_text(rc.get("lowercase",""))}</dd>')
    out.append('</dl>')
    note = rc.get('note', '')
    if note:
        out.append(f'<p class="subtitle">{escape_text(note)}</p>')
    # Quality suffixes
    qs = conv.get('quality_suffixes', {})
    out.append('<h3>Quality suffixes</h3>')
    out.append('<table class="data"><tr><th>Suffix</th><th>Meaning</th></tr>')
    for suf, meaning in qs.items():
        disp = suf if suf else '<i>(none)</i>'
        out.append(f'<tr><td class="num">{escape_text(disp) if suf else "<i>(none)</i>"}</td>'
                   f'<td>{escape_text(meaning)}</td></tr>')
    out.append('</table>')
    # Inversion superscripts
    inv = conv.get('inversion_superscripts', {})
    out.append('<h3>Inversion superscripts</h3>')
    out.append('<dl class="kv">')
    for k, v in inv.items():
        out.append(f'<dt>{escape_text(k)}</dt><dd>{escape_text(v)}</dd>')
    out.append('</dl>')
    # Interval alphabet
    ia = conv.get('interval_alphabet_from_tonic', {})
    out.append('<h3>Interval-from-tonic alphabet</h3>')
    out.append('<dl class="kv" style="grid-template-columns: repeat(4, auto 1fr); gap: 2px 10px;">')
    for k, v in ia.items():
        out.append(f'<dt>{escape_text(k)}</dt><dd>{escape_text(v)}</dd>')
    out.append('</dl>')
    # Figure parsing
    fp = conv.get('figure_parsing', {})
    out.append('<h3>Figure parsing</h3>')
    out.append(f'<p>{escape_text(fp.get("definition",""))}</p>')
    out.append(f'<p class="subtitle">{escape_text(fp.get("span_formula",""))}</p>')
    ex = fp.get('examples', [])
    if ex:
        out.append('<table class="data"><tr><th>Figure</th><th>Parse</th>'
                   '<th>Span</th><th>Fingers</th><th>In key of C</th></tr>')
        for e in ex:
            out.append(
                f'<tr><td class="fig">{escape_text(e.get("figure",""))}</td>'
                f'<td>{escape_text(e.get("parse",""))}</td>'
                f'<td class="num">{e.get("span","")}</td>'
                f'<td class="num">{e.get("fingers","")}</td>'
                f'<td class="rn">{render_rn_inline(e.get("chord_in_C",""))}</td></tr>')
        out.append('</table>')
    # LH/RH pair notation
    pn = conv.get('lh_rh_figure_pair_notation', {})
    out.append('<h3>LH / RH figure-pair notation</h3>')
    out.append(f'<p>{escape_text(pn.get("definition",""))}</p>')
    ex = pn.get('examples', [])
    if ex:
        out.append('<table class="data"><tr><th>Pair</th><th>Meaning</th></tr>')
        for e in ex:
            out.append(f'<tr><td class="fig">{escape_text(e.get("pair",""))}</td>'
                       f'<td>{escape_text(e.get("meaning",""))}</td></tr>')
        out.append('</table>')
    nd = conv.get('nd_marker', '')
    if nd:
        out.append(f'<p><b>Non-diatonic marker (—):</b> {escape_text(nd)}</p>')
    return '\n'.join(out)


def render_patterns(patterns):
    out = ['<h2>Finger patterns (14)</h2>',
           '<p>Each pattern is an interval sequence walked from a starting '
           'scale degree. <code>fingers</code> = notes per chord; '
           '<code>span</code> = total strings spanned.</p>',
           '<table class="data"><tr><th>ID</th><th>Intervals</th>'
           '<th>Fingers</th><th>Span</th></tr>']
    for p in patterns:
        intervals = ' · '.join(str(i) for i in p.get('intervals', []))
        out.append(
            f'<tr><td class="fig">{escape_text(p.get("id",""))}</td>'
            f'<td class="num">{intervals}</td>'
            f'<td class="num">{p.get("fingers","")}</td>'
            f'<td class="num">{p.get("span","")}</td></tr>')
    out.append('</table>')
    return '\n'.join(out)


def render_cycles(cycles):
    out = ['<h2>Diatonic cycles (3)</h2>',
           '<p>Each cycle is a closed loop of 7 diatonic chords starting and '
           'ending at <span class="rn"><i>I</i></span>. CW and CCW are the '
           'two directions of traversal; every edge has a CW mood label and a '
           'CCW mood label.</p>']
    cycle_class = {'2nds': 'twos', '3rds': 'thirds', '4ths': 'fourths'}
    for name, cyc in cycles.items():
        klass = cycle_class.get(name, '')
        step = cyc.get('step_interval', '')
        trav_cw = ' → '.join(cyc.get('traversal_cw', []))
        trav_ccw = ' → '.join(cyc.get('traversal_ccw', []))
        out.append(f'<div class="cycle {klass}">')
        out.append(f'<h3>{escape_text(name)} cycle  <span style="color:var(--flavcol);font-weight:400;">(step interval {step}, color {escape_text(cyc.get("color",""))})</span></h3>')
        out.append(f'<div class="traversal"><b>CW:</b>&nbsp; {" → ".join(render_rn_inline(r) for r in cyc.get("traversal_cw",[]))}</div>')
        out.append(f'<div class="traversal"><b>CCW:</b> {" → ".join(render_rn_inline(r) for r in cyc.get("traversal_ccw",[]))}</div>')
        out.append('<table class="data"><tr><th>From</th><th>To</th>'
                   '<th>CW label</th><th>CCW label</th></tr>')
        for e in cyc.get('edges', []):
            out.append(
                f'<tr><td class="rn">{render_rn_inline(e.get("from",""))}</td>'
                f'<td class="rn">{render_rn_inline(e.get("to",""))}</td>'
                f'<td>{escape_text(e.get("cw_label",""))}</td>'
                f'<td>{escape_text(e.get("ccw_label",""))}</td></tr>')
        out.append('</table></div>')
    return '\n'.join(out)


def render_jazz(entries):
    out = [f'<h2>Jazz progressions ({len(entries)})</h2>',
           '<p>Paired LH / RH voicings along the three diatonic cycles. CW '
           'ascends, CCW descends. Each row is one <i>edge</i> of one cycle.</p>',
           '<table class="data"><tr>'
           '<th>Cycle</th><th>Verse</th><th>LH</th><th>LH fig</th>'
           '<th>RH</th><th>RH fig</th><th>CW</th><th>CCW</th></tr>']
    for e in entries:
        out.append(
            f'<tr><td>{escape_text(e.get("cycle",""))}</td>'
            f'<td class="num">{e.get("verse","")}</td>'
            f'<td class="rn lh">{render_rn_inline(e.get("lh_roman",""))}</td>'
            f'<td class="fig lh">{escape_text(e.get("lh_figure",""))}</td>'
            f'<td class="rn rh">{render_rn_inline(e.get("rh_roman",""))}</td>'
            f'<td class="fig rh">{escape_text(e.get("rh_figure",""))}</td>'
            f'<td>{escape_text(e.get("cw_label",""))}</td>'
            f'<td>{escape_text(e.get("ccw_label",""))}</td></tr>')
    out.append('</table>')
    return '\n'.join(out)


def render_stacked(entries):
    out = [f'<h2>Stacked chords ({len(entries)})</h2>',
           '<p>Single-sonority two-handed voicings built by stacking an RH '
           'voicing over an LH voicing. Sorted by LH.</p>',
           '<table class="data"><tr>'
           '<th>LH</th><th>LH fig</th><th>RH</th><th>RH fig</th>'
           '<th>Mood</th></tr>']
    for e in entries:
        out.append(
            f'<tr><td class="rn lh">{render_rn_inline(e.get("lh_roman",""))}</td>'
            f'<td class="fig lh">{escape_text(e.get("lh_figure",""))}</td>'
            f'<td class="rn rh">{render_rn_inline(e.get("rh_roman",""))}</td>'
            f'<td class="fig rh">{escape_text(e.get("rh_figure",""))}</td>'
            f'<td>{escape_text(e.get("mood",""))}</td></tr>')
    out.append('</table>')
    return '\n'.join(out)


def render_intro(d):
    title = d.get('title', 'Harp Chord System')
    htu = d.get('how_to_use', {})
    purpose = htu.get('purpose', '')
    out = [f'<h2>{escape_text(title)}</h2>',
           f'<p>{escape_text(purpose)}</p>']
    what = htu.get('what_this_contains', [])
    if what:
        out.append('<h3>Sections</h3><ul>')
        for item in what:
            out.append(f'<li>{escape_text(item)}</li>')
        out.append('</ul>')
    crit = htu.get('critical_distinctions', [])
    if crit:
        out.append('<h3>Critical distinctions</h3><ul>')
        for item in crit:
            out.append(f'<li>{escape_text(item)}</li>')
        out.append('</ul>')
    return '\n'.join(out)


def render_nav():
    links = [
        ('#intro', 'Overview'),
        ('#conventions', 'Conventions'),
        ('#patterns', 'Finger patterns (14)'),
        ('#cycles', 'Diatonic cycles (3)'),
        ('#jazz', 'Jazz progressions (42)'),
        ('#stacked', 'Stacked chords (76)'),
    ]
    items = '\n'.join(f'<li><a href="{href}">{escape_text(label)}</a></li>'
                     for href, label in links)
    return (
        '<nav id="sidebar">'
        '<h1>Chord System</h1>'
        '<a class="back" href="review.html">← Hymn review</a>'
        f'<ol>{items}</ol>'
        '</nav>'
    )


def build_html(d):
    intro = render_intro(d)
    conv = render_conventions(d.get('conventions', {}))
    pat = render_patterns(d.get('patterns', []))
    cyc = render_cycles(d.get('cycles', {}))
    jazz = render_jazz(d.get('jazz_progressions', {}).get('entries', []))
    stacked = render_stacked(d.get('stacked_chords', {}).get('entries', []))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Harp Chord System — Reference</title>
<style>{CSS}</style></head><body>
{render_nav()}
<main>
<article class="sheet" id="intro">{intro}</article>
<article class="sheet" id="conventions">{conv}</article>
<article class="sheet" id="patterns">{pat}</article>
<article class="sheet" id="cycles">{cyc}</article>
<article class="sheet" id="jazz">{jazz}</article>
<article class="sheet" id="stacked">{stacked}</article>
</main></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', help='HarpChordSystem.json')
    ap.add_argument('-o', '--output', required=True, help='Output HTML file')
    args = ap.parse_args()
    with open(args.input) as f:
        d = json.load(f)
    out = build_html(d)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'Wrote {args.output} ({len(out):,} bytes)')


if __name__ == '__main__':
    main()
