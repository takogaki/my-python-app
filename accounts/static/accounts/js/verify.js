document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("verify-btn");

    if (!btn) return;

    btn.addEventListener("click", async () => {
        // 🔥 連打防止
        btn.disabled = true;
        const originalText = btn.innerText;
        btn.innerText = "確認中...";

        try {
            const res = await fetch("/accounts/verify/");
            const data = await res.json();

            if (data.url) {
                window.location.href = data.url;
            } else {
                alert("エラーが発生しました");
                btn.disabled = false;
                btn.innerText = originalText;
            }
        } catch (e) {
            alert("通信エラー");
            btn.disabled = false;
            btn.innerText = originalText;
        }
    });
});