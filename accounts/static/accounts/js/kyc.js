document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // 🔥 デバイス判定
    // =========================
    const isMobile = /iPhone|Android.+Mobile|iPad/.test(navigator.userAgent);

    // =========================
    // 🔥 QR判定
    // =========================
    const params = new URLSearchParams(window.location.search);
    const isQR = params.get("qr") === "1";

    // =========================
    // 🔥 要素取得
    // =========================
    const pc = document.getElementById("pc-only");
    const mobile = document.getElementById("mobile-only");

    // =========================
    // 🔥 初期リセット
    // =========================
    if (pc) pc.style.display = "none";
    if (mobile) mobile.style.display = "none";

    // =========================
    // 🔥 表示分岐
    // =========================
    if (isMobile) {

        if (mobile) mobile.style.display = "block";

        if (isQR) {
            console.log("QR経由でアクセス");

            // 🔥 スクロール誘導（ここに統合）
            setTimeout(() => {
                window.scrollTo({
                    top: 300,
                    behavior: "smooth"
                });
            }, 300);
        }

    } else {

        if (pc) pc.style.display = "block";

    }

});


// =========================
// 🔥 カメラ起動（ユーザー操作必須）
// =========================
function startCamera() {
    const input = document.getElementById("id_image_input");
    if (input) {
        input.click();
    }
}