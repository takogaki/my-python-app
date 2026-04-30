document.addEventListener("DOMContentLoaded", function () {

    const chatBox = document.getElementById("chat-box");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message-input");

    if (!chatBox) return;

    const username = chatBox.dataset.username;
    const currentUser = chatBox.dataset.currentUser;

    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

    const socket = new WebSocket(
        protocol + window.location.host + "/ws/chat/" + username + "/"
    );

    // 受信メッセージ処理
    socket.onmessage = function (e) {
        
        const data = JSON.parse(e.data);

        // チャット行の作成
        const row = document.createElement("div");
        row.classList.add("chat-row");
        row.classList.add(data.sender === currentUser ? "my-row" : "other-row");

        // アバター
        const avatar = document.createElement("img");
        avatar.src = data.image_url || "/static/accounts/img/default_avatar.png";
        avatar.classList.add("chat-avatar");

        // バブルラッパー
        const wrapper = document.createElement("div");
        wrapper.classList.add("chat-bubble-wrapper");

        // ユーザー名
        const usernameEl = document.createElement("a");
        usernameEl.classList.add("chat-username");
        usernameEl.href = "/accounts/" + data.sender + "/";
        usernameEl.textContent = data.sender;

        // メッセージバブル
        const bubble = document.createElement("div");
        bubble.classList.add("chat-bubble");
        bubble.textContent = data.message;

        // DOM構造を組み立てる
        wrapper.appendChild(usernameEl);
        wrapper.appendChild(bubble);
        row.appendChild(avatar);
        row.appendChild(wrapper);
        chatBox.appendChild(row);

        // 最新スクロール
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // メッセージ送信
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const message = input.value.trim();
        if (!message) return;

        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ message }));
        }

        input.value = "";
    });

});