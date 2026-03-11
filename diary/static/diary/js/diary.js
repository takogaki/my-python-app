document.addEventListener("DOMContentLoaded", function(){

    const button = document.getElementById("like-button");

    if(!button) return;

    button.addEventListener("click", function(){

        const url = button.dataset.url;

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
            }
        })
        .then(res => res.json())
        .then(data => {

            document.getElementById("likes-count").textContent = data.likes;
            document.getElementById("unique-users-count").textContent = data.unique_users;

        });

    });

});