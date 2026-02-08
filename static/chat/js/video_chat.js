let api = null;

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("start-jitsi");
    const container = document.getElementById("jitsi-container");

    if (!btn || !container) {
        console.error("Jitsi 初期化失敗：要素が見つかりません");
        return;
    }

    const roomSlug = btn.dataset.roomSlug;
    const username = btn.dataset.username;
    const password = btn.dataset.password;

    btn.addEventListener("click", () => {
        if (api) return;

        api = new JitsiMeetExternalAPI("meet.jit.si", {
            roomName: `videochat-${roomSlug}`,
            parentNode: container,
            userInfo: {
                displayName: username
            },
            configOverwrite: {
                prejoinPageEnabled: false
            }
        });

        if (password) {
            api.addEventListener("videoConferenceJoined", () => {
                api.executeCommand("password", password);
            });
        }
    });
});