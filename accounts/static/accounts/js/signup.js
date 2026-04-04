document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const checkbox = document.querySelector('input[name="agree"]');
    const button = document.getElementById("submitBtn");

    // 🔹 ボタン制御
    if (checkbox && button) {
        button.disabled = !checkbox.checked;
        checkbox.addEventListener("change", function () {
            button.disabled = !this.checked;
        });
    }

    // 🔹 保存
    form.addEventListener("input", () => {
        const data = new FormData(form);
        const obj = {};

        data.forEach((value, key) => {
            // 🔒 パスワードは保存しない
            if (key !== "password1" && key !== "password2") {
                obj[key] = value;
            }
        });

        sessionStorage.setItem("signup_form", JSON.stringify(obj));
    });

    // 🔹 復元
    const saved = sessionStorage.getItem("signup_form");
    if (saved) {
        const data = JSON.parse(saved);

        Object.keys(data).forEach(key => {
            const field = form.elements[key];
            if (field) {
                if (field.type === "checkbox") {
                    field.checked = data[key] === "on";
                } else {
                    field.value = data[key];
                }
            }
        });

        // 復元後もボタン制御
        if (checkbox && button) {
            button.disabled = !checkbox.checked;
        }
    }

    // 🔹 送信時クリア
    form.addEventListener("submit", () => {
        sessionStorage.removeItem("signup_form");
    });
});