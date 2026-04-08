document.querySelectorAll(".progress").forEach(el => {
    el.style.width = el.dataset.width + "%";
});