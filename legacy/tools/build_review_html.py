#!/usr/bin/env python3
"""
build_review_html.py — render a set of reharm JSONs into a single static
review HTML with a left-sidebar navigation pane. Styled to approximate the
PDF lead sheet on a tablet (16:10 landscape content area).

Input: one or more reharm JSONs produced by
    `python3 tools/export_to_reharm.py --escape html <export>.json -o <reharm>.json`

Usage:
    python3 tools/build_review_html.py reharm1.json reharm2.json ... -o review.html
    python3 tools/build_review_html.py --dir path/to/reharms -o review.html
"""
import argparse
import glob
import json
import os
import re
import sys


# Quality-code → HTML rendering (mirrors fill_template.py::rndqparse)
# Each returns a small HTML fragment (may contain <sup>).
def _render_qual(code):
    if not code:
        return ''
    # LaTeX macro rules (mirroring \rndqparse):
    #   - Inversions ¹²³ → superscript (\inv{N})
    #   - Halfdim ∅ → superscript (\halfdim)
    #   - Diminished ° → superscript ($^\circ$)
    #   - Everything else (m, q, s, Δ, digits 6/7, +8) → BASELINE
    table = {
        'm':       '<i>m</i>',
        'm7':      '<i>m</i>7',
        'm6':      '<i>m</i>6',
        'q':       '<i>q</i>',
        'q7':      '<i>q</i>7',
        's4+8':    '<i>s</i>4+8',
        's4':      '<i>s</i>4',
        's2':      '<i>s</i>2',
        '+8':      '+8',
        'D':       '&#916;',
        'o7':      '<sup>&#248;</sup>7',
        'o':       '<sup>&#176;</sup>',
        '7':       '7',
        '6':       '6',
        'm7i':     '<i>m</i>7<sup class="inv">1</sup>',
        'm7ii':    '<i>m</i>7<sup class="inv">2</sup>',
        'm7iii':   '<i>m</i>7<sup class="inv">3</sup>',
        'o7i':     '<sup>&#248;</sup>7<sup class="inv">1</sup>',
        'o7ii':    '<sup>&#248;</sup>7<sup class="inv">2</sup>',
        'o7iii':   '<sup>&#248;</sup>7<sup class="inv">3</sup>',
        '7i':      '7<sup class="inv">1</sup>',
        '7ii':     '7<sup class="inv">2</sup>',
        '7iii':    '7<sup class="inv">3</sup>',
        'oi':      '<sup>&#176;</sup><sup class="inv">1</sup>',
        'oii':     '<sup>&#176;</sup><sup class="inv">2</sup>',
        'i':       '<sup class="inv">1</sup>',
        'ii':      '<sup class="inv">2</sup>',
        'iii':     '<sup class="inv">3</sup>',
        # Maj7 + inversion (Δ baseline + inv superscript)
        'Di':      '&#916;<sup class="inv">1</sup>',
        'Dii':     '&#916;<sup class="inv">2</sup>',
        'Diii':    '&#916;<sup class="inv">3</sup>',
        # Second-inversion + octave doubling
        'ii+8':    '<sup class="inv">2</sup>+8',
    }
    return table.get(code, code)


# Roman numerals: reuse fill_template.py::split_rn logic in HTML form
SUP_TO_CODE = {'\u00B9': 'i', '\u00B2': 'ii', '\u00B3': 'iii',
               '\u0394': 'D', '\u00B0': 'o', '\u00F8': 'o',
               '\u2077': '7'}


def split_rn(rn):
    lead = ''
    if rn and rn[0] in '#b':
        lead = rn[0]
        rn = rn[1:]
    m = re.match(r'^([ivIV]+)(.*)$', rn)
    if not m:
        return rn, ''
    numerals, rest = m.groups()
    rest = rest.replace('\u00F87', 'o7').replace('\u00F8', 'o')
    code = ''
    for ch in rest:
        if ch in SUP_TO_CODE:
            code += SUP_TO_CODE[ch]
        elif ch in 'mbqs+D\u00B0':
            code += ch.replace('\u00B0', 'o')
        elif ch.isdigit():
            code += ch
        else:
            code += ch
    return lead + numerals, code


def render_rn(rn):
    num, qual = split_rn(rn)
    accidental = ''
    if num and num[0] == 'b':
        accidental = '&#9837;'   # ♭
        num = num[1:]
    elif num and num[0] == '#':
        accidental = '&#9839;'   # ♯
        num = num[1:]
    return f'{accidental}<span class="num">{num}</span>{_render_qual(qual)}'


