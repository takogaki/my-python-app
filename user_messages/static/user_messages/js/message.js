document.addEventListener("DOMContentLoaded", function () {

    const chatBox =
        document.getElementById("chat-box");

    const form =
        document.getElementById("chat-form");

    const input =
        document.getElementById("message-input");


    if (!chatBox) return;


    /* ==================================================
       初期スクロール
    ================================================== */

    chatBox.scrollTop =
        chatBox.scrollHeight;


    const username =
        chatBox.dataset.username;

    const currentUser =
        chatBox.dataset.currentUser;


    /* ==================================================
       プロフィールクリック
    ================================================== */

    chatBox.addEventListener(
        "click",
        function (e) {

            const target =
                e.target.closest(
                    ".chat-avatar, .chat-username"
                );

            if (!target) return;


            const url =
                target.dataset.url;

            if (!url) return;


            window.location.href = url;
        }
    );


    /* ==================================================
       WebSocket
    ================================================== */

    const protocol =
        window.location.protocol === "https:"
            ? "wss://"
            : "ws://";


    const socket =
        new WebSocket(
            protocol +
            window.location.host +
            "/ws/chat/" +
            username +
            "/"
        );


    /* ==================================================
       WebSocket状態
    ================================================== */

    socket.onopen =
        () => {

            console.log(
                "✅ WebSocket接続成功"
            );
        };


    socket.onerror =
        (e) => {

            console.error(
                "❌ WebSocketエラー",
                e
            );
        };


    socket.onclose =
        () => {

            console.log(
                "🔌 WebSocket切断"
            );
        };


    /* ==================================================
       受信
    ================================================== */

    socket.onmessage =
        function (e) {

            const data =
                JSON.parse(e.data);


            if (
                data.type ===
                "notification"
            ) {
                return;
            }


            if (
                data.type !==
                "chat"
            ) {
                return;
            }


            const isMine =
                data.sender ===
                currentUser;


            /* ==================================================
               行
            ================================================== */

            const row =
                document.createElement("div");

            row.className =
                `chat-row ${
                    isMine
                        ? "my-row"
                        : "other-row"
                }`;


            /* ==================================================
               アバター
            ================================================== */

            const avatar =
                document.createElement("img");

            avatar.src =
                data.image_url ||
                "/static/accounts/img/default_avatar.png";

            avatar.className =
                "chat-avatar";


            /* ==================================================
               ユーザー名
            ================================================== */

            const usernameEl =
                document.createElement("a");

            usernameEl.className =
                "chat-username";

            usernameEl.textContent =
                data.sender;


            /* ==================================================
               プロフィール
            ================================================== */

            const goProfile =
                () => {

                    if (
                        data.sender ===
                        currentUser
                    ) {

                        window.location.href =
                            "/accounts/mypage/";

                    } else {

                        window.location.href =
                            `/accounts/user/${data.sender}/`;
                    }
                };


            avatar.addEventListener(
                "click",
                goProfile
            );


            usernameEl.addEventListener(
                "click",
                function (e) {

                    e.preventDefault();

                    goProfile();
                }
            );


            /* ==================================================
               ラッパー
            ================================================== */

            const wrapper =
                document.createElement("div");

            wrapper.className =
                "chat-bubble-wrapper";


            wrapper.appendChild(
                usernameEl
            );


            /* ==================================================
               バブル
            ================================================== */

            const bubble =
                document.createElement("div");

            bubble.className =
                `chat-bubble ${
                    isMine
                        ? "my-bubble"
                        : "other-bubble"
                }`;

            bubble.textContent =
                data.message;


            wrapper.appendChild(
                bubble
            );


            /* ==================================================
               メタ
            ================================================== */

            const meta =
                document.createElement("div");

            meta.className =
                "chat-meta";


            const time =
                document.createElement("span");

            time.className =
                "chat-time";


            if (data.sent_at) {

                const date =
                    new Date(
                        data.sent_at
                    );

                time.textContent =
                    date.toLocaleTimeString(
                        "ja-JP",
                        {
                            hour: "2-digit",
                            minute: "2-digit",
                            hour12: false
                        }
                    );
            }


            meta.appendChild(
                time
            );


            if (isMine) {

                const read =
                    document.createElement("span");


                if (data.is_read) {

                    read.className =
                        "read-status read";

                    read.textContent =
                        "既読";

                } else {

                    read.className =
                        "read-status unread";

                    read.textContent =
                        "";
                }


                meta.appendChild(
                    read
                );
            }


            wrapper.appendChild(
                meta
            );


            /* ==================================================
               DOM
            ================================================== */

            row.appendChild(
                avatar
            );

            row.appendChild(
                wrapper
            );

            chatBox.appendChild(
                row
            );


            /* ==================================================
               最下部
            ================================================== */

            chatBox.scrollTop =
                chatBox.scrollHeight;
        };


    /* ==================================================
       送信
    ================================================== */

    form.addEventListener(
        "submit",
        function (e) {

            e.preventDefault();


            const message =
                input.value.trim();


            if (!message) return;


            if (
                socket.readyState ===
                WebSocket.OPEN
            ) {

                socket.send(
                    JSON.stringify({
                        message: message
                    })
                );

            } else {

                console.error(
                    "WebSocket未接続"
                );

                return;
            }


            input.value = "";

            input.focus();
        }
    );

});


/* ==================================================
   ページロード後に最下部
================================================== */

window.addEventListener(
    "load",
    function () {

        const chatBox =
            document.getElementById(
                "chat-box"
            );


        if (!chatBox) return;


        setTimeout(
            () => {

                chatBox.scrollTop =
                    chatBox.scrollHeight;

            },
            100
        );
    }
);


/* ==================================================
📱 DMチャット
募集チャットと同じキーボード対応
================================================== */

(function () {

    function updateChatViewport() {

        if (!window.visualViewport) {
            return;
        }


        const viewport =
            window.visualViewport;


        /* ==================================================
           キーボード高さ
        ================================================== */

        const keyboardHeight =
            Math.max(
                0,
                window.innerHeight
                - viewport.height
                - viewport.offsetTop
            );


        /* ==================================================
           CSSへ渡す
        ================================================== */

        document.documentElement.style.setProperty(
            "--chat-keyboard-height",
            keyboardHeight + "px"
        );


        console.log(
            "📱 DM Chat viewport:",
            {
                viewportHeight:
                    viewport.height,

                windowHeight:
                    window.innerHeight,

                keyboardHeight:
                    keyboardHeight
            }
        );
    }


    /* ==================================================
       初期計算
    ================================================== */

    updateChatViewport();


    /* ==================================================
       visualViewport
    ================================================== */

    if (window.visualViewport) {

        window.visualViewport.addEventListener(
            "resize",
            updateChatViewport
        );

        window.visualViewport.addEventListener(
            "scroll",
            updateChatViewport
        );
    }


    /* ==================================================
       通常resize
    ================================================== */

    window.addEventListener(
        "resize",
        updateChatViewport
    );


    /* ==================================================
       入力欄フォーカス
    ================================================== */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            const input =
                document.getElementById(
                    "message-input"
                );


            if (!input) return;


            input.addEventListener(
                "focus",
                function () {

                    setTimeout(
                        updateChatViewport,
                        100
                    );

                    setTimeout(
                        updateChatViewport,
                        300
                    );

                    setTimeout(
                        updateChatViewport,
                        500
                    );
                }
            );


            input.addEventListener(
                "blur",
                function () {

                    setTimeout(
                        updateChatViewport,
                        300
                    );
                }
            );

        }
    );

})();