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