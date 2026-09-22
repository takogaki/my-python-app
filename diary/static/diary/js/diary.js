document.addEventListener("DOMContentLoaded", function () {

    const button = document.getElementById("like-button");

    if (!button) return;

    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {

            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {

                cookie = cookie.trim();

                if (cookie.startsWith(name + '=')) {

                    cookieValue = decodeURIComponent(
                        cookie.slice(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    button.addEventListener("click", async function () {

        // 連打防止
        if (button.disabled) return;

        button.disabled = true;

        try {

            const res = await fetch(button.dataset.url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            if (res.status === 401) {
                alert("いいねするにはログインしてください。");
                button.disabled = false;
                return;
            }

            if (!res.ok) {
                throw new Error("HTTP ERROR: " + res.status);
            }

            const data = await res.json();

            console.log(data);

            // 総数
            document.getElementById("likes-count").textContent =
                data.likes;

            // ユニークユーザー数
            document.getElementById("unique-users-count").textContent =
                data.unique_users;

            // 自分のいいね回数
            document.getElementById("user-likes-count").textContent =
                data.user_like_count;

            // いいね済みに変更
            button.textContent = "👍 いいね済み";
            button.disabled = true;

        } catch (err) {

            console.error("LIKE ERROR:", err);

            // エラー時は再試行可能にする
            button.disabled = false;

        }

    });

});