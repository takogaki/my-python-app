/* =========================================================
   SPIRYTUS BLOG JS
   Instagram × YouTube Style
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       返信フォーム
       ===================================================== */

    function closeAllReplyForms() {

        document
            .querySelectorAll(".reply-form")
            .forEach(function (form) {

                form.hidden = true;


                /*
                 * 返信先ユーザーIDをクリア
                 */
                const replyToInput =
                    form.querySelector(
                        'input[name="reply_to"]'
                    );

                if (replyToInput) {
                    replyToInput.value = "";
                }


                /*
                 * 「○○さんへの返信」をクリア
                 */
                const replyingTo =
                    form.querySelector(
                        ".replying-to"
                    );

                if (replyingTo) {

                    replyingTo.textContent = "";

                    replyingTo.hidden = true;

                }

            });

    }


    /* =====================================================
       返信ボタン
       ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const replyButton =
                event.target.closest(
                    ".reply-toggle"
                );


            if (replyButton) {

                event.preventDefault();


                const id =
                    replyButton.dataset.id;


                if (!id) {
                    return;
                }


                /*
                 * 対象コメントの返信フォーム
                 */
                const form =
                    document.getElementById(
                        "reply-form-comment-" + id
                    );


                if (!form) {
                    return;
                }


                /*
                 * 現在フォームが閉じているか
                 */
                const wasHidden =
                    form.hidden;


                /*
                 * 他の返信フォームを閉じる
                 */
                closeAllReplyForms();


                /*
                 * 同じボタンを再度押した場合
                 * → 閉じたまま
                 */
                if (!wasHidden) {
                    return;
                }


                /* =================================================
                   返信先ユーザー情報
                   ================================================= */

                /*
                 * DBに保存する値
                 *
                 * data-reply-to
                 * = comment.author.id
                 *
                 * 例：
                 * 15
                 */
                const replyUserId =
                    replyButton.dataset.replyTo || "";


                /*
                 * 画面表示用
                 *
                 * data-reply-username
                 *
                 * 例：
                 * takogaki1115
                 */
                let replyUsername =
                    replyButton.dataset.replyUsername || "";


                /*
                 * data-reply-username がない場合の
                 * 保険としてコメント欄から取得
                 */
                if (!replyUsername) {

                    const comment =
                        replyButton.closest(
                            ".youtube-comment"
                        );


                    if (comment) {

                        const author =
                            comment.querySelector(
                                ".comment-author"
                            );


                        if (author) {

                            replyUsername =
                                author.textContent.trim();

                        }

                    }

                }


                /* =================================================
                   hidden input にユーザーIDをセット
                   ================================================= */

                const replyToInput =
                    form.querySelector(
                        'input[name="reply_to"]'
                    );


                if (replyToInput) {

                    /*
                     * ここにはユーザー名ではなく
                     * ユーザーIDを入れる
                     */
                    replyToInput.value =
                        replyUserId;

                }


                /* =================================================
                   返信先表示
                   ================================================= */

                const replyingTo =
                    form.querySelector(
                        ".replying-to"
                    );


                if (
                    replyingTo &&
                    replyUsername
                ) {

                    replyingTo.textContent =
                        "@" +
                        replyUsername +
                        " への返信";

                    replyingTo.hidden =
                        false;

                }


                /* =================================================
                   フォーム表示
                   ================================================= */

                form.hidden =
                    false;


                /*
                 * textareaへフォーカス
                 */
                const textarea =
                    form.querySelector(
                        "textarea"
                    );


                if (textarea) {

                    setTimeout(
                        function () {

                            textarea.focus();

                        },
                        100
                    );

                }


                return;

            }


            /* =====================================================
               返信一覧
               ===================================================== */

            const repliesButton =
                event.target.closest(
                    ".replies-toggle"
                );


            if (repliesButton) {

                event.preventDefault();


                const id =
                    repliesButton.dataset.commentId;


                if (!id) {
                    return;
                }


                const replies =
                    document.getElementById(
                        "replies-" + id
                    );


                if (!replies) {
                    return;
                }


                const isHidden =
                    replies.hidden;


                replies.hidden =
                    !isHidden;


                /*
                 * aria-expandedを同期
                 */
                repliesButton.setAttribute(
                    "aria-expanded",
                    String(!replies.hidden)
                );


                return;

            }

        }
    );


    /* =====================================================
       画像モーダル
       ===================================================== */

    const modal =
        document.getElementById(
            "media-modal"
        );


    const modalContent =
        document.getElementById(
            "media-content"
        );


    const modalClose =
        document.querySelector(
            ".media-modal-close"
        );


    /* -----------------------------------------------------
       モーダルを開く
       ----------------------------------------------------- */

    function openMediaModal(image) {

        if (
            !modal ||
            !modalContent
        ) {
            return;
        }


        /*
         * 既存内容を削除
         */
        modalContent.innerHTML =
            "";


        /*
         * 新しい画像を作成
         */
        const newImage =
            document.createElement(
                "img"
            );


        newImage.src =
            image.currentSrc ||
            image.src;


        newImage.alt =
            image.alt ||
            "";


        modalContent.appendChild(
            newImage
        );


        /*
         * モーダル表示
         */
        modal.classList.add(
            "is-open"
        );


        modal.setAttribute(
            "aria-hidden",
            "false"
        );


        /*
         * 背景スクロール停止
         */
        document.body.style.overflow =
            "hidden";

    }


    /* -----------------------------------------------------
       モーダルを閉じる
       ----------------------------------------------------- */

    function closeMediaModal() {

        if (!modal) {
            return;
        }


        modal.classList.remove(
            "is-open"
        );


        modal.setAttribute(
            "aria-hidden",
            "true"
        );


        if (modalContent) {

            modalContent.innerHTML =
                "";

        }


        /*
         * 背景スクロール復元
         */
        document.body.style.overflow =
            "";

    }


    /* =====================================================
       投稿・コメント画像クリック
       ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const image =
                event.target.closest(
                    ".post-media-thumb, .comment-media-thumb"
                );


            if (!image) {
                return;
            }


            /*
             * 他のクリック処理への伝播を防止
             */
            event.stopPropagation();


            openMediaModal(image);

        }
    );


    /* =====================================================
       モーダル背景クリック
       ===================================================== */

    if (modal) {

        modal.addEventListener(
            "click",
            function (event) {

                /*
                 * 背景部分をクリック
                 */
                if (
                    event.target === modal
                ) {

                    closeMediaModal();

                }

            }
        );

    }


    /* =====================================================
       モーダル閉じるボタン
       ===================================================== */

    if (modalClose) {

        modalClose.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                closeMediaModal();

            }
        );

    }


    /* =====================================================
       ESCキー
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                modal.classList.contains(
                    "is-open"
                )
            ) {

                closeMediaModal();

            }

        }
    );


    /* =====================================================
       SNS埋め込み再処理
       ===================================================== */

    function reloadSocialEmbeds() {


        /* -------------------------------------------------
           Instagram
           ------------------------------------------------- */

        if (
            window.instgrm &&
            window.instgrm.Embeds &&
            typeof window.instgrm.Embeds.process ===
                "function"
        ) {

            window.instgrm.Embeds.process();

        }


        /* -------------------------------------------------
           X / Twitter
           ------------------------------------------------- */

        if (
            window.twttr &&
            window.twttr.widgets &&
            typeof window.twttr.widgets.load ===
                "function"
        ) {

            window.twttr.widgets.load();

        }

    }


    /*
     * 外部Script読み込み後に実行
     */
    setTimeout(
        reloadSocialEmbeds,
        800
    );


    /* =====================================================
       投稿メニュー
       ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const menuButton =
                event.target.closest(
                    ".post-menu-button"
                );


            if (!menuButton) {
                return;
            }


            /*
             * 現在の既存機能は変更しない
             */

        }
    );


});

