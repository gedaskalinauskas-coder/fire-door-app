/* S B Fire Door App – service worker (offline app shell)
   © S B Fire Door App. All rights reserved. Licensed use only. See LICENSE.
   - Scope: this folder only (registered as ./sw.js with scope ./).
   - HTML: network first (updates show on the next open), cached copy only when offline.
   - Icons / manifest / logo: cache first, refreshed in the background.
   - Never touched: cross-origin requests, non-GET requests, door.html (public QR page),
     records/ (published client door records), and anything not in the list below.
   - Survey data lives in localStorage / IndexedDB and is never read or cached here.
   Bump VERSION whenever an app file changes so old caches are removed. */
const VERSION = 'sb-doors-v4';
const SHELL = [
  './', './index.html', './invite.html', './manifest.webmanifest',
  './icons/apple-touch-icon.png', './icons/favicon-32.png', './icons/favicon-16.png', './icons/favicon.ico',
  './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-192.png', './icons/icon-maskable-512.png',
  './icons/logo-wordmark.png'
];
const BASE = new URL('./', self.location).href;
const SHELL_URLS = new Set(SHELL.map(p => new URL(p, BASE).href));
const HTML_PAGES = new Set(['./', './index.html', './invite.html'].map(p => new URL(p, BASE).href));

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION)
    .then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' }))))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('sb-doors-') && k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

const withTimeout = (p, ms) => new Promise((res, rej) => { const t = setTimeout(() => rej(new Error('timeout')), ms); p.then(v => { clearTimeout(t); res(v) }, e => { clearTimeout(t); rej(e) }) });

async function networkFirst(req, key) {
  const cache = await caches.open(VERSION);
  const cached = await cache.match(key);
  const net = fetch(key, { cache: 'no-cache', credentials: 'same-origin' }).then(r => {
    if (r.ok && r.type === 'basic') cache.put(key, r.clone());
    return r;
  });
  try {
    // with a cached copy, don't leave the surveyor waiting on a weak signal
    return await (cached ? withTimeout(net, 4000) : net);
  } catch (err) {
    if (cached) return cached;
    throw err;
  }
}

async function cacheFirst(key) {
  const cache = await caches.open(VERSION);
  const cached = await cache.match(key);
  const net = fetch(key, { cache: 'no-cache' }).then(r => { if (r.ok && r.type === 'basic') cache.put(key, r.clone()); return r });
  if (cached) { net.catch(() => {}); return cached; }
  return net;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !url.href.startsWith(BASE)) return; // cross-origin / outside the app: browser default
  const key = url.origin + url.pathname;              // ignore ?query and #hash (index.html uses #/routes)
  if (HTML_PAGES.has(key)) { e.respondWith(networkFirst(req, key)); return; }
  if (SHELL_URLS.has(key)) { e.respondWith(cacheFirst(key)); return; }
  // everything else (door.html, records/, sw.js, robots.txt, ...) goes straight to the network, uncached
});
