// Batch-render jazz hymn ABC -> SVG through the abcjsharp FORK (harp grand-staff:
// V:1 stems up, V:2 stems down) so the Jazz Hymnal looks like the rest of the harp
// apps instead of an abcm2ps "PDF". Loads jsdom + the fork once, loops all hymns.
//
//   node jazz/fork_render.js <job.json>
//   job.json = { "outdir": "...", "items": [ { "slug": "...", "abc": "..." }, ... ] }
//
// jsdom lives in ~/projects/hymnal/node_modules; invoke with NODE_PATH set there.
const fs = require('fs'), path = require('path'), os = require('os');
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><div id="p"></div>');
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;          // jsdom>=22: abcjs reads navigator
const abcjs = require(path.join(os.homedir(), 'projects/abcjsharp/dist/abcjs-basic.js'));

const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const el = document.getElementById('p');
let ok = 0; const fail = [];
for (const it of job.items) {
  el.innerHTML = '';
  try {
    abcjs.renderAbc(el, it.abc, {
      staffwidth: 1100, oneSvgPerLine: false,
      wrap: { minSpacing: 1.8, maxSpacing: 2.7, minSpacingLimit: 1.0, lastLineLimit: true },
    });
    const svg = el.querySelector('svg');
    if (!svg) { fail.push(it.slug + ': no svg'); continue; }
    // currentColor -> ink so it shows black inside an <img>; drop the live-DOM style.
    let s = svg.outerHTML.replace(/currentColor/g, '#11110d')
                         .replace(/\sstyle="[^"]*"/, '');
    fs.writeFileSync(path.join(job.outdir, it.slug + '.svg'), s);
    ok++;
  } catch (e) { fail.push(it.slug + ': ' + e.message); }
}
console.log(JSON.stringify({ ok, fail }));
