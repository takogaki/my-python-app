document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("verify-btn");

    if (!btn) return;

    btn.addEventListener("click", async () => {
        try {
            const res = await fetch("/accounts/verify/");
            const data = await res.json();

            if (data.url) {
                window.location.href = data.url;
            } else {
                alert("エラーが発生しました");
            }
        } catch (e) {
            alert("通信エラー");
        }
    });
});