// HarpHymnal SATB→Harp dev UI.
//
// Layout:
//   - hymn dropdown + Arrange + Play/Stop
//   - editable ABC textarea (left) | abc2svg rendered score (right)
//   - audits table at the bottom
//
// Playback strategy:
//   v1 = call /api/midi (server-side abc2midi) and feed the bytes into a
//   hidden <audio> element via a blob URL. Simple and robust.
//   (play-1.js / AbcPlay() is loaded so a future enhancement can call
//   abcplay.play() directly without a server round-trip.)

const $ = (sel) => document.querySelector(sel);

const els = {
  input:    $('#hymn-input'),
  datalist: $('#hymn-list'),
  pattern:  $('#pattern-select'),
  arrange:  $('#arrange-btn'),
  play:     $('#play-btn'),
  stop:     $('#stop-btn'),
  status:   $('#status'),
  abc:      $('#abc-source'),
  score:    $('#score'),
  audits:   $('#audits-table tbody'),
  audio:    $('#midi-audio'),
};

let hymnsByLabel = new Map();
let hymnsByNumber = new Map();

let currentMidiUrl = null;
let renderTimer = null;

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
  const userCb = {
    // abc2svg calls img_out(svg_string) one or more times.
    img_out(s) { chunks.push(s); },
    // Errors come through errmsg or err_msg depending on version.
    errmsg(msg, l, c) {
      console.warn('abc2svg:', msg, 'line', l, 'col', c);
    },
    read_file(fn) { return ''; },
    // get_abcmodel etc. left default.
    anno_stop() {},
  };
  try {
    const abc = new Abc(userCb);
    abc.tosvg('source.abc', text);
  } catch (e) {
    els.score.textContent = 'render error: ' + e.message;
    return;
  }
  els.score.innerHTML = chunks.join('\n');
}

function scheduleRender() {
  if (renderTimer) clearTimeout(renderTimer);
  renderTimer = setTimeout(() => renderABC(els.abc.value), 500);
}

// ───────────────────────────────────────────────────────────────────────────
//   Audits table
// ───────────────────────────────────────────────────────────────────────────
function setAudits(audits) {
  els.audits.innerHTML = '';
  if (!audits || !audits.length) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 3;
    td.style.color = '#888';
    td.textContent = '(no audits)';
    tr.appendChild(td);
    els.audits.appendChild(tr);
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
  els.status.style.color = isError ? '#ffd0d0' : '#fff';
}

// ───────────────────────────────────────────────────────────────────────────
//   Network
// ───────────────────────────────────────────────────────────────────────────
async function loadHymns() {
  try {
    const r = await fetch('/api/hymns');
    const j = await r.json();
    const hymns = j.hymns || [];
    els.datalist.innerHTML = '';
    hymnsByLabel.clear();
    hymnsByNumber.clear();
    for (const h of hymns) {
      const opt = document.createElement('option');
      opt.value = h.label;
      els.datalist.appendChild(opt);
      hymnsByLabel.set(h.label, h.title);
      hymnsByNumber.set(String(h.n).padStart(3, '0'), h.title);
    }
    els.input.placeholder = `type number or title (${hymns.length} hymns)…`;
  } catch (e) {
    status('load hymns failed: ' + e.message, true);
  }
}

function resolveTitle(raw) {
  const v = (raw || '').trim();
  if (!v) return '';
  if (hymnsByLabel.has(v)) return hymnsByLabel.get(v);
  // Bare 3-digit number (or 1-2 digit number) → look up by zero-padded.
  if (/^\d{1,3}$/.test(v)) {
    const k = v.padStart(3, '0');
    if (hymnsByNumber.has(k)) return hymnsByNumber.get(k);
  }
  // Otherwise treat as a raw title (also strip "NNN " prefix if present).
  const m = v.match(/^\d{3}\s+(.+)$/);
  return m ? m[1] : v;
}

async function loadPatterns() {
  try {
    const r = await fetch('/api/patterns');
    const j = await r.json();
    const patterns = j.patterns || [];
    for (const p of patterns) {
      const opt = document.createElement('option');
      opt.value = p; opt.textContent = p;
      els.pattern.appendChild(opt);
    }
  } catch (e) {
    console.warn('load patterns failed:', e);
  }
}

async function arrange() {
  const title = resolveTitle(els.input.value);
  const pattern = els.pattern.value || null;
  if (!title) { status('pick a hymn first', true); return; }
  status('arranging ' + title + '…');
  els.arrange.disabled = true;
  try {
    const r = await fetch('/api/arrange', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title, pattern}),
    });
    const j = await r.json();
    if (j.abc) {
      els.abc.value = j.abc;
      renderABC(j.abc);
      setAudits(j.audits || []);
      if (r.ok) {
        status(`arranged (${j.beats || 0} beats)`);
      } else if (j.fallback) {
        status('analyzer/consolidator not ready — serving fallback ABC', true);
      } else {
        status('server returned ' + r.status, true);
      }
    } else {
      const detail = j.error || ('HTTP ' + r.status);
      status('arrange failed: ' + detail, true);
      if (j.traceback) console.error(j.traceback);
    }
  } catch (e) {
    status('arrange failed: ' + e.message, true);
  } finally {
    els.arrange.disabled = false;
  }
}

async function play() {
  const abc = els.abc.value;
  if (!abc.trim()) { status('no ABC to play', true); return; }
  status('rendering audio…');
  els.play.disabled = true;
  try {
    const r = await fetch('/api/audio', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({abc}),
    });
    if (!r.ok) {
      let detail = 'HTTP ' + r.status;
      try { const j = await r.json(); detail = j.error || detail; } catch {}
      status('audio render failed: ' + detail, true);
      return;
    }
    const blob = await r.blob();
    if (currentMidiUrl) URL.revokeObjectURL(currentMidiUrl);
    currentMidiUrl = URL.createObjectURL(blob);
    els.audio.src = currentMidiUrl;
    els.audio.controls = true;
    els.audio.style.display = '';
    await els.audio.play();
    status('playing');
  } catch (e) {
    status('audio failed: ' + e.message, true);
  } finally {
    els.play.disabled = false;
  }
}

function stop() {
  try { els.audio.pause(); els.audio.currentTime = 0; } catch {}
  status('stopped');
}

// ───────────────────────────────────────────────────────────────────────────
//   Wire up
// ───────────────────────────────────────────────────────────────────────────
els.arrange.addEventListener('click', arrange);
els.play.addEventListener('click', play);
els.stop.addEventListener('click', stop);
els.abc.addEventListener('input', scheduleRender);
// Changing pattern re-arranges automatically — pick-and-listen feedback loop.
els.pattern.addEventListener('change', arrange);

window.addEventListener('DOMContentLoaded', async () => {
  await Promise.all([loadHymns(), loadPatterns()]);
  // Auto-arrange hymn 001 on page open.
  els.input.value = '001';
  arrange();
});
