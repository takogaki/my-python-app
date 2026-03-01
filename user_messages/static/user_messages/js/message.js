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

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        const row = document.createElement("div");
        row.classList.add("chat-row");

        if (data.sender === currentUser) {
            row.classList.add("my-row");
        } else {
            row.classList.add("other-row");
        }

        const imageUrl = data.image_url && data.image_url !== ""
            ? data.image_url
            : "/static/accounts/img/default_avatar.png";

        row.innerHTML = `
            <img src="${imageUrl}" class="chat-avatar">

            <div class="chat-bubble-wrapper">
                <a class="chat-username">${data.sender}</a>
                <div class="chat-bubble">
                    ${data.message}
                </div>
            </div>
        `;

        chatBox.appendChild(row);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const message = input.value.trim();
        if (!message) return;

        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                message: message
            }));
        }

        input.value = "";
    });

});