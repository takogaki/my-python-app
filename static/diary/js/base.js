document.addEventListener("DOMContentLoaded", function () {

    console.log("base.js loaded");

    /* =========================
       時計表示
    ========================== */
    const clock = document.getElementById("clock");

    if (clock) {
        function updateTime() {
            const now = new Date();

            const year    = now.getFullYear();
            const month   = String(now.getMonth() + 1).padStart(2, "0");
            const day     = String(now.getDate()).padStart(2, "0");
            const hours   = String(now.getHours()).padStart(2, "0");
            const minutes = String(now.getMinutes()).padStart(2, "0");
            const seconds = String(now.getSeconds()).padStart(2, "0");

            clock.textContent =
                `${year}年${month}月${day}日 ` +
                `${hours}時${minutes}分${seconds}秒`;
        }

        updateTime();
        setInterval(updateTime, 1000);
    }


    /* =========================
       画像モーダル
    ========================== */

    const modal    = document.getElementById("image-modal");
    const modalImg = document.getElementById("modal-image");
    const closeBtn = document.querySelector(".image-modal .close");

    // モーダル自体が無いページでは何もしない
    if (modal && modalImg) {

        const clickableImages = document.querySelectorAll(
            ".avatar-clickable, .thumbnail-clickable"
        );

        clickableImages.forEach(img => {
            img.addEventListener("click", () => {
                modal.style.display = "flex";
                modalImg.src = img.src;
            });
        });

        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                modal.style.display = "none";
            });
        }

        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });
    }

});