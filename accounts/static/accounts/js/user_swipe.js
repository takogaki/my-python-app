document.addEventListener("DOMContentLoaded", function () {

    console.log("JS START");

    const cards = document.querySelectorAll(".card");
    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");

    console.log("cards:", cards.length);
    console.log("nextBtn:", nextBtn);

    if (!cards.length) return;

    let currentIndex = 0;

    function showTopCard() {
        cards.forEach((card, i) => {
            card.style.display = i === currentIndex ? "block" : "none";
        });
    }

    function nextCard() {
        console.log("next clicked");
        currentIndex = (currentIndex + 1) % cards.length;
        showTopCard();
    }

    function prevCard() {
        currentIndex = (currentIndex - 1 + cards.length) % cards.length;
        showTopCard();
    }

    if (nextBtn) nextBtn.addEventListener("click", nextCard);
    if (prevBtn) prevBtn.addEventListener("click", prevCard);

    showTopCard();
});