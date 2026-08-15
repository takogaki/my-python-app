/* ==================================================
🧠 Feed共通参照
================================================== */

let feed = null;
let fullscreenImage = null;
let fullscreenPlaceholder = null;


document.addEventListener("DOMContentLoaded", () => {

    /* =========================
    🧠 状態管理
    ========================= */
    let currentIndex = 0;
    let currentPostId = null;
    let isCommentOpen = false;
    let isLocked = false;

    feed = document.querySelector(".video-feed");

    if (!feed) return;
    const modal = document.getElementById("commentModal");
    const commentList = document.querySelector(".comment-list");

    /* =========================
    🧼 CSRF
    ========================= */
    function getCSRFToken() {
        return document.cookie
            .split("; ")
            .find(r => r.startsWith("csrftoken"))
            ?.split("=")[1];
    }

    /* =========================
    🎯 投稿取得ヘルパー
    ========================= */
    function getCard(el) {
        return el.closest(".video-card");
    }

    function getPostId(card) {
        return card.querySelector(".like-btn")?.dataset.id;
    }

    /* =========================
    ❤️ いいね（イベント委譲）
    ========================= */
    document.addEventListener("click", async (e) => {

        const btn = e.target.closest(".like-btn");
        if (!btn) return;

        e.stopPropagation();

        const card = getCard(btn);
        const postId = btn.dataset.id;

        try {
            const res = await fetch(`/videos/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                }
            });

            const data = await res.json();

            btn.querySelector(".count").textContent = data.count;

            if (data.liked) {
                btn.classList.add("liked");
                spawnHearts(card);
            } else {
                btn.classList.remove("liked");
            }

        } catch (err) {
            console.error("like error", err);
        }
    });

    /* =========================
    💬 コメントモーダル開く
    ========================= */
    document.addEventListener("click", (e) => {

        const btn = e.target.closest(".comment-btn");
        if (!btn) return;

        e.stopPropagation();

        const card = getCard(btn);

        currentPostId = getPostId(card);
        isCommentOpen = true;

        modal.classList.add("show");

        loadComments(currentPostId);

        setTimeout(() => {
            document.getElementById("commentText")?.focus();
        }, 100);
    });

    /* =========================
    💬 コメント取得
    ========================= */
    async function loadComments(postId) {

        if (!postId) return;

        const res = await fetch(`/videos/comments/${postId}/`);
        const data = await res.json();

        commentList.innerHTML = data.comments.map(c => `
            <div class="comment">

                <a href="${c.profile_url}" class="comment-user">
                    <img src="${c.icon}" class="comment-avatar">
                    <b>${c.user}</b>
                </a>

                <p>${c.text}</p>

            </div>
        `).join("");
    }

    /* =========================
    💬 コメント送信（安定版）
    ========================= */
    document.addEventListener("click", (e) => {

        if (!e.target.closest("#sendComment")) return;

        sendComment();
    });

    async function sendComment() {

        const input = document.getElementById("commentText");
        const text = input.value.trim();

        if (!text || !currentPostId) return;

        try {
            const res = await fetch(`/videos/comment/add/${currentPostId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `text=${encodeURIComponent(text)}`
            });

            const data = await res.json();

            commentList.insertAdjacentHTML("afterbegin", `
                <div class="comment">

                    <a href="${data.profile_url}" class="comment-user">
                        <img src="${data.icon}" class="comment-avatar">
                        <b>${data.user}</b>
                    </a>

                    <p>${data.text}</p>

                </div>
            `);

            input.value = "";

            const card = document.querySelector(
                `.like-btn[data-id="${currentPostId}"]`
            )?.closest(".video-card");

            if (card) {
                card.querySelector(".comment-btn .count").textContent = data.count;
            }

        } catch (err) {
            console.error("comment error", err);
        }
    }

    /* =========================
    💥 ハート演出
    ========================= */
    function spawnHearts(card) {

        const likeBtn = card.querySelector(".like-btn");
        const rect = likeBtn.getBoundingClientRect();
        const cardRect = card.getBoundingClientRect();

        const baseX = rect.left - cardRect.left + rect.width / 2;
        const baseY = rect.top - cardRect.top;

        for (let i = 0; i < 6; i++) {

            const heart = document.createElement("div");
            heart.className = "heart-pop";
            heart.textContent = "❤️";

            heart.style.left = baseX + (Math.random() * 20 - 10) + "px";
            heart.style.top = baseY + "px";

            card.appendChild(heart);

            setTimeout(() => heart.remove(), 800);
        }
    }

    /* =========================
    💬 モーダル閉じる
    ========================= */
    modal?.addEventListener("click", (e) => {
        if (!e.target.closest(".comment-box")) {
            modal.classList.remove("show");
            isCommentOpen = false;
        }
    });

    /* =========================
    🖱️ Feedカードクリック
    ========================= */

    document.addEventListener("click", (e) => {

        const card = e.target.closest(".video-card");

        if (!card) return;


        /* =========================
        クリックしてもカード遷移させないもの
        ========================= */

        if (
            e.target.closest(".action-btn") ||
            e.target.closest(".more-btn") ||
            e.target.closest(".comment-user") ||
            e.target.closest(".recruit-image-clickable") ||
            e.target.closest(".recruit-image-modal") ||
            e.target.closest(".feed-post-image")
        ) {
            return;
        }


    /* =========================
       カードURLへ移動
    ========================= */

    const url = card.dataset.url;

    if (url) {
        location.href = url;
    }

});

    document.addEventListener("click", (e) => {

        const btn = e.target.closest(".more-btn");
        if (!btn) return;

        e.stopPropagation();

        const caption = btn.closest(".caption");
        const text = caption.querySelector(".caption-text");

        text.classList.toggle("open");

        btn.textContent = text.classList.contains("open")
            ? "閉じる"
            : "…もっと見る";
    });

    /* =========================
    📷 募集写真 拡大表示
    ========================= */

    const recruitImageModal = document.getElementById("recruitImageModal");
    const recruitImageModalImage = document.getElementById("recruitImageModalImage");
    const recruitImageClose = document.getElementById("recruitImageClose");


    document.addEventListener("click", (e) => {

        const image = e.target.closest(".recruit-image-clickable");

        if (!image) return;

        e.preventDefault();
        e.stopPropagation();

        if (!recruitImageModal || !recruitImageModalImage) {
            return;
        }

        recruitImageModalImage.src = image.src;
        recruitImageModalImage.alt = image.alt || "";

        recruitImageModal.classList.add("show");

        feed.style.overflowY = "hidden";
    });


    function closeRecruitImageModal() {

        if (!recruitImageModal) return;

        recruitImageModal.classList.remove("show");

        if (recruitImageModalImage) {
            recruitImageModalImage.src = "";
        }

        feed.style.overflowY = "scroll";
    }


    recruitImageClose?.addEventListener("click", (e) => {

        e.preventDefault();
        e.stopPropagation();

        closeRecruitImageModal();

    });


    recruitImageModal?.addEventListener("click", (e) => {

        if (e.target === recruitImageModal) {
            closeRecruitImageModal();
        }

    });


    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") {
            closeRecruitImageModal();
        }

    });


    /* ❌ 閉じる */

    function closeRecruitImageModal() {

        if (!recruitImageModal) return;

        recruitImageModal.classList.remove("show");

        if (recruitImageModalImage) {
            recruitImageModalImage.src = "";
        }

        /*
        * Feedのスクロールを戻す
        */
        feed.style.overflowY = "scroll";

    }


    /* × ボタン */

    recruitImageClose?.addEventListener("click", (e) => {

        e.preventDefault();
        e.stopPropagation();

        closeRecruitImageModal();

    });


    /* 背景クリック */

    recruitImageModal?.addEventListener("click", (e) => {

        if (e.target === recruitImageModal) {
            closeRecruitImageModal();
        }

    });


    /* ESCキー */

    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") {
            closeRecruitImageModal();
        }

    });

    /* =========================
    🎬 動画制御（完全安定版）
    ========================= */
    const cards = document.querySelectorAll(".video-card:not(.ad-card)");
    const videos = document.querySelectorAll(".video-card:not(.ad-card) video");

    // 高さ（fallback付き）
    const cardHeight = feed.clientHeight || window.innerHeight;

    // =========================
    // 🎯 IntersectionObserver
    // =========================
    const observer = new IntersectionObserver((entries) => {

        entries.forEach(entry => {

            const video = entry.target.querySelector("video");
            if (!video) return;

            if (entry.isIntersecting) {
                video.play().catch(() => {});
                video.muted = false;
            } else {
                video.pause();
                video.currentTime = 0;
                video.muted = true;
            }

        });

    }, { threshold: 0.6 });

    cards.forEach(card => observer.observe(card));


    // =========================
    // 🚀 スクロール制御
    // =========================
    feed.addEventListener("scroll", () => {

        const index = Math.round(feed.scrollTop / cardHeight);

        const next = videos[index + 1];
        const prev = videos[index - 1];

        // 🔥 次動画
        if (next && next.preload !== "auto") {
            next.preload = "auto";
            next.load();
        }

        // 🔥 前動画
        if (prev && prev.preload !== "auto") {
            prev.preload = "auto";
            prev.load();
        }
    });
});

