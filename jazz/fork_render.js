// Batch-render jazz hymn ABC -> SVG through the abcjsharp FORK (harp grand-staff:
// V:1 stems up, V:2 stems down) so the Jazz Hymnal looks like the rest of the harp
// apps instead of an abcm2ps "PDF". Loads jsdom + the fork once, loops all hymns.
//
//   node jazz/fork_render.js <job.json>
//   job.json = { "outdir": "...", "items": [ { "slug", "abc", "staffwidth" }, ... ] }
//
// jsdom lives in ~/projects/hymnal/node_modules; invoke with NODE_PATH set there.
const fs = require('fs'), path = require('path'), os = require('os');
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><div id="p"></div>');
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;          // jsdom>=22: abcjs reads navigator
const abcjs = require(path.join(os.homedir(), 'projects/abcjsharp/dist/abcjs-basic.js'));

// --- middle-C alignment (verbatim from the practice app) ----------------------
// abcjs leaves a wide, uneven gap between the treble and bass staves. This pulls
// the bass staff up so middle C sits exactly halfway between them -- i.e. the
// middle-C ledger line gets the same vertical spacing as a real staff line.
// Pure path-string math (no getBBox/layout), so it runs under jsdom.
function shiftPathY(d, yFn) {
  const tokens = [];
  const re = /([MmLlHhVvCcSsQqTtAaZz])|(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)/g;
  let mm;
  while ((mm = re.exec(d)) !== null) tokens.push(mm[1] || mm[2]);
  const out = [];
  let i = 0, prevCmd = '';
  while (i < tokens.length) {
    const tok = tokens[i];
    if (/^[A-Za-z]$/.test(tok)) { out.push(tok); prevCmd = tok; i++; continue; }
    const cmd = prevCmd.toUpperCase();
    const isAbs = prevCmd === cmd;
    let stride, yIdxs;
    switch (cmd) {
      case 'M': case 'L': case 'T': stride = 2; yIdxs = [1]; break;
      case 'H': stride = 1; yIdxs = []; break;
      case 'V': stride = 1; yIdxs = [0]; break;
      case 'C': stride = 6; yIdxs = [1,3,5]; break;
      case 'S': case 'Q': stride = 4; yIdxs = [1,3]; break;
      case 'A': stride = 7; yIdxs = [6]; break;
      default: stride = 2; yIdxs = []; break;
    }
    const args = tokens.slice(i, i + stride).map(Number);
    if (args.length !== stride) break;
    if (isAbs) yIdxs.forEach(yi => { args[yi] = yFn(args[yi]); });
    args.forEach(n => out.push(+n.toFixed(4)));
    i += stride;
    if (prevCmd === 'M') prevCmd = 'L';
    else if (prevCmd === 'm') prevCmd = 'l';
  }
  return out.join(' ');
}

