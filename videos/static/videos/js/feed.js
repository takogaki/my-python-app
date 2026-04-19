document.addEventListener("DOMContentLoaded", () => {

    const feed = document.querySelector(".feed-inner");
    const cards = document.querySelectorAll(".video-card");
    const videos = document.querySelectorAll("video");

    let currentIndex = 0;

    let startY = 0;
    let currentY = 0;
    let isDragging = false;

    let isLocked = false; // ★最重要

    const headerHeight = 60;
    let viewportHeight = window.innerHeight - headerHeight;

    // =========================
    // 移動
    // =========================
    function moveTo(index) {
        if (index < 0 || index >= cards.length) return;
        if (isLocked) return; // ★ここで完全ブロック

        isLocked = true;
        currentIndex = index;

        feed.style.transition = "transform 0.4s ease";
        feed.style.transform = `translateY(-${index * viewportHeight}px)`;

        updateVideos();

        // ★完全ロック（ここが核心）
        setTimeout(() => {
            isLocked = false;
        }, 450);
    }

    // =========================
    // 動画制御
    // =========================
    function updateVideos() {
        videos.forEach((v, i) => {
            if (i === currentIndex) {
                v.play().catch(()=>{});
            } else {
                v.pause();
                v.currentTime = 0;
            }
        });
    }

    updateVideos();

    // =========================
    // タッチ
    // =========================
    document.addEventListener("touchstart", (e) => {
        if (isLocked) return;

        isDragging = true;
        startY = e.touches[0].clientY;
        currentY = startY;

        feed.style.transition = "none";
    }, { passive: true });

    document.addEventListener("touchmove", (e) => {
        if (!isDragging || isLocked) return;

        currentY = e.touches[0].clientY;
        const diff = currentY - startY;

        feed.style.transform =
            `translateY(${-currentIndex * viewportHeight + diff}px)`;

    }, { passive: true });

    document.addEventListener("touchend", () => {

        if (!isDragging || isLocked) return;
        isDragging = false;

        const diff = currentY - startY;

        // ★1回だけ判定
        if (Math.abs(diff) > 80) {
            if (diff < 0) {
                moveTo(currentIndex + 1);
            } else {
                moveTo(currentIndex - 1);
            }
        } else {
            moveTo(currentIndex);
        }

    });

    // =========================
    // PCホイール（完全固定）
    // =========================
    let wheelLocked = false;

    document.addEventListener("wheel", (e) => {

        if (wheelLocked || isLocked) return;

        wheelLocked = true;

        if (e.deltaY > 0) {
            moveTo(currentIndex + 1);
        } else {
            moveTo(currentIndex - 1);
        }

        setTimeout(() => {
            wheelLocked = false;
        }, 500);

    }, { passive: true });

});