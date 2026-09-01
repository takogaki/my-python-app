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

document.addEventListener("DOMContentLoaded", () => {

    const usernameInput = document.getElementById("id_username");
    const usernameWarning = document.getElementById("username-warning");

    if (!usernameInput || !usernameWarning) {
        return;
    }

    usernameInput.addEventListener("input", () => {

        const value = usernameInput.value;

        if (!value) {
            usernameWarning.textContent = "";
            return;
        }

        // 許可する文字
        const invalidMatch = value.match(/[^\w.\-]/u);

        if (invalidMatch) {

            usernameWarning.textContent =
                `⚠️ 「${invalidMatch[0]}」は使用できません。`;

            usernameWarning.classList.add("show");

            return;
        }

        // 最初の記号
        if (/^[._-]/.test(value)) {

            usernameWarning.textContent =
                "⚠️ 「.」「-」「_」から始めることはできません。";

            usernameWarning.classList.add("show");

            return;
        }

        // 最後の記号
        if (/[._-]$/.test(value)) {

            usernameWarning.textContent =
                "⚠️ 「.」「-」「_」で終わることはできません。";

            usernameWarning.classList.add("show");

            return;
        }

        usernameWarning.textContent = "";
        usernameWarning.classList.remove("show");
    });

});