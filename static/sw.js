// Service Worker for Helmex Task Management PWA
const CACHE_NAME = 'helmex-tasks-v1.0.0';
const urlsToCache = [
    '/',
    '/static/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
    'https://code.jquery.com/jquery-3.6.0.min.js'
];

// Install event - cache resources
self.addEventListener('install', event => {
    console.log('SW: Install event');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('SW: Caching app shell');
                return cache.addAll(urlsToCache);
            })
            .catch(error => {
                console.log('SW: Cache failed', error);
            })
    );
});

// Activate event - clean old caches
self.addEventListener('activate', event => {
    console.log('SW: Activate event');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('SW: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip chrome-extension and dev server requests
    if (event.request.url.startsWith('chrome-extension://') || 
        event.request.url.includes('hot-update')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                if (response) {
                    console.log('SW: Serving from cache', event.request.url);
                    return response;
                }

                console.log('SW: Fetching from network', event.request.url);
                return fetch(event.request)
                    .then(response => {
                        // Check if we received a valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response for caching
                        const responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then(cache => {
                                // Only cache certain types of requests
                                if (event.request.url.startsWith('http')) {
                                    cache.put(event.request, responseToCache);
                                }
                            });

                        return response;
                    })
                    .catch(error => {
                        console.log('SW: Fetch failed', error);
                        
                        // Return offline page for navigation requests
                        if (event.request.destination === 'document') {
                            return caches.match('/');
                        }
                        
                        throw error;
                    });
            })
    );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
    console.log('SW: Background sync', event.tag);
    
    if (event.tag === 'sync-tasks') {
        event.waitUntil(syncTasks());
    }
});

// Push notifications
self.addEventListener('push', event => {
    console.log('SW: Push received', event);
    
    const options = {
        body: event.data ? event.data.text() : 'Yeni görev bildirimi',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Görevi Aç',
                icon: '/static/icons/icon-72x72.png'
            },
            {
                action: 'close',
                title: 'Kapat',
                icon: '/static/icons/icon-72x72.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Helmex Görev Yönetimi', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
    console.log('SW: Notification click', event);
    
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Sync tasks function
async function syncTasks() {
    try {
        // Sync logic would go here
        console.log('SW: Syncing tasks...');
        return Promise.resolve();
    } catch (error) {
        console.log('SW: Sync failed', error);
        throw error;
    }
}
