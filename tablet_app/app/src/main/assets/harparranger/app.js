// HarpHymnal — SATB → Pedal-Harp Arranger (tablet tile, static-only).
//
// Reads `manifest.json` + pre-baked `abc/<NNN>__<pattern_slug>.abc` files
// produced by `python3 -m tools.satb_to_harp.bake_all`. Renders score via
// abc2svg. Playback is delegated to the Composer tile (sharing the WebView's
// localStorage), which has its own bundled audio synth.

const $ = (s) => document.querySelector(s);
const els = {
  status:    $("#status"),
  hymnInput: $("#hymn-input"),
  hymnList:  $("#hymn-list"),
  pattern:   $("#pattern-select"),
  prev:      $("#prev-btn"),
  next:      $("#next-btn"),
  compose:   $("#compose-btn"),
  home:      $("#home-btn"),
  score:     $("#score"),
  abc:       $("#abc-source"),
};

const state = {
  manifest: null,
  hymnsByLabel: new Map(),    // "001 Title" → n
  hymnsByN:     new Map(),    // 1 → title
  patternSlug:  new Map(),    // pattern name (or "__default__") → slug
  patternNames: [],           // ordered, first is "__default__"
  currentN: null,
};

// ──────────────────────────────────────────────────────────────────────────
//   Status
// ──────────────────────────────────────────────────────────────────────────
function status(msg, isErr) {
  els.status.textContent = msg || "";
  els.status.classList.toggle("err", !!isErr);
}

// ──────────────────────────────────────────────────────────────────────────
//   Manifest load
// ──────────────────────────────────────────────────────────────────────────
async function loadManifest() {
  const r = await fetch("manifest.json", { cache: "no-cache" });
  if (!r.ok) throw new Error("manifest.json: HTTP " + r.status);
  const m = await r.json();
  state.manifest = m;

  // Hymns: build the datalist + lookup maps.
  els.hymnList.innerHTML = "";
  state.hymnsByLabel.clear();
  state.hymnsByN.clear();
  for (const h of m.hymns) {
    const label = String(h.n).padStart(3, "0") + " " + h.title;
    const opt = document.createElement("option");
    opt.value = label;
    els.hymnList.appendChild(opt);
    state.hymnsByLabel.set(label, h.n);
    state.hymnsByN.set(h.n, h.title);
  }

  // Patterns: dropdown options + slug lookup.
  state.patternNames = [];
  state.patternSlug.clear();
  // Default goes first.
  state.patternNames.push("__default__");
  state.patternSlug.set("__default__", "default");
  // existing default option already in the HTML
  for (const [k, slug] of Object.entries(m.pattern_slugs || {})) {
    if (k === "__default__") continue;
    state.patternNames.push(k);
    state.patternSlug.set(k, slug);
    const opt = document.createElement("option");
    opt.value = k; opt.textContent = k;
    els.pattern.appendChild(opt);
  }
}

// ──────────────────────────────────────────────────────────────────────────
//   Resolve free-text input to a hymn number
// ──────────────────────────────────────────────────────────────────────────
function resolveN(raw) {
  const v = (raw || "").trim();
  if (!v) return null;
  if (state.hymnsByLabel.has(v)) return state.hymnsByLabel.get(v);
  // bare digits → zero-pad and find by label prefix
  if (/^\d{1,3}$/.test(v)) {
    const n = parseInt(v, 10);
    if (state.hymnsByN.has(n)) return n;
  }
  // strip leading "NNN "
  const m = v.match(/^(\d{1,3})\s+/);
  if (m) {
    const n = parseInt(m[1], 10);
    if (state.hymnsByN.has(n)) return n;
  }
  // title substring (case-insensitive)
  const lv = v.toLowerCase();
  for (const [n, title] of state.hymnsByN.entries()) {
    if (title.toLowerCase().includes(lv)) return n;
  }
  return null;
}

