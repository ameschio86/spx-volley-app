const CACHE_NAME = 'spx-app-v1';

const APP_SHELL = [
  './',
  'index.html',
  'iscrizione.html',
  'iscrizione-prima-volta.html',
  'iscrizione-gia-atleta.html',
  'quote.html',
  'quote-pagamento.html',
  'materiale.html',
  'moduli.html',
  'faq.html',
  'css/style.css',
  'js/app.js',
  'manifest.json',
  'logo_nuovo_Giallo.png',
  'assets/icons/icon-192.png',
  'assets/icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

// Nessun dato sensibile passa da qui: solo pagine informative statiche.
// Le pagine HTML si aggiornano dalla rete quando possibile (network-first),
// gli asset statici (css/js/immagini) vengono serviti dalla cache (cache-first).
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const isHTML = event.request.mode === 'navigate' || event.request.headers.get('accept')?.includes('text/html');

  if (isHTML) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        })
        .catch(() => caches.match(event.request).then((cached) => cached || caches.match('index.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