def fmt_melody(p):
    if not p:
        return '&mdash;'
    # Accidentals render as superscripts (♯, ♭) so the note letter and octave
    # sit on the baseline: B♭4, F♯5, etc.
    return (p.replace('#', '<sup>&#9839;</sup>')   # ♯
             .replace('-', '<sup>&#9837;</sup>'))  # ♭


def hymn_slug(title):
    return re.sub(r'[^A-Za-z0-9]+', '_', title).strip('_')


CSS = """
:root {
  --rhcol: #1F4E79;
  --lhcol: #7B2B2B;
  --desccol: #2A3342;
  --flavcol: #6B7A8F;
  --paper: #F4ECD8;
  --ink: #1A1612;
  --accent: #8B6F47;
  --leafred: rgb(220,75,75);
  --leafyellow: rgb(190,155,30);
  --leafcyan: rgb(40,180,190);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #2b2722; color: var(--ink);
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; }
body { display: flex; min-height: 100vh; }
nav#sidebar {
  width: 280px; flex-shrink: 0;
  background: #1f1c19; color: #d8ccb0;
  position: sticky; top: 0; align-self: flex-start;
  height: 100vh; overflow-y: auto; padding: 14px 10px;
  border-right: 1px solid #000;
}
nav#sidebar h1 {
  font-size: 15px; margin: 0 0 8px 2px; color: #e8d8b4;
  font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;
}
nav#sidebar input {
  width: 100%; padding: 6px 8px; margin-bottom: 10px;
  background: #2d2924; color: #e8d8b4; border: 1px solid #3a342c;
  border-radius: 3px; font-size: 12px;
}
nav#sidebar .hint { font-size: 10px; color: #7a7161; margin: -6px 0 8px 2px;
  font-style: italic; }
nav#sidebar details { margin: 1px 0; }
nav#sidebar summary { cursor: pointer; padding: 4px 8px; color: #e8d8b4;
  font-weight: 600; font-size: 12px; list-style: none; border-radius: 3px;
  user-select: none; }
nav#sidebar summary::-webkit-details-marker { display: none; }
nav#sidebar summary::before { content: '▶'; display: inline-block;
  width: 10px; font-size: 8px; color: #7a7161; transition: transform 0.15s; }
nav#sidebar details[open] > summary::before { transform: rotate(90deg); }
nav#sidebar summary:hover { background: #2d2924; }
nav#sidebar summary .count { color: #7a7161; font-weight: 400; font-size: 10px;
  margin-left: 4px; }
nav#sidebar ul { list-style: none; margin: 0; padding: 0 0 4px 12px; }
nav#sidebar li { margin: 0; }
nav#sidebar a {
  display: block; padding: 3px 8px 3px 10px; color: #c8bc9c; font-size: 11px;
  text-decoration: none; border-radius: 3px;
}
nav#sidebar a .id { display: inline-block; width: 34px; color: #7a7161;
  font-family: ui-monospace, monospace; font-size: 10px; }
nav#sidebar a:hover { background: #2d2924; color: #f0e4c4; }
nav#sidebar a.current { background: #3a3429; color: #fff; }
nav#sidebar a.ref-link { display: block; padding: 6px 10px; margin-bottom: 10px;
  background: #2d2924; color: #e8d8b4; font-weight: 600; border-radius: 3px;
  border-left: 3px solid var(--accent); font-size: 12px; }
nav#sidebar a.ref-link:hover { background: #3a3429; color: #fff; }

main { flex: 1; padding: 20px; overflow-x: auto; }
.hymn-sheet {
  background: var(--paper);
  width: 100%; max-width: 1100px;
  aspect-ratio: auto;
  margin: 0 auto 28px auto;
  padding: 12px 16px;
  border-radius: 4px; box-shadow: 0 3px 16px rgba(0,0,0,0.4);
  color: var(--ink);
}
.hymn-header { display: flex; flex-direction: column; align-items: baseline;
  gap: 2px; padding-bottom: 4px;
  border-bottom: 1px solid var(--ink); margin-bottom: 6px; }
.hymn-header .title { font-family: "Palatino", "Palatino Linotype", "Book Antiqua",
  Georgia, serif; font-size: 32px; font-weight: 700; font-style: italic;
  line-height: 1.05; margin: 0; color: var(--ink); }
.hymn-header .meta-line { color: var(--desccol); font-size: 13px;
  line-height: 1.4; }

.phrase-banner {
  display: flex; align-items: center; gap: 8px;
  padding: 3px 6px; margin: 5px 0 2px 0; border-radius: 2px;
  background: var(--banner-bg);
}
.phrase.leafyellow { --banner-bg: rgba(190,155,30,0.18); --badge-bg: rgba(130,100,15,0.85); }
.phrase.leafred    { --banner-bg: rgba(220,75,75,0.18);  --badge-bg: rgba(155,45,45,0.85); }
.phrase.leafcyan   { --banner-bg: rgba(40,180,190,0.18); --badge-bg: rgba(25,110,115,0.85); }
.phrase.accent     { --banner-bg: rgba(139,111,71,0.18); --badge-bg: rgba(85,65,40,0.85); }

.phrase-label { font-variant: small-caps; font-weight: 700; font-size: 17px;
  color: var(--desccol); letter-spacing: 0.5px; }
.phrase-strategy { font-style: italic; font-size: 17px; color: var(--desccol); flex: 1; }
.phrase-cycle { color: #fff; background: var(--badge-bg); padding: 4px 11px;
  border-radius: 2px; font-weight: 700; font-size: 15px; letter-spacing: 0.4px; }

.bar-grid { display: grid;
  grid-template-columns: repeat(var(--bars), 1fr);
  border: 1px solid var(--ink); background: var(--paper);
  border-radius: 2px; overflow: hidden; }
.bar {
  padding: 8px 9px; border-right: 1px solid #cfc3a8;
  display: flex; flex-direction: column; align-items: center;
  min-height: 120px; justify-content: flex-start; gap: 4px;
}
.bar:last-child { border-right: none; }
.bar-top { display: flex; width: 100%; justify-content: space-between;
  align-items: baseline; gap: 8px; }
.bar-num { color: var(--accent); font-weight: 700; font-size: 14px;
  letter-spacing: 0.3px; white-space: nowrap; flex-shrink: 0; }
.edge-label { color: var(--accent); font-style: italic; font-size: 15px; }
.edge-label .mel-inline { color: var(--ink); font-weight: 700;
  font-family: "Palatino","Palatino Linotype",Georgia,serif;
  font-style: normal; font-size: 16px; margin-right: 5px;
  font-feature-settings: "onum" 1; }
.frac { display: flex; flex-direction: column; align-items: center;
  gap: 3px; margin: 4px 0; }
.frac .rh { color: var(--rhcol); font-family: "Palatino","Palatino Linotype","Book Antiqua",Georgia,serif;
  font-weight: 700; font-size: 28px; line-height: 1.05;
  font-feature-settings: "onum" 1; }
.frac .lh { color: var(--lhcol); font-family: "Palatino","Palatino Linotype","Book Antiqua",Georgia,serif;
  font-weight: 700; font-size: 28px; line-height: 1.05;
  font-feature-settings: "onum" 1; }
.bar .fig { color: var(--flavcol);
  font-family: "Courier New", ui-monospace, Consolas, Menlo, monospace;
  font-size: 17px; letter-spacing: 0.5px; margin-top: 4px; }
.frac sup { font-size: 70%; vertical-align: super; line-height: 0;
  font-feature-settings: "onum" 1; }
.frac sup.inv { font-size: 60%; vertical-align: super; line-height: 0; }
.frac .num { font-style: normal; }
.frac i { font-style: italic; font-weight: 700; }

.lyrics { display: flex; flex-direction: column; gap: 2px;
  padding: 5px 10px; background: rgba(255,255,255,0.5); margin-top: 2px;
  border-radius: 2px; font-size: 17px; font-style: italic; }
.lyrics .verse { width: 100%; }
.lyrics .verse { display: flex; gap: 6px; align-items: baseline; }
.lyrics .verse-tag { color: var(--accent); font-family: ui-monospace, monospace;
  font-weight: 700; font-style: normal; font-size: 13px; }

footer.top-bar { position: sticky; top: 0; background: #2b2722; z-index: 10;
  padding: 8px 16px; border-bottom: 1px solid #000; color: #d8ccb0;
  font-size: 12px; display: flex; justify-content: space-between; }
"""


