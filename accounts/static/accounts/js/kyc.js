document.addEventListener("DOMContentLoaded", function () {

    const isMobile = /iPhone|Android.+Mobile|iPad/.test(navigator.userAgent);

    const pc = document.getElementById("pc-only");
    const mobile = document.getElementById("mobile-only");

    if (isMobile) {
        if (mobile) mobile.style.display = "block";

        // 🔥 カメラ自動起動
        setTimeout(() => {
            const fileInput = document.querySelector('input[name="id_image"]');
            if (fileInput) {
                fileInput.click();
            }
        }, 500);

    } else {
        if (pc) pc.style.display = "block";
    }

});