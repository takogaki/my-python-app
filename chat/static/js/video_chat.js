const endStreamUrl = window.endStreamUrl;
const roomName = window.roomName;
const localVideo = document.getElementById('localVideo');
const remoteVideosContainer = document.getElementById('remoteVideos');
let localStream = null;
let peerConnections = {};


    // カメラとマイクのストリームを取得
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
        // ストリームが取得できたら、ビデオ要素にストリームを設定
        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.autoplay = true;
        document.body.appendChild(videoElement); // 画面に表示

        // 取得したストリームをグローバルに保存（後で使用するため）
        window.localStream = stream;
    })
    .catch(error => {
        console.error('カメラエラー:', error);
        alert('カメラのアクセスに失敗しました。');
    });

const configuration = {
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
};

const chatSocket = new WebSocket(
    (window.location.protocol === "https:" ? "wss://" : "ws://") +
    window.location.host + '/ws/chat/' + roomName + '/'
);

async function startLocalStream() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideo.srcObject = localStream;
    } catch (error) {
        console.error('カメラエラー:', error);
        alert('カメラやマイクのアクセスに失敗しました。');
    }
}

function createPeerConnection(userId) {
    const pc = new RTCPeerConnection(configuration);
    peerConnections[userId] = pc;
    localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

    pc.ontrack = (event) => {
        let remoteVideo = document.getElementById(`remoteVideo_${userId}`);
        if (!remoteVideo) {
            remoteVideo = document.createElement('video');
            remoteVideo.id = `remoteVideo_${userId}`;
            remoteVideo.autoplay = true;
            remoteVideo.playsInline = true;
            remoteVideosContainer.appendChild(remoteVideo);
        }
        remoteVideo.srcObject = event.streams[0];
    };

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            chatSocket.send(JSON.stringify({
                type: 'new-ice-candidate',
                candidate: event.candidate,
                target: userId
            }));
        }
    };

    return pc;
}

chatSocket.onopen = () => {
    chatSocket.send(JSON.stringify({ type: 'join', room: roomName }));
};

chatSocket.onmessage = async (e) => {
    const data = JSON.parse(e.data);
    if (data.type === 'user-joined') {
        const pc = createPeerConnection(data.user_id);
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        chatSocket.send(JSON.stringify({
            type: 'offer',
            sdp: pc.localDescription,
            target: data.user_id
        }));
    } else if (data.type === 'offer') {
        const pc = createPeerConnection(data.user_id);
        await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        chatSocket.send(JSON.stringify({
            type: 'answer',
            sdp: pc.localDescription,
            target: data.user_id
        }));
    } else if (data.type === 'answer') {
        const pc = peerConnections[data.user_id];
        await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
    } else if (data.type === 'new-ice-candidate') {
        const pc = peerConnections[data.user_id];
        if (pc) {
            await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
    }
};

chatSocket.onclose = () => {
    console.log("WebSocket connection closed");
};

document.getElementById("endStreamBtn").addEventListener("click", async (event) => {
    event.preventDefault();
    const csrftoken = document.querySelector('[name=csrf-token]').content;

    try {
        const response = await fetch(endStreamUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
        });

        if (response.ok) {
            alert("配信を終了しました。");
            localStream.getTracks().forEach(track => track.stop());
            chatSocket.close();
            window.location.href = "{% url 'diary' %}";
        } else {
            alert("配信終了に失敗しました。");
        }
    } catch (error) {
        console.error('配信終了エラー:', error);
    }
});

startLocalStream();