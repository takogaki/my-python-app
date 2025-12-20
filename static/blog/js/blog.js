/* =========================
   返信フォーム関連
========================= */

function showReplyForm(commentId) {
    document.querySelectorAll(".reply-form").forEach(form => {
        form.style.display = "none";
    });

    const form = document.getElementById(`reply-form-${commentId}`);
    if (form) form.style.display = "block";
}

function toggleReply(id) {
    const el = document.getElementById(`reply-form-${id}`);
    if (!el) return;
    el.style.display = el.style.display === "block" ? "none" : "block";
}

function toggleReplies(id) {
    const el = document.getElementById(`replies-${id}`);
    if (!el) return;
    el.style.display = el.style.display === "block" ? "none" : "block";
}


/* =========================
   メディアモーダル（共通）
========================= */

document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("media-modal");
    const content = document.getElementById("media-content");
    const closeBtn = document.querySelector(".media-close");

    if (!modal || !content) {
        console.error("media modal elements not found");
        return;
    }

    /* ===== モーダルを開く ===== */
    function openMedia({ url, type }) {
        content.innerHTML = "";

        if (type === "image") {
            const img = document.createElement("img");
            img.src = url;
            img.style.maxWidth = "100%";
            img.style.maxHeight = "90vh";
            img.style.objectFit = "contain";
            content.appendChild(img);
        }

        if (type === "video") {
            const video = document.createElement("video");
            video.src = url;
            video.controls = true;
            video.autoplay = true;
            video.playsInline = true;       // iOS対策
            video.preload = "metadata";     // ストリーミング
            video.style.width = "100%";
            video.style.maxHeight = "90vh";
            content.appendChild(video);
        }

        modal.style.display = "flex";
    }

    /* ===== モーダルを閉じる ===== */
    function closeMedia() {
        content.innerHTML = "";
        modal.style.display = "none";
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closeMedia);
    }

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeMedia();
        }
    });

    /* =========================
       クリックイベント（委譲）
    ========================= */
    document.addEventListener("click", (e) => {

        /* 動画を見る */
        const videoBtn = e.target.closest(".video-thumb");
        if (videoBtn) {
            const url = videoBtn.dataset.videoUrl;
            if (!url) return;

            openMedia({ url, type: "video" });
            return;
        }

        /* 画像クリック */
        const imgThumb = e.target.closest(".comment-media-thumb, .post-media-thumb");
        if (imgThumb) {
            const url = imgThumb.dataset.imageUrl || imgThumb.src;
            if (!url) return;

            openMedia({ url, type: "image" });
            return;
        }

        /* 閉じるボタン */
        if (e.target.classList.contains("media-close")) {
            closeMedia();
        }
    });
});