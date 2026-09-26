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

/* ==================================================
   🖼️ 投稿画像 全画面表示
   ・複数画像対応
   ・左右スワイプ対応
   ・画像タップで閉じる
================================================== */

(function () {

    let currentImages = [];
    let currentIndex = 0;

    let touchStartX = 0;
    let touchStartY = 0;


    /* ==================================================
       画像を開く
    ================================================== */

    function openImageModal(images, startIndex) {

        const imageModal = document.getElementById(
            "user-detail-image-modal"
        );

        const modalImage = document.getElementById(
            "user-detail-modal-image"
        );

        if (
            !images ||
            !images.length ||
            !imageModal ||
            !modalImage
        ) {
            return;
        }

        currentImages = images;
        currentIndex = startIndex || 0;

        /* 範囲外防止 */
        if (currentIndex < 0) {
            currentIndex = 0;
        }

        if (currentIndex >= currentImages.length) {
            currentIndex = currentImages.length - 1;
        }

        modalImage.src = currentImages[currentIndex];

        imageModal.classList.add("is-open");

        document.body.style.overflow = "hidden";
    }


    /* ==================================================
       閉じる
    ================================================== */

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

        currentImages = [];
        currentIndex = 0;
    }


    /* ==================================================
       次の画像
    ================================================== */

    function showNextImage() {

        if (currentImages.length <= 1) {
            return;
        }

        currentIndex++;

        /* 最後 → 最初 */
        if (currentIndex >= currentImages.length) {
            currentIndex = 0;
        }

        const modalImage = document.getElementById(
            "user-detail-modal-image"
        );

        if (modalImage) {
            modalImage.src = currentImages[currentIndex];
        }
    }


    /* ==================================================
       前の画像
    ================================================== */

    function showPreviousImage() {

        if (currentImages.length <= 1) {
            return;
        }

        currentIndex--;

        /* 最初 → 最後 */
        if (currentIndex < 0) {
            currentIndex = currentImages.length - 1;
        }

        const modalImage = document.getElementById(
            "user-detail-modal-image"
        );

        if (modalImage) {
            modalImage.src = currentImages[currentIndex];
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
            ".user-detail-media-item[data-full-image], .user-detail-media-stack-card[data-full-image]"
        );

        if (mediaItem) {

            event.preventDefault();


            /* ==================================================
               複数画像投稿
            ================================================== */

            const stack = mediaItem.closest(
                ".user-detail-media-stack"
            );

            if (stack) {

                const cards = Array.from(
                    stack.querySelectorAll(
                        ".user-detail-media-stack-card[data-full-image]"
                    )
                );

                const images = cards.map(function (card) {
                    return card.dataset.fullImage;
                });

                const clickedIndex = cards.indexOf(
                    mediaItem
                );

                openImageModal(
                    images,
                    clickedIndex >= 0 ? clickedIndex : 0
                );

                return;
            }


            /* ==================================================
               通常の1枚画像
            ================================================== */

            const imageUrl = mediaItem.dataset.fullImage;

            if (imageUrl) {

                openImageModal(
                    [imageUrl],
                    0
                );

            }

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
       👆 スワイプ開始
    ================================================== */

    document.addEventListener(
        "touchstart",
        function (event) {

            const imageModal = document.getElementById(
                "user-detail-image-modal"
            );

            if (
                !imageModal ||
                !imageModal.classList.contains("is-open")
            ) {
                return;
            }

            if (!event.touches.length) {
                return;
            }

            touchStartX = event.touches[0].clientX;
            touchStartY = event.touches[0].clientY;

        },
        { passive: true }
    );


    /* ==================================================
       👆 スワイプ終了
    ================================================== */

    document.addEventListener(
        "touchend",
        function (event) {

            const imageModal = document.getElementById(
                "user-detail-image-modal"
            );

            if (
                !imageModal ||
                !imageModal.classList.contains("is-open")
            ) {
                return;
            }

            if (!event.changedTouches.length) {
                return;
            }

            const touchEndX =
                event.changedTouches[0].clientX;

            const touchEndY =
                event.changedTouches[0].clientY;

            const diffX =
                touchEndX - touchStartX;

            const diffY =
                touchEndY - touchStartY;


            /* 縦方向の操作は無視 */
            if (
                Math.abs(diffY) >
                Math.abs(diffX)
            ) {
                return;
            }


            /* 小さい移動は無視 */
            if (Math.abs(diffX) < 50) {
                return;
            }


            /* 左スワイプ → 次 */
            if (diffX < 0) {

                showNextImage();

            }


            /* 右スワイプ → 前 */
            else {

                showPreviousImage();

            }

        },
        { passive: true }
    );


    /* ==================================================
       ⌨️ ESCで閉じる
    ================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            const imageModal = document.getElementById(
                "user-detail-image-modal"
            );

            if (
                !imageModal ||
                !imageModal.classList.contains("is-open")
            ) {
                return;
            }


            /* ESC */
            if (event.key === "Escape") {

                closeImageModal();

                return;
            }


            /* ← */
            if (event.key === "ArrowLeft") {

                showPreviousImage();

                return;
            }


            /* → */
            if (event.key === "ArrowRight") {

                showNextImage();

                return;
            }

        }
    );

})();