JS = """
const navInput = document.getElementById('filter');
const navLinks = [...document.querySelectorAll('nav#sidebar a.hymn-link')];
const navGroups = [...document.querySelectorAll('nav#sidebar details.group')];

function isId(q) { return /^\\d{1,3}$/.test(q.trim()); }

navInput.addEventListener('input', () => {
  const raw = navInput.value.trim();
  const q = raw.toLowerCase();

  if (isId(raw)) {
    const padded = raw.padStart(3, '0');
    let hit = null;
    navLinks.forEach(a => {
      const id = a.dataset.id;
      const match = (id === padded);
      a.parentElement.style.display = match ? '' : 'none';
      if (match) hit = a;
    });
    // Open all groups so the match is visible, focus it
    navGroups.forEach(g => { g.open = true; g.style.display = ''; });
    if (hit) { hit.scrollIntoView({block:'center'}); hit.click(); }
    return;
  }

  navLinks.forEach(a => {
    const match = !q || a.textContent.toLowerCase().includes(q);
    a.parentElement.style.display = match ? '' : 'none';
  });
  // Hide groups with no visible children, and auto-expand groups with matches
  navGroups.forEach(g => {
    const visible = [...g.querySelectorAll('li')].some(li => li.style.display !== 'none');
    g.style.display = visible ? '' : 'none';
    if (q) g.open = visible;
  });
});

const hymns = [...document.querySelectorAll('.hymn-sheet')];
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const id = e.target.id;
      navLinks.forEach(a => a.classList.toggle('current', a.getAttribute('href') === '#' + id));
    }
  });
}, { rootMargin: '-40% 0px -40% 0px' });
hymns.forEach(h => io.observe(h));
"""