async function loadNearbyRecruits() {

    const container =
        document.getElementById(
            "nearbyRecruitList"
        );

    if (!container) return;

    try {

        const response =
            await fetch(
                "/locations/nearby-recruits/"
            );

        const data =
            await response.json();

        if (!response.ok || !data.success) {

            container.innerHTML =
                "<p>近くの募集を取得できませんでした。</p>";

            return;
        }

        if (!data.results.length) {

            container.innerHTML =
                "<p>近くに募集はありません。</p>";

            return;
        }

        container.innerHTML =
            data.results.map(recruit => {

                return `
                    <a
                        href="/videos/recruit/${recruit.id}/"
                        class="nearby-recruit-card"
                    >

                        <div class="nearby-recruit-title">
                            ${escapeHtml(recruit.title)}
                        </div>

                        <div class="nearby-recruit-place">
                            📍 ${escapeHtml(recruit.place || "")}
                        </div>

                        <div class="nearby-recruit-distance">
                            📏 ${recruit.distance} km
                        </div>

                    </a>
                `;

            }).join("");

    } catch (error) {

        console.error(
            "近くの募集取得エラー",
            error
        );

        container.innerHTML =
            "<p>読み込みに失敗しました。</p>";
    }
}


function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadNearbyRecruits();

    }
);

