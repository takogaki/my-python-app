document.addEventListener("DOMContentLoaded", () => {

    /* =========================
    🧠 状態管理
    ========================= */
    let currentIndex = 0;
    let currentPostId = null;
    let isCommentOpen = false;
    let isLocked = false;

    const feed = document.querySelector(".video-feed");
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
                <b>${c.user}</b>
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
                    <b>${data.user}</b>
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
    🧠 外側クリック制御（TikTok仕様）
    ========================= */
    document.addEventListener("click", (e) => {

        const card = e.target.closest(".video-card");
        if (!card) return;

        if (e.target.closest(".action-btn")) return;

        const url = card.dataset.url;
        if (url) location.href = url;
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
    🎬 動画制御（完全安定版）
    ========================= */

    const feed = document.querySelector(".video-feed");
    if (!feed) return; // ← 超重要

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

        // 🔥 広告ロード
        if (window.adsbygoogle) {
            document.querySelectorAll(".adsbygoogle").forEach(ad => {
                if (!ad.classList.contains("ads-loaded")) {
                    try {
                        (adsbygoogle = window.adsbygoogle || []).push({});
                        ad.classList.add("ads-loaded");
                    } catch (e) {}
                }
            });
        }
    });
});