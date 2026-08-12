document.addEventListener("DOMContentLoaded", function () {

    const chatBox = document.getElementById("chat-box");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message-input");

    if (!chatBox) return;

    chatBox.scrollTop = chatBox.scrollHeight;

    const username = chatBox.dataset.username;
    const currentUser = chatBox.dataset.currentUser;

    chatBox.addEventListener("click", function (e) {
        const target = e.target.closest(".chat-avatar, .chat-username");
        if (!target) return;

        const url = target.dataset.url;
        if (!url) return;

        window.location.href = url;
    });

    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

    const socket = new WebSocket(
        protocol + window.location.host + "/ws/chat/" + username + "/"
    );

    // =========================
    // 🔥 WebSocket状態ログ
    // =========================
    socket.onopen = () => console.log("✅ WebSocket接続成功");
    socket.onerror = (e) => console.error("❌ WebSocketエラー", e);
    socket.onclose = () => console.log("🔌 WebSocket切断");

    // =========================
    // 💬 受信処理
    // =========================
    socket.onmessage = function (e) {

        const data = JSON.parse(e.data);

        // 🔥 通知は無視（重要）
        if (data.type === "notification") return;

        // 🔥 チャット以外も無視（安全設計）
        if (data.type !== "chat") return;

        const isMine = data.sender === currentUser;

        // =========================
        // 行
        // =========================
        const row = document.createElement("div");
        row.className = `chat-row ${isMine ? "my-row" : "other-row"}`;

        // =========================
        // アバター
        // =========================
        const avatar = document.createElement("img");
        avatar.src = data.image_url || "/static/accounts/img/default_avatar.png";
        avatar.className = "chat-avatar";

        // =========================
        // ユーザー名（先に作る）
        // =========================
        // ユーザー名
        const usernameEl = document.createElement("a");
        usernameEl.className = "chat-username";
        usernameEl.textContent = data.sender;
        usernameEl.href = "javascript:void(0);";

        // =========================
        // 🔥 遷移ロジック（共通化）
        // =========================
        // プロフィール遷移
        const goProfile = () => {
            if (data.sender === currentUser) {
                window.location.href = "/accounts/mypage/";
            } else {
                window.location.href = `/accounts/user/${data.sender}/`;
            }
        };

        // avatar
        avatar.addEventListener("click", goProfile);

        // username
        usernameEl.addEventListener("click", (e) => {
            e.preventDefault();
            goProfile();
        });

        // =========================
        // ラッパー
        // =========================
        const wrapper = document.createElement("div");
        wrapper.className = "chat-bubble-wrapper";

        // =========================
        // ユーザー名
        // =========================
        usernameEl.className = "chat-username";
        usernameEl.href = `/accounts/user/${data.sender}/`;
        usernameEl.textContent = data.sender;

        // =========================
        // バブル
        // =========================
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${isMine ? "my-bubble" : "other-bubble"}`;
        bubble.textContent = data.message;

        // =========================
        // メタ（時間＋既読）
        // =========================
        const meta = document.createElement("div");
        meta.className = "chat-meta";

        const time = document.createElement("span");
        time.className = "chat-time";

        if (data.sent_at) {
            const date = new Date(data.sent_at);
            time.textContent = date.toLocaleTimeString("ja-JP", {
                hour: "2-digit",
                minute: "2-digit",
                hour12: false
            });
        }

        meta.appendChild(time);

        if (isMine) {
            const read = document.createElement("span");

            if (data.is_read) {
                read.className = "read-status read";
                read.textContent = "既読";
            } else {
                read.className = "read-status unread";
                read.textContent = "未読";
            }

            meta.appendChild(read);
        }

        // =========================
        // DOM構築
        // =========================
        wrapper.appendChild(usernameEl);
        wrapper.appendChild(bubble);
        wrapper.appendChild(meta);

        row.appendChild(avatar);
        row.appendChild(wrapper);

        chatBox.appendChild(row);

        // スクロール最下部
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // =========================
    // 📤 送信
    // =========================
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const message = input.value.trim();
        if (!message) return;

        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ message }));
        } else {
            console.error("WebSocket未接続");
        }

        input.value = "";
    });

});

window.addEventListener("load", function () {
    const chatBox = document.getElementById("chat-box");
    if (!chatBox) return;

    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 100);
});

/* ==================================================
   📱 キーボード表示時のビューポート対応
================================================== */

(function () {

    const chatContainer =
        document.querySelector(".chat-container");

    if (!chatContainer) return;

    const updateChatViewport = () => {

        if (!window.visualViewport) return;

        const viewport = window.visualViewport;

        const headerHeight =
            parseFloat(
                getComputedStyle(document.documentElement)
                    .getPropertyValue("--chat-header-height")
            ) || 64;

        const footerHeight =
            parseFloat(
                getComputedStyle(document.documentElement)
                    .getPropertyValue("--footer-height")
            ) || 70;

        const visibleHeight =
            viewport.height
            - headerHeight
            - footerHeight;

        document.documentElement.style.setProperty(
            "--chat-visible-height",
            `${Math.max(visibleHeight, 200)}px`
        );
    };


    updateChatViewport();


    if (window.visualViewport) {

        window.visualViewport.addEventListener(
            "resize",
            updateChatViewport
        );

        window.visualViewport.addEventListener(
            "scroll",
            updateChatViewport
        );
    }

})();