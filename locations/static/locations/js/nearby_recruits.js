document.addEventListener("DOMContentLoaded", () => {

    console.log("📍 近くの募集 START");

    loadNearbyRecruits();

});


async function loadNearbyRecruits() {

    const container =
        document.getElementById(
            "nearbyRecruitList"
        );

    if (!container) return;


    try {

        const response =
            await fetch(
                "/locations/nearby-recruits/"
            );

        const data =
            await response.json();


        if (!response.ok || !data.success) {

            container.innerHTML =
                "<p>近くの募集を取得できませんでした。</p>";

            return;
        }


        if (!data.results.length) {

            container.innerHTML =
                "<p>近くに募集はありません。</p>";

            return;
        }


        container.innerHTML =
            data.results.map(recruit => {

                /* =========================
                   🚻 性別
                ========================= */

                let genderText = "";

                switch (recruit.gender) {

                    case "M":
                        genderText = "男性";
                        break;

                    case "F":
                        genderText = "女性";
                        break;

                    default:
                        genderText = "";
                        break;
                }


                /* =========================
                   🃏 カード
                ========================= */

                return `

                    <a
                        href="/videos/recruit/${recruit.id}/"
                        class="nearby-recruit-card"
                    >


                        <!-- =========================
                             📷 募集画像
                        ========================= -->

                        ${
                            recruit.image
                            ? `
                                <div
                                    class="nearby-recruit-image-wrapper"
                                >

                                    <img
                                        src="${escapeHtml(
                                            recruit.image
                                        )}"
                                        class="nearby-recruit-image"
                                        alt=""
                                    >

                                </div>
                            `
                            : ""
                        }


                        <!-- =========================
                             👤 ユーザー
                        ========================= -->

                        <div class="nearby-recruit-user">

                            <img
                                src="${escapeHtml(
                                    recruit.profile_image
                                )}"
                                class="nearby-recruit-avatar"
                                alt=""
                            >


                            <div
                                class="nearby-recruit-user-info"
                            >

                                <div
                                    class="nearby-recruit-username"
                                >
                                    ${escapeHtml(
                                        recruit.username
                                    )}
                                </div>


                                <div
                                    class="nearby-recruit-gender"
                                >
                                    ${genderText}
                                </div>

                            </div>

                        </div>


                        <!-- =========================
                             🤝 募集タイトル
                        ========================= -->

                        <div
                            class="nearby-recruit-title"
                        >

                            ${escapeHtml(
                                recruit.title
                            )}

                        </div>


                        <!-- =========================
                             📍 場所
                        ========================= -->

                        <div
                            class="nearby-recruit-place"
                        >

                            📍
                            ${escapeHtml(
                                recruit.place || ""
                            )}

                        </div>


                        <!-- =========================
                             📏 距離
                        ========================= -->

                        <div
                            class="nearby-recruit-distance"
                        >

                            📏
                            ${recruit.distance}
                            km

                        </div>


                    </a>

                `;

            }).join("");


    }
    catch (error) {

        console.error(
            "近くの募集取得エラー",
            error
        );

        container.innerHTML =
            "<p>読み込みに失敗しました。</p>";

    }

}


/* ==================================================
   🛡️ HTMLエスケープ
================================================== */

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value ?? "";

    return div.innerHTML;

}
