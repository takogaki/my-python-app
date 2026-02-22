document.addEventListener("DOMContentLoaded", function () {

    const container = document.querySelector(".swipe-container");
    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");

    if (!container) return;

    function getCards() {
        return container.querySelectorAll(".card");
    }

    function swipe(direction) {
        const cards = getCards();
        const topCard = cards[0];
        if (!topCard) return;

        const className =
            direction === "right" ? "swipe-right" : "swipe-left";

        topCard.classList.add(className);

        setTimeout(() => {
            topCard.classList.remove(className);
            container.appendChild(topCard);
        }, 400);
    }

    nextBtn?.addEventListener("click", () => swipe("right"));
    prevBtn?.addEventListener("click", () => swipe("left"));

    /* =========================
    📱 モバイルスワイプ（安定版）
    ========================= */

    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    container.addEventListener("touchstart", (e) => {
        const cards = getCards();
        if (!cards.length) return;

        const topCard = cards[0];

        isDragging = true;
        startX = e.touches[0].clientX;
        currentX = startX;

        // ドラッグ開始時にtransition解除
        topCard.style.transition = "none";
        });
    
    });

    container.addEventListener("touchmove", (e) => {
        if (!isDragging) return;

        const cards = getCards();
        const topCard = cards[0];
        if (!topCard) return;

        currentX = e.touches[0].clientX;
        const diffX = currentX - startX;

        topCard.style.transform =
            `translateX(${diffX}px) rotate(${diffX * 0.05}deg)`;
    });

    container.addEventListener("touchend", () => {
        if (!isDragging) return;

        const cards = getCards();
        const topCard = cards[0];
        if (!topCard) return;

        const diffX = currentX - startX;
        const threshold = 120;

        topCard.style.transition = "transform 0.35s ease, opacity 0.35s ease";

        if (Math.abs(diffX) > threshold) {

            // 画面外へアニメーション
            const direction = diffX > 0 ? 1 : -1;
            topCard.style.transform =
                `translateX(${direction * 600}px) rotate(${direction * 25}deg)`;
            topCard.style.opacity = "0";

            setTimeout(() => {
                // ★ 完全リセット（超重要）
                topCard.style.transition = "";
                topCard.style.transform = "";
                topCard.style.opacity = "";

                container.appendChild(topCard);
            }, 350);

        } else {
            // 元の位置へ戻す
            topCard.style.transform = "translateX(0) rotate(0)";
        }

        isDragging = false;
    });