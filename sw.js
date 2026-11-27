/* 피클마린트래킹 서비스 워커 (v3)
   - data/fleet.json : 네트워크 전용(캐시 우선 금지). 성공한 응답만 캐시에 남겨 오프라인 폴백으로만 사용
   - index.html(화면 이동) : 네트워크 우선 → 항상 최신 화면, 실패 시 캐시
   - 그 밖의 같은 출처 자산 : 네트워크 우선 + 캐시 폴백
   - 지도 타일·Leaflet CDN : 네트워크 우선 + 캐시 폴백 */
const VERSION = 'pickle-marine-v3';
const FLEET_CACHE_KEY = './data/fleet.json';
const SHELL = [
  './',
  './index.html',
  './manifest.json',
  './data/fleet.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/pickle-avatar.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(VERSION).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function isFleetRequest(url) {
  return /\/data\/fleet\.json$/.test(url.pathname);
}

function putCopy(request, response) {
  const copy = response.clone();
  caches.open(VERSION).then((c) => c.put(request, copy)).catch(() => {});
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;

  // 1) 선박 데이터: Network-Only (절대 캐시 우선으로 주지 않음) + 실패 시 캐시 폴백
  if (sameOrigin && isFleetRequest(url)) {
    event.respondWith(
      fetch(req, { cache: 'no-store' })
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(VERSION).then((c) => c.put(FLEET_CACHE_KEY, copy)).catch(() => {});
          }
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match(FLEET_CACHE_KEY)))
    );
    return;
  }

  // 2) 화면 이동: 네트워크 우선 → 최신 index.html, 오프라인이면 캐시
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put('./index.html', copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match('./index.html').then((r) => r || caches.match('./')))
    );
    return;
  }

  // 3) 같은 출처 정적 자산: 네트워크 우선(항상 최신), 실패 시 캐시
  if (sameOrigin) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // 4) 외부 리소스(지도 타일·Leaflet CDN): 네트워크 우선 + 캐시 폴백
  event.respondWith(
    fetch(req)
      .then((res) => {
        putCopy(req, res);
        return res;
      })
      .catch(() => caches.match(req))
  );
});
