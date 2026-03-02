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


document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener("click", function (e) {

        /* =========================
           親コメントへの返信
        ========================= */
        const replyBtn = e.target.closest(".reply-toggle");
        if (replyBtn) {
            const id = replyBtn.dataset.id;
            if (!id) return;

            const form = document.getElementById(
                `reply-form-comment-${id}`
            );
            if (!form) return;

            form.style.display =
                form.style.display === "block" ? "none" : "block";
            return;
        }

        /* =========================
           返信一覧の表示切り替え
        ========================= */
        const repliesBtn = e.target.closest(".replies-toggle");
        if (repliesBtn) {
            const id = repliesBtn.dataset.commentId;
            if (!id) return;

            const replies = document.getElementById(`replies-${id}`);
            if (!replies) return;

            replies.style.display =
                replies.style.display === "block" ? "none" : "block";
        }

    });

});

// blog 画像のモーダル表示
document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("media-modal");
    const content = document.getElementById("media-content");

    // 画像クリック
    document.querySelectorAll(".post-media-thumb, .comment-media-thumb").forEach(img => {
        img.addEventListener("click", () => {
            content.innerHTML = `<img src="${img.src}">`;
            modal.style.display = "flex";
        });
    });

    // モーダル閉じる
    modal.addEventListener("click", () => {
        modal.style.display = "none";
        content.innerHTML = "";
    });

});