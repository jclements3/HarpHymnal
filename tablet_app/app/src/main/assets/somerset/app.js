// HarpHymnal — Somerset (tablet tile, static-only).
//
// Mirrors the layout + behavior of tools/satb_to_harp/static/app.js (the
// Flask version), adapted to read pre-baked artifacts from local assets
// instead of hitting `/api/arrange` etc. The ABC textarea is readonly here
// — Somerset is a viewer, not an editor.
//
// Static reads use XMLHttpRequest, not fetch(): Android WebView blocks
// fetch() against file:// URLs even with setAllow*FileURLs(true).

const $ = (sel) => document.querySelector(sel);

const els = {
  input:    $('#hymn-input'),
  datalist: $('#hymn-list'),
  pattern:  $('#pattern-select'),
  arrange:  $('#arrange-btn'),
  play:     $('#play-btn'),
  stop:     $('#stop-btn'),
  home:     $('#home-btn'),
  status:   $('#status'),
  abc:      $('#abc-source'),
  score:    $('#score'),
  audits:   $('#audits-table tbody'),
  audio:    $('#midi-audio'),
};

let manifest = null;
let hymnsByLabel = new Map();
let hymnsByNumber = new Map();
let patternSlugByName = new Map();   // "Calypso" → "calypso"; "" → "default"

// ───────────────────────────────────────────────────────────────────────────
//   XHR helpers (fetch is blocked on file:// in Android WebView)
// ───────────────────────────────────────────────────────────────────────────
function xhrText(url) {
  return new Promise((resolve, reject) => {
    const x = new XMLHttpRequest();
    x.open('GET', url, true);
    x.responseType = 'text';
    x.onload = () => {
      const ok = x.status === 0 || (x.status >= 200 && x.status < 300);
      if (ok) resolve(x.responseText);
      else   reject(new Error('HTTP ' + x.status));
    };
    x.onerror = () => reject(new Error('network error'));
    x.send();
  });
}

// ───────────────────────────────────────────────────────────────────────────
//   abc2svg renderer
// ───────────────────────────────────────────────────────────────────────────
function renderABC(text) {
  els.score.innerHTML = '';
  if (!text || !text.trim()) return;
  if (typeof Abc !== 'function') {
    els.score.textContent = '(abc2svg not loaded)';
    return;
  }
  const chunks = [];
  try {
    const abc = new Abc({
      img_out(s) { chunks.push(s); },
      errmsg(msg, l, c) { console.warn('abc2svg:', msg, 'line', l, 'col', c); },
      read_file() { return ''; },
      anno_stop() {},
    });
    abc.tosvg('source.abc', text);
  } catch (e) {
    els.score.textContent = 'render error: ' + e.message;
    return;
  }
  els.score.innerHTML = chunks.join('\n');
}

// ───────────────────────────────────────────────────────────────────────────
//   Audits table
// ───────────────────────────────────────────────────────────────────────────
function setAudits(audits) {
  els.audits.innerHTML = '';
  if (!audits || !audits.length) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 3; td.style.color = '#888';
    td.textContent = '(no audits)';
    tr.appendChild(td); els.audits.appendChild(tr);
    return;
  }
  for (const a of audits) {
    const tr = document.createElement('tr');
    tr.classList.add('sev-' + (a.severity || 'warn'));
    const beat = document.createElement('td'); beat.textContent = a.beat ?? '';
    const sev  = document.createElement('td'); sev.textContent  = a.severity ?? '';
    const msg  = document.createElement('td'); msg.textContent  = a.message ?? '';
    tr.append(beat, sev, msg);
    els.audits.appendChild(tr);
  }
}

function status(msg, isError) {
  els.status.textContent = msg || '';
  els.status.classList.toggle('err', !!isError);
}

// ───────────────────────────────────────────────────────────────────────────
//   Bootstrap: load manifest, populate datalist + pattern dropdown
// ───────────────────────────────────────────────────────────────────────────
async function loadManifest() {
  try {
    const text = await xhrText('manifest.json');
    manifest = JSON.parse(text);
  } catch (e) {
    status('load manifest failed: ' + e.message, true);
    return;
  }

  // Hymns
  els.datalist.innerHTML = '';
  hymnsByLabel.clear(); hymnsByNumber.clear();
  for (const h of (manifest.hymns || [])) {
    const label = String(h.n).padStart(3, '0') + ' ' + h.title;
    const opt = document.createElement('option');
    opt.value = label;
    els.datalist.appendChild(opt);
    hymnsByLabel.set(label, h.title);
    hymnsByNumber.set(String(h.n).padStart(3, '0'), h.title);
  }
  els.input.placeholder =
    `type number or title (${(manifest.hymns || []).length} hymns)…`;

  // Patterns: empty value is "default" (no pattern); other entries come
  // from manifest.pattern_slugs (name → slug).
  patternSlugByName.clear();
  patternSlugByName.set('', 'default');
  const slugs = manifest.pattern_slugs || {};
  for (const [name, slug] of Object.entries(slugs)) {
    if (name === '__default__') continue;
    patternSlugByName.set(name, slug);
    const opt = document.createElement('option');
    opt.value = name; opt.textContent = name;
    els.pattern.appendChild(opt);
  }
}

