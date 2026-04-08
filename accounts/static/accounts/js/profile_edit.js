document.addEventListener("DOMContentLoaded", function () {

    const tagBlocks = document.querySelectorAll(".tag-block");

    function levelText(level) {
        if (level == 1) return "少し";
        if (level == 2) return "普通";
        if (level == 3) return "かなり";
    }

    function updateSelectedTags() {

        // 🔥 全カテゴリの表示エリアをリセット
        document.querySelectorAll(".selected-tags").forEach(box => {
            box.innerHTML = "";
        });

        tagBlocks.forEach(block => {

            const checkbox = block.querySelector("input[type='checkbox']");
            const label = block.querySelector(".tag-name");
            const select = block.querySelector(".tag-level");
            const categoryId = block.dataset.categoryId;

            if (checkbox.checked) {

                const chip = document.createElement("span");
                chip.className = "tag-chip";

                const level = select.value;
                chip.textContent = `${label.textContent}（${levelText(level)}）`;

                // 🔥 カテゴリごとに振り分け
                const targetBox = document.getElementById(`selected-${categoryId}`);
                if (targetBox) {
                    targetBox.appendChild(chip);
                }
            }
        });
    }

    // =========================
    // チェック＆レベル制御
    // =========================
    tagBlocks.forEach(block => {

        const checkbox = block.querySelector("input[type='checkbox']");
        const select = block.querySelector(".tag-level");

        // 初期表示
        select.style.display = checkbox.checked ? "inline-block" : "none";

        checkbox.addEventListener("change", () => {
            select.style.display = checkbox.checked ? "inline-block" : "none";
            updateSelectedTags();
            saveDraft();
        });

        select.addEventListener("change", () => {
            updateSelectedTags();
            saveDraft();
        });
    });

    // =========================
    // 🔥 下書き保存
    // =========================
    function saveDraft() {
        const form = document.querySelector("form");
        const data = new FormData(form);

        // checkbox複数対応
        const obj = {};
        for (let [key, value] of data.entries()) {
            if (obj[key]) {
                if (!Array.isArray(obj[key])) {
                    obj[key] = [obj[key]];
                }
                obj[key].push(value);
            } else {
                obj[key] = value;
            }
        }

        localStorage.setItem("profile_draft", JSON.stringify(obj));
    }

    // =========================
    // 🔥 下書き復元
    // =========================
    const saved = localStorage.getItem("profile_draft");

    if (saved) {
        const data = JSON.parse(saved);

        Object.keys(data).forEach(name => {

            const elements = document.querySelectorAll(`[name="${name}"]`);

            elements.forEach(el => {

                if (el.type === "checkbox") {
                    if (Array.isArray(data[name])) {
                        el.checked = data[name].includes(el.value);
                    } else {
                        el.checked = true;
                    }
                } else {
                    el.value = data[name];
                }

            });
        });
    }

    // =========================
    // 初期描画
    // =========================
    updateSelectedTags();
});