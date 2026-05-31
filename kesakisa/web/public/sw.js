const CACHE_NAME = 'kesakisa-2026-v3'
const APP_SHELL = ['/kesakisa/', '/kesakisa/admin/', '/kesakisa/manifest.webmanifest', '/kesakisa/icon.svg']

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') {
    return
  }

  const requestUrl = new URL(event.request.url)

  if (requestUrl.pathname.startsWith('/kesakisa/api')) {
    return
  }

  const shouldPreferNetwork = event.request.mode === 'navigate' || APP_SHELL.includes(requestUrl.pathname)

  if (shouldPreferNetwork) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const responseClone = response.clone()
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone))
          return response
        })
        .catch(() => caches.match(event.request))
    )
    return
  }

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) {
        return cached
      }

      return fetch(event.request).then(response => {
        if (requestUrl.origin === self.location.origin && requestUrl.pathname.startsWith('/kesakisa/')) {
          const responseClone = response.clone()
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone))
        }

        return response
      })
    })
  )
})
