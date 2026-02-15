document.addEventListener("DOMContentLoaded", function () {

    const likeButton = document.getElementById('like-button');

    if (!likeButton) {
        console.log("like-button not found");
        return;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    likeButton.addEventListener('click', function () {

        const url = likeButton.dataset.url;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('likes-count').textContent = data.likes;
            document.getElementById('unique-users-count').textContent = data.unique_users;
            document.getElementById('user-likes-count').textContent = data.user_like_count;
        })
        .catch(error => console.error("Error:", error));
    });

});