self.addEventListener('install', function(e) {
  console.log('Service Worker instalado');
});

self.addEventListener('fetch', function(e) {
  console.log('Fetch interceptado para:', e.request.url);
});