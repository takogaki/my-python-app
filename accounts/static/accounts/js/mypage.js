document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       📊 プログレスバー（既存）
    ========================= */
    document.querySelectorAll(".progress").forEach(el => {
        el.style.width = el.dataset.width + "%";
    });

    /* =========================
       🔔 通知リアルタイム
    ========================= */

    const socket = new WebSocket(
        (location.protocol === "https:" ? "wss://" : "ws://") +
        location.host +
        "/ws/notifications/"
    );

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data.type === "notification") {

            // 🔢 バッジ更新
            const badge = document.querySelector(".notification-count");

            if (badge) {
                badge.textContent = Number(badge.textContent || 0) + 1;
            }

            // 🔥 デバッグ（確認用）
            console.log("通知受信:", data);
        }
    };

    socket.onopen = () => {
        console.log("通知Socket接続OK");
    };

    socket.onerror = (err) => {
        console.error("Socketエラー:", err);
    };

    socket.onclose = () => {
        console.log("Socket切断");
    };

});