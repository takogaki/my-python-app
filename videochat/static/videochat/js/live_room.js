/* ==================================================
   SPIRYTUS LIVE
   配信者側 WebRTC
================================================== */

(() => {

    "use strict";


    /* ==================================================
       CONFIG
    ================================================== */

    const config = window.LIVE_CONFIG;

    if (!config) {

        console.error(
            "[LIVE] LIVE_CONFIG がありません。"
        );

        return;
    }


    /* ==================================================
       STATE
    ================================================== */

    let socket = null;

    let socketChannelName = null;

    let localStream = null;

    let cameraEnabled = true;

    let microphoneEnabled = true;

    let currentViewerCount = 0;


    /*
     * 視聴者ごとのPeerConnection
     *
     * channel_name -> RTCPeerConnection
     */
    const peerConnections = new Map();


    /*
     * 視聴者情報
     *
     * channel_name -> {
     *     user_id,
     *     username
     * }
     */
    const viewers = new Map();


    /*
     * WebRTCのICE candidate保留
     *
     * remoteDescription設定前に
     * ICEが届いた場合に備える
     */
    const pendingIceCandidates = new Map();


    /* ==================================================
       DOM
    ================================================== */

    const localVideo =
        document.getElementById(
            "local-video"
        );


    const cameraPlaceholder =
        document.getElementById(
            "camera-placeholder"
        );


    const cameraToggle =
        document.getElementById(
            "camera-toggle"
        );


    const micToggle =
        document.getElementById(
            "mic-toggle"
        );


    const endLiveButton =
        document.getElementById(
            "end-live"
        );


    const commentForm =
        document.getElementById(
            "comment-form"
        );


    const commentInput =
        document.getElementById(
            "comment-input"
        );


    const commentsList =
        document.getElementById(
            "comments-list"
        );


    const viewerCount =
        document.getElementById(
            "viewer-count"
        );


    const requestsList =
        document.getElementById(
            "requests-list"
        );


    /* ==================================================
       WebRTC
    ================================================== */

    const rtcConfiguration = {

        iceServers: [

            {
                urls: [
                    "stun:stun.l.google.com:19302"
                ]
            }

        ]

    };


    /* ==================================================
       WebSocket
    ================================================== */

    function connectSocket() {

        console.log(
            "[LIVE] WebSocket connecting..."
        );


        socket =
            new WebSocket(
                config.websocketUrl
            );


        socket.onopen = () => {

            console.log(
                "[LIVE] WebSocket connected"
            );

            sendMessage({

                type:
                    "identify",

                role:
                    "host"

            });

        };


        socket.onmessage = async (
            event
        ) => {

            let data;


            try {

                data =
                    JSON.parse(
                        event.data
                    );

            } catch (error) {

                console.error(
                    "[LIVE] JSON error",
                    error
                );

                return;
            }


            console.log(
                "[LIVE] Received:",
                data
            );


            await handleSocketMessage(
                data
            );

        };


        socket.onclose = () => {

            console.log(
                "[LIVE] WebSocket closed"
            );

        };


        socket.onerror = (
            error
        ) => {

            console.error(
                "[LIVE] WebSocket error",
                error
            );

        };

    }


    /* ==================================================
       WebSocket message
    ================================================== */

    async function handleSocketMessage(
        data
    ) {


        /* ------------------------------------------
           Connection information
        ------------------------------------------ */

        if (
            data.type ===
            "connection_info"
        ) {

            socketChannelName =
                data.channel_name;


            console.log(
                "[LIVE] My channel:",
                socketChannelName
            );


            return;
        }


        /* ------------------------------------------
           Current viewers
        ------------------------------------------ */

        if (
            data.type ===
            "current_viewers"
        ) {

            console.log(
                "[LIVE] Current viewers:",
                data.viewers
            );


            if (
                Array.isArray(
                    data.viewers
                )
            ) {

                for (
                    const viewer
                    of data.viewers
                ) {

                    if (
                        !viewer.channel_name
                    ) {

                        continue;
                    }


                    viewers.set(
                        viewer.channel_name,
                        {
                            user_id:
                                viewer.user_id,

                            username:
                                viewer.username
                        }
                    );


                    /*
                     * 既存視聴者とのWebRTC開始
                     */
                    await createOfferForViewer(
                        viewer.channel_name
                    );

                }

            }


            updateViewerCount();


            return;
        }


        /* ------------------------------------------
           LIVE system
        ------------------------------------------ */

        if (
            data.type ===
            "live_system"
        ) {

            await handleSystemEvent(
                data
            );

            return;
        }


        /* ------------------------------------------
           WebRTC answer
        ------------------------------------------ */

        if (
            data.type ===
            "answer"
        ) {

            await handleAnswer(
                data
            );

            return;
        }


        /* ------------------------------------------
           WebRTC ICE
        ------------------------------------------ */

        if (
            data.type ===
            "ice-candidate"
        ) {

            await handleIceCandidate(
                data
            );

            return;
        }


        /* ------------------------------------------
           Comment
        ------------------------------------------ */

        if (
            data.type ===
            "comment"
        ) {

            addComment(
                data.username,
                data.text
            );

            return;
        }


        /* ------------------------------------------
           Participant request
        ------------------------------------------ */

        if (
            data.type ===
            "participant_request"
        ) {

            addParticipantRequest(
                data
            );

            return;
        }

    }


    /* ==================================================
       System event
    ================================================== */

    async function handleSystemEvent(
        data
    ) {


        /* ------------------------------------------
           Viewer joined
        ------------------------------------------ */

        if (
            data.event ===
            "viewer_joined"
        ) {

            /*
             * 自分自身を除外
             */
            if (
                data.channel_name ===
                socketChannelName
            ) {

                return;
            }


            /*
             * 配信者自身を除外
             */
            if (
                Number(data.user_id) ===
                Number(config.userId)
            ) {

                return;
            }


            if (
                !data.channel_name
            ) {

                return;
            }


            /*
             * すでに登録済みなら
             * 二重接続しない
             */
            const alreadyExists =
                viewers.has(
                    data.channel_name
                );


            viewers.set(
                data.channel_name,
                {
                    user_id:
                        data.user_id,

                    username:
                        data.username
                }
            );


            updateViewerCount();


            if (
                !alreadyExists &&
                data.username
            ) {

                addSystemMessage(
                    `${data.username} さんが参加しました`
                );

            }


            /*
             * WebRTC接続
             */
            if (
                !alreadyExists
            ) {

                await createOfferForViewer(
                    data.channel_name
                );

            }


            return;
        }


        /* ------------------------------------------
           Viewer left
        ------------------------------------------ */

        if (
            data.event ===
            "viewer_left"
        ) {

            if (
                data.channel_name
            ) {

                removeViewer(
                    data.channel_name
                );

            }

            return;
        }


        /* ------------------------------------------
           LIVE ended
        ------------------------------------------ */

        if (
            data.event ===
            "live_ended"
        ) {

            addSystemMessage(
                "LIVEが終了しました"
            );

        }

    }


    /* ==================================================
       Send WebSocket
    ================================================== */

    function sendMessage(
        data
    ) {

        if (
            !socket ||
            socket.readyState !==
            WebSocket.OPEN
        ) {

            console.warn(
                "[LIVE] Socket is not open"
            );

            return false;
        }


        socket.send(
            JSON.stringify(
                data
            )
        );


        return true;
    }


    /* ==================================================
       Camera / microphone
    ================================================== */

    async function startMedia() {

        try {

            localStream =
                await navigator
                    .mediaDevices
                    .getUserMedia({

                        video: true,

                        audio: true

                    });


            if (
                localVideo
            ) {

                localVideo.srcObject =
                    localStream;

            }


            cameraPlaceholder
                ?.classList
                .add(
                    "hidden"
                );


            console.log(
                "[LIVE] Media started"
            );


        } catch (error) {

            console.error(
                "[LIVE] Media error:",
                error
            );


            cameraPlaceholder
                ?.classList
                .remove(
                    "hidden"
                );


            alert(
                "カメラ・マイクを使用できませんでした。ブラウザの権限を確認してください。"
            );

        }

    }


    /* ==================================================
       Create PeerConnection
    ================================================== */

    function createPeerConnection(
        viewerChannel
    ) {

        /*
         * 既存接続を終了
         */
        if (
            peerConnections.has(
                viewerChannel
            )
        ) {

            try {

                peerConnections
                    .get(
                        viewerChannel
                    )
                    .close();

            } catch (error) {}

            peerConnections.delete(
                viewerChannel
            );

        }


        const pc =
            new RTCPeerConnection(
                rtcConfiguration
            );


        /* ------------------------------------------
           Local tracks
        ------------------------------------------ */

        if (
            localStream
        ) {

            localStream
                .getTracks()
                .forEach(
                    track => {

                        pc.addTrack(
                            track,
                            localStream
                        );

                    }
                );

        }


        /* ------------------------------------------
           ICE
        ------------------------------------------ */

        pc.onicecandidate = (
            event
        ) => {

            if (
                !event.candidate
            ) {

                return;
            }


            sendMessage({

                type:
                    "ice-candidate",

                target_channel:
                    viewerChannel,

                candidate:
                    event.candidate

            });

        };


        /* ------------------------------------------
           Connection state
        ------------------------------------------ */

        pc.onconnectionstatechange =
            () => {

                console.log(
                    "[LIVE] Viewer:",
                    viewerChannel,
                    "state:",
                    pc.connectionState
                );


                if (
                    pc.connectionState ===
                    "failed"
                ) {

                    removePeerConnection(
                        viewerChannel
                    );

                }

            };


        peerConnections.set(
            viewerChannel,
            pc
        );


        return pc;

    }


    /* ==================================================
       Create offer
    ================================================== */

    async function createOfferForViewer(
        viewerChannel
    ) {

        if (
            !localStream
        ) {

            console.warn(
                "[LIVE] localStream がありません"
            );

            return;

        }


        if (
            !viewerChannel
        ) {

            return;

        }


        console.log(
            "[LIVE] Creating offer:",
            viewerChannel
        );


        const pc =
            createPeerConnection(
                viewerChannel
            );


        try {

            const offer =
                await pc.createOffer();


            await pc.setLocalDescription(
                offer
            );


            sendMessage({

                type:
                    "offer",

                target_channel:
                    viewerChannel,

                sdp:
                    offer.sdp

            });


            console.log(
                "[LIVE] Offer sent:",
                viewerChannel
            );


        } catch (error) {

            console.error(
                "[LIVE] Offer error:",
                error
            );

        }

    }


    /* ==================================================
       Answer
    ================================================== */

    async function handleAnswer(
        data
    ) {

        const senderChannel =
            data.sender_channel;


        if (
            !senderChannel
        ) {

            return;
        }


        const pc =
            peerConnections.get(
                senderChannel
            );


        if (
            !pc
        ) {

            console.warn(
                "[LIVE] PeerConnection not found:",
                senderChannel
            );

            return;
        }


        if (
            !data.sdp
        ) {

            return;
        }


        try {

            await pc.setRemoteDescription({

                type:
                    "answer",

                sdp:
                    data.sdp

            });


            /*
             * 保留していたICEを追加
             */
            await flushPendingIceCandidates(
                senderChannel,
                pc
            );


            console.log(
                "[LIVE] Answer applied:",
                senderChannel
            );


        } catch (error) {

            console.error(
                "[LIVE] Answer error:",
                error
            );

        }

    }


    /* ==================================================
       ICE candidate
    ================================================== */

    async function handleIceCandidate(
        data
    ) {

        const senderChannel =
            data.sender_channel;


        if (
            !senderChannel ||
            !data.candidate
        ) {

            return;
        }


        const pc =
            peerConnections.get(
                senderChannel
            );


        /*
         * PeerConnectionがまだない場合
         */
        if (
            !pc
        ) {

            storePendingIceCandidate(
                senderChannel,
                data.candidate
            );

            return;
        }


        /*
         * RemoteDescriptionがまだない場合
         */
        if (
            !pc.remoteDescription
        ) {

            storePendingIceCandidate(
                senderChannel,
                data.candidate
            );

            return;
        }


        try {

            await pc.addIceCandidate(
                new RTCIceCandidate(
                    data.candidate
                )
            );

        } catch (error) {

            console.error(
                "[LIVE] ICE error:",
                error
            );

        }

    }


    /* ==================================================
       Pending ICE
    ================================================== */

    function storePendingIceCandidate(
        channel,
        candidate
    ) {

        if (
            !pendingIceCandidates.has(
                channel
            )
        ) {

            pendingIceCandidates.set(
                channel,
                []
            );

        }


        pendingIceCandidates
            .get(channel)
            .push(candidate);

    }


    async function flushPendingIceCandidates(
        channel,
        pc
    ) {

        const candidates =
            pendingIceCandidates.get(
                channel
            );


        if (
            !candidates ||
            !candidates.length
        ) {

            return;
        }


        for (
            const candidate
            of candidates
        ) {

            try {

                await pc.addIceCandidate(
                    new RTCIceCandidate(
                        candidate
                    )
                );

            } catch (error) {

                console.error(
                    "[LIVE] Pending ICE error:",
                    error
                );

            }

        }


        pendingIceCandidates.delete(
            channel
        );

    }


    /* ==================================================
       Remove viewer
    ================================================== */

    function removeViewer(
        viewerChannel
    ) {

        const viewer =
            viewers.get(
                viewerChannel
            );


        if (
            viewer
        ) {

            addSystemMessage(
                `${viewer.username} さんが退出しました`
            );

        }


        viewers.delete(
            viewerChannel
        );


        pendingIceCandidates.delete(
            viewerChannel
        );


        removePeerConnection(
            viewerChannel
        );


        updateViewerCount();

    }


    /* ==================================================
       Remove PeerConnection
    ================================================== */

    function removePeerConnection(
        viewerChannel
    ) {

        const pc =
            peerConnections.get(
                viewerChannel
            );


        if (
            pc
        ) {

            try {

                pc.close();

            } catch (error) {}

        }


        peerConnections.delete(
            viewerChannel
        );

    }


    /* ==================================================
       Camera toggle
    ================================================== */

    function toggleCamera() {

        if (
            !localStream
        ) {

            return;
        }


        const tracks =
            localStream.getVideoTracks();


        if (
            !tracks.length
        ) {

            return;
        }


        cameraEnabled =
            !cameraEnabled;


        tracks.forEach(
            track => {

                track.enabled =
                    cameraEnabled;

            }
        );


        if (
            cameraToggle
        ) {

            cameraToggle.textContent =
                cameraEnabled
                    ? "📹 カメラ"
                    : "🚫 カメラOFF";


            cameraToggle.classList.toggle(
                "off",
                !cameraEnabled
            );

        }


        cameraPlaceholder
            ?.classList
            .toggle(
                "hidden",
                cameraEnabled
            );

    }


    /* ==================================================
       Microphone toggle
    ================================================== */

    function toggleMicrophone() {

        if (
            !localStream
        ) {

            return;
        }


        const tracks =
            localStream.getAudioTracks();


        if (
            !tracks.length
        ) {

            return;
        }


        microphoneEnabled =
            !microphoneEnabled;


        tracks.forEach(
            track => {

                track.enabled =
                    microphoneEnabled;

            }
        );


        if (
            micToggle
        ) {

            micToggle.textContent =
                microphoneEnabled
                    ? "🎤 マイク"
                    : "🔇 マイクOFF";


            micToggle.classList.toggle(
                "off",
                !microphoneEnabled
            );

        }

    }


    /* ==================================================
       Comment
    ================================================== */

    function sendComment(
        text
    ) {

        sendMessage({

            type:
                "comment",

            text:
                text

        });

    }


    function addComment(
        username,
        text
    ) {

        if (
            !commentsList
        ) {

            return;
        }


        const item =
            document.createElement(
                "div"
            );


        item.className =
            "comment";


        const usernameElement =
            document.createElement(
                "span"
            );


        usernameElement.className =
            "comment-username";


        usernameElement.textContent =
            username;


        const textElement =
            document.createElement(
                "span"
            );


        textElement.textContent =
            text;


        item.appendChild(
            usernameElement
        );


        item.appendChild(
            textElement
        );


        commentsList.appendChild(
            item
        );


        commentsList.scrollTop =
            commentsList.scrollHeight;

    }


    function addSystemMessage(
        text
    ) {

        if (
            !commentsList
        ) {

            return;
        }


        const item =
            document.createElement(
                "div"
            );


        item.className =
            "comment-system";


        item.textContent =
            text;


        commentsList.appendChild(
            item
        );


        commentsList.scrollTop =
            commentsList.scrollHeight;

    }


    /* ==================================================
       Viewer count
    ================================================== */

    function updateViewerCount() {

        currentViewerCount =
            viewers.size;


        if (
            viewerCount
        ) {

            viewerCount.textContent =
                `👥 ${currentViewerCount}`;

        }

    }


    /* ==================================================
       Participant request
    ================================================== */

    function addParticipantRequest(
        data
    ) {

        if (
            !requestsList
        ) {

            return;
        }


        const empty =
            requestsList.querySelector(
                ".empty-request"
            );


        if (
            empty
        ) {

            empty.remove();

        }


        const wrapper =
            document.createElement(
                "div"
            );


        wrapper.className =
            "participant-request";


        const name =
            document.createElement(
                "span"
            );


        name.textContent =
            `${data.username} さん`;


        const button =
            document.createElement(
                "button"
            );


        button.type =
            "button";


        button.textContent =
            data.request_type ===
            "video"
                ? "📹 映像参加を許可"
                : "🎤 音声参加を許可";


        /*
         * ここではまだ許可処理本体は
         * Consumer側との仕様確定後に接続する
         */
        button.addEventListener(
            "click",
            () => {

                sendMessage({

                    type:
                        "approve_participation",

                    target_channel:
                        data.channel_name,

                    participation_type:
                        data.request_type

                });


                wrapper.remove();

            }
        );


        wrapper.appendChild(
            name
        );


        wrapper.appendChild(
            button
        );


        requestsList.appendChild(
            wrapper
        );

    }


    /* ==================================================
       End LIVE
    ================================================== */

    async function endLive() {

        const confirmed =
            window.confirm(
                "LIVEを終了しますか？"
            );


        if (
            !confirmed
        ) {

            return;
        }


        /*
         * WebSocket
         */
        sendMessage({

            type:
                "end_live"

        });


        try {

            const csrfToken =
                document.querySelector(
                    "[name=csrfmiddlewaretoken]"
                )?.value;


            await fetch(
                `/videochat/${config.roomSlug}/end/`,
                {

                    method:
                        "POST",

                    headers: {

                        "X-CSRFToken":
                            csrfToken

                    }

                }
            );


        } catch (error) {

            console.error(
                "[LIVE] End error:",
                error
            );


        } finally {

            /*
             * PeerConnection終了
             */

            peerConnections.forEach(
                pc => {

                    try {

                        pc.close();

                    } catch (error) {}

                }
            );


            peerConnections.clear();


            viewers.clear();


            pendingIceCandidates.clear();


            /*
             * Media停止
             */

            if (
                localStream
            ) {

                localStream
                    .getTracks()
                    .forEach(
                        track => {

                            track.stop();

                        }
                    );

            }


            /*
             * WebSocket終了
             */

            if (
                socket
            ) {

                try {

                    socket.close();

                } catch (error) {}

            }


            /*
             * LIVE一覧へ
             */

            window.location.href =
                "/videochat/";

        }

    }


    /* ==================================================
       Event listeners
    ================================================== */

    cameraToggle?.addEventListener(
        "click",
        toggleCamera
    );


    micToggle?.addEventListener(
        "click",
        toggleMicrophone
    );


    endLiveButton?.addEventListener(
        "click",
        endLive
    );


    commentForm?.addEventListener(
        "submit",
        event => {

            event.preventDefault();


            const text =
                commentInput
                    ?.value
                    .trim();


            if (
                !text
            ) {

                return;
            }


            sendComment(
                text
            );


            commentInput.value =
                "";

        }
    );


    /* ==================================================
       Initialize
    ================================================== */

    async function initialize() {

        /*
         * カメラ・マイクを先に取得
         */
        await startMedia();


        /*
         * Media取得後にWebSocket
         */
        connectSocket();

    }


    initialize();

})();