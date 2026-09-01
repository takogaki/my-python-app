/* ==================================================
   SPIRYTUS LIVE
   視聴者側 WebRTC
================================================== */

(() => {

    "use strict";


    /* ==================================================
       CONFIG
    ================================================== */

    const config =
        window.LIVE_CONFIG;


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

    let hostChannelName = null;

    let peerConnection = null;

    let currentViewerCount = 0;

    let liveEnded = false;


    /*
     * 配信者からICEが
     * RemoteDescription設定前に届いた場合に保留
     */
    const pendingIceCandidates = [];


    /* ==================================================
       DOM
    ================================================== */

    const remoteVideo =
        document.getElementById(
            "remote-video"
        );


    const videoPlaceholder =
        document.getElementById(
            "video-placeholder"
        );


    const viewerCount =
        document.getElementById(
            "viewer-count"
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


    const requestAudioButton =
        document.getElementById(
            "request-audio"
        );


    const requestVideoButton =
        document.getElementById(
            "request-video"
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


            /*
             * 視聴者として参加
             */
            sendMessage({

                type:
                    "identify",

                role:
                    "viewer"

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
                    "[LIVE] JSON error:",
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
                "[LIVE] WebSocket error:",
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
           WebRTC Offer
        ------------------------------------------ */

        if (
            data.type ===
            "offer"
        ) {

            await handleOffer(
                data
            );

            return;
        }

        /* ==================================================
        Participation approved
        ================================================== */

        async function handleParticipationApproved(
            data
        ) {

            const participationType =
                data.participation_type;


            const hostChannel =
                data.host_channel;


            if (
                !hostChannel
            ) {

                console.warn(
                    "[LIVE] Host channel がありません"
                );

                return;
            }


            console.log(
                "[LIVE] Participation approved:",
                participationType
            );


            /*
            * 配信者channelを保存
            */

            hostChannelName =
                hostChannel;


            /*
            * 現在のPeerConnectionがあれば
            * 一度終了
            */

            if (
                peerConnection
            ) {

                try {

                    peerConnection.close();

                } catch (error) {}

                peerConnection =
                    null;

            }


            /*
            * 視聴者側のカメラ・マイクを取得
            */

            try {

                const stream =
                    await navigator
                        .mediaDevices
                        .getUserMedia({

                            video:
                                participationType ===
                                "video",

                            audio:
                                true

                        });


                /*
                * 新しいPeerConnection
                */

                const pc =
                    createPeerConnection();


                /*
                * 自分の参加用Mediaを追加
                */

                stream
                    .getTracks()
                    .forEach(
                        track => {

                            pc.addTrack(
                                track,
                                stream
                            );

                        }
                    );


                /*
                * Offer作成
                */

                const offer =
                    await pc.createOffer();


                await pc.setLocalDescription(
                    offer
                );


                /*
                * 配信者へOffer
                */

                sendMessage({

                    type:
                        "offer",

                    target_channel:
                        hostChannelName,

                    sdp:
                        offer.sdp

                });


                console.log(
                    "[LIVE] Participation offer sent"
                );


            } catch (error) {

                console.error(
                    "[LIVE] Participation media error:",
                    error
                );


                alert(
                    "カメラ・マイクを使用できませんでした。"
                );

            }

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
        Participation approved
        ------------------------------------------ */

        if (
            data.type ===
            "participation_approved"
        ) {

            await handleParticipationApproved(
                data
            );

            return;
        }


        /* ------------------------------------------
           LIVE system
        ------------------------------------------ */

        if (
            data.type ===
            "live_system"
        ) {

            handleSystemEvent(
                data
            );

            return;
        }

    }


    /* ==================================================
       WebRTC PeerConnection
    ================================================== */

    function createPeerConnection() {

        /*
         * 既存接続があれば終了
         */
        if (
            peerConnection
        ) {

            try {

                peerConnection.close();

            } catch (error) {}

        }


        peerConnection =
            new RTCPeerConnection(
                rtcConfiguration
            );


        /* ------------------------------------------
           Remote stream
        ------------------------------------------ */

        peerConnection.ontrack = (
            event
        ) => {

            console.log(
                "[LIVE] Remote track received"
            );


            if (
                event.streams &&
                event.streams[0]
            ) {

                remoteVideo.srcObject =
                    event.streams[0];


                /*
                 * autoplay
                 */
                remoteVideo
                    .play()
                    .catch(
                        error => {

                            console.warn(
                                "[LIVE] Autoplay blocked:",
                                error
                            );

                        }
                    );


                videoPlaceholder
                    ?.classList
                    .add(
                        "hidden"
                    );

            }

        };


        /* ------------------------------------------
           ICE
        ------------------------------------------ */

        peerConnection.onicecandidate = (
            event
        ) => {

            if (
                !event.candidate
            ) {

                return;
            }


            if (
                !hostChannelName
            ) {

                console.warn(
                    "[LIVE] Host channel がありません"
                );

                return;
            }


            sendMessage({

                type:
                    "ice-candidate",

                target_channel:
                    hostChannelName,

                candidate:
                    event.candidate

            });

        };


        /* ------------------------------------------
           Connection state
        ------------------------------------------ */

        peerConnection.onconnectionstatechange =
            () => {

                if (
                    !peerConnection
                ) {

                    return;
                }


                const state =
                    peerConnection.connectionState;


                console.log(
                    "[LIVE] WebRTC state:",
                    state
                );


                if (
                    state ===
                    "connected"
                ) {

                    videoPlaceholder
                        ?.classList
                        .add(
                            "hidden"
                        );

                }


                if (
                    [
                        "failed",
                        "disconnected",
                        "closed"
                    ].includes(
                        state
                    )
                ) {

                    videoPlaceholder
                        ?.classList
                        .remove(
                            "hidden"
                        );

                }

            };


        return peerConnection;

    }


    /* ==================================================
       Handle Offer
    ================================================== */

    async function handleOffer(
        data
    ) {

        console.log(
            "[LIVE] Offer received"
        );


        /*
         * Offerを送ってきた相手 = 配信者
         */
        if (
            data.sender_channel
        ) {

            hostChannelName =
                data.sender_channel;

        }


        if (
            !hostChannelName
        ) {

            console.error(
                "[LIVE] 配信者channelがありません"
            );

            return;
        }


        if (
            !data.sdp
        ) {

            console.error(
                "[LIVE] SDPがありません"
            );

            return;
        }


        const pc =
            createPeerConnection();


        try {

            /*
             * 配信者のOfferを設定
             */
            await pc.setRemoteDescription({

                type:
                    "offer",

                sdp:
                    data.sdp

            });


            /*
             * 保留していたICEを追加
             */
            await flushPendingIceCandidates(
                pc
            );


            /*
             * Answer作成
             */
            const answer =
                await pc.createAnswer();


            /*
             * LocalDescription設定
             */
            await pc.setLocalDescription(
                answer
            );


            /*
             * 配信者へAnswer
             */
            sendMessage({

                type:
                    "answer",

                target_channel:
                    hostChannelName,

                sdp:
                    answer.sdp

            });


            console.log(
                "[LIVE] Answer sent"
            );


        } catch (error) {

            console.error(
                "[LIVE] Offer handling error:",
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

        if (
            data.sender_channel
        ) {

            hostChannelName =
                data.sender_channel;

        }


        if (
            !data.candidate
        ) {

            return;
        }


        /*
         * PeerConnectionがまだない
         */
        if (
            !peerConnection
        ) {

            pendingIceCandidates.push(
                data.candidate
            );

            return;
        }


        /*
         * RemoteDescriptionがまだない
         */
        if (
            !peerConnection.remoteDescription
        ) {

            pendingIceCandidates.push(
                data.candidate
            );

            return;
        }


        try {

            await peerConnection.addIceCandidate(
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

    async function flushPendingIceCandidates(
        pc
    ) {

        if (
            !pendingIceCandidates.length
        ) {

            return;
        }


        console.log(
            "[LIVE] Flushing ICE:",
            pendingIceCandidates.length
        );


        while (
            pendingIceCandidates.length
        ) {

            const candidate =
                pendingIceCandidates.shift();


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
       Comments
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

    function handleSystemEvent(
        data
    ) {


        /* ------------------------------------------
           自分の参加通知
        ------------------------------------------ */

        if (
            data.event ===
            "viewer_joined"
        ) {

            if (
                data.channel_name ===
                socketChannelName
            ) {

                return;
            }


            /*
             * 配信者自身は視聴者数に含めない
             */
            if (
                Number(data.user_id) ===
                Number(config.hostUserId)
            ) {

                return;
            }


            /*
             * viewer_joined は
             * 自分以外の視聴者が入った場合
             */
            currentViewerCount++;


            updateViewerCount();


            if (
                data.username
            ) {

                addSystemMessage(
                    `${data.username} さんが参加しました`
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
                data.channel_name ===
                socketChannelName
            ) {

                return;
            }


            currentViewerCount--;


            if (
                currentViewerCount < 0
            ) {

                currentViewerCount = 0;

            }


            updateViewerCount();


            return;
        }


        /* ------------------------------------------
           LIVE ended
        ------------------------------------------ */

        if (
            data.event ===
            "live_ended"
        ) {

            liveEnded =
                true;


            addSystemMessage(
                "配信が終了しました"
            );


            videoPlaceholder
                ?.classList
                .remove(
                    "hidden"
                );


            if (
                remoteVideo
            ) {

                remoteVideo.srcObject =
                    null;

            }


            if (
                peerConnection
            ) {

                try {

                    peerConnection.close();

                } catch (error) {}

                peerConnection =
                    null;

            }


            return;
        }

    }


    function updateViewerCount() {

        if (
            viewerCount
        ) {

            viewerCount.textContent =
                `👥 ${currentViewerCount}`;

        }

    }


    /* ==================================================
       Participation request
    ================================================== */

    function requestParticipation(
        type
    ) {

        if (
            liveEnded
        ) {

            alert(
                "このLIVEは終了しています。"
            );

            return;
        }


        const messageType =
            type === "audio"
                ? "request_audio"
                : "request_video";


        const sent =
            sendMessage({

                type:
                    messageType

            });


        if (
            !sent
        ) {

            alert(
                "LIVEへの接続が完了していません。"
            );

            return;
        }


        alert(
            type === "audio"
                ? "音声参加をリクエストしました。"
                : "映像参加をリクエストしました。"
        );

    }


    /* ==================================================
       Events
    ================================================== */

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


    requestAudioButton?.addEventListener(
        "click",
        () => {

            requestParticipation(
                "audio"
            );

        }
    );


    requestVideoButton?.addEventListener(
        "click",
        () => {

            requestParticipation(
                "video"
            );

        }
    );


    /* ==================================================
       Cleanup
    ================================================== */

    function cleanup() {

        if (
            peerConnection
        ) {

            try {

                peerConnection.close();

            } catch (error) {}

            peerConnection =
                null;

        }


        if (
            remoteVideo
        ) {

            remoteVideo.srcObject =
                null;

        }

    }


    window.addEventListener(
        "beforeunload",
        cleanup
    );


    /* ==================================================
       Initialize
    ================================================== */

    function initialize() {

        console.log(
            "[LIVE] Viewer initialize"
        );


        connectSocket();

    }


    initialize();

})();