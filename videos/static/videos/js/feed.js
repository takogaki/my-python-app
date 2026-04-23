document.addEventListener("DOMContentLoaded", () => {

    const feed = document.querySelector(".feed-inner");
    const cards = document.querySelectorAll(".video-card");
    const videos = document.querySelectorAll("video");
    const likeButtons = document.querySelectorAll(".like-btn");

    let currentIndex = 0;

    let startY = 0;
    let currentY = 0;
    let isDragging = false;
    let isCommentOpen = false;

    let isLocked = false;

    const headerHeight = 60;
    let viewportHeight = window.innerHeight - headerHeight;

    // =========================
    // 初期いいね状態
    // =========================
    likeButtons.forEach(btn => {
        if (btn.dataset.liked === "1") {
            btn.classList.add("liked");
        }
    });

    // =========================
    // ❤️ いいねクリック（修正版）
    // =========================
    likeButtons.forEach(btn => {

        btn.addEventListener("click", (e) => {

            e.stopPropagation();

            const postId = btn.dataset.id;

            fetch(`/videos/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                }
            })
            .then(res => res.json())
            .then(data => {

                const countEl = btn.querySelector(".count");
                const card = btn.closest(".video-card");

                if (data.liked) {
                    btn.classList.add("liked");

                    // 🔥 ここが本体（ハート生成）
                    spawnHearts(card);

                } else {
                    btn.classList.remove("liked");
                }

                countEl.textContent = data.count;
            });

        });

    });

    // =========================
    // ❤️ ハート生成（完成版）
    // =========================
    function spawnHearts(card) {

        const container = card.querySelector(".actions");

        for (let i = 0; i < 6; i++) {

            const heart = document.createElement("div");
            heart.className = "heart-pop";
            heart.textContent = "❤️";

            // 🔥 完全ランダム配置
            heart.style.left = (Math.random() * 40 + 10) + "px";
            heart.style.bottom = (Math.random() * 150 + 100) + "px";

            // 🔥 少し遅延（これが超重要）
            heart.style.animationDelay = (i * 0.08) + "s";

            container.appendChild(heart);

            setTimeout(() => {
                heart.remove();
            }, 700);
        }
    }

    // =========================
    // CSRF取得
    // =========================
    function getCSRFToken() {
        return document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken"))
            ?.split("=")[1];
    }

    // =========================
    // 移動
    // =========================
    function moveTo(index) {
        if (index < 0 || index >= cards.length) return;
        if (isLocked) return;

        isLocked = true;
        currentIndex = index;

        // 🔥 コメント閉じる（ここが超重要）
        const modal = document.getElementById("commentModal");
        if (modal) modal.classList.remove("show");

        feed.style.transition = "transform 0.4s ease";
        feed.style.transform = `translateY(-${index * viewportHeight}px)`;

        updateVideos();

        setTimeout(() => {
            isLocked = false;
        }, 450);
    }

    // =========================
    // 動画制御
    // =========================
    function updateVideos() {
        videos.forEach((v, i) => {
            if (i === currentIndex) {
                v.play().catch(()=>{});
            } else {
                v.pause();
                v.currentTime = 0;
            }
        });
    }

    updateVideos();

    // =========================
    // タッチ
    // =========================
    document.addEventListener("touchstart", (e) => {
        
        if (isCommentOpen) return;

        if (isLocked) return;

        isDragging = true;
        startY = e.touches[0].clientY;
        currentY = startY;

        feed.style.transition = "none";
    }, { passive: true });

    document.addEventListener("touchmove", (e) => {

        if (isCommentOpen) return;

        if (!isDragging || isLocked) return;

        currentY = e.touches[0].clientY;
        const diff = currentY - startY;

        feed.style.transform =
            `translateY(${-currentIndex * viewportHeight + diff}px)`;

    }, { passive: true });

    document.addEventListener("touchend", () => {

        if (isCommentOpen) return;

        if (!isDragging || isLocked) return;
        isDragging = false;

        const diff = currentY - startY;

        if (Math.abs(diff) > 80) {
            if (diff < 0) {
                moveTo(currentIndex + 1);
            } else {
                moveTo(currentIndex - 1);
            }
        } else {
            moveTo(currentIndex);
        }

    });

    // =========================
    // PCホイール
    // =========================
    let wheelLocked = false;

    document.addEventListener("wheel", (e) => {

        if (isCommentOpen) return;

        if (wheelLocked || isLocked) return;

        wheelLocked = true;

        if (e.deltaY > 0) {
            moveTo(currentIndex + 1);
        } else {
            moveTo(currentIndex - 1);
        }

        setTimeout(() => {
            wheelLocked = false;
        }, 500);

    }, { passive: true });

    // =========================
// 🎯 タップでプロフィール遷移
// =========================
let tapStartY = 0;
let tapMoved = false;

document.addEventListener("touchstart", (e) => {
    tapStartY = e.touches[0].clientY;
    tapMoved = false;
}, { passive: true });

document.addEventListener("touchmove", (e) => {
    const currentY = e.touches[0].clientY;

    if (Math.abs(currentY - tapStartY) > 10) {
        tapMoved = true;
    }
}, { passive: true });

document.addEventListener("touchend", (e) => {

    if (tapMoved) return;

    const card = e.target.closest(".video-card");
    if (!card) return;

    // 🔥 いいね・コメント押したときは無効
    if (e.target.closest(".action-btn")) return;

    const url = card.dataset.url;
    if (url) {
        window.location.href = url;
    }

});

// =========================
// 🖱 PCクリック対応
// =========================
document.addEventListener("click", (e) => {

    const card = e.target.closest(".video-card");
    if (!card) return;

    if (e.target.closest(".action-btn")) return;

    const url = card.dataset.url;
    if (url) {
        window.location.href = url;
    }

});

// =========================
// 💥 ダブルタップ検知
// =========================
let lastTap = 0;

document.addEventListener("touchend", (e) => {

    const now = new Date().getTime();
    const tapGap = now - lastTap;

    const card = e.target.closest(".video-card");
    if (!card) return;

    // ボタンは除外
    if (e.target.closest(".action-btn")) return;

    if (tapGap < 300) {
        // 🔥 ダブルタップ成立
        handleDoubleTap(card);
    }

    lastTap = now;

}, { passive: true });


// =========================
// 💥 ダブルタップ処理
// =========================
function handleDoubleTap(card) {

    const likeBtn = card.querySelector(".like-btn");

    // 既にいいね済みなら何もしない
    if (likeBtn.classList.contains("liked")) return;

    const postId = likeBtn.dataset.id;

    fetch(`/videos/like/${postId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
        }
    })
    .then(res => res.json())
    .then(data => {

        const countEl = likeBtn.querySelector(".count");

        likeBtn.classList.add("liked");
        countEl.textContent = data.count;

        // 💥 爆発演出
        showBigHeart(card);

        // 💥 小ハートばら撒き（既存のやつ）
        spawnHearts(card);

    });

}


// =========================
// 💥 中央ハート表示
// =========================
function showBigHeart(card) {

    const heart = card.querySelector(".double-heart");

    heart.classList.remove("show");
    void heart.offsetWidth;
    heart.classList.add("show");
}

let lastClick = 0;

document.addEventListener("click", (e) => {

    const now = new Date().getTime();
    const gap = now - lastClick;

    const card = e.target.closest(".video-card");
    if (!card) return;

    if (e.target.closest(".action-btn")) return;

    if (gap < 300) {
        handleDoubleTap(card);
    }

    lastClick = now;
});

// =========================
// 💬 モーダル取得
// =========================
const modal = document.getElementById("commentModal");
const commentList = document.querySelector(".comment-list");

let currentPostId = null;


// =========================
// 💬 コメント開く
// =========================
document.querySelectorAll(".comment-btn").forEach(btn => {

    btn.addEventListener("click", (e) => {

        e.stopPropagation();

        const card = btn.closest(".video-card");
        currentPostId = card.querySelector(".like-btn").dataset.id;

        modal.classList.add("show");
        isCommentOpen = true;

        loadComments(currentPostId);
    });

});


// =========================
// 💬 コメント取得
// =========================
function loadComments(postId) {

    fetch(`/videos/comments/${postId}/`)
    .then(res => res.json())
    .then(data => {

        commentList.innerHTML = "";

        data.comments.forEach(c => {
            commentList.innerHTML += `
                <div class="comment">
                    <b>${c.user}</b>
                    <p>${c.text}</p>
                </div>
            `;
        });

    });
}


// =========================
// 💬 投稿（修正版）
// =========================
document.getElementById("sendComment").addEventListener("click", () => {

    const input = document.getElementById("commentText");
    const text = input.value.trim();

    if (!text || !currentPostId) return;

    fetch(`/videos/comment/add/${currentPostId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `text=${encodeURIComponent(text)}`
    })
    .then(res => res.json())
    .then(data => {

        // 🔥 即時追加
        commentList.insertAdjacentHTML("afterbegin", `
            <div class="comment">
                <b>${data.user}</b>
                <p>${data.text}</p>
            </div>
        `);

        input.value = "";

        // 🔥 カウント更新
        const card = document.querySelector(
            `.like-btn[data-id="${currentPostId}"]`
        ).closest(".video-card");

        card.querySelector(".comment-btn .count").textContent = data.count;

    });

});


// =========================
// 💬 背景クリックで閉じる
// =========================
modal.addEventListener("click", (e) => {
    if (!e.target.closest(".comment-box")) {
        modal.classList.remove("show");
        isCommentOpen = false;
    }
});

// =========================
// 💬 コメント内スクロール制御（完全修正版）
// =========================
// =========================
// 💬 コメント全体スワイプ制御（最適版）
// =========================
const commentBox = document.querySelector(".comment-box");

let commentStartY = 0;

if (commentBox) {

    commentBox.addEventListener("touchstart", (e) => {
        commentStartY = e.touches[0].clientY;
    }, { passive: true });

    commentBox.addEventListener("touchmove", (e) => {

        const list = commentBox.querySelector(".comment-list");
        if (!list) return;

        const currentY = e.touches[0].clientY;
        const diff = currentY - commentStartY;

        const isAtTop = list.scrollTop === 0;
        const isAtBottom =
            list.scrollHeight - list.scrollTop <= list.clientHeight;

        // 上端・下端ならフィードに任せる
        if ((isAtTop && diff > 0) || (isAtBottom && diff < 0)) {
            return;
        }

        // それ以外はコメント内スクロール優先
        e.stopPropagation();
        e.preventDefault();

    }, { passive: false });

    // PCホイール
    commentBox.addEventListener("wheel", (e) => {

        const list = commentBox.querySelector(".comment-list");
        if (!list) return;

        const isAtTop = list.scrollTop === 0;
        const isAtBottom =
            list.scrollHeight - list.scrollTop <= list.clientHeight;

        if ((isAtTop && e.deltaY < 0) || (isAtBottom && e.deltaY > 0)) {
            return;
        }

        e.stopPropagation();

    }, { passive: true });
}

document.querySelectorAll(".more-btn").forEach(btn => {

    btn.addEventListener("click", (e) => {

        e.stopPropagation();

        const text = btn.previousElementSibling;

        text.classList.toggle("open");

        if (text.classList.contains("open")) {
            btn.textContent = "閉じる";
        } else {
            btn.textContent = "…もっと見る";
        }

    });

});

});