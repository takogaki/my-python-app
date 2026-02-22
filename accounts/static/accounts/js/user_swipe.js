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
       📱 モバイルスワイプ
    ========================= */

    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    container.addEventListener("touchstart", (e) => {
        const cards = getCards();
        if (!cards.length) return;

        isDragging = true;
        startX = e.touches[0].clientX;
    });

    container.addEventListener("touchmove", (e) => {
        if (!isDragging) return;

        const cards = getCards();
        const topCard = cards[0];
        if (!topCard) return;

        currentX = e.touches[0].clientX;
        const diffX = currentX - startX;

        topCard.style.transition = "none";
        topCard.style.transform =
            `translateX(${diffX}px) rotate(${diffX * 0.05}deg)`;
    });

    container.addEventListener("touchend", () => {
        if (!isDragging) return;

        const cards = getCards();
        const topCard = cards[0];
        if (!topCard) return;

        const diffX = currentX - startX;
        const threshold = 100;

        topCard.style.transition = "transform 0.4s ease";

        if (diffX > threshold) {
            swipe("right");
        } else if (diffX < -threshold) {
            swipe("left");
        } else {
            topCard.style.transform = "translateX(0) rotate(0)";
        }

        isDragging = false;
    });

});