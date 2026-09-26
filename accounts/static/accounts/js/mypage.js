document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       📊 プログレスバー（既存）
    ========================= */
    document.querySelectorAll(".progress").forEach(el => {
        el.style.width = el.dataset.width + "%";
    });

    /* =========================
       🔔 通知リアルタイム
    ========================= */

    const socket = new WebSocket(
        (location.protocol === "https:" ? "wss://" : "ws://") +
        location.host +
        "/ws/notifications/"
    );

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data.type === "notification") {

            // 🔢 バッジ更新
            const badge = document.querySelector(".notification-count");

            if (badge) {
                badge.textContent = Number(badge.textContent || 0) + 1;
            }

            // 🔥 デバッグ（確認用）
            console.log("通知受信:", data);
        }
    };

    socket.onopen = () => {
        console.log("通知Socket接続OK");
    };

    socket.onerror = (err) => {
        console.error("Socketエラー:", err);
    };

    socket.onclose = () => {
        console.log("Socket切断");
    };

});

/* ==================================================
   🖼️ 投稿画像 全画面表示
   初回表示・動的表示対応
   画像をもう一度タップすると閉じる
================================================== */

(function () {

    /* =========================
       画像を開く
    ========================= */

    function openMypageImageModal(imageUrl) {

        const imageModal = document.getElementById(
            "mypage-image-modal"
        );

        const modalImage = document.getElementById(
            "mypage-modal-image"
        );

        if (!imageUrl || !imageModal || !modalImage) {
            return;
        }

        modalImage.src = imageUrl;

        imageModal.classList.add("is-open");

        document.body.style.overflow = "hidden";
    }


    /* =========================
       閉じる
    ========================= */

    function closeMypageImageModal() {

        const imageModal = document.getElementById(
            "mypage-image-modal"
        );

        const modalImage = document.getElementById(
            "mypage-modal-image"
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
       📸 クリック処理
    ================================================== */

    document.addEventListener("click", function (event) {

        /* =========================
           投稿画像をクリック
        ========================= */

        const mediaItem = event.target.closest(
            ".mypage-media-item[data-full-image], .mypage-media-stack-card[data-full-image]"
        );

        if (mediaItem) {

            event.preventDefault();

            const imageUrl = mediaItem.dataset.fullImage;

            openMypageImageModal(imageUrl);

            return;
        }


        /* ==================================================
           🔍 全画面表示中の画像をもう一度クリック
           → 閉じる
        ================================================== */

        const modalImage = event.target.closest(
            "#mypage-modal-image"
        );

        if (modalImage) {

            event.preventDefault();

            closeMypageImageModal();

            return;
        }


        /* =========================
           ×ボタン
        ========================= */

        const modalClose = event.target.closest(
            ".mypage-image-modal-close"
        );

        if (modalClose) {

            event.preventDefault();

            closeMypageImageModal();

            return;
        }


        /* =========================
           黒背景をクリック
        ========================= */

        const imageModal = document.getElementById(
            "mypage-image-modal"
        );

        if (
            imageModal &&
            event.target === imageModal
        ) {

            closeMypageImageModal();

        }

    });


    /* =========================
       ESCで閉じる
    ========================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                const imageModal = document.getElementById(
                    "mypage-image-modal"
                );

                if (
                    imageModal &&
                    imageModal.classList.contains("is-open")
                ) {
                    closeMypageImageModal();
                }

            }

        }
    );

})();