// ──────────────────────────────────────────────────────────────────────────
//   abc2svg render
// ──────────────────────────────────────────────────────────────────────────
function renderScore(text) {
  els.score.innerHTML = "";
  if (!text || !text.trim()) return;
  if (typeof Abc !== "function") {
    els.score.textContent = "(abc2svg not loaded)";
    return;
  }
  const chunks = [];
  try {
    const abc = new Abc({
      img_out(s) { chunks.push(s); },
      errmsg(msg, l, c) { console.warn("abc2svg:", msg, "line", l, "col", c); },
      read_file() { return ""; },
      anno_stop() {},
    });
    abc.tosvg("source.abc", text);
  } catch (e) {
    els.score.textContent = "render error: " + e.message;
    return;
  }
  els.score.innerHTML = chunks.join("\n");
}

// ──────────────────────────────────────────────────────────────────────────
//   Fetch + display one arrangement
// ──────────────────────────────────────────────────────────────────────────
async function show() {
  const n = state.currentN;
  if (!n) { status("pick a hymn", true); return; }
  const patName = els.pattern.value || "__default__";
  const slug = state.patternSlug.get(patName) || "default";
  const file = "abc/" + String(n).padStart(3, "0") + "__" + slug + ".abc";
  status("loading " + file + "…");
  try {
    const r = await fetch(file, { cache: "force-cache" });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const text = await r.text();
    els.abc.value = text;
    renderScore(text);
    const title = state.hymnsByN.get(n) || "";
    const pat = patName === "__default__" ? "default" : patName;
    status(String(n).padStart(3, "0") + " " + title + " · " + pat);
  } catch (e) {
    status("load failed: " + e.message, true);
    els.abc.value = "";
    els.score.innerHTML = "";
  }
}

// ──────────────────────────────────────────────────────────────────────────
//   Open the current ABC inside the Composer tile (shared localStorage).
// ──────────────────────────────────────────────────────────────────────────
function openInComposer() {
  if (!els.abc.value.trim()) { status("nothing to open", true); return; }
  const n = state.currentN;
  const title = state.hymnsByN.get(n) || "untitled";
  const slug = (title.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "").toLowerCase()
                || "untitled");
  const pat = els.pattern.value || "__default__";
  const patSlug = state.patternSlug.get(pat) || "default";
  const fname = String(n).padStart(3, "0") + "_" + slug + "__" + patSlug + ".abc";
  try {
    localStorage.setItem("abccomposer.abc", els.abc.value);
    localStorage.setItem("abccomposer.filename", fname);
  } catch (e) {
    status("localStorage write failed: " + e.message, true);
    return;
  }
  window.location.href = "../abccomposer/index.html";
}

// ──────────────────────────────────────────────────────────────────────────
//   Wire up
// ──────────────────────────────────────────────────────────────────────────
function pickHymn() {
  const n = resolveN(els.hymnInput.value);
  if (n == null) { status("hymn not found", true); return; }
  state.currentN = n;
  show();
}

els.hymnInput.addEventListener("change", pickHymn);
els.hymnInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") pickHymn();
});
els.pattern.addEventListener("change", show);
els.prev.addEventListener("click", () => {
  if (state.currentN && state.currentN > 1) {
    state.currentN -= 1;
    els.hymnInput.value = String(state.currentN).padStart(3, "0") + " " +
                          state.hymnsByN.get(state.currentN);
    show();
  }
});
els.next.addEventListener("click", () => {
  const max = state.manifest ? state.manifest.hymns.length : 0;
  if (state.currentN && state.currentN < max) {
    state.currentN += 1;
    els.hymnInput.value = String(state.currentN).padStart(3, "0") + " " +
                          state.hymnsByN.get(state.currentN);
    show();
  }
});
els.compose.addEventListener("click", openInComposer);
els.home.addEventListener("click", () => { window.location.href = "../index.html"; });

window.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadManifest();
    status("ready — " + state.manifest.hymns.length + " hymns × " +
           state.patternNames.length + " variants");
    state.currentN = 1;
    els.hymnInput.value = "001 " + state.hymnsByN.get(1);
    show();
  } catch (e) {
    status("init failed: " + e.message, true);
  }
});
