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

        cards.forEach((card, index) => {
            card.style.pointerEvents = index === 0 ? "auto" : "none";
            card.style.zIndex = cards.length - index;
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
            container.appendChild(topCard);
            topCard.classList.remove(className);
            updateTopCardState();
        }, 400);
    }

    nextBtn?.addEventListener("click", () => swipe("right"));
    prevBtn?.addEventListener("click", () => swipe("left"));

    updateTopCardState();

    /* =========================
       📱 モバイルスワイプ
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

        topCard.style.transition = "none";
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

        topCard.style.transition = "";

        if (Math.abs(diffX) > threshold) {
            topCard.style.transform = "";
            swipe(diffX > 0 ? "right" : "left");
        } else {
            topCard.style.transition = "transform 0.3s ease";
            topCard.style.transform = "translateX(0) rotate(0)";
        }

        isDragging = false;
    });

    /* =========================
       ❤ LIKE処理（最重要）
    ========================= */

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    container.addEventListener("click", function (e) {

        const btn = e.target.closest(".likeBtn");
        if (!btn) return;

        e.stopPropagation();

        const userId = btn.dataset.userId;

        fetch(`/accounts/like/${userId}/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json",
            },
        })
        .then(res => res.json())
        .then(data => {

            console.log("Success:", data);

            // 🔥 マッチ成立
            if (data.status === "match") {

                // 🎉 演出ページへ
                window.location.href = "/accounts/match-result/";
                return;
            }

            // 👍 通常いいね
            if (data.status === "liked" || data.status === "already_liked") {
                // 🔥 二重クリック防止
                btn.disabled = true;
                btn.classList.add("liked");
                
                const card = btn.closest(".card");
                if (card) {
                    card.classList.add("liked-effect");
                    setTimeout(() => {
                        card.classList.remove("liked-effect");
                    }, 300);
                }
            }
        })
        .catch(error => console.error("Error:", error));
    });
});