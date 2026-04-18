#!/usr/bin/env python3
"""
build_harphymnal_html.py — emit hymnal_html/HarpHymnal.html with:
  - full-height left sidebar (nav from review.html)
  - right column split: piano score (top) + reharm iframe (bottom)

Controls sit above the navigator so the right column is all music + reharm.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
review = (ROOT / 'hymnal_html' / 'review.html').read_text()

# Extract sidebar <nav id="sidebar">...</nav>
m = re.search(r'<nav id="sidebar".*?</nav>', review, re.DOTALL)
if not m:
    raise SystemExit('could not find <nav id="sidebar"> in review.html')
sidebar = m.group(0)

# Replace the <h1>Reharm sheets</h1> with an in-page MIDI player.
# html-midi-player is a Magenta.js web component that plays MIDI via
# Web Audio + a default soundfont — no OS handoff needed.
sidebar = re.sub(
    r'<h1>[^<]*</h1>',
    '<a id="play-midi" class="play-midi" href="silent_night.midi" '
    'download title="Open in your MIDI player">▶&nbsp; Play MIDI</a>',
    sidebar, count=1,
)

# Retarget hymn links: cross-file anchors + iframe target
sidebar = re.sub(
    r'<a class="hymn-link" href="(#h-[^"]+)"',
    r'<a class="hymn-link" target="reharm-frame" href="review.html\1"',
    sidebar,
)
# Chord System reference link also opens in the iframe
sidebar = re.sub(
    r'(<a class="ref-link")(\s+href=)',
    r'\1 target="reharm-frame"\2',
    sidebar,
)

# Extract minimal sidebar-related CSS from review.html.  The sidebar CSS
# lives near the top of review.html; grab the whole <style> block and let
# unused rules sit dormant.  (They don't collide with our layout rules.)
style_m = re.search(r'<style>(.*?)</style>', review, re.DOTALL)
review_css = style_m.group(1) if style_m else ''

# Extract the filter/search JS from review.html's inline <script>.
script_m = re.search(r'<script>(.*?)</script>', review, re.DOTALL)
review_js = script_m.group(1) if script_m else ''

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HarpHymnal — piano score + reharm</title>
<style>
{review_css}

/* --- HarpHymnal layout overrides --- */
html, body {{ margin: 0; height: 100%; overflow: hidden; }}
body {{ display: grid; grid-template-columns: 260px 1fr;
  grid-template-rows: 100vh; }}

/* Left column: controls above, nav below, full height */
#left-col {{ display: flex; flex-direction: column; background: #2b2722;
  color: #d8ccb0; overflow: hidden; border-right: 1px solid #000; }}
#controls {{ flex: 0 0 auto; padding: 10px 12px;
  border-bottom: 1px solid #444; background: #1f1b17; }}
#controls h1 {{ margin: 0 0 6px 0; font-size: 12px; font-style: italic;
  font-family: Palatino, Georgia, serif; color: #d8ccb0; }}
#controls .btn-row {{ display: flex; gap: 4px; }}
#controls button {{ flex: 1; font: 10px/1.2 Palatino, serif;
  padding: 4px 6px; border: 1px solid #8b6f47; background: #3b2f24;
  color: #d8ccb0; cursor: pointer; border-radius: 2px; }}
#controls button:hover {{ background: #4c3d2e; }}

/* Override review.html's fixed-width sidebar so our nav fills the column */
nav#sidebar {{ position: static !important; width: auto !important;
  flex: 1 1 auto !important; overflow: auto !important;
  max-height: none !important; height: auto !important; }}

/* Play-MIDI button that replaces the "Reharm sheets" heading */
.play-midi {{ display: block; margin: 0 0 8px 0; padding: 8px 12px;
  background: #8b6f47; color: #f4ecd8; text-align: center;
  text-decoration: none; font-family: Palatino, serif;
  font-size: 14px; font-weight: bold; border-radius: 3px;
  cursor: pointer; transition: background 0.15s; }}
.play-midi:hover {{ background: #a88960; color: #fff; }}

/* Right column: split piano score + iframe */
#right-col {{ position: relative; overflow: hidden;
  background: var(--bg, #f4ecd8); }}
#score {{ position: absolute; left: 0; right: 0; top: 0;
  overflow: auto; background: white; }}
#score object {{ display: block; width: 100%; height: auto; }}
#divider {{ position: absolute; left: 0; right: 0; height: 6px;
  background: #8b6f47; cursor: ns-resize; z-index: 10; }}
#divider:hover {{ background: #a88960; }}
#reharm {{ position: absolute; left: 0; right: 0; bottom: 0;
  overflow: hidden; }}
#reharm iframe {{ width: 100%; height: 100%; border: 0; display: block;
  background: white; }}
</style>
</head>
<body>
<aside id="left-col">
  <div id="controls">
    <h1>HarpHymnal</h1>
    <div class="btn-row">
      <button id="btn-score">Score full</button>
      <button id="btn-half">Half</button>
      <button id="btn-reharm">Reharm full</button>
    </div>
  </div>
  {sidebar}
</aside>

<section id="right-col">
  <div id="score">
    <object id="score-obj" type="image/svg+xml" data="silent_night.svg"></object>
  </div>
  <div id="divider"></div>
  <div id="reharm">
    <iframe name="reharm-frame" src="review.html"></iframe>
  </div>
</section>

<script>
// --- Filter / search JS lifted from review.html (still operates on #sidebar) ---
{review_js}

// --- Split-pane resizing ---
(function() {{
  const scorePane = document.getElementById('score');
  const reharmPane = document.getElementById('reharm');
  const divider = document.getElementById('divider');
  const right = document.getElementById('right-col');
  const DIV_H = 6;
  const MIN_PX = 50;

  function layout(frac) {{
    const h = right.clientHeight;
    const topH = Math.max(MIN_PX, Math.min(h - MIN_PX - DIV_H, h * frac));
    scorePane.style.height = topH + 'px';
    divider.style.top = topH + 'px';
    reharmPane.style.top = (topH + DIV_H) + 'px';
  }}

  // Default: reharm collapsed to its minimum strip so the score has max height.
  layout(1.0);
  window.addEventListener('resize', () => {{
    const cur = parseFloat(scorePane.style.height) || right.clientHeight;
    layout(cur / right.clientHeight);
  }});

  document.getElementById('btn-score').onclick = () => layout(0.92);
  document.getElementById('btn-half').onclick = () => layout(0.5);
  document.getElementById('btn-reharm').onclick = () => layout(0.08);

  let dragging = false;
  divider.addEventListener('mousedown', e => {{
    dragging = true;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'ns-resize';
    e.preventDefault();
  }});
  window.addEventListener('mousemove', e => {{
    if (!dragging) return;
    const rect = right.getBoundingClientRect();
    layout((e.clientY - rect.top) / rect.height);
  }});
  window.addEventListener('mouseup', () => {{
    dragging = false;
    document.body.style.userSelect = '';
    document.body.style.cursor = '';
  }});
}})();

// --- Hide the duplicated sidebar inside the reharm iframe ---
(function() {{
  const iframe = document.querySelector('iframe[name="reharm-frame"]');
  iframe.addEventListener('load', () => {{
    try {{
      const doc = iframe.contentDocument;
      if (!doc) return;
      const innerNav = doc.getElementById('sidebar');
      if (innerNav) innerNav.style.display = 'none';
      // review.html's <main> has left padding sized to the sidebar; reset it
      const main = doc.querySelector('main');
      if (main) {{
        main.style.marginLeft = '0';
        main.style.paddingLeft = '20px';
      }}
    }} catch (e) {{ /* cross-origin (shouldn't happen for same-file) */ }}
  }});
}})();

// --- Swap piano score + MIDI link when user clicks a hymn in the nav ---
// Only silent_night.svg/.midi exist for now; fall back when not rendered.
(function() {{
  const obj = document.getElementById('score-obj');
  const midiBtn = document.getElementById('play-midi');
  document.querySelectorAll('nav#sidebar a.hymn-link').forEach(a => {{
    a.addEventListener('click', () => {{
      const slug = a.getAttribute('href').replace(/^.*#h-/, '').toLowerCase();
      const svgPath = slug + '.svg';
      const midiPath = slug + '.midi';
      fetch(svgPath, {{method: 'HEAD'}})
        .then(r => {{ if (r.ok) obj.data = svgPath; }})
        .catch(() => {{}});
      fetch(midiPath, {{method: 'HEAD'}})
        .then(r => {{
          if (r.ok && midiBtn) {{
            midiBtn.href = midiPath;
            midiBtn.download = midiPath;
          }}
        }})
        .catch(() => {{}});
    }});
  }});
}})();
</script>
</body>
</html>
"""

out_path = ROOT / 'hymnal_html' / 'HarpHymnal.html'
out_path.write_text(html)
print(f'Wrote {out_path} ({len(html)} chars)')
