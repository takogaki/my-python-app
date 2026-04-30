document.addEventListener("DOMContentLoaded", function () {

    const protocol = location.protocol === "https:" ? "wss://" : "ws://";

    const socket = new WebSocket(
        protocol + location.host + "/ws/notifications/"
    );

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        console.log("通知受信:", data);

        if (data.type === "notification") {

            const badge = document.querySelector(".notification-count");

            if (badge) {
                badge.textContent = Number(badge.textContent || 0) + 1;
            }
        }
    };

});