// ==============================
// 返信件数の開閉
// ==============================

document.querySelectorAll(".reply-count-toggle").forEach((button) => {
    button.addEventListener("click", () => {
        const commentId = button.dataset.id;
        const replies = document.getElementById(`replies-${commentId}`);

        if (!replies) return;

        replies.hidden = !replies.hidden;
    });
});

// ==============================
// 投稿メニュー・通報フォーム
// ==============================

document.addEventListener("DOMContentLoaded", function () {

    const menus = document.querySelectorAll(".post-menu");

    function closeAllMenus() {

        document.querySelectorAll(".post-menu-dropdown").forEach(function (dropdown) {
            dropdown.hidden = true;
        });

        document.querySelectorAll(".post-menu-button").forEach(function (button) {
            button.setAttribute("aria-expanded", "false");
        });

    }


    menus.forEach(function (menu) {

        const menuButton = menu.querySelector(".post-menu-button");
        const dropdown = menu.querySelector(".post-menu-dropdown");
        const reportButton = menu.querySelector(".report-menu-open");
        const reportForm = menu.querySelector(".post-report-form");

        if (!menuButton || !dropdown) {
            return;
        }


        // ⋯ メニューの開閉
        menuButton.addEventListener("click", function (event) {

            event.preventDefault();
            event.stopPropagation();

            const isClosed = dropdown.hidden;

            closeAllMenus();

            if (isClosed) {
                dropdown.hidden = false;
                menuButton.setAttribute("aria-expanded", "true");
            }

        });


        // 通報ボタン
        if (reportButton && reportForm) {

            reportButton.addEventListener("click", function (event) {

                event.preventDefault();
                event.stopPropagation();

                // 通報フォームを表示
                reportForm.hidden = false;

                // 通報ボタンを非表示
                reportButton.hidden = true;

            });


            // フォーム内のクリックではメニューを閉じない
            reportForm.addEventListener("click", function (event) {

                event.stopPropagation();

            });

        }

    });


    // メニュー外をクリックした場合のみ閉じる
    document.addEventListener("click", function (event) {

        if (!event.target.closest(".post-menu")) {
            closeAllMenus();
        }

    });

});