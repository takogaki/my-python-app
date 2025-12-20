function showReplyForm(commentId) {
    // すべての返信フォームを閉じる
    const allForms = document.querySelectorAll('.reply-form');
    allForms.forEach(form => form.style.display = 'none');

    // 指定された返信フォームを開く
    const form = document.getElementById('reply-form-' + commentId);
    if (form) {
        form.style.display = 'block';
    }
}





    function openMedia(url, type) {
        const modal = document.getElementById("media-modal");
        const content = document.getElementById("media-content");

        if (!modal || !content) {
            console.error("media modal not found");
            return;
        }

        content.innerHTML = "";

        if (type === "image") {
            content.innerHTML = `<img src="${url}" style="max-width:90vw; max-height:90vh;">`;
        } else {
            content.innerHTML = `<video src="${url}" controls autoplay style="max-width:90vw; max-height:90vh;"></video>`;
        }

        modal.style.display = "flex";
    }

    function closeMedia() {
        const modal = document.getElementById("media-modal");
        const content = document.getElementById("media-content");
        if (!modal || !content) return;

        content.innerHTML = "";
        modal.style.display = "none";
    }




    function toggleReply(id) {
        const el = document.getElementById(`reply-form-${id}`);
        el.style.display = el.style.display === "none" ? "block" : "none";
    }
            function toggleReplies(id) {
    const el = document.getElementById(`replies-${id}`);
    if (!el) return;
    el.style.display = el.style.display === "none" ? "block" : "none";
}


    function openMedia(url, type) {
        const modal = document.getElementById("media-modal");
        const content = document.getElementById("media-content");

        content.innerHTML = "";

        if (type === "image") {
            content.innerHTML = `<img src="${url}">`;
        } else {
            content.innerHTML = `<video src="${url}" controls autoplay></video>`;
        }

        modal.style.display = "flex";
    }

    function closeMedia() {
        const modal = document.getElementById("media-modal");
        const content = document.getElementById("media-content");

        content.innerHTML = "";
        modal.style.display = "none";
    }





document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("media-modal");
    const content = document.getElementById("media-content");
    const closeBtn = document.querySelector(".media-close");

    if (!modal || !content || !closeBtn) return;

    /* =========================
       動画クリック → 初ロード
    ========================= */
    document.querySelectorAll(".video-thumb").forEach(el => {
        el.addEventListener("click", () => {

            const url = el.dataset.videoUrl;
            if (!url) return;

            content.innerHTML = "";

            const video = document.createElement("video");
            video.controls = true;
            video.autoplay = true;
            video.playsInline = true;   // iOS対策
            video.preload = "metadata"; // 最低限
            video.src = url;            // ← クリック時にロード開始

            content.appendChild(video);
            modal.style.display = "flex";
        });
    });

    /* =========================
       モーダルを閉じる
    ========================= */
    function closeModal() {
        content.innerHTML = "";
        modal.style.display = "none";
    }

    closeBtn.addEventListener("click", closeModal);

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
});