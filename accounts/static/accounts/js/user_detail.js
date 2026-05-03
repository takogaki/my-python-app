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

    // 🔥 読み込み確認（1回だけ）
    console.log("user_detail.js loaded");


    // =========================
    // ❤️ ユーザーLIKE処理
    // =========================
    document.addEventListener("click", async (e) => {

        const btn = e.target.closest(".user-like-btn");
        if (!btn) return;

        e.stopPropagation();

        const userId = btn.dataset.userId;

        if (!userId) {
            console.error("userIdが取得できていません");
            return;
        }

        const container = btn.closest(".user-like-section");
        const countEl = container?.querySelector(".user-like-count");

        try {
            const res = await fetch(`/accounts/like/${userId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                }
            });

            console.log("status:", res.status);

            if (!res.ok) {
                console.error("HTTPエラー", res.status);
                return;
            }

            const data = await res.json();
            console.log("LIKEレスポンス:", data);

            // =========================
            // 🔥 状態反映
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

            if (countEl && data.count !== undefined) {
                countEl.textContent = data.count;
            }

        } catch (err) {
            console.error("通信エラー", err);
        }

    });


    // =========================
    // 🧠 外側クリック制御（バグ修正版）
    // =========================
    document.addEventListener("click", (e) => {

        const card = e.target.closest(".video-card");
        if (!card) return;

        // 🔥 これがないとLIKEが無反応になる
        if (
            e.target.closest(".action-btn") ||
            e.target.closest(".user-like-btn")
        ) return;

        const url = card.dataset.url;
        if (url) location.href = url;
    });
});