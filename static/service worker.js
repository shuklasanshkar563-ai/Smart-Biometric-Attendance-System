/**
 * BioAttend - Service Worker
 * Handles caching for offline support
 */

const CACHE_NAME = 'bioattend-v1';

const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/js/pwa-install.js',
  '/manifest.json',
  '/login',
  '/parent-view'
];

// ---- Install: cache static assets ----
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// ---- Activate: clean old caches ----
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// ---- Fetch: network-first with cache fallback ----
self.addEventListener('fetch', event => {
  const { request } = event;

  // Skip non-GET requests and API calls
  if (request.method !== 'GET') return;
  if (request.url.includes('/api/') || request.url.includes('/export-')) return;

  event.respondWith(
    fetch(request)
      .then(response => {
        // Cache successful responses for static files
        if (response.ok && (
          request.url.includes('/static/') ||
          request.url === '/' ||
          request.url.includes('/login') ||
          request.url.includes('/parent-view')
        )) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => {
        // Return cached version if available
        return caches.match(request).then(cached => {
          if (cached) return cached;
          // Return offline fallback for navigation requests
          if (request.mode === 'navigate') {
            return new Response(
              `<!DOCTYPE html>
              <html>
              <head><title>Offline - BioAttend</title>
              <style>
                body { font-family: sans-serif; display: flex; align-items: center; justify-content: center;
                       min-height: 100vh; background: #f8fafc; margin: 0; }
                .box { text-align: center; padding: 2rem; }
                h1 { color: #4f46e5; } p { color: #6b7280; }
                a { color: #4f46e5; }
              </style></head>
              <body>
                <div class="box">
                  <h1>📵 You're Offline</h1>
                  <p>Please check your internet connection and try again.</p>
                  <a href="/">Try Again</a>
                </div>
              </body>
              </html>`,
              { headers: { 'Content-Type': 'text/html' } }
            );
          }
        });
      })
  );
});
