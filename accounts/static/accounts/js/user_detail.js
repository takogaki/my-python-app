document.addEventListener("click", async (e) => {

    // =========================
    // 🔐 CSRF取得
    // =========================
    function getCSRFToken() {
        return document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }

    // =========================
    // 🔥 戻る対策（bfcache）
    // =========================
    window.addEventListener("pageshow", function (event) {
        if (event.persisted) {
            window.location.reload();
        }
    });

    // =========================
    // ❤️ LIKE処理（最強安定版）
    // =========================
    document.addEventListener("click", async (e) => {

        const btn = e.target.closest(".user-like-btn");
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const userId = btn.dataset.userId;
        if (!userId) return;

        // 🔥 二重クリック防止
        if (btn.dataset.loading === "true") return;
        btn.dataset.loading = "true";

        try {
            const res = await fetch(`/accounts/like/${userId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                }
            });

            if (!res.ok) return;

            const data = await res.json();

            // =========================
            // 状態反映
            // =========================
            if (data.status === "match") {
                window.location.href = "/accounts/match-result/";
                return;
            }

            if (data.status === "liked") {
                btn.classList.add("liked");
                btn.innerHTML = "❤️ ライク済み";
            }

            if (data.status === "unliked") {
                btn.classList.remove("liked");
                btn.innerHTML = "❤️ LIKEする";
            }

        } catch (err) {
            console.error("LIKE error:", err);
        } finally {
            btn.dataset.loading = "false";
        }
    });
});