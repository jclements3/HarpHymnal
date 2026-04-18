/* Harp Trefoil — tablet viewer
 *
 * Single-page, no framework. Loads data/index.json, builds the left nav
 * (hymns + drills), swaps the right pane on selection. Uses pushState for
 * shareable URLs. Registers a cache-first service worker for offline use.
 */
(function () {
  'use strict';

  // ───────────────────────── helpers ──────────────────────────
  const $  = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  const el = (tag, attrs, ...children) => {
    const n = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v == null || v === false) continue;
        if (k === 'class') n.className = v;
        else if (k === 'text') n.textContent = v;
        else if (k.startsWith('on') && typeof v === 'function') {
          n.addEventListener(k.slice(2), v);
        } else if (k === 'dataset') {
          for (const [dk, dv] of Object.entries(v)) n.dataset[dk] = dv;
        } else if (v === true) {
          n.setAttribute(k, '');
        } else {
          n.setAttribute(k, v);
        }
      }
    }
    for (const c of children) {
      if (c == null) continue;
      n.append(c.nodeType ? c : document.createTextNode(String(c)));
    }
    return n;
  };

  const letterBucket = (title) => {
    const ch = (title || '').trim().charAt(0).toUpperCase();
    return /[A-Z]/.test(ch) ? ch : '#';
  };

  const headOk = (url) =>
    fetch(url, { method: 'HEAD' }).then(r => r.ok).catch(() => false);

  // ───────────────────────── state ────────────────────────────
  const state = {
    manifest: { hymns: [], drills: [] },
    hymnsBySlug: new Map(),
    drillsBySlug: new Map(),
    current: null, // {kind:'hymn'|'drill', slug:string}
  };

  // ────────────────────────── main ────────────────────────────
  document.addEventListener('DOMContentLoaded', boot);

  async function boot() {
    wireChrome();
    try {
      state.manifest = await loadIndex();
    } catch (err) {
      console.warn('index.json not found — showing empty state', err);
      state.manifest = { hymns: [], drills: [] };
    }
    indexManifest(state.manifest);
    renderNav(state.manifest);
    const initial = routeFromLocation();
    if (initial) {
      activate(initial.kind, initial.slug, { push: false });
    } else {
      showView('welcome');
    }
    registerSW();
  }

  async function loadIndex() {
    const res = await fetch('data/index.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error('index.json status ' + res.status);
    return res.json();
  }

  function indexManifest(m) {
    state.hymnsBySlug.clear();
    (m.hymns || []).forEach(h => state.hymnsBySlug.set(h.slug, h));
    state.drillsBySlug.clear();
    (m.drills || []).forEach(d => state.drillsBySlug.set(d.slug, d));
  }

  // ───────────────────────── chrome ───────────────────────────
  function wireChrome() {
    const toggle = $('#nav-toggle');
    const nav    = $('#nav');
    const scrim  = $('#nav-scrim');

    function closeDrawer() {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      scrim.hidden = true;
    }
    function openDrawer() {
      nav.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      scrim.hidden = false;
    }
    toggle.addEventListener('click', () => {
      if (nav.classList.contains('is-open')) closeDrawer();
      else openDrawer();
    });
    scrim.addEventListener('click', closeDrawer);
    // Close the drawer when window widens past the breakpoint.
    const mq = window.matchMedia('(min-width: 768px)');
    mq.addEventListener ? mq.addEventListener('change', e => e.matches && closeDrawer())
                        : mq.addListener(e => e.matches && closeDrawer());

    // Section-level collapses (Hymns / Drills).
    $$('.nav-section-toggle').forEach(btn => {
      btn.addEventListener('click', () => {
        const body = $('#' + btn.getAttribute('aria-controls'));
        const open = btn.getAttribute('aria-expanded') !== 'true';
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (body) body.hidden = !open;
      });
    });

    window.addEventListener('popstate', () => {
      const r = routeFromLocation();
      if (r) activate(r.kind, r.slug, { push: false });
      else showView('welcome');
    });
  }

  // ───────────────────────── routing ──────────────────────────
  function routeFromLocation() {
    const h = window.location.hash || '';
    // #hymn/<slug> or #drill/<technique_slug>/<path_slug>
    const m = h.match(/^#(hymn|drill)\/(.+)$/);
    if (!m) return null;
    return { kind: m[1], slug: decodeURIComponent(m[2]) };
  }

  function pushRoute(kind, slug) {
    const hash = '#' + kind + '/' + slug;
    if (window.location.hash !== hash) {
      history.pushState({ kind, slug }, '', hash);
    }
  }

  // ───────────────────────── nav render ───────────────────────
  function renderNav(manifest) {
    renderHymnNav(manifest.hymns || []);
    renderDrillNav(manifest.drills || []);
  }

  function renderHymnNav(hymns) {
    const body  = $('#hymn-list');
    const empty = $('#hymn-empty');
    const count = $('#hymn-count');
    count.textContent = hymns.length;

    // clear previous (keep the empty-state paragraph for reuse)
    Array.from(body.children).forEach(c => { if (c !== empty) c.remove(); });

    if (hymns.length === 0) {
      empty.hidden = false;
      return;
    }
    empty.hidden = true;

    const buckets = new Map();
    for (const h of hymns) {
      const k = letterBucket(h.title);
      if (!buckets.has(k)) buckets.set(k, []);
      buckets.get(k).push(h);
    }
    const letters = Array.from(buckets.keys()).sort();
    for (const L of letters) {
      const items = buckets.get(L);
      const head = el('button', {
        class: 'alpha-group-head',
        type: 'button',
        'aria-expanded': 'false',
      },
        el('span', { class: 'chev', 'aria-hidden': 'true' }),
        el('span', { class: 'label' }, L),
        el('span', { class: 'count' }, items.length),
      );
      const ul = el('div', { class: 'alpha-group-body', hidden: true });
      for (const h of items) {
        ul.append(el('button', {
          class: 'nav-item hymn-item',
          type: 'button',
          dataset: { slug: h.slug },
          onclick: () => activate('hymn', h.slug, { push: true }),
        }, h.title));
      }
      head.addEventListener('click', () => {
        const open = head.getAttribute('aria-expanded') !== 'true';
        head.setAttribute('aria-expanded', open ? 'true' : 'false');
        ul.hidden = !open;
      });
      body.append(el('div', { class: 'alpha-group' }, head, ul));
    }
  }

  function renderDrillNav(drills) {
    const body  = $('#drill-list');
    const empty = $('#drill-empty');
    const count = $('#drill-count');
    count.textContent = drills.length;

    Array.from(body.children).forEach(c => { if (c !== empty) c.remove(); });

    if (drills.length === 0) {
      empty.hidden = false;
      return;
    }
    empty.hidden = true;

    // Group by top-level tag (Substitution / Approach / Voicing / Placement)
    // via a lookup on the technique label.  Fall back to the technique
    // itself when we can't classify.
    const TAG = {
      'Third sub':'Substitution','Quality sub':'Substitution',
      'Modal reframing':'Substitution','Deceptive sub':'Substitution',
      'Common-tone pivot':'Substitution',
      'Step approach':'Approach','Third approach':'Approach',
      'Dominant approach':'Approach','Suspension approach':'Approach',
      'Double approach':'Approach',
      'Inversion':'Voicing','Density':'Voicing','Stacking':'Voicing',
      'Pedal':'Voicing','Voice leading':'Voicing','Open/closed spread':'Voicing',
      'Anticipation':'Placement','Delay':'Placement',
    };
    const TAG_ORDER = ['Substitution','Approach','Voicing','Placement'];

    // bucket → technique → [drills]
    const byTag = new Map();
    for (const d of drills) {
      const tag = TAG[d.technique] || 'Other';
      if (!byTag.has(tag)) byTag.set(tag, new Map());
      const tMap = byTag.get(tag);
      if (!tMap.has(d.technique)) tMap.set(d.technique, []);
      tMap.get(d.technique).push(d);
    }

    const tags = Array.from(byTag.keys()).sort((a, b) => {
      const ia = TAG_ORDER.indexOf(a), ib = TAG_ORDER.indexOf(b);
      return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    });

    for (const tag of tags) {
      const tagMap = byTag.get(tag);
      const tagHead = el('button', {
        class: 'alpha-group-head',
        type: 'button',
        'aria-expanded': 'false',
      },
        el('span', { class: 'chev', 'aria-hidden': 'true' }),
        el('span', { class: 'label' }, tag),
        el('span', { class: 'count' },
          Array.from(tagMap.values()).reduce((n, a) => n + a.length, 0)),
      );
      const tagBody = el('div', { class: 'alpha-group-body', hidden: true });
      tagHead.addEventListener('click', () => {
        const open = tagHead.getAttribute('aria-expanded') !== 'true';
        tagHead.setAttribute('aria-expanded', open ? 'true' : 'false');
        tagBody.hidden = !open;
      });

      const techniques = Array.from(tagMap.keys()).sort();
      for (const tech of techniques) {
        const items = tagMap.get(tech);
        const tHead = el('button', {
          class: 'drill-technique-head',
          type: 'button',
          'aria-expanded': 'false',
        },
          el('span', { class: 'chev', 'aria-hidden': 'true' }),
          el('span', { class: 'label' }, tech),
          el('span', { class: 'count' }, items.length),
        );
        const tBody = el('div', { class: 'drill-technique-body', hidden: true });
        tHead.addEventListener('click', () => {
          const open = tHead.getAttribute('aria-expanded') !== 'true';
          tHead.setAttribute('aria-expanded', open ? 'true' : 'false');
          tBody.hidden = !open;
        });
        for (const d of items) {
          tBody.append(el('button', {
            class: 'nav-item drill-item',
            type: 'button',
            dataset: { slug: d.slug },
            onclick: () => activate('drill', d.slug, { push: true }),
          }, d.path));
        }
        tagBody.append(el('div', { class: 'drill-technique' }, tHead, tBody));
      }

      body.append(el('div', { class: 'alpha-group' }, tagHead, tagBody));
    }
  }

  // ───────────────────────── activation ───────────────────────
  function activate(kind, slug, opts) {
    const push = opts && opts.push;
    state.current = { kind, slug };

    // highlight
    $$('.nav-item.is-current').forEach(n => n.classList.remove('is-current'));
    const selector = (kind === 'hymn' ? '.hymn-item' : '.drill-item');
    const node = $$(selector).find(n => n.dataset.slug === slug);
    if (node) {
      node.classList.add('is-current');
      // Open any ancestor collapsible sections so the highlight is visible.
      for (let p = node.parentElement; p; p = p.parentElement) {
        if (p.classList && p.classList.contains('alpha-group-body')) {
          p.hidden = false;
          const head = p.previousElementSibling;
          if (head) head.setAttribute('aria-expanded', 'true');
        }
        if (p.classList && p.classList.contains('drill-technique-body')) {
          p.hidden = false;
          const head = p.previousElementSibling;
          if (head) head.setAttribute('aria-expanded', 'true');
        }
      }
    }

    // Close mobile drawer after selection.
    const nav = $('#nav');
    if (nav.classList.contains('is-open')) {
      nav.classList.remove('is-open');
      $('#nav-toggle').setAttribute('aria-expanded', 'false');
      $('#nav-scrim').hidden = true;
    }

    if (push) pushRoute(kind, slug);

    if (kind === 'hymn') showHymn(slug);
    else if (kind === 'drill') showDrill(slug);
    else showView('welcome');
  }

  function showView(which) {
    $('#view-welcome').hidden = which !== 'welcome';
    $('#view-hymn').hidden    = which !== 'hymn';
    $('#view-drill').hidden   = which !== 'drill';
    const stage = $('#stage'); stage.scrollTop = 0;
  }

  // ───────────────────────── hymn view ────────────────────────
  async function showHymn(slug) {
    showView('hymn');
    const info = state.hymnsBySlug.get(slug) || { slug, title: slug, key: '', meter: '' };
    $('#hymn-title').textContent = info.title || slug;
    const meta = [info.key, info.meter].filter(Boolean).join(' · ');
    $('#hymn-meta').textContent = meta;

    const img       = $('#score-img');
    const fallback  = $('#score-fallback');
    const midiLink  = $('#midi-link');
    const midiAudio = $('#midi-audio');

    const svgUrl  = 'data/scores/' + encodeURIComponent(slug) + '.svg';
    const midiUrl = 'data/scores/' + encodeURIComponent(slug) + '.midi';

    img.hidden = true; fallback.hidden = true;
    midiLink.hidden = true; midiAudio.hidden = true;

    const [hasSvg, hasMidi] = await Promise.all([headOk(svgUrl), headOk(midiUrl)]);

    if (hasSvg) {
      img.src = svgUrl;
      img.alt = info.title || slug;
      img.hidden = false;
    } else {
      fallback.hidden = false;
    }

    if (hasMidi) {
      midiLink.href = midiUrl;
      midiLink.setAttribute('download', slug + '.midi');
      midiLink.hidden = false;
      // Some browsers can play MIDI in <audio>; show the element as a
      // progressive enhancement for those that do.
      midiAudio.src = midiUrl;
      // Keep <audio> hidden by default; the download link is the reliable
      // cross-tablet fallback.  Uncomment the next line to expose it.
      // midiAudio.hidden = false;
    }
  }

  // ───────────────────────── drill view ───────────────────────
  async function showDrill(slug) {
    showView('drill');
    const info = state.drillsBySlug.get(slug)
              || { technique: '', path: '', slug, steps_count: 0 };
    $('#drill-title').textContent = [info.technique, info.path].filter(Boolean).join(' — ')
                                   || slug;
    $('#drill-meta').textContent  = info.steps_count
      ? (info.steps_count + ' step' + (info.steps_count === 1 ? '' : 's'))
      : '';

    const body = $('#drill-body');
    const fallback = $('#drill-fallback');
    body.innerHTML = ''; fallback.hidden = true;

    let payload = null;
    try {
      const res = await fetch('data/drills/' + slug + '.json', { cache: 'no-cache' });
      if (res.ok) payload = await res.json();
    } catch (_) { /* swallow */ }

    const steps = (payload && Array.isArray(payload.steps)) ? payload.steps : [];
    if (steps.length === 0) {
      fallback.hidden = false;
      return;
    }

    steps.forEach((s, i) => {
      const tr = el('tr',
        null,
        el('td', { class: 'step' }, String(i + 1)),
        el('td', { class: 'abc' }, s.abc || ''),
        el('td', { class: 'cmt' }, s.comment || ''),
      );
      body.append(tr);
    });
  }

  // ─────────────────────── service worker ─────────────────────
  function registerSW() {
    if (!('serviceWorker' in navigator)) return;
    // Only register over http(s); file:// cannot host a SW.
    if (!/^https?:/.test(window.location.protocol)) return;
    navigator.serviceWorker.register('sw.js').catch(err => {
      console.info('service worker registration skipped:', err.message);
    });
  }
})();
