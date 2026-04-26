document.addEventListener("DOMContentLoaded", function(){

    const button = document.getElementById("like-button");
    if(!button) return;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    button.addEventListener("click", function(){

        fetch(button.dataset.url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            }
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("likes-count").textContent = data.likes;
            document.getElementById("unique-users-count").textContent = data.unique_users;
        });

    });

});