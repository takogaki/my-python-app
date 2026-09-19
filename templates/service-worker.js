// ==============================
// SPIRYTUS Service Worker
// ==============================

self.addEventListener("install", event => {
    console.log("SPIRYTUS Service Worker installed");

    // 新しいService Workerをすぐに有効化
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("SPIRYTUS Service Worker activated");

    // 開いているページをすぐに制御
    event.waitUntil(
        self.clients.claim()
    );
});

self.addEventListener("fetch", event => {
    // 現時点では通常のネットワーク通信を使用
});