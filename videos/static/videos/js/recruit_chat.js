    console.log("🔥 RECRUIT CHAT JS START");


    document.addEventListener(
        "DOMContentLoaded",
        function () {

            console.log(
                "🔥 RECRUIT CHAT DOM LOADED"
            );


            /* ==================================================
               基本情報
            ================================================== */

            const recruitId =
                "{{ recruit.id }}";

            const currentUserId =
                "{{ request.user.id }}";

            const currentUsername =
                "{{ request.user.username|escapejs }}";

            const currentUserProfileImage =
                "{% if request.user.get_profile_image %}{{ request.user.get_profile_image|escapejs }}{% endif %}";


            /* ==================================================
               DOM
            ================================================== */

            const messageContainer =
                document.getElementById(
                    "recruit-chat-messages"
                );

            const form =
                document.getElementById(
                    "recruit-chat-form"
                );

            const input =
                document.getElementById(
                    "recruit-chat-input"
                );

            const status =
                document.getElementById(
                    "recruit-chat-status"
                );


            if (!messageContainer) {
                console.error(
                    "❌ recruit-chat-messages が見つかりません"
                );
                return;
            }

            if (!form) {
                console.error(
                    "❌ recruit-chat-form が見つかりません"
                );
                return;
            }

            if (!input) {
                console.error(
                    "❌ recruit-chat-input が見つかりません"
                );
                return;
            }


            /* ==================================================
               URL
            ================================================== */

            function getUserDetailUrl(username) {

                if (!username) {
                    return "#";
                }

                return (
                    "/accounts/users/" +
                    encodeURIComponent(username) +
                    "/"
                );
            }


            /* ==================================================
               WebSocket
            ================================================== */

            const protocol =
                window.location.protocol === "https:"
                    ? "wss"
                    : "ws";

            const socketUrl =
                `${protocol}://${window.location.host}/ws/recruit/${recruitId}/`;

            console.log(
                "🔥 WebSocket URL =",
                socketUrl
            );

            const socket =
                new WebSocket(socketUrl);


            /* ==================================================
               接続成功
            ================================================== */

            socket.onopen =
                function () {

                    console.log(
                        "🟢 RECRUIT CHAT WEBSOCKET CONNECTED"
                    );

                    if (status) {
                        status.textContent =
                            "🟢 接続済み";
                    }

                };


            /* ==================================================
               メッセージ受信
            ================================================== */

            socket.onmessage =
                function (event) {

                    let data;

                    try {

                        data =
                            JSON.parse(
                                event.data
                            );

                    } catch (error) {

                        console.error(
                            "❌ JSON解析エラー:",
                            error
                        );

                        return;
                    }


                    /* 空メッセージ削除 */

                    const empty =
                        document.getElementById(
                            "recruit-chat-empty"
                        );

                    if (empty) {
                        empty.remove();
                    }


                    /* 自分か */

                    const mine =
                        String(data.user_id) ===
                        String(currentUserId);


                    /* 行 */

                    const row =
                        document.createElement("div");

                    row.className =
                        "recruit-chat-row " +
                        (
                            mine
                                ? "my-row"
                                : "other-row"
                        );


                    /* ==================================================
                       アバター
                    ================================================== */

                    let avatar;

                    if (data.profile_image) {

                        avatar =
                            document.createElement("img");

                        avatar.src =
                            data.profile_image;

                        avatar.alt =
                            data.username || "ユーザー";

                        avatar.className =
                            "recruit-chat-avatar";

                    } else {

                        avatar =
                            document.createElement("div");

                        avatar.className =
                            "recruit-chat-avatar recruit-chat-avatar-default";

                        avatar.textContent = "👤";

                    }


                    /* 相手 */

                    if (!mine) {

                        if (data.is_superuser) {

                            const avatarContainer =
                                document.createElement("div");

                            avatarContainer.className =
                                "recruit-chat-avatar-link";

                            avatarContainer.appendChild(
                                avatar
                            );

                            row.appendChild(
                                avatarContainer
                            );

                        } else {

                            const avatarLink =
                                document.createElement("a");

                            avatarLink.className =
                                "recruit-chat-avatar-link";

                            avatarLink.href =
                                getUserDetailUrl(
                                    data.username
                                );

                            avatarLink.appendChild(
                                avatar
                            );

                            row.appendChild(
                                avatarLink
                            );

                        }

                    }


                    /* ==================================================
                       吹き出し
                    ================================================== */

                    const bubbleWrapper =
                        document.createElement("div");

                    bubbleWrapper.className =
                        "recruit-chat-bubble-wrapper";


                    /* ユーザー名 */

                    if (!mine) {

                        let usernameElement;

                        if (data.is_superuser) {

                            usernameElement =
                                document.createElement("span");

                        } else {

                            usernameElement =
                                document.createElement("a");

                            usernameElement.href =
                                getUserDetailUrl(
                                    data.username
                                );
                        }

                        usernameElement.className =
                            "recruit-chat-username";

                        usernameElement.textContent =
                            data.username || "ユーザー";

                        bubbleWrapper.appendChild(
                            usernameElement
                        );
                    }


                    /* バブル */

                    const bubble =
                        document.createElement("div");

                    bubble.className =
                        "recruit-chat-bubble " +
                        (
                            mine
                                ? "my-bubble"
                                : "other-bubble"
                        );

                    bubble.textContent =
                        data.text || "";

                    bubbleWrapper.appendChild(
                        bubble
                    );


                    /* 時刻 */

                    const meta =
                        document.createElement("div");

                    meta.className =
                        "recruit-chat-meta";

                    const time =
                        document.createElement("span");

                    time.className =
                        "recruit-chat-time";

                    time.textContent =
                        data.created_at || "";

                    meta.appendChild(
                        time
                    );

                    bubbleWrapper.appendChild(
                        meta
                    );


                    row.appendChild(
                        bubbleWrapper
                    );


                    /* ==================================================
                       自分のアバター
                    ================================================== */

                    if (mine) {

                        let myAvatar;

                        if (currentUserProfileImage) {

                            myAvatar =
                                document.createElement("img");

                            myAvatar.src =
                                currentUserProfileImage;

                            myAvatar.alt =
                                currentUsername;

                            myAvatar.className =
                                "recruit-chat-avatar";

                        } else {

                            myAvatar =
                                document.createElement("div");

                            myAvatar.className =
                                "recruit-chat-avatar recruit-chat-avatar-default";

                            myAvatar.textContent =
                                "👤";

                        }


                        const myAvatarLink =
                            document.createElement("a");

                        myAvatarLink.className =
                            "recruit-chat-avatar-link";

                        myAvatarLink.href =
                            "{% url 'accounts:mypage' %}";

                        myAvatarLink.appendChild(
                            myAvatar
                        );

                        row.appendChild(
                            myAvatarLink
                        );

                    }


                    /* 追加 */

                    messageContainer.appendChild(
                        row
                    );


                    /* 最下部 */

                    messageContainer.scrollTop =
                        messageContainer.scrollHeight;

                };


            /* ==================================================
               WebSocketエラー
            ================================================== */

            socket.onerror =
                function (error) {

                    console.error(
                        "🔴 RECRUIT CHAT WEBSOCKET ERROR:",
                        error
                    );

                    if (status) {
                        status.textContent =
                            "🔴 接続エラー";
                    }

                };


            /* ==================================================
               WebSocket切断
            ================================================== */

            socket.onclose =
                function (event) {

                    console.log(
                        "🔴 RECRUIT CHAT WEBSOCKET CLOSED:",
                        event
                    );

                    if (status) {
                        status.textContent =
                            "🔴 接続が切断されました";
                    }

                };


            /* ==================================================
               送信
            ================================================== */

            form.addEventListener(
                "submit",
                function (event) {

                    event.preventDefault();

                    const text =
                        input.value.trim();

                    if (!text) {
                        return;
                    }

                    if (
                        socket.readyState !==
                        WebSocket.OPEN
                    ) {

                        alert(
                            "チャットサーバーに接続されていません。"
                        );

                        return;
                    }

                    socket.send(
                        JSON.stringify({
                            text: text
                        })
                    );

                    input.value = "";

                    input.focus();

                }
            );


            /* ==================================================
               初期スクロール
            ================================================== */

            messageContainer.scrollTop =
                messageContainer.scrollHeight;

        }
    );

    /* ==================================================
    募集チャット
    スマホキーボード対応
    Footerを常に表示領域内へ固定
    ================================================== */

    (function () {

        function adjustRecruitChatViewport() {

            if (!window.visualViewport) {
                return;
            }

            const viewport =
                window.visualViewport;

            const keyboardHeight =
                Math.max(
                    0,
                    window.innerHeight -
                    viewport.height -
                    viewport.offsetTop
                );

            document.documentElement
                .style
                .setProperty(
                    "--recruit-keyboard-height",
                    keyboardHeight + "px"
                );
        }


        if (window.visualViewport) {

            window.visualViewport.addEventListener(
                "resize",
                adjustRecruitChatViewport
            );

            window.visualViewport.addEventListener(
                "scroll",
                adjustRecruitChatViewport
            );
        }


        window.addEventListener(
            "resize",
            adjustRecruitChatViewport
        );


        document.addEventListener(
            "DOMContentLoaded",
            adjustRecruitChatViewport
        );


        adjustRecruitChatViewport();

    })();