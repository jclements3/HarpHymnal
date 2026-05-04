// abccomposer service worker.
//
// Strategy:
//   - HTML / navigation requests: network-first (fall back to cache offline).
//     This guarantees that pushing a new index.html lands on the next reload
//     without manual cache busts.
//   - Same-origin static assets (vendor/, icons, manifest): cache-first.
//   - Cross-origin (api.anthropic.com, CDNs): pass through entirely.
//   - Non-GET (the chat POST): pass through entirely.
//
// Bump CACHE_NAME on every release that ships changed app-shell files.
// activate() purges old caches.

const CACHE_NAME = "abccomposer-v2";
const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./vendor/codemirror.css",
  "./vendor/dracula.css",
  "./vendor/dialog.css",
  "./vendor/codemirror.js",
  "./vendor/vim.js",
  "./vendor/dialog.js",
  "./vendor/search.js",
  "./vendor/searchcursor.js",
  "./vendor/matchbrackets.js",
  "./vendor/abcjs-basic-min.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((c) => c.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;                    // POST to anthropic etc.
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;          // CDNs / api.anthropic.com pass through

  const accept = req.headers.get("accept") || "";
  const isNav = req.mode === "navigate" || accept.includes("text/html");

  if (isNav) {
    // Network-first for HTML so new releases land on next reload.
    e.respondWith(
      fetch(req).then((resp) => {
        const clone = resp.clone();
        caches.open(CACHE_NAME).then((c) => c.put(req, clone));
        return resp;
      }).catch(() => caches.match(req))
    );
    return;
  }

  // Cache-first for static same-origin assets.
  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((resp) => {
        if (resp.ok && /\.(css|js|webmanifest|png|svg|woff2?)$/.test(url.pathname)) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then((c) => c.put(req, clone));
        }
        return resp;
      });
    })
  );
});
