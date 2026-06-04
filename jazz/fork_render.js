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
    // No `wrap`. staffwidth (per hymn = bars/line * KERN) sets the note kerning:
    // abcjs justifies each row to it, so a small staffwidth packs notes tight and a
    // larger one adds air. Line breaks come from the source (one [V:1]/[V:2] pair per
    // system); fit-to-screen then scales the whole block up to fill the display.
    abcjs.renderAbc(el, it.abc, { staffwidth: it.staffwidth || 900, oneSvgPerLine: false });
    const svg = el.querySelector('svg');
    if (!svg) { fail.push(it.slug + ': no svg'); continue; }
    // currentColor -> ink so it shows black inside an <img>; drop the live-DOM style.
    let s = svg.outerHTML.replace(/currentColor/g, '#11110d')
                         .replace(/\sstyle="[^"]*"/, '');
    // abcjs outerHTML omits the default SVG namespace (it lives in the DOM, not the
    // markup). rsvg tolerates that, but an <img src=*.svg> in a WebView needs it or
    // the image is broken. Add it back so the file is a valid standalone SVG.
    if (!/xmlns="http:\/\/www\.w3\.org\/2000\/svg"/.test(s)) {
      s = s.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ');
    }
    fs.writeFileSync(path.join(job.outdir, it.slug + '.svg'), s);
    ok++;
  } catch (e) { fail.push(it.slug + ': ' + e.message); }
}
console.log(JSON.stringify({ ok, fail }));
