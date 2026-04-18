/* Harp Trefoil — service worker
 *
 * Cache-first strategy for the viewer shell and everything under data/.
 * Bump CACHE_VERSION when app.html / app.css / app.js changes to force a
 * fresh install on next load.
 */
const CACHE_VERSION = 'harphymnal-v1';
const SHELL = [
  './',
  './index.html',
  './app.css',
  './app.js',
  './data/index.json',
];

self.addEventListener('install', (ev) => {
  ev.waitUntil(
    caches.open(CACHE_VERSION).then((cache) =>
      // addAll is atomic — bail silently if any shell item 404s.
      Promise.all(SHELL.map((url) =>
        cache.add(url).catch(() => null)
      ))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (ev) => {
  ev.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (ev) => {
  const req = ev.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  // Only handle same-origin GETs.
  if (url.origin !== self.location.origin) return;

  ev.respondWith(
    caches.open(CACHE_VERSION).then(async (cache) => {
      const hit = await cache.match(req);
      if (hit) {
        // Revalidate in the background for data/ and shell resources.
        fetch(req).then((r) => {
          if (r && r.ok) cache.put(req, r.clone()).catch(() => {});
        }).catch(() => {});
        return hit;
      }
      try {
        const resp = await fetch(req);
        if (resp && resp.ok && (
          url.pathname.startsWith('/data/')
          || url.pathname.endsWith('/data/index.json')
          || /\/data\//.test(url.pathname)
          || SHELL.some((s) => url.pathname.endsWith(s.replace(/^\.\//, '/')))
        )) {
          cache.put(req, resp.clone()).catch(() => {});
        }
        return resp;
      } catch (err) {
        // Offline and uncached — let the browser surface the failure.
        return new Response('', { status: 504, statusText: 'Offline' });
      }
    })
  );
});