function alignMiddleC(scoreEl) {
  scoreEl.querySelectorAll('svg').forEach(svg => {
    const isStaffLinePath = p => {
      const d = p.getAttribute('d') || '';
      const m = d.match(/^M\s+\d+(?:\.\d+)?\s+(\d+(?:\.\d+)?)\s+L\s+\d+(?:\.\d+)?\s+(\d+(?:\.\d+)?)\s+L\s+\d+(?:\.\d+)?\s+(\d+(?:\.\d+)?)/);
      if (!m) return false;
      const y1 = +m[1], y2 = +m[2], y3 = +m[3];
      return y1 === y2 && Math.abs(y3 - y1) < 1.5;
    };
    const lineGroups = [];
    svg.querySelectorAll('g').forEach(g => {
      const ps = Array.from(g.children).filter(c => c.tagName.toLowerCase() === 'path');
      if (ps.length === 5 && ps.every(isStaffLinePath)) lineGroups.push(g);
    });
    if (lineGroups.length < 2) return;
    const yOf = p => parseFloat((p.getAttribute('d').match(/^M\s+\d+(?:\.\d+)?\s+(\d+(?:\.\d+)?)/) || [])[1]);
    const NS = 'http://www.w3.org/2000/svg';
    let totalDelta = 0;

    const firstLineD = lineGroups[0].children[0].getAttribute('d') || '';
    const staffOriginX = parseFloat((firstLineD.match(/^M\s+(\d+(?:\.\d+)?)/) || [])[1]) || 25;

    const matchVerticalRect = d => {
      const m = d.match(/^M\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*L\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*L\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*L\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)/);
      if (!m) return null;
      const x1 = +m[1], y1 = +m[2], x2 = +m[3], y2 = +m[4], x3 = +m[5];
      if (x1 !== x2 || Math.abs(x3 - x1) > 5) return null;
      return { x: x1, y1, y2, width: Math.abs(x3 - x1) };
    };
    const isStartBarline = p => {
      const r = matchVerticalRect(p.getAttribute('d') || '');
      if (!r) return false;
      return Math.abs(r.x - staffOriginX) < 2 && Math.abs(r.y2 - r.y1) > 30;
    };
    const thicken = (p, newWidth) => {
      const r = matchVerticalRect(p.getAttribute('d') || '');
      if (!r) return;
      const yt = Math.min(r.y1, r.y2), yb = Math.max(r.y1, r.y2);
      p.setAttribute('d',
        'M ' + r.x + ' ' + yb + ' L ' + r.x + ' ' + yt +
        ' L ' + (r.x + newWidth) + ' ' + yt +
        ' L ' + (r.x + newWidth) + ' ' + yb + ' z');
    };

    const jobs = [];
    for (let i = 0; i + 1 < lineGroups.length; i += 2) {
      const trebleLG = lineGroups[i], bassLG = lineGroups[i + 1];
      const parent = bassLG.parentNode;
      const siblings = Array.from(parent.children);
      const startIdx = siblings.indexOf(bassLG);
      let endIdx = siblings.length;
      if (i + 2 < lineGroups.length) {
        const nextTreble = lineGroups[i + 2];
        if (nextTreble.parentNode === parent) {
          const nIdx = siblings.indexOf(nextTreble);
          if (nIdx > startIdx) endIdx = nIdx;
        }
      }
      const toWrap = siblings.slice(startIdx, endIdx);
      const insertAt = siblings[endIdx] || null;
      const trebleYs = Array.from(trebleLG.children).map(yOf).filter(y => !isNaN(y)).sort((a,b)=>a-b);
      const bassYs   = Array.from(bassLG.children).map(yOf).filter(y => !isNaN(y)).sort((a,b)=>a-b);
      if (trebleYs.length < 5 || bassYs.length < 5) continue;
      const trebleBot = trebleYs[4], bassTop = bassYs[0];
      const lineSpacing = trebleYs[1] - trebleYs[0];
      const delta = (bassTop - trebleBot) - 2 * lineSpacing;
      if (delta < 0.01) continue;
      jobs.push({ parent, toWrap, insertAt, delta, threshold: (trebleBot + bassTop) / 2, trebleBot, bassTop });
    }

    const wrappers = [];
    jobs.forEach(job => {
      const toWrap = [];
      job.toWrap.forEach(el => {
        const dn = (el.getAttribute && el.getAttribute('data-name') || '').toLowerCase();
        if (dn === 'bar') {
          el.querySelectorAll('path').forEach(p => {
            const d = p.getAttribute('d') || '';
            p.setAttribute('d', shiftPathY(d, y => y >= job.threshold ? y - job.delta : y));
          });
          return;
        }
        if (el.tagName.toLowerCase() === 'path' && isStartBarline(el)) {
          thicken(el, 1.8);
          return;
        }
        toWrap.push(el);
      });
      const wrapper = svg.ownerDocument.createElementNS(NS, 'g');
      wrapper.setAttribute('transform', 'translate(0, ' + (-job.delta).toFixed(3) + ')');
      toWrap.forEach(el => wrapper.appendChild(el));
      job.parent.insertBefore(wrapper, job.insertAt);
      wrappers.push(wrapper);
      totalDelta += job.delta;
    });

    svg.querySelectorAll('path').forEach(p => {
      for (const w of wrappers) {
        let a = p.parentNode;
        while (a) { if (a === w) return; a = a.parentNode; }
      }
      let anc = p.parentNode;
      while (anc && anc.getAttribute) {
        if ((anc.getAttribute('data-name') || '').toLowerCase() === 'bar') return;
        anc = anc.parentNode;
      }
      const d = p.getAttribute('d') || '';
      const nums = (d.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
      if (!nums.length) return;
      const xs = [], ys = [];
      for (let i = 0; i < nums.length; i += 2) { xs.push(nums[i]); ys.push(nums[i + 1]); }
      const xmin = Math.min(...xs), xmax = Math.max(...xs);
      const ymin = Math.min(...ys), ymax = Math.max(...ys);
      const isBrace = /[Cc]/.test(d) && xmin < staffOriginX - 2 && xmax < staffOriginX + 12;
      const isStartBar = !isBrace && (xmax - xmin) < 5
        && Math.abs(xmin - staffOriginX) < 2 && (ymax - ymin) > 30;
      if (!isBrace && !isStartBar) return;
      for (const job of jobs) {
        if (ymin < job.threshold && ymax >= job.threshold
            && ymin > job.trebleBot - 100 && ymax < job.bassTop + 400) {
          if (isBrace) {
            const yRange = ymax - ymin;
            const scaleY = yRange > 0.01 ? (yRange - job.delta) / yRange : 1;
            p.setAttribute('transform',
              'translate(' + (staffOriginX - 2).toFixed(3) + ',' + ymin.toFixed(3) + ')'
              + ' scale(0.5,' + scaleY.toFixed(5) + ')'
              + ' translate(' + (-staffOriginX).toFixed(3) + ',' + (-ymin).toFixed(3) + ')');
          } else {
            p.setAttribute('d', shiftPathY(d, y => y >= job.threshold ? y - job.delta : y));
          }
          return;
        }
      }
    });

    const lastDelta = jobs.length > 0 ? jobs[jobs.length - 1].delta : 0;
    if (lastDelta > 0) {
      const h = parseFloat(svg.getAttribute('height') || '0');
      if (h > 0) svg.setAttribute('height', (h - lastDelta).toFixed(3));
      const vb = (svg.getAttribute('viewBox') || '').split(/\s+/).map(Number);
      if (vb.length === 4 && !isNaN(vb[3])) { vb[3] -= lastDelta; svg.setAttribute('viewBox', vb.join(' ')); }
    }
  });
}
// -----------------------------------------------------------------------------