/* ==================================================
📷 Feed投稿画像 全画面表示
================================================== */


/* =========================
画像を開く
========================= */

document.addEventListener("click", (event) => {

    const image =
        event.target.closest(".feed-post-image");

    if (!image) return;


    event.preventDefault();
    event.stopPropagation();


    /* =========================
       すでに全画面なら閉じる
    ========================= */

    if (fullscreenImage) {

        closeFullscreenImage();

        return;
    }


    /* =========================
       元の位置を保存
    ========================= */

    fullscreenPlaceholder =
        document.createComment(
            "feed-image-placeholder"
        );


    image.parentNode.insertBefore(
        fullscreenPlaceholder,
        image
    );


    /* =========================
       全画面用にbodyへ移動
    ========================= */

    fullscreenImage = image;

    document.body.appendChild(
        fullscreenImage
    );


    /* =========================
       全画面クラス
    ========================= */

    fullscreenImage.classList.add(
        "image-fullscreen"
    );


    /* =========================
       Feedスクロール停止
    ========================= */

    if (feed) {

        feed.style.overflowY = "hidden";
        feed.style.overflowX = "hidden";

    }

});


/* =========================
画像を閉じる
========================= */

function closeFullscreenImage() {

    if (!fullscreenImage) {
        return;
    }


    /* =========================
       全画面クラス解除
    ========================= */

    fullscreenImage.classList.remove(
        "image-fullscreen"
    );


    /* =========================
       元の場所へ戻す
    ========================= */

    if (
        fullscreenPlaceholder &&
        fullscreenPlaceholder.parentNode
    ) {

        fullscreenPlaceholder.parentNode.insertBefore(
            fullscreenImage,
            fullscreenPlaceholder.nextSibling
        );

        fullscreenPlaceholder.remove();

    }


    /* =========================
       状態リセット
    ========================= */

    fullscreenImage = null;
    fullscreenPlaceholder = null;


    /* =========================
       Feedスクロール復活
    ========================= */

    if (feed) {

        feed.style.overflowY = "scroll";
        feed.style.overflowX = "hidden";

    }

}


/* =========================
ESCで閉じる
========================= */

document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {

        closeFullscreenImage();

    }

});