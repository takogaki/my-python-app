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

        try {

            const res = await fetch(button.dataset.url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            if (!res.ok) {
                throw new Error("HTTP ERROR: " + res.status);
            }

            const data = await res.json();

            console.log(data);

            // 👍総数
            document.getElementById("likes-count").textContent =
                data.likes;

            // 👥ユニーク人数
            document.getElementById("unique-users-count").textContent =
                data.unique_users;

            // 🔥あなたの回数
            document.getElementById("user-likes-count").textContent =
                data.user_like_count;

        } catch (err) {

            console.error("LIKE ERROR:", err);

        }

    });

});