const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const el = document.getElementById('p');
let ok = 0; const fail = [];
for (const it of job.items) {
  el.innerHTML = '';
  try {
    // No `wrap`. staffwidth (per hymn = bars/line * KERN) sets the note kerning:
    // abcjs justifies each row to it. Line breaks come from the source (one
    // [V:1]/[V:2] pair per system); fit-to-screen then scales the block up.
    abcjs.renderAbc(el, it.abc, { staffwidth: it.staffwidth || 900, oneSvgPerLine: false });
    alignMiddleC(el);                              // pull bass staff up; center middle C
    const svg = el.querySelector('svg');
    if (!svg) { fail.push(it.slug + ': no svg'); continue; }
    let s = svg.outerHTML.replace(/currentColor/g, '#11110d').replace(/\sstyle="[^"]*"/, '');
    if (!/xmlns="http:\/\/www\.w3\.org\/2000\/svg"/.test(s)) {
      s = s.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ');
    }
    if (!/viewBox=/.test(s)) {           // viewers scale by viewBox; add it from w/h
      const wm = /width="([\d.]+)"/.exec(s), hm = /height="([\d.]+)"/.exec(s);
      if (wm && hm) s = s.replace('<svg ', '<svg viewBox="0 0 ' + wm[1] + ' ' + hm[1] + '" ');
    }
    // it.out (e.g. "hymns/L1/slug.svg") overrides the default slug.svg path.
    const outPath = path.join(job.outdir, it.out || (it.slug + '.svg'));
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, s);
    ok++;
  } catch (e) { fail.push(it.slug + ': ' + e.message); }
}
console.log(JSON.stringify({ ok, fail }));
