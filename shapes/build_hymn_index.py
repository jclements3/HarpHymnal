#!/usr/bin/env python3
"""Build the A-Z collapsible navigator pages for the Shapes hymnal.

Two outputs, sharing the same hymn metadata (loaded from data/hymns/*.json):

  shapes/hymns/index.html   — links to the full-level hymn pages
  shapes/chopin/index.html  — links to the chopin-only hymn pages

Both pages mirror the pattern used by the tablet's Retab Hymnal /
Reharm Hymnal screens: a search box at the top, hymns grouped by their
title's first letter, each group collapsible. Selecting a hymn opens
its detail page in the same area.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHAPES = REPO / 'shapes'
HYMNS_DIR = REPO / 'data' / 'hymns'


def _strip_lead(s: str) -> str:
    return re.sub(r'^[\'"\s]+', '', s)


def _letter_for(title: str) -> str:
    t = _strip_lead(title)
    return t[0].upper() if t and t[0].isalpha() else '#'


def collect_hymns() -> list[dict]:
    out: list[dict] = []
    for p in sorted(HYMNS_DIR.glob('*.json')):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        out.append({
            'slug': p.stem,
            'title': d.get('title') or p.stem,
            'key': (d.get('key') or {}).get('root', ''),
            'mode': (d.get('key') or {}).get('mode', ''),
            'meter': f"{(d.get('meter') or {}).get('beats','')}/{(d.get('meter') or {}).get('unit','')}",
            'phrases': len(d.get('phrases') or []),
            'bars': len(d.get('bars') or []),
        })
    return out


def render_index(hymns: list[dict], target_dir: str, title: str) -> str:
    """target_dir = 'hymns' or 'chopin' (where the per-hymn pages live)."""
    nav_back = '../'
    is_chopin = target_dir == 'chopin'
    nav = (
        '<nav class="shape-nav">'
        f'<a href="{nav_back}index.html">index</a>'
        f'<a href="{nav_back}QRG.html">QRG</a>'
        f'<a href="{nav_back}README.html">README</a>'
        f'<a href="{nav_back}DRILLS.html">DRILLS</a>'
        f'<a href="{nav_back}SAMPLES.html">SAMPLES</a>'
        f'<a href="{nav_back}HANDOUT.html">HANDOUT</a>'
        f'<a href="{nav_back}VERIFY.html">VERIFY</a>'
        f'<a href="{nav_back}Chords.html">Chords</a>'
        f'<a href="{nav_back}hymns/index.html">Hymns</a>'
        f'<a href="{nav_back}chopin/index.html">Chopin</a>'
        f'<a href="{nav_back}HANDOFF.html">HANDOFF</a>'
        f'<a href="{nav_back}NEXTSESSION.html">NEXTSESSION</a>'
        '</nav>'
    )

    payload = json.dumps(hymns)
    body_class = 'chopin-active' if is_chopin else 'auto-active'

    blurb = (
        'Each hymn is rendered with its melody on top and the inner '
        'voices voice-led beneath, Chopin-style. One ▶ play per phrase. '
        'No level selector here — just the chopin view.'
        if is_chopin else
        'Every hymn, every level: SATB · retab L1-L7 · reharm L1-L7 · '
        'auto · chopin. The level selector at the top of each hymn '
        'switches between them.'
    )

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="../style.css">
<style>
  #hrecent-bar {{ margin: 1rem 0 0.5rem; padding: 0.5rem 0.7rem;
                   background: var(--code-bg); border: 1px solid var(--rule);
                   border-radius: 4px; font-size: 0.9rem; }}
  #hrecent-bar strong {{ color: var(--accent); margin-right: 0.4rem; }}
  #hrecent .hrecent-link {{ display: inline-block; margin: 0 0.5rem 0 0;
                              padding: 0.1rem 0.45rem; border: 1px solid var(--rule);
                              border-radius: 3px; text-decoration: none;
                              color: var(--fg); background: #fff; }}
  #hrecent .hrecent-link:hover {{ background: var(--accent); color: #fff; }}
  #hrecent .hrecent-empty {{ color: var(--muted); font-style: italic; }}
  #hrecent-clear {{ font-size: 0.8rem; color: var(--muted); margin-left: 0.4rem; }}
  #hsearch-bar {{ margin: 0.5rem 0 1rem; }}
  #hsearch {{ width: 100%; padding: 0.45rem 0.7rem; font-size: 1rem;
              border: 1px solid var(--rule); border-radius: 4px; }}
  #hcount {{ color: var(--muted); font-size: 0.85rem; margin-left: 0.4rem; }}
  #hindex {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.4rem 0.6rem;
    align-items: start;
  }}
  .letter-group {{ border: 1px solid var(--rule); border-radius: 4px; overflow: hidden; }}
  .letter-header {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.55rem 0.8rem; cursor: pointer;
    background: var(--code-bg); user-select: none;
  }}
  .letter-header:hover {{ background: #e6dfd0; }}
  .letter-header::before {{
    content: '▸'; margin-right: 0.45rem; transition: transform 0.15s;
  }}
  .letter-group.open .letter-header::before {{ transform: rotate(90deg); }}
  .letter-count {{ color: var(--muted); font-size: 0.85rem; }}
  .letter-items {{ display: none; }}
  .letter-group.open .letter-items {{ display: block; }}
  .hitem {{ padding: 0.45rem 0.8rem; border-top: 1px solid var(--rule);
           text-decoration: none; color: var(--fg); display: block; }}
  .hitem:hover {{ background: var(--code-bg); }}
  .hitem-meta {{ color: var(--muted); font-size: 0.82rem; margin-top: 0.1rem; }}
</style>
</head><body class="{body_class}">
{nav}
<h1>{title}</h1>
<p>{blurb}</p>
<div id="hrecent-bar">
  <strong>Recent:</strong>
  <span id="hrecent"><em class="hrecent-empty">(none yet — open a hymn to build this list)</em></span>
  <a href="#" id="hrecent-clear" style="display:none;">clear</a>
</div>
<div id="hsearch-bar">
  <input id="hsearch" type="search" placeholder="Search title or slug…" autocomplete="off">
  <span id="hcount"></span>
</div>
<div id="hindex"></div>
<script>
const HYMNS = {payload};
const TARGET = {json.dumps(target_dir)};
function escapeHtml(s) {{
  return String(s).replace(/[&<>"]/g, c => ({{
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'
  }})[c]);
}}
function letterFor(title) {{
  const t = title.replace(/^[\\'"\\s]+/, '');
  return /^[A-Za-z]/.test(t) ? t[0].toUpperCase() : '#';
}}
function render(query) {{
  const idx = document.getElementById('hindex');
  const q = (query || '').trim().toLowerCase();
  const matches = q
    ? HYMNS.filter(h => (h.title || '').toLowerCase().includes(q)
                      || (h.slug || '').toLowerCase().includes(q))
    : HYMNS;
  document.getElementById('hcount').textContent = matches.length + ' / ' + HYMNS.length;
  idx.innerHTML = '';
  const groups = {{}};
  for (const h of matches) {{
    const L = letterFor(h.title);
    (groups[L] = groups[L] || []).push(h);
  }}
  const letters = Object.keys(groups).sort((a,b) => a==='#' ? 1 : b==='#' ? -1 : a.localeCompare(b));
  for (const L of letters) {{
    const g = document.createElement('div');
    g.className = 'letter-group' + (q ? ' open' : '');
    const head = document.createElement('div');
    head.className = 'letter-header';
    head.innerHTML = '<span>' + escapeHtml(L) + '</span>'
                   + '<span class="letter-count">' + groups[L].length + '</span>';
    head.addEventListener('click', () => g.classList.toggle('open'));
    g.appendChild(head);
    const items = document.createElement('div');
    items.className = 'letter-items';
    for (const h of groups[L]) {{
      const a = document.createElement('a');
      a.className = 'hitem';
      a.href = h.slug + '.html';
      const meta = [h.key && (h.key + (h.mode ? ' ' + h.mode : '')), h.meter, h.bars + ' bars'].filter(Boolean).join(' · ');
      a.innerHTML = '<strong>' + escapeHtml(h.title) + '</strong>'
                  + '<div class="hitem-meta">' + escapeHtml(meta) + '</div>';
      items.appendChild(a);
    }}
    g.appendChild(items);
    idx.appendChild(g);
  }}
}}
// Single shared Recent bucket across hymns + chopin — when you've just
// looked at a hymn in either view, it should be one tap away from the
// other. Each entry stays a slug; we link to it via TARGET so the
// current navigator sends you to its own variant.
const RECENT_KEY = 'shapes.recent';
const RECENT_MAX = 10;
function loadRecent() {{
  try {{ return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]'); }}
  catch (e) {{ return []; }}
}}
function renderRecent() {{
  const slugs = loadRecent();
  const wrap = document.getElementById('hrecent');
  const clearBtn = document.getElementById('hrecent-clear');
  if (!slugs.length) {{
    wrap.innerHTML = '<em class="hrecent-empty">(none yet — open a hymn to build this list)</em>';
    clearBtn.style.display = 'none';
    return;
  }}
  const bySlug = Object.fromEntries(HYMNS.map(h => [h.slug, h]));
  const links = slugs.filter(s => bySlug[s]).map(s => {{
    const h = bySlug[s];
    return '<a class="hrecent-link" href="' + escapeHtml(h.slug) + '.html">'
         + escapeHtml(h.title) + '</a>';
  }});
  wrap.innerHTML = links.length ? links.join('') :
    '<em class="hrecent-empty">(none yet — open a hymn to build this list)</em>';
  clearBtn.style.display = links.length ? '' : 'none';
}}
document.getElementById('hrecent-clear').addEventListener('click', e => {{
  e.preventDefault();
  localStorage.removeItem(RECENT_KEY);
  renderRecent();
}});
document.getElementById('hsearch').addEventListener('input', e => render(e.target.value));
renderRecent();
render('');
</script>
</body></html>'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.parse_args()  # accept no flags
    hymns = collect_hymns()
    print(f'collected {len(hymns)} hymns')
    (SHAPES / 'hymns').mkdir(parents=True, exist_ok=True)
    (SHAPES / 'chopin').mkdir(parents=True, exist_ok=True)
    (SHAPES / 'hymns' / 'index.html').write_text(
        render_index(hymns, 'hymns', 'Shapes — Hymnal')
    )
    (SHAPES / 'chopin' / 'index.html').write_text(
        render_index(hymns, 'chopin', 'Shapes — Chopin')
    )
    print('wrote shapes/hymns/index.html and shapes/chopin/index.html')


if __name__ == '__main__':
    main()
