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

/* ==================================================
   🖼️ 投稿画像 全画面表示
   初回表示・動的表示どちらにも対応
================================================== */

(function () {

    function openImageModal(imageUrl) {

        const imageModal = document.getElementById(
            "user-detail-image-modal"
        );

        const modalImage = document.getElementById(
            "user-detail-modal-image"
        );

        if (!imageUrl || !imageModal || !modalImage) {
            return;
        }

        modalImage.src = imageUrl;

        imageModal.classList.add("is-open");

        document.body.style.overflow = "hidden";
    }


    function closeImageModal() {

        const imageModal = document.getElementById(
            "user-detail-image-modal"
        );

        const modalImage = document.getElementById(
            "user-detail-modal-image"
        );

        if (!imageModal) {
            return;
        }

        imageModal.classList.remove("is-open");

        document.body.style.overflow = "";

        if (modalImage) {
            modalImage.src = "";
        }
    }


    /* ==================================================
       📸 投稿画像クリック
       イベント委譲方式
    ================================================== */

    document.addEventListener("click", function (event) {

        /* ==================================================
           🔍 拡大前の画像
        ================================================== */

        const mediaItem = event.target.closest(
            ".user-detail-media-item[data-full-image]"
        );

        if (mediaItem) {

            event.preventDefault();

            const imageUrl = mediaItem.dataset.fullImage;

            openImageModal(imageUrl);

            return;
        }


        /* ==================================================
           🔍 拡大表示中の画像をもう一度クリック
           → モーダルを閉じる
        ================================================== */

        const modalImage = event.target.closest(
            "#user-detail-modal-image"
        );

        if (modalImage) {

            event.preventDefault();

            closeImageModal();

            return;
        }


        /* ==================================================
           ❌ 閉じるボタン
        ================================================== */

        const closeButton = event.target.closest(
            ".user-detail-image-modal-close"
        );

        if (closeButton) {

            event.preventDefault();

            closeImageModal();

            return;
        }


        /* ==================================================
           🖤 モーダル背景クリック
        ================================================== */

        const imageModal = document.getElementById(
            "user-detail-image-modal"
        );

        if (
            imageModal &&
            event.target === imageModal
        ) {

            closeImageModal();

        }

    });


    /* ==================================================
       ⌨️ ESCキーで閉じる
    ================================================== */

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            const imageModal = document.getElementById(
                "user-detail-image-modal"
            );

            if (
                imageModal &&
                imageModal.classList.contains("is-open")
            ) {

                closeImageModal();

            }

        }

    });

})();