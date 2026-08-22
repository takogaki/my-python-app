/* ==================================================
   SPIRYTUS RANDOM CALL
   本番用 WebRTC 統合版
   - 音声通話
   - カメラON/OFF
   - マイクON/OFF
   - スピーカー
   - WebRTC Offer / Answer
   - ICE Candidate
   - Remote Video
================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* ==================================================
       DOM
    ================================================== */

    const callButton =
        document.getElementById("call-button");

    const cancelButton =
        document.getElementById("cancel-button");

    const leaveButton =
        document.getElementById("leave-button");

    const retryButton =
        document.getElementById("retry-button");

    const micButton =
        document.getElementById("mic-button");

    const cameraButton =
        document.getElementById("camera-button");

    const speakerButton =
        document.getElementById("speaker-button");

    const remoteAudio =
        document.getElementById("remote-audio");

    const videoArea =
        document.getElementById("video-area");

    const voiceCallScreen =
        document.getElementById("voice-call-screen");

    const voiceCallStatus =
        document.getElementById("voice-call-status");

    const searchStatus =
        document.getElementById("search-status");

    const matchedStatus =
        document.getElementById("matched-status");

    const endedStatus =
        document.getElementById("ended-status");

    const videoPlaceholder =
        document.getElementById("video-placeholder");

    const remoteVideo =
        document.getElementById("remote-video");

    const localVideo =
        document.getElementById("local-video");


    /* ==================================================
       状態
    ================================================== */

    let currentState = "idle";

    let callId = null;

    let isInitiator = false;

    let peerConnection = null;

    let localStream = null;

    let remoteStream = null;

    let pendingIceCandidates = [];

    let isMicEnabled = true;

    let isCameraEnabled = false;

    let isSpeakerEnabled = false;


    /* ==================================================
       WebRTC設定
    ================================================== */

    const rtcConfiguration = {

        iceServers: [
            {
                urls: "stun:stun.l.google.com:19302"
            }
        ]

    };


    /* ==================================================
       WebSocket
    ================================================== */

    const protocol =
        window.location.protocol === "https:"
            ? "wss:"
            : "ws:";

    const socket =
        new WebSocket(
            `${protocol}//${window.location.host}/ws/random-call/`
        );


    /* ==================================================
       状態切り替え
    ================================================== */

    function showState(state) {

        currentState = state;

        document
            .querySelectorAll(".random-call-state")
            .forEach(element => {

                element.classList.remove(
                    "is-active"
                );

            });


        const target =
            document.getElementById(
                `state-${state}`
            );


        if (target) {

            target.classList.add(
                "is-active"
            );

        }

    }


    /* ==================================================
       Video Placeholder
    ================================================== */

    function hideVideoPlaceholder() {

        if (!videoPlaceholder) {
            return;
        }

        videoPlaceholder.style.display =
            "none";

    }


    function showVideoPlaceholder(
        message = "接続しています…"
    ) {

        if (!videoPlaceholder) {
            return;
        }


        videoPlaceholder.style.display =
            "flex";


        const text =
            videoPlaceholder.querySelector("p");


        if (text) {

            text.textContent =
                message;

        }

    }


    /* ==================================================
       Local Media
    ================================================== */

    async function getLocalMedia() {

        if (localStream) {

            return localStream;

        }


        try {

            localStream =
                await navigator.mediaDevices.getUserMedia({

                    audio: true,

                    video: true

                });


            /* ------------------------------------------
               初期状態ではカメラOFF
            ------------------------------------------ */

            const videoTracks =
                localStream.getVideoTracks();


            videoTracks.forEach(track => {

                track.enabled = false;

            });


            /* ------------------------------------------
               自分の映像
            ------------------------------------------ */

            if (localVideo) {

                localVideo.srcObject =
                    localStream;

                localVideo.muted = true;

                localVideo.playsInline = true;

                try {

                    await localVideo.play();

                } catch (error) {

                    console.warn(
                        "Local video autoplay:",
                        error
                    );

                }

            }


            console.log(
                "RANDOM CALL: Local media ready"
            );


            return localStream;

        } catch (error) {

            console.error(
                "RANDOM CALL: getUserMedia error",
                error
            );


            if (matchedStatus) {

                if (
                    error.name ===
                    "NotAllowedError"
                ) {

                    matchedStatus.textContent =
                        "カメラとマイクの使用を許可してください。";

                } else {

                    matchedStatus.textContent =
                        "カメラ・マイクを取得できませんでした。";

                }

            }


            throw error;

        }

    }


    /* ==================================================
       Remote Stream 初期化
    ================================================== */

    function initializeRemoteStream() {

        remoteStream =
            new MediaStream();


        if (remoteVideo) {

            remoteVideo.srcObject =
                remoteStream;

            remoteVideo.autoplay = true;

            remoteVideo.playsInline = true;

        }


        if (remoteAudio) {

            remoteAudio.srcObject =
                remoteStream;

            remoteAudio.autoplay = true;

        }

    }


    /* ==================================================
       PeerConnection 作成
    ================================================== */

    async function createPeerConnection() {

        if (peerConnection) {

            return peerConnection;

        }


        console.log(
            "RANDOM CALL: Creating PeerConnection"
        );


        peerConnection =
            new RTCPeerConnection(
                rtcConfiguration
            );


        /* ------------------------------------------
           Local Media
        ------------------------------------------ */

        const stream =
            await getLocalMedia();


        /* ------------------------------------------
           ★重要
           音声・映像トラックを両方送信
        ------------------------------------------ */

        stream
            .getTracks()
            .forEach(track => {

                console.log(
                    "RANDOM CALL: Adding local track:",
                    track.kind,
                    track.id,
                    "enabled:",
                    track.enabled
                );


                peerConnection.addTrack(
                    track,
                    stream
                );

            });


        /* ------------------------------------------
           Remote Stream
        ------------------------------------------ */

        initializeRemoteStream();


        /* ==================================================
           Remote Track
        ================================================== */

        peerConnection.addEventListener(
            "track",
            async event => {

                console.log(
                    "RANDOM CALL: Remote track received:",
                    event.track.kind,
                    event.track.id
                );


                /* --------------------------------------
                   event.streams が存在する場合
                -------------------------------------- */

                if (
                    event.streams &&
                    event.streams[0]
                ) {

                    const incomingStream =
                        event.streams[0];


                    incomingStream
                        .getTracks()
                        .forEach(track => {

                            const exists =
                                remoteStream
                                    .getTracks()
                                    .some(
                                        existing =>
                                            existing.id ===
                                            track.id
                                    );


                            if (!exists) {

                                remoteStream.addTrack(
                                    track
                                );

                            }

                        });

                } else {

                    /*
                     * 念のため event.streams が
                     * 無い場合にも対応
                     */

                    const exists =
                        remoteStream
                            .getTracks()
                            .some(
                                existing =>
                                    existing.id ===
                                    event.track.id
                            );


                    if (!exists) {

                        remoteStream.addTrack(
                            event.track
                        );

                    }

                }


                /* --------------------------------------
                   Remote Video
                -------------------------------------- */

                if (
                    event.track.kind ===
                    "video"
                ) {

                    console.log(
                        "RANDOM CALL: Remote VIDEO received"
                    );


                    if (videoArea) {

                        videoArea.classList.add(
                            "remote-video-active"
                        );

                    }


                    if (remoteVideo) {

                        remoteVideo.srcObject =
                            remoteStream;

                        remoteVideo.style.display =
                            "block";

                        try {

                            await remoteVideo.play();

                        } catch (error) {

                            console.warn(
                                "Remote video play error:",
                                error
                            );

                        }

                    }

                }


                /* --------------------------------------
                   Remote Audio
                -------------------------------------- */

                if (
                    event.track.kind ===
                    "audio"
                ) {

                    console.log(
                        "RANDOM CALL: Remote AUDIO received"
                    );


                    if (remoteAudio) {

                        remoteAudio.srcObject =
                            remoteStream;

                        try {

                            await remoteAudio.play();

                        } catch (error) {

                            console.warn(
                                "Remote audio play error:",
                                error
                            );

                        }

                    }

                }


                hideVideoPlaceholder();

            }
        );


        /* ==================================================
           ICE Candidate
        ================================================== */

        peerConnection.addEventListener(
            "icecandidate",
            event => {

                if (!event.candidate) {

                    return;

                }


                sendSignal({

                    type: "ice-candidate",

                    candidate:
                        event.candidate

                });

            }
        );


        /* ==================================================
           Connection State
        ================================================== */

        peerConnection.addEventListener(
            "connectionstatechange",
            () => {

                if (!peerConnection) {

                    return;

                }


                const state =
                    peerConnection.connectionState;


                console.log(
                    "RANDOM CALL: WebRTC connection state:",
                    state
                );


                if (
                    state === "connecting"
                ) {

                    if (matchedStatus) {

                        matchedStatus.textContent =
                            "相手と接続しています…";

                    }

                }


                if (
                    state === "connected"
                ) {

                    console.log(
                        "RANDOM CALL: WebRTC CONNECTED"
                    );


                    if (matchedStatus) {

                        matchedStatus.textContent =
                            "通話中です。";

                    }


                    hideVideoPlaceholder();

                }


                if (
                    state === "disconnected"
                ) {

                    if (matchedStatus) {

                        matchedStatus.textContent =
                            "接続が不安定です。";

                    }

                }


                if (
                    state === "failed"
                ) {

                    console.error(
                        "RANDOM CALL: WebRTC FAILED"
                    );


                    if (matchedStatus) {

                        matchedStatus.textContent =
                            "接続できませんでした。";

                    }

                }

            }
        );


        /* ==================================================
           ICE Connection State
        ================================================== */

        peerConnection.addEventListener(
            "iceconnectionstatechange",
            () => {

                if (!peerConnection) {

                    return;

                }


                console.log(
                    "RANDOM CALL: ICE state:",
                    peerConnection.iceConnectionState
                );

            }
        );


        return peerConnection;

    }


    /* ==================================================
       Signal送信
    ================================================== */

    function sendSignal(data) {

        if (
            socket.readyState !==
            WebSocket.OPEN
        ) {

            console.error(
                "RANDOM CALL: WebSocket is not open"
            );

            return;

        }


        socket.send(
            JSON.stringify({

                action: "signal",

                data: data

            })
        );

    }


    /* ==================================================
       Offer
    ================================================== */

    async function createOffer() {

        if (!peerConnection) {

            return;

        }


        try {

            console.log(
                "RANDOM CALL: Creating OFFER"
            );


            const offer =
                await peerConnection.createOffer();


            await peerConnection.setLocalDescription(
                offer
            );


            sendSignal({

                type: "offer",

                sdp:
                    peerConnection.localDescription

            });


            console.log(
                "RANDOM CALL: OFFER sent"
            );

        } catch (error) {

            console.error(
                "RANDOM CALL: Offer error:",
                error
            );

        }

    }


    /* ==================================================
       Answer
    ================================================== */

    async function createAnswer() {

        if (!peerConnection) {

            return;

        }


        try {

            console.log(
                "RANDOM CALL: Creating ANSWER"
            );


            const answer =
                await peerConnection.createAnswer();


            await peerConnection.setLocalDescription(
                answer
            );


            sendSignal({

                type: "answer",

                sdp:
                    peerConnection.localDescription

            });


            console.log(
                "RANDOM CALL: ANSWER sent"
            );

        } catch (error) {

            console.error(
                "RANDOM CALL: Answer error:",
                error
            );

        }

    }


    /* ==================================================
       ICE Candidate
    ================================================== */

    async function addIceCandidate(
        candidate
    ) {

        if (!candidate) {

            return;

        }


        if (!peerConnection) {

            pendingIceCandidates.push(
                candidate
            );

            return;

        }


        if (
            !peerConnection.remoteDescription
        ) {

            pendingIceCandidates.push(
                candidate
            );

            return;

        }


        try {

            await peerConnection.addIceCandidate(
                new RTCIceCandidate(
                    candidate
                )
            );


            console.log(
                "RANDOM CALL: ICE candidate added"
            );

        } catch (error) {

            console.error(
                "RANDOM CALL: ICE candidate error:",
                error
            );

        }

    }


    /* ==================================================
       保留ICE処理
    ================================================== */

    async function flushPendingIceCandidates() {

        if (
            !peerConnection ||
            !peerConnection.remoteDescription
        ) {

            return;

        }


        if (
            pendingIceCandidates.length === 0
        ) {

            return;

        }


        const candidates =
            [...pendingIceCandidates];


        pendingIceCandidates = [];


        console.log(
            "RANDOM CALL: Flushing ICE candidates:",
            candidates.length
        );


        for (
            const candidate of candidates
        ) {

            try {

                await peerConnection.addIceCandidate(
                    new RTCIceCandidate(
                        candidate
                    )
                );

            } catch (error) {

                console.error(
                    "RANDOM CALL: Pending ICE error:",
                    error
                );

            }

        }

    }


    /* ==================================================
       Signal処理
    ================================================== */

    async function handleSignal(data) {

        const signal =
            data.data;


        if (!signal) {

            return;

        }


        console.log(
            "RANDOM CALL: Signal:",
            signal.type
        );


        /* ==================================================
           OFFER
        ================================================== */

        if (
            signal.type === "offer"
        ) {

            try {

                await createPeerConnection();


                await peerConnection.setRemoteDescription(
                    new RTCSessionDescription(
                        signal.sdp
                    )
                );


                console.log(
                    "RANDOM CALL: Remote OFFER set"
                );


                await flushPendingIceCandidates();


                await createAnswer();

            } catch (error) {

                console.error(
                    "RANDOM CALL: Offer handling error:",
                    error
                );

            }


            return;

        }


        /* ==================================================
           ANSWER
        ================================================== */

        if (
            signal.type === "answer"
        ) {

            try {

                if (!peerConnection) {

                    await createPeerConnection();

                }


                await peerConnection.setRemoteDescription(
                    new RTCSessionDescription(
                        signal.sdp
                    )
                );


                console.log(
                    "RANDOM CALL: Remote ANSWER set"
                );


                await flushPendingIceCandidates();

            } catch (error) {

                console.error(
                    "RANDOM CALL: Answer handling error:",
                    error
                );

            }


            return;

        }


        /* ==================================================
           ICE
        ================================================== */

        if (
            signal.type === "ice-candidate"
        ) {

            await addIceCandidate(
                signal.candidate
            );

        }

    }


    /* ==================================================
       WebRTC開始
    ================================================== */

    async function startWebRTC(
        initiator
    ) {

        console.log(
            "RANDOM CALL: Starting WebRTC",
            {
                callId: callId,
                initiator: initiator
            }
        );


        showVideoPlaceholder(
            "カメラとマイクを準備しています…"
        );


        try {

            await createPeerConnection();


            if (initiator) {

                await createOffer();

            }

        } catch (error) {

            console.error(
                "RANDOM CALL: WebRTC start error:",
                error
            );


            if (matchedStatus) {

                matchedStatus.textContent =
                    "通話を開始できませんでした。";

            }

        }

    }


    /* ==================================================
       WebRTC終了
    ================================================== */

    function closePeerConnection() {

        console.log(
            "RANDOM CALL: Closing WebRTC"
        );


        if (peerConnection) {

            peerConnection.close();

            peerConnection = null;

        }


        if (remoteVideo) {

            remoteVideo.srcObject =
                null;

        }


        if (remoteAudio) {

            remoteAudio.srcObject =
                null;

        }


        if (videoArea) {

            videoArea.classList.remove(
                "remote-video-active"
            );

            videoArea.classList.remove(
                "camera-active"
            );

        }


        remoteStream = null;

        pendingIceCandidates = [];


        if (localStream) {

            localStream
                .getTracks()
                .forEach(track => {

                    track.stop();

                });

            localStream = null;

        }


        if (localVideo) {

            localVideo.srcObject =
                null;

        }


        showVideoPlaceholder(
            "接続しています…"
        );

    }


    /* ==================================================
       マイク
    ================================================== */

    function toggleMicrophone() {

        if (!localStream) {

            return;

        }


        const audioTracks =
            localStream.getAudioTracks();


        if (
            audioTracks.length === 0
        ) {

            return;

        }


        isMicEnabled =
            !isMicEnabled;


        audioTracks.forEach(track => {

            track.enabled =
                isMicEnabled;

        });


        if (micButton) {

            micButton.classList.toggle(
                "is-off",
                !isMicEnabled
            );


            micButton.textContent =
                isMicEnabled
                    ? "🎤"
                    : "🔇";

        }


        console.log(
            "RANDOM CALL: Microphone:",
            isMicEnabled
                ? "ON"
                : "OFF"
        );

    }


    /* ==================================================
    カメラ
    自分のカメラだけを制御
    ================================================== */

    function toggleCamera() {

        if (!localStream) {
            return;
        }


        const videoTracks =
            localStream.getVideoTracks();


        if (!videoTracks.length) {
            return;
        }


        /*
        * 自分のカメラ状態だけ反転
        */
        isCameraEnabled =
            !isCameraEnabled;


        /*
        * 自分のVideoTrackだけ変更
        */
        videoTracks.forEach(track => {

            track.enabled =
                isCameraEnabled;

        });


        /*
        * 自分の映像表示だけ変更
        *
        * remote-video には一切触れない
        */
        if (localVideo) {

            localVideo.style.display =
                isCameraEnabled
                    ? "block"
                    : "none";

        }


        /*
        * 自分の映像表示だけ変更
        */
        if (videoArea) {

            videoArea.classList.toggle(
                "camera-active",
                isCameraEnabled
            );

        }


        /* ==================================================
        通話中テキスト
        カメラON → 非表示
        カメラOFF → 表示
        ================================================== */

        const matchedIcon =
            document.querySelector(
                "#state-matched .matched-icon"
            );

        const matchedEyebrow =
            document.querySelector(
                "#state-matched .random-call-eyebrow"
            );

        const matchedTitle =
            document.querySelector(
                "#state-matched > h1"
            );

        const matchedDescription =
            document.querySelector(
                "#state-matched .random-call-description"
            );


        const matchedTextElements = [
            matchedIcon,
            matchedEyebrow,
            matchedTitle,
            matchedDescription
        ];


        matchedTextElements.forEach(element => {

            if (!element) {
                return;
            }

            element.style.display =
                isCameraEnabled
                    ? "none"
                    : "";

        });


        /*
        * ボタン
        */
        if (cameraButton) {

            cameraButton.classList.toggle(
                "is-off",
                !isCameraEnabled
            );


            cameraButton.classList.toggle(
                "is-active",
                isCameraEnabled
            );


            cameraButton.textContent =
                isCameraEnabled
                    ? "📹"
                    : "🚫";

        }


        console.log(
            "RANDOM CALL: My Camera:",
            isCameraEnabled
                ? "ON"
                : "OFF"
        );

    }


    /* ==================================================
    カメラ状態設定
    自分のカメラだけを制御
    ================================================== */

    function setCameraState(enabled) {

        isCameraEnabled =
            enabled;


        /*
        * localStream がまだない場合
        */
        if (!localStream) {
            return;
        }


        const videoTracks =
            localStream.getVideoTracks();


        /*
        * 自分のVideoTrackだけ変更
        */
        videoTracks.forEach(track => {

            track.enabled =
                enabled;

        });


        /*
        * 自分の映像だけ表示 / 非表示
        */
        if (localVideo) {

            localVideo.style.display =
                enabled
                    ? "block"
                    : "none";

        }


        /*
        * 自分のカメラ状態
        */
        if (videoArea) {

            videoArea.classList.toggle(
                "camera-active",
                enabled
            );

        }


        /*
        * ボタン
        */
        if (cameraButton) {

            cameraButton.classList.toggle(
                "is-off",
                !enabled
            );


            cameraButton.classList.toggle(
                "is-active",
                enabled
            );


            cameraButton.textContent =
                enabled
                    ? "📹"
                    : "🚫";

        }

    }


    /* ==================================================
    スピーカー
    安定版
    ================================================== */

    async function toggleSpeaker() {

        if (!remoteAudio) {
            console.warn(
                "RANDOM CALL: remoteAudio not found"
            );

            return;
        }


        /*
        * 現在の状態を反転
        */
        isSpeakerEnabled =
            !isSpeakerEnabled;


        /*
        * スピーカーON
        *
        * remoteAudio の音声を有効化
        */
        if (isSpeakerEnabled) {

            remoteAudio.muted = false;

            remoteAudio.volume = 1.0;

            try {

                await remoteAudio.play();

            } catch (error) {

                console.warn(
                    "RANDOM CALL: remoteAudio play:",
                    error
                );

            }

        }


        /*
        * スピーカーOFF
        *
        * 音声をミュート
        */
        else {

            remoteAudio.muted = true;

        }


        /*
        * UI更新
        */
        if (speakerButton) {

            speakerButton.classList.toggle(
                "is-active",
                isSpeakerEnabled
            );


            speakerButton.textContent =
                isSpeakerEnabled
                    ? "🔊"
                    : "🔈";

        }


        console.log(
            "RANDOM CALL: Speaker",
            isSpeakerEnabled
                ? "ON"
                : "OFF"
        );

    }


    /* ==================================================
       WebSocket OPEN
    ================================================== */

    socket.addEventListener(
        "open",
        () => {

            console.log(
                "RANDOM CALL: WebSocket connected."
            );

        }
    );


    /* ==================================================
       WebSocket MESSAGE
    ================================================== */

    socket.addEventListener(
        "message",
        async event => {

            let data;


            try {

                data =
                    JSON.parse(
                        event.data
                    );

            } catch (error) {

                console.error(
                    "RANDOM CALL: Invalid WebSocket message:",
                    event.data
                );

                return;

            }


            console.log(
                "RANDOM CALL: Received:",
                data
            );


            /* ==========================================
               Connected
            ========================================== */

            if (
                data.type === "connected"
            ) {

                console.log(
                    "RANDOM CALL: READY"
                );

                return;

            }


            /* ==========================================
               Waiting
            ========================================== */

            if (
                data.type === "waiting"
            ) {

                showState(
                    "searching"
                );


                if (searchStatus) {

                    searchStatus.textContent =
                        "SPIRYTUSにいる誰かを探しています。";

                }


                return;

            }


            /* ==========================================
               Already Waiting
            ========================================== */

            if (
                data.type ===
                "already_waiting"
            ) {

                showState(
                    "searching"
                );


                if (searchStatus) {

                    searchStatus.textContent =
                        data.message ||
                        "すでに相手を探しています。";

                }


                return;

            }


            /* ==========================================
               MATCHED
            ========================================== */

            if (
                data.type === "matched"
            ) {

                console.log(
                    "RANDOM CALL: MATCHED",
                    data
                );


                callId =
                    data.call_id;


                isInitiator =
                    data.is_initiator === true;


                showState(
                    "matched"
                );


                showVideoPlaceholder(
                    "カメラとマイクを準備しています…"
                );


                if (matchedStatus) {

                    matchedStatus.textContent =
                        "通話を開始しています。";

                }


                /*
                 * 初期状態
                 * カメラOFF
                 */

                isMicEnabled = true;

                setCameraState(false);


                /*
                 * WebRTC開始
                 */

                await startWebRTC(
                    isInitiator
                );


                return;

            }


            /* ==========================================
               CANCELLED
            ========================================== */

            if (
                data.type === "cancelled"
            ) {

                closePeerConnection();

                callId = null;

                showState(
                    "idle"
                );

                return;

            }


            /* ==========================================
               PARTNER LEFT
            ========================================== */

            if (
                data.type === "partner_left"
            ) {

                closePeerConnection();

                callId = null;

                showState(
                    "ended"
                );


                if (endedStatus) {

                    endedStatus.textContent =
                        "相手との通話が終了しました。";

                }


                return;

            }


            /* ==========================================
               LEFT
            ========================================== */

            if (
                data.type === "left"
            ) {

                closePeerConnection();

                callId = null;

                showState(
                    "ended"
                );


                if (endedStatus) {

                    endedStatus.textContent =
                        "通話が終了しました。";

                }


                return;

            }


            /* ==========================================
               ALREADY IN CALL
            ========================================== */

            if (
                data.type ===
                "already_in_call"
            ) {

                console.warn(
                    data.message
                );

                return;

            }


            /* ==========================================
               GENDER NOT SUPPORTED
            ========================================== */

            if (
                data.type ===
                "gender_not_supported"
            ) {

                alert(
                    data.message ||
                    "性別を設定してください。"
                );

                return;

            }


            /* ==========================================
               WEBRTC SIGNAL
            ========================================== */

            if (
                data.type === "signal"
            ) {

                await handleSignal(
                    data
                );

                return;

            }

        }
    );


    /* ==================================================
       WebSocket ERROR
    ================================================== */

    socket.addEventListener(
        "error",
        error => {

            console.error(
                "RANDOM CALL: WebSocket error:",
                error
            );

        }
    );


    /* ==================================================
       WebSocket CLOSE
    ================================================== */

    socket.addEventListener(
        "close",
        event => {

            console.log(
                "RANDOM CALL: WebSocket closed:",
                event.code
            );


            closePeerConnection();

        }
    );


    /* ==================================================
       誰かと話す
    ================================================== */

    if (callButton) {

        callButton.addEventListener(
            "click",
            () => {

                if (
                    socket.readyState !==
                    WebSocket.OPEN
                ) {

                    console.error(
                        "RANDOM CALL: WebSocket is not open:",
                        socket.readyState
                    );

                    return;

                }


                console.log(
                    "RANDOM CALL: FIND"
                );


                socket.send(
                    JSON.stringify({

                        action: "find"

                    })
                );

            }
        );

    }


    /* ==================================================
       キャンセル
    ================================================== */

    if (cancelButton) {

        cancelButton.addEventListener(
            "click",
            () => {

                if (
                    socket.readyState !==
                    WebSocket.OPEN
                ) {

                    return;

                }


                console.log(
                    "RANDOM CALL: CANCEL"
                );


                socket.send(
                    JSON.stringify({

                        action: "cancel"

                    })
                );

            }
        );

    }


    /* ==================================================
       通話終了
    ================================================== */

    if (leaveButton) {

        leaveButton.addEventListener(
            "click",
            () => {

                if (
                    socket.readyState !==
                    WebSocket.OPEN
                ) {

                    return;

                }


                console.log(
                    "RANDOM CALL: LEAVE"
                );


                closePeerConnection();


                socket.send(
                    JSON.stringify({

                        action: "leave"

                    })
                );

            }
        );

    }


    /* ==================================================
       もう一度話す
    ================================================== */

    if (retryButton) {

        retryButton.addEventListener(
            "click",
            () => {

                if (
                    socket.readyState !==
                    WebSocket.OPEN
                ) {

                    return;

                }


                closePeerConnection();


                callId = null;

                isInitiator = false;

                isMicEnabled = true;

                isCameraEnabled = false;

                isSpeakerEnabled = false;


                if (micButton) {

                    micButton.textContent =
                        "🎤";

                    micButton.classList.remove(
                        "is-off"
                    );

                }


                if (cameraButton) {

                    cameraButton.textContent =
                        "🚫";

                    cameraButton.classList.add(
                        "is-off"
                    );

                }


                if (speakerButton) {

                    speakerButton.textContent =
                        "🔈";

                    speakerButton.classList.remove(
                        "is-active"
                    );

                }


                console.log(
                    "RANDOM CALL: RETRY"
                );


                socket.send(
                    JSON.stringify({

                        action: "find"

                    })
                );

            }
        );

    }


    /* ==================================================
       マイクボタン
    ================================================== */

    if (micButton) {

        micButton.addEventListener(
            "click",
            toggleMicrophone
        );

    }


    /* ==================================================
       カメラボタン
    ================================================== */

    if (cameraButton) {

        cameraButton.addEventListener(
            "click",
            toggleCamera
        );

    }


    /* ==================================================
       スピーカーボタン
    ================================================== */

    if (speakerButton) {

        speakerButton.addEventListener(
            "click",
            toggleSpeaker
        );

    }


    /* ==================================================
       初期UI
    ================================================== */

    showState("idle");

    /* ==================================================
    自分の映像
    ドラッグ移動
    ================================================== */

    function enableLocalVideoDrag() {

        if (!localVideo) {
            return;
        }

        /* ==========================================
        初期位置を右下に固定
        ========================================== */

        localVideo.style.left = "auto";
        localVideo.style.top = "auto";
        localVideo.style.right = "12px";
        localVideo.style.bottom = "12px";

        let isDragging = false;

        let startX = 0;
        let startY = 0;

        let startLeft = 0;
        let startTop = 0;


        localVideo.addEventListener(
            "pointerdown",
            event => {

                event.preventDefault();

                isDragging = true;

                localVideo.classList.add(
                    "dragging"
                );

                const rect =
                    localVideo.getBoundingClientRect();

                startX = event.clientX;
                startY = event.clientY;

                startLeft = rect.left;
                startTop = rect.top;

                localVideo.setPointerCapture(
                    event.pointerId
                );

            }
        );


        localVideo.addEventListener(
            "pointermove",
            event => {

                if (!isDragging) {
                    return;
                }

                event.preventDefault();


                const deltaX =
                    event.clientX - startX;

                const deltaY =
                    event.clientY - startY;


                let newLeft =
                    startLeft + deltaX;

                let newTop =
                    startTop + deltaY;


                /*
                * 通話画面から
                * はみ出さないようにする
                */

                const parent =
                    localVideo.parentElement;

                if (!parent) {
                    return;
                }


                const parentRect =
                    parent.getBoundingClientRect();

                const videoRect =
                    localVideo.getBoundingClientRect();


                const maxLeft =
                    parentRect.width -
                    videoRect.width;


                const maxTop =
                    parentRect.height -
                    videoRect.height;


                newLeft =
                    Math.max(
                        0,
                        Math.min(
                            newLeft -
                            parentRect.left,
                            maxLeft
                        )
                    );


                newTop =
                    Math.max(
                        0,
                        Math.min(
                            newTop -
                            parentRect.top,
                            maxTop
                        )
                    );


                localVideo.style.left =
                    `${newLeft}px`;

                localVideo.style.top =
                    `${newTop}px`;

                localVideo.style.right =
                    "auto";

                localVideo.style.bottom =
                    "auto";

            }
        );


        localVideo.addEventListener(
            "pointerup",
            event => {

                isDragging = false;

                localVideo.classList.remove(
                    "dragging"
                );

                try {

                    localVideo.releasePointerCapture(
                        event.pointerId
                    );

                } catch (error) {}

            }
        );


        localVideo.addEventListener(
            "pointercancel",
            () => {

                isDragging = false;

                localVideo.classList.remove(
                    "dragging"
                );

            }
        );

    }


    /* ドラッグ機能開始 */

    enableLocalVideoDrag();

});