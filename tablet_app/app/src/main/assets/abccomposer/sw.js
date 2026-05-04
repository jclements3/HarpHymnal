// abccomposer service worker — cache-first for the app shell, pass-through
// for everything else (notably api.anthropic.com so chat works online).
//
// Bump CACHE_NAME on every release that ships changed app-shell files;
// activate() purges old caches.

const CACHE_NAME = "abccomposer-v1";
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
  if (url.origin !== location.origin) return;           // CDNs / api.anthropic.com pass through

  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((resp) => {
        // Opportunistically cache app-shell-shaped GETs that succeeded.
        if (resp.ok && /\.(html|css|js|webmanifest|png|svg|woff2?)$/.test(url.pathname)) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then((c) => c.put(req, clone));
        }
        return resp;
      });
    })
  );
});