function resolveHymnNumber(raw) {
  const v = (raw || '').trim();
  if (!v) return null;
  if (hymnsByLabel.has(v)) {
    return parseInt(v.slice(0, 3), 10);
  }
  if (/^\d{1,3}$/.test(v)) {
    const k = v.padStart(3, '0');
    if (hymnsByNumber.has(k)) return parseInt(k, 10);
  }
  const m = v.match(/^(\d{1,3})\s+/);
  if (m) {
    const k = m[1].padStart(3, '0');
    if (hymnsByNumber.has(k)) return parseInt(k, 10);
  }
  // Title substring (case-insensitive)
  const lv = v.toLowerCase();
  for (const [key, title] of hymnsByNumber.entries()) {
    if (title.toLowerCase().includes(lv)) return parseInt(key, 10);
  }
  return null;
}

// ───────────────────────────────────────────────────────────────────────────
//   Arrange (= load a pre-baked ABC)
// ───────────────────────────────────────────────────────────────────────────
async function arrange() {
  const n = resolveHymnNumber(els.input.value);
  if (n == null) { status('pick a hymn first', true); return; }
  const patName = els.pattern.value || '';
  const slug = patternSlugByName.get(patName) || 'default';
  const file = 'abc/' + String(n).padStart(3, '0') + '__' + slug + '.abc';

  status('loading ' + file + '…');
  els.arrange.disabled = true;
  try {
    const text = await xhrText(file);
    els.abc.value = text;
    renderABC(text);
    setAudits([]);  // pre-baked corpus stripped audits to keep manifest small
    const title = (hymnsByNumber.get(String(n).padStart(3, '0')) || '');
    status(String(n).padStart(3, '0') + ' ' + title +
           (patName ? ' · ' + patName : ' · default'));
  } catch (e) {
    status('load failed: ' + e.message, true);
    els.abc.value = '';
    els.score.innerHTML = '';
  } finally {
    els.arrange.disabled = false;
  }
}

// ───────────────────────────────────────────────────────────────────────────
//   Play / Stop  — in-browser via abc2svg's AbcPlay(). No server round-trip.
//   On Android WebView the default soundfont URL is unreachable offline; if
//   the synth fails we surface a status message rather than throwing.
// ───────────────────────────────────────────────────────────────────────────
let abcplay = null;
async function play() {
  const abc = els.abc.value;
  if (!abc.trim()) { status('no ABC to play', true); return; }
  if (typeof AbcPlay !== 'function') {
    status('audio engine not loaded', true); return;
  }
  status('preparing audio…');
  els.play.disabled = true;
  try {
    if (!abcplay) {
      abcplay = AbcPlay({
        onend: () => status('done'),
        errmsg: (m) => console.warn('AbcPlay:', m),
      });
    }
    abcplay.clear();
    const abc2 = new Abc({
      img_out() {},
      errmsg() {},
      read_file() { return ''; },
      anno_stop() {},
      get_abcmodel(tsfirst, voice_tb) { abcplay.add(tsfirst, voice_tb); },
    });
    abc2.tosvg('play.abc', abc);
    abcplay.play(0, -1);
    status('playing');
  } catch (e) {
    status('audio unavailable: ' + e.message, true);
  } finally {
    els.play.disabled = false;
  }
}

function stop() {
  try { if (abcplay) abcplay.stop(); } catch {}
  status('stopped');
}

// ───────────────────────────────────────────────────────────────────────────
//   Wire up
// ───────────────────────────────────────────────────────────────────────────
els.arrange.addEventListener('click', arrange);
els.play.addEventListener('click', play);
els.stop.addEventListener('click', stop);
els.home.addEventListener('click', () => { window.location.href = '../index.html'; });
els.pattern.addEventListener('change', arrange);
els.input.addEventListener('change', arrange);
els.input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') arrange();
});

window.addEventListener('DOMContentLoaded', async () => {
  await loadManifest();
  if (manifest) {
    els.input.value = '001';
    arrange();
  }
});
