/* ==================================================
   📍 近くの募集
================================================== */

console.log("📍 nearby_recruits.js 読み込み");


async function loadNearbyRecruits() {

    console.log(
        "📍 loadNearbyRecruits START"
    );


    const container =
        document.getElementById(
            "nearbyRecruitList"
        );


    /* ==================================================
       UI確認
    ================================================== */

    if (!container) {

        console.error(
            "❌ nearbyRecruitList がありません"
        );

        return;

    }


    console.log(
        "📍 nearbyRecruitList OK"
    );


    /* ==================================================
       読み込み表示
    ================================================== */

    container.innerHTML = `
        <p class="nearby-recruit-message">
            📍 近くの募集を検索しています…
        </p>
    `;


    try {

        console.log(
            "📍 API REQUEST START"
        );


        const response =
            await fetch(
                "/locations/nearby-recruits/",
                {
                    method: "GET",
                    credentials: "same-origin",
                    cache: "no-store",
                }
            );


        console.log(
            "📍 API RESPONSE",
            response.status,
            response.ok
        );


        const data =
            await response.json();


        console.log(
            "📍 近くの募集API:",
            data
        );


        /* ==================================================
           APIエラー
        ================================================== */

        if (
            !response.ok ||
            !data.success
        ) {

            container.innerHTML = `
                <p class="nearby-recruit-message">
                    📍 ${
                        escapeHtml(
                            data.message ||
                            data.error ||
                            "近くの募集を取得できませんでした。"
                        )
                    }
                </p>
            `;

            return;

        }


        /* ==================================================
           募集なし
        ================================================== */

        if (
            !data.results ||
            !data.results.length
        ) {

            console.log(
                "📍 近くの募集 0件"
            );


            container.innerHTML = `
                <p class="nearby-recruit-message">
                    📍 近くに募集はありません。
                </p>
            `;

            return;

        }


        console.log(
            "📍 近くの募集件数:",
            data.results.length
        );


        /* ==================================================
           カード生成
        ================================================== */

        container.innerHTML =
            data.results.map(
                function (recruit) {

                    let genderText = "";


                    if (
                        recruit.gender === "M"
                    ) {

                        genderText =
                            "男性";

                    }
                    else if (
                        recruit.gender === "F"
                    ) {

                        genderText =
                            "女性";

                    }


                    return `

                        <a
                            href="/videos/recruit/${recruit.id}/"
                            class="nearby-recruit-card"
                        >

                            <div class="nearby-recruit-user">

                                <img
                                    src="${escapeHtml(
                                        recruit.profile_image
                                    )}"
                                    class="nearby-recruit-avatar"
                                    alt=""
                                >


                                <div class="nearby-recruit-user-info">

                                    <div class="nearby-recruit-username">
                                        ${escapeHtml(
                                            recruit.username
                                        )}
                                    </div>


                                    ${
                                        genderText
                                            ? `
                                                <div class="nearby-recruit-gender">
                                                    ${genderText}
                                                </div>
                                            `
                                            : ""
                                    }

                                </div>

                            </div>


                            <div class="nearby-recruit-title">

                                ${escapeHtml(
                                    recruit.title
                                )}

                            </div>


                            ${
                                recruit.place
                                    ? `
                                        <div class="nearby-recruit-place">
                                            📍
                                            ${escapeHtml(
                                                recruit.place
                                            )}
                                        </div>
                                    `
                                    : ""
                            }


                            <div class="nearby-recruit-distance">

                                📏
                                ${recruit.distance}
                                km

                            </div>

                        </a>

                    `;

                }
            ).join("");


    }
    catch (error) {

        console.error(
            "❌ 近くの募集APIエラー:",
            error
        );


        container.innerHTML = `
            <p class="nearby-recruit-message">
                ❌ 近くの募集を読み込めませんでした。
            </p>
        `;

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


/* ==================================================
   🌐 外部公開
================================================== */

window.loadNearbyRecruits =
    loadNearbyRecruits;