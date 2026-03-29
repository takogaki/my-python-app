document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // 🔥 デバイス判定
    // =========================
    const isMobile = /iPhone|Android.+Mobile|iPad/.test(navigator.userAgent);

    // =========================
    // 🔥 QR経由判定
    // =========================
    const params = new URLSearchParams(window.location.search);
    const isQR = params.get("qr") === "1";

    // =========================
    // 🔥 要素取得
    // =========================
    const pc = document.getElementById("pc-only");
    const mobile = document.getElementById("mobile-only");
    const fileInput = document.querySelector('input[name="id_image"]');

    // =========================
    // 🔥 初期状態リセット（安全対策）
    // =========================
    if (pc) pc.style.display = "none";
    if (mobile) mobile.style.display = "none";

    // =========================
    // 🔥 分岐処理
    // =========================
    if (isMobile) {

        // モバイル表示
        if (mobile) mobile.style.display = "block";

        // =========================
        // 🔥 QR経由のみカメラ自動起動
        // =========================
        if (isQR && fileInput) {
            setTimeout(() => {
                fileInput.click();
            }, 500);
        }

    } else {

        // PC表示（QR表示）
        if (pc) pc.style.display = "block";

    }

});