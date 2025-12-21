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
   画像モーダル（共通）
========================= */

document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("media-modal");
    const content = document.getElementById("media-content");
    const closeBtn = document.querySelector(".media-close");

    // モーダルが存在しないページでは何もしない
    if (!modal || !content) return;

    /* ===== モーダルを開く（画像のみ） ===== */
    function openImage(url) {
        content.innerHTML = "";

        const img = document.createElement("img");
        img.src = url;
        img.alt = "image preview";
        img.style.width = "100%";
        img.style.maxHeight = "90vh";
        img.style.objectFit = "contain";

        content.appendChild(img);
        modal.style.display = "flex";
    }

    /* ===== モーダルを閉じる ===== */
    function closeModal() {
        content.innerHTML = "";
        modal.style.display = "none";
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closeModal);
    }

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    /* =========================
       クリックイベント（委譲）
    ========================= */
    document.addEventListener("click", (e) => {

        // 画像サムネイル
        const imgThumb = e.target.closest(".comment-media-thumb, .post-media-thumb");
        if (imgThumb) {
            const url = imgThumb.dataset.imageUrl || imgThumb.src;
            if (!url) return;

            openImage(url);
        }

        // 閉じるボタン
        if (e.target.classList.contains("media-close")) {
            closeModal();
        }
    });
});