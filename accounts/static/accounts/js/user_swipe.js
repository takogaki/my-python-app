document.addEventListener("DOMContentLoaded", function () {

    const container = document.querySelector(".swipe-container");
    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");

    if (!container) return;

    function getCards() {
        return Array.from(container.querySelectorAll(".card"));
    }

    function updateTopCardState() {
        const cards = getCards();

        cards.forEach((card, index) => {
            if (index === 0) {
                card.style.pointerEvents = "auto";
                card.style.zIndex = "100";
            } else {
                card.style.pointerEvents = "none";
                card.style.zIndex = "0";
            }
        });
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

            // 🔥 これが超重要
            requestAnimationFrame(() => {
                updateTopCardState();
            });

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

    // 🔥 ハート演出（LIKE時）
    function createHeart(card) {
        const heart = document.createElement("div");
        heart.className = "like-heart-pop";
        heart.textContent = "❤️";

        // ランダム位置（自然さUP）
        heart.style.left = (40 + Math.random() * 20) + "%";

        card.appendChild(heart);

        setTimeout(() => {
            heart.remove();
        }, 800);
    }

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

            // 🎉 マッチ
            if (data.status === "match") {
                window.location.href = "/accounts/match-result/";
                return;
            }

            // 👍 LIKE
            if (data.status === "liked") {
                btn.classList.add("liked");

                const card = btn.closest(".card");
                if (card) {
                    card.classList.add("liked-effect");

                    for (let i = 0; i < 6; i++) {
                        setTimeout(() => createHeart(card), i * 120);
                    }

                    setTimeout(() => {
                        card.classList.remove("liked-effect");
                    }, 300);
                }
            }

            // ❌ 取り消し（←追加）
            if (data.status === "unliked") {
                btn.classList.remove("liked");
            }

        })
        .catch(error => console.error("Error:", error));
    });
});

/* =========================
   Guest Like
========================= */

document.querySelectorAll(".guestLikeBtn").forEach(btn => {

    btn.addEventListener("click", () => {

        // ボタンぷにっ
        btn.classList.add("pop");

        // ❤️生成
        const heart = document.createElement("div");
        heart.className = "guest-heart-pop";
        heart.innerHTML = "❤";

        btn.parentElement.appendChild(heart);

        // 0.4秒後に登録画面へ
        setTimeout(() => {
            window.location.href = "/accounts/signup/";
        }, 1000);

        // 後処理
        setTimeout(() => {
            btn.classList.remove("pop");
            heart.remove();
        }, 800);

    });

});