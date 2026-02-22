document.addEventListener("DOMContentLoaded", function () {

    const container = document.querySelector(".swipe-container");
    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");

    if (!container) return;

    function getCards() {
        return container.querySelectorAll(".card");
    }

    function updateTopCardState() {
        const cards = getCards();

        cards.forEach(card => {
            card.style.pointerEvents = "none";
            card.style.zIndex = "0";
        });

        if (cards.length > 0) {
            cards[0].style.pointerEvents = "auto";
            cards[0].style.zIndex = "10";
        }
    }

    function swipe(direction) {
        const cards = getCards();
        const topCard = cards[0];
        if (!topCard) return;

        const className = direction === "right"
            ? "swipe-right"
            : "swipe-left";

        topCard.classList.add(className);

        setTimeout(() => {
            topCard.classList.remove(className);
            container.appendChild(topCard);
            updateTopCardState();
        }, 400);
    }

    nextBtn?.addEventListener("click", () => swipe("right"));
    prevBtn?.addEventListener("click", () => swipe("left"));

    // 初期化
    updateTopCardState();

});