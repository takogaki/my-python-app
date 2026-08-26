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

    let localStream = null;

    let cameraEnabled = true;

    let microphoneEnabled = true;


    /*
     * 視聴者ごとのPeerConnection
     *
     * {
     *     channel_name: RTCPeerConnection
     * }
     */
    const peerConnections = new Map();


    /*
     * 視聴者情報
     *
     * {
     *     channel_name: {
     *         user_id,
     *         username
     *     }
     * }
     */
    const viewers = new Map();


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

        socket = new WebSocket(
            config.websocketUrl
        );


        socket.onopen = () => {

            console.log(
                "[LIVE] WebSocket connected"
            );


            /*
             * 接続後、現在の視聴者へ
             * 接続情報を要求
             */
            sendMessage({
                type: "request_viewers"
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
           自分の接続情報
        ------------------------------------------ */

        if (
            data.type ===
            "connection_info"
        ) {

            console.log(
                "[LIVE] Connection info:",
                data
            );

            return;
        }


        /* ------------------------------------------
           視聴者参加
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
           コメント
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
           参加リクエスト
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
             * 自分自身のjoin通知は無視
             */
            if (
                data.channel_name ===
                socketChannelName
            ) {

                return;
            }


            /*
             * 配信者自身の通知は無視
             */
            if (
                Number(data.user_id) ===
                Number(config.userId)
            ) {

                return;
            }


            if (
                data.channel_name
            ) {

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


                addSystemMessage(
                    `${data.username} さんが参加しました`
                );


                /*
                 * 視聴者とのWebRTC接続開始
                 */
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
       Own WebSocket channel
    ================================================== */

    let socketChannelName = null;


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

            return false;
        }


        socket.send(
            JSON.stringify(data)
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


            localVideo.srcObject =
                localStream;


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
                "[LIVE] Media error",
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
         * 既存接続があれば終了
         */
        if (
            peerConnections.has(
                viewerChannel
            )
        ) {

            peerConnections
                .get(
                    viewerChannel
                )
                .close();


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

        if (localStream) {

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
           ICE candidate
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
                    [
                        "failed",
                        "closed",
                        "disconnected"
                    ].includes(
                        pc.connectionState
                    )
                ) {

                    /*
                     * disconnected は
                     * 一時的な場合もあるため、
                     * Mapからは即削除しない。
                     */

                    if (
                        pc.connectionState ===
                        "failed"
                    ) {

                        removePeerConnection(
                            viewerChannel
                        );

                    }

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


        console.log(
            "[LIVE] Creating offer for:",
            viewerChannel
        );


        const pc =
            createPeerConnection(
                viewerChannel
            );


        try {

            const offer =
                await pc.createOffer({

                    offerToReceiveAudio:
                        false,

                    offerToReceiveVideo:
                        false

                });


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

            console.warn(
                "[LIVE] Answer sender_channel がありません"
            );

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


        try {

            await pc.setRemoteDescription({

                type:
                    "answer",

                sdp:
                    data.sdp

            });


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
            !senderChannel
        ) {

            return;
        }


        const pc =
            peerConnections.get(
                senderChannel
            );


        if (
            !pc ||
            !data.candidate
        ) {

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
       Remove viewer
    ================================================== */

    function removeViewer(
        viewerChannel
    ) {

        const viewer =
            viewers.get(
                viewerChannel
            );


        if (viewer) {

            addSystemMessage(
                `${viewer.username} さんが退出しました`
            );

        }


        viewers.delete(
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


        if (pc) {

            try {

                pc.close();

            } catch (error) {

                console.error(
                    "[LIVE] Peer close error:",
                    error
                );

            }

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


        if (cameraToggle) {

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


        if (micToggle) {

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
                "[LIVE] End error",
                error
            );


        } finally {

            /*
             * 全PeerConnection終了
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


            /*
             * カメラ・マイク停止
             */

            if (
                localStream
            ) {

                localStream
                    .getTracks()
                    .forEach(
                        track =>
                            track.stop()
                    );

            }


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
         * 先にカメラを取得
         */
        await startMedia();


        /*
         * その後WebSocket
         */
        connectSocket();

    }


    initialize();

})();