def render_bar_cell(asn):
    if not asn:
        return '<div class="bar"></div>'
    bar_num = asn.get('bar', '')
    mood = asn.get('mood', '')
    lh_rom = asn.get('lh_rom', '')
    rh_rom = asn.get('rh_rom', '')
    lh_fig = asn.get('lh_fig', '')
    rh_fig = asn.get('rh_fig', '')
    mel = fmt_melody(asn.get('mel', ''))
    return (
        '<div class="bar">'
        '<div class="bar-top">'
        f'<span class="edge-label"><span class="mel-inline">{mel}</span> {mood}</span>'
        f'<span class="bar-num">{bar_num}</span>'
        '</div>'
        f'<div class="fig">{lh_fig}&emsp;{rh_fig}</div>'
        '<div class="frac">'
        f'<div class="rh">{render_rn(rh_rom)}</div>'
        f'<div class="lh">{render_rn(lh_rom)}</div>'
        '</div>'
        '</div>'
    )


def render_phrase(phrase, assignments_by_bar):
    cycle_color = phrase.get('cycle_color', 'leafyellow')
    label = phrase.get('label', '')
    bars = phrase.get('bars', [])
    if not bars:
        return ''
    first, last = bars[0], bars[-1]
    strategy = phrase.get('strategy', '')
    cycle = phrase.get('cycle', 'stacked')
    lyrics = phrase.get('lyrics', {})
    v1 = lyrics.get('v1', '')
    v2 = lyrics.get('v2', '')
    cells = ''.join(render_bar_cell(assignments_by_bar.get(b)) for b in bars)
    lyric_html = ''
    if v1 or v2:
        verses = []
        if v1:
            verses.append(f'<div class="verse"><span class="verse-tag">v.1</span>{v1}</div>')
        if v2:
            verses.append(f'<div class="verse"><span class="verse-tag">v.2</span>{v2}</div>')
        lyric_html = f'<div class="lyrics">{"".join(verses)}</div>'
    return (
        f'<section class="phrase {cycle_color}">'
        '<div class="phrase-banner">'
        f'<span class="phrase-label">Phrase {label} &middot; bars {first}&ndash;{last}</span>'
        f'<span class="phrase-strategy">{strategy}</span>'
        f'<span class="phrase-cycle">{cycle}</span>'
        '</div>'
        f'<div class="bar-grid" style="--bars: {len(bars)}">{cells}</div>'
        f'{lyric_html}'
        '</section>'
    )


def render_hymn(data):
    title = data.get('title', 'Untitled')
    slug = hymn_slug(title)
    words = data.get('words', '')
    music = data.get('music', '')
    tune = data.get('tune', '')
    key = data.get('key', '')
    meter = data.get('meter', '')
    bpm = data.get('bpm', 100)
    phrases = data.get('phrases', [])
    assignments = data.get('assignments', [])
    n_bars = max((a.get('bar', 0) for a in assignments), default=0)
    n_phrases = len(phrases)
    assignments_by_bar = {a['bar']: a for a in assignments}
    body = ''.join(render_phrase(p, assignments_by_bar) for p in phrases)
    line1_parts = []
    if words and words != '[unknown]':
        line1_parts.append(f'Words: {words}')
    if music and music != '[unknown]':
        line1_parts.append(f'Music: {music}')

    line2_parts = []
    if tune and tune != '[unknown]':
        line2_parts.append(f'Tune: {tune}')
    line2_parts.append(f'Key of {key}')
    line2_parts.append(f'{meter} &nbsp;&#9833;={bpm}')
    line2_parts.append(
        f'{n_bars} bars, {n_phrases} phrase{"s" if n_phrases != 1 else ""}')

    line1 = ' &middot; '.join(line1_parts)
    line2 = ' &middot; '.join(line2_parts)

    return (
        f'<article class="hymn-sheet" id="h-{slug}">'
        '<div class="hymn-header">'
        f'<h2 class="title">{title}</h2>'
        f'<div class="meta-line">{line1}</div>'
        f'<div class="meta-line">{line2}</div>'
        '</div>'
        f'{body}'
        '</article>'
    )


def render_nav(hymns_meta):
    """hymns_meta is a list of (slug, title) tuples. Assigns a zero-padded
    3-digit ID based on alphabetical position and groups by first letter."""
    # Sort alphabetically by title (case-insensitive)
    sorted_meta = sorted(hymns_meta, key=lambda x: x[1].lower())
    # Assign IDs
    ided = [(f'{i+1:03d}', slug, title) for i, (slug, title) in enumerate(sorted_meta)]

    # Group by first letter (non-alpha first chars go to '#')
    from collections import defaultdict
    groups = defaultdict(list)
    for hid, slug, title in ided:
        # Find first alpha char
        first = next((c for c in title if c.isalpha()), '#').upper()
        groups[first].append((hid, slug, title))

    # Render — first group is open by default
    html_parts = []
    first = True
    for letter in sorted(groups):
        entries = groups[letter]
        items = ''.join(
            f'<li><a class="hymn-link" href="#h-{slug}" data-id="{hid}">'
            f'<span class="id">{hid}</span>{title}</a></li>'
            for hid, slug, title in entries
        )
        open_attr = ' open' if first else ''
        first = False
        html_parts.append(
            f'<details class="group"{open_attr}>'
            f'<summary>{letter} <span class="count">{len(entries)}</span></summary>'
            f'<ul>{items}</ul>'
            f'</details>'
        )
    groups_html = ''.join(html_parts)

    return (
        '<nav id="sidebar">'
        '<h1>Reharm sheets</h1>'
        '<a class="ref-link" href="chord_system.html">Chord System reference &rarr;</a>'
        '<input id="filter" placeholder="name, or 3-digit id (e.g. 042)" type="search">'
        '<div class="hint">Type a name to filter, or a number to jump to an ID.</div>'
        f'{groups_html}'
        '</nav>'
    )


def build_html(reharms):
    hymns_meta = [(hymn_slug(d.get('title', 'untitled')), d.get('title', 'Untitled'))
                  for d in reharms]
    nav_html = render_nav(hymns_meta)
    bodies = '\n'.join(render_hymn(d) for d in reharms)
    return (
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>HarpHymnal &mdash; Reharm Review</title>'
        # Hide the sidebar when this page is loaded inside an iframe
        # (e.g. by HarpHymnal.html).
        '<script>if(window.parent!==window)'
        'document.documentElement.classList.add("embedded");</script>'
        f'<style>{CSS}\n'
        'html.embedded nav#sidebar{display:none!important}\n'
        'html.embedded main{margin-left:0!important;padding-left:20px!important}'
        '</style>'
        '</head><body>'
        f'{nav_html}'
        f'<main>{bodies}</main>'
        f'<script>{JS}</script>'
        '</body></html>'
    )


def main():
    ap = argparse.ArgumentParser(
        description='Render reharm JSONs into a static review HTML')
    ap.add_argument('inputs', nargs='*', help='Reharm JSON files')
    ap.add_argument('--dir', help='Directory containing reharm JSON files')
    ap.add_argument('-o', '--output', required=True, help='Output HTML file')
    args = ap.parse_args()

    paths = list(args.inputs)
    if args.dir:
        paths.extend(sorted(glob.glob(os.path.join(args.dir, '*.json'))))
    if not paths:
        print('Error: no input files (pass positional args or --dir)', file=sys.stderr)
        sys.exit(2)

    reharms = []
    for p in paths:
        with open(p) as f:
            reharms.append(json.load(f))

    html = build_html(reharms)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote {args.output} ({len(reharms)} hymns, {len(html):,} bytes)',
          file=sys.stderr)


if __name__ == '__main__':
    main()
