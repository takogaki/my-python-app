document.addEventListener('DOMContentLoaded', function() {
    function updateTime() {
        const now = new Date();

        const year           = now.getFullYear();
        const month          = (now.getMonth() + 1).toString().padStart(2, '0');
        const day            = now.getDate().toString().padStart(2, '0');
        const hours          = now.getHours().toString().padStart(2, '0');
        const minutes        = now.getMinutes().toString().padStart(2, '0');
        const seconds        = now.getSeconds().toString().padStart(2, '0');
        const dateString     = `${year}年${month}月${day}日`;
        const timeString     = `${hours}時${minutes}分${seconds}秒`;
        const dateTimeString = `${dateString} ${timeString}`;
        document.getElementById('clock').textContent = dateTimeString;
    }
    updateTime();
    setInterval(updateTime, 1000);
});

// プロフィール画像のモーダル表示
document.addEventListener("DOMContentLoaded", () => {
    const avatar = document.querySelector(".avatar-clickable");
    const modal = document.getElementById("image-modal");
    const modalImg = document.getElementById("modal-image");
    const closeBtn = document.querySelector(".image-modal .close");

    avatar.addEventListener("click", () => {
        modal.style.display = "block";
        modalImg.src = avatar.src;
    });

    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });
});



document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("image-modal");
    const modalImg = document.getElementById("modal-image");
    const closeBtn = document.querySelector(".image-modal .close");

    document.querySelectorAll(
        ".avatar-clickable, .thumbnail-clickable"
    ).forEach(img => {
        img.addEventListener("click", () => {
            modal.style.display = "flex";
            modalImg.src = img.src;
        });
    });

    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    modal.addEventListener("click", e => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });
});