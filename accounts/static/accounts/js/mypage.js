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

            const badge = document.querySelector(".notification-count");

            if (badge) {
                badge.textContent = Number(badge.textContent || 0) + 1;
            }

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
   ・複数画像対応
   ・左右スワイプ対応
   ・左右ボタン対応
   ・画像タップで閉じる
================================================== */

(function () {

    let currentImages = [];
    let currentIndex = 0;

    let touchStartX = 0;
    let touchStartY = 0;


    /* ==================================================
       DOM
    ================================================== */

    function getModal() {
        return document.getElementById("mypage-image-modal");
    }

    function getModalImage() {
        return document.getElementById("mypage-modal-image");
    }


    /* ==================================================
       モーダルにナビゲーションボタンを作成
    ================================================== */

    function createNavigation() {

        const modal = getModal();

        if (!modal) {
            return;
        }

        /* すでに作成済みなら何もしない */
        if (modal.querySelector(".mypage-image-prev")) {
            return;
        }


        /* =========================
           ← 前の画像
        ========================= */

        const prevButton = document.createElement("button");

        prevButton.type = "button";
        prevButton.className = "mypage-image-prev";
        prevButton.setAttribute("aria-label", "前の画像");
        prevButton.textContent = "‹";


        /* =========================
           → 次の画像
        ========================= */

        const nextButton = document.createElement("button");

        nextButton.type = "button";
        nextButton.className = "mypage-image-next";
        nextButton.setAttribute("aria-label", "次の画像");
        nextButton.textContent = "›";


        modal.appendChild(prevButton);
        modal.appendChild(nextButton);


        /* =========================
           前へ
        ========================= */

        prevButton.addEventListener("click", function (event) {

            event.stopPropagation();

            showPreviousImage();

        });


        /* =========================
           次へ
        ========================= */

        nextButton.addEventListener("click", function (event) {

            event.stopPropagation();

            showNextImage();

        });

    }


    /* ==================================================
       現在の画像を表示
    ================================================== */

    function updateModalImage() {

        const modalImage = getModalImage();

        if (!modalImage || !currentImages.length) {
            return;
        }

        modalImage.src = currentImages[currentIndex];


        /* =========================
           ボタン表示状態
        ========================= */

        const modal = getModal();

        if (!modal) {
            return;
        }

        const prevButton = modal.querySelector(
            ".mypage-image-prev"
        );

        const nextButton = modal.querySelector(
            ".mypage-image-next"
        );


        /* 画像が1枚だけなら非表示 */

        if (currentImages.length <= 1) {

            if (prevButton) {
                prevButton.style.display = "none";
            }

            if (nextButton) {
                nextButton.style.display = "none";
            }

            return;
        }


        /* 複数画像 */

        if (prevButton) {
            prevButton.style.display = "flex";
        }

        if (nextButton) {
            nextButton.style.display = "flex";
        }

    }


    /* ==================================================
       画像を開く
    ================================================== */

    function openMypageImageModal(images, startIndex) {

        const modal = getModal();
        const modalImage = getModalImage();

        if (
            !modal ||
            !modalImage ||
            !images ||
            !images.length
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


        createNavigation();

        updateModalImage();

        modal.classList.add("is-open");

        document.body.style.overflow = "hidden";

    }


    /* ==================================================
       閉じる
    ================================================== */

    function closeMypageImageModal() {

        const modal = getModal();
        const modalImage = getModalImage();

        if (!modal) {
            return;
        }

        modal.classList.remove("is-open");

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

        /* 最後まで行ったら先頭へ */

        if (currentIndex >= currentImages.length) {
            currentIndex = 0;
        }

        updateModalImage();

    }


    /* ==================================================
       前の画像
    ================================================== */

    function showPreviousImage() {

        if (currentImages.length <= 1) {
            return;
        }

        currentIndex--;

        /* 先頭より前なら最後へ */

        if (currentIndex < 0) {
            currentIndex = currentImages.length - 1;
        }

        updateModalImage();

    }


    /* ==================================================
       📸 投稿画像クリック
    ================================================== */

    document.addEventListener("click", function (event) {

        const mediaItem = event.target.closest(
            ".mypage-media-item[data-full-image], .mypage-media-stack-card[data-full-image]"
        );


        if (mediaItem) {

            event.preventDefault();


            /* ==================================================
               複数画像カードの場合
            ================================================== */

            const stack = mediaItem.closest(
                ".mypage-media-stack"
            );


            if (stack) {

                const cards = Array.from(
                    stack.querySelectorAll(
                        ".mypage-media-stack-card[data-full-image]"
                    )
                );


                const images = cards.map(function (card) {
                    return card.dataset.fullImage;
                });


                const clickedIndex = cards.indexOf(
                    mediaItem
                );


                openMypageImageModal(
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

                openMypageImageModal(
                    [imageUrl],
                    0
                );

            }

            return;
        }


        /* ==================================================
           🔍 全画面画像をタップ
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
           黒背景
        ========================= */

        const modal = getModal();

        if (
            modal &&
            event.target === modal
        ) {

            closeMypageImageModal();

        }

    });


    /* ==================================================
       👆 スワイプ開始
    ================================================== */

    document.addEventListener(
        "touchstart",
        function (event) {

            const modal = getModal();

            if (
                !modal ||
                !modal.classList.contains("is-open")
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

            const modal = getModal();

            if (
                !modal ||
                !modal.classList.contains("is-open")
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


            /* ==================================================
               縦方向の動きが大きい場合は無視
            ================================================== */

            if (
                Math.abs(diffY) >
                Math.abs(diffX)
            ) {
                return;
            }


            /* ==================================================
               小さい動きはタップ扱い
            ================================================== */

            if (Math.abs(diffX) < 50) {
                return;
            }


            /* ==================================================
               左スワイプ
               → 次の画像
            ================================================== */

            if (diffX < 0) {

                showNextImage();

            }


            /* ==================================================
               右スワイプ
               → 前の画像
            ================================================== */

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

            const modal = getModal();

            if (
                !modal ||
                !modal.classList.contains("is-open")
            ) {
                return;
            }


            if (event.key === "Escape") {

                closeMypageImageModal();

                return;

            }


            /* =========================
               ← キー
            ========================= */

            if (event.key === "ArrowLeft") {

                showPreviousImage();

                return;

            }


            /* =========================
               → キー
            ========================= */

            if (event.key === "ArrowRight") {

                showNextImage();

                return;

            }

        }
    );

})();