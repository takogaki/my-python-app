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

    let peerConnection = null;

    let myChannelName = null;

    let hostChannelName = null;


    let currentViewerCount = 0;


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

        socket =
            new WebSocket(
                config.websocketUrl
            );


        socket.onopen = () => {

            console.log(
                "[LIVE] WebSocket connected"
            );

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


            await handleMessage(
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
       Message handler
    ================================================== */

    async function handleMessage(
        data
    ) {


        /* ------------------------------------------
           Connection information
        ------------------------------------------ */

        if (
            data.type ===
            "connection_info"
        ) {

            myChannelName =
                data.channel_name;


            console.log(
                "[LIVE] My channel:",
                myChannelName
            );


            return;
        }


        /* ------------------------------------------
           WebRTC offer
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


        /* ------------------------------------------
           ICE candidate
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
           System
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
       Create PeerConnection
    ================================================== */

    function createPeerConnection() {

        if (
            peerConnection
        ) {

            peerConnection.close();

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


                remoteVideo
                    .play()
                    .catch(
                        error => {

                            console.log(
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
                    "[LIVE] Host channel not found"
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
                    state ===
                    "failed"
                ) {

                    videoPlaceholder
                        ?.classList
                        .remove(
                            "hidden"
                        );

                }


                if (
                    state ===
                    "closed"
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
       Handle offer
    ================================================== */

    async function handleOffer(
        data
    ) {

        console.log(
            "[LIVE] Offer received"
        );


        /*
         * Offerを送ってきた相手が
         * 配信者
         */

        hostChannelName =
            data.sender_channel;


        if (
            !hostChannelName
        ) {

            console.error(
                "[LIVE] sender_channel がありません"
            );

            return;
        }


        const pc =
            createPeerConnection();


        try {

            await pc.setRemoteDescription({

                type:
                    "offer",

                sdp:
                    data.sdp

            });


            const answer =
                await pc.createAnswer();


            await pc.setLocalDescription(
                answer
            );


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
                "[LIVE] Offer handling error",
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
            !peerConnection
        ) {

            return;
        }


        if (
            !data.candidate
        ) {

            return;
        }


        /*
         * 配信者のchannelを覚える
         */

        if (
            data.sender_channel
        ) {

            hostChannelName =
                data.sender_channel;

        }


        try {

            await peerConnection
                .addIceCandidate(
                    new RTCIceCandidate(
                        data.candidate
                    )
                );


        } catch (error) {

            console.error(
                "[LIVE] ICE error",
                error
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

        /*
         * 自分自身の参加通知は
         * 視聴者数に加えない
         */

        if (
            data.event ===
            "viewer_joined"
        ) {

            if (
                data.channel_name ===
                myChannelName
            ) {

                return;
            }


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


        if (
            data.event ===
            "viewer_left"
        ) {

            if (
                data.channel_name ===
                myChannelName
            ) {

                return;
            }


            currentViewerCount--;


            if (
                currentViewerCount <
                0
            ) {

                currentViewerCount = 0;

            }


            updateViewerCount();


            return;
        }


        if (
            data.event ===
            "live_ended"
        ) {

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

        /*
         * 今回はこちらをWebSocket方式に統一
         */

        sendMessage({

            type:
                type === "audio"
                    ? "request_audio"
                    : "request_video"

        });


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
       Initialize
    ================================================== */

    function initialize() {

        connectSocket();

    }


    initialize();

})();