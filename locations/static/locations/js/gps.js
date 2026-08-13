document.addEventListener("DOMContentLoaded", () => {

    console.log("📍 GPS START");

    // ==================================================
    // GPS対応チェック
    // ==================================================

    if (!navigator.geolocation) {

        console.error(
            "❌ このブラウザはGPSに対応していません。"
        );

        return;
    }


    console.log("📍 GPS API OK");


    // ==================================================
    // CSRF取得
    // ==================================================

    const csrfToken =
        document.querySelector(
            'meta[name="csrf-token"]'
        )?.getAttribute("content");


    console.log(
        "🔐 CSRF:",
        csrfToken ? "取得成功" : "取得失敗"
    );


    if (!csrfToken) {

        console.error(
            "❌ CSRFトークンが見つかりません。"
        );

        return;
    }


    // ==================================================
    // GPS取得
    // ==================================================

    console.log(
        "📍 現在地を取得しています..."
    );


    navigator.geolocation.getCurrentPosition(

        // ==================================================
        // 成功
        // ==================================================

        async (position) => {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            console.log(
                "📍 GPS取得成功",
                {
                    latitude,
                    longitude
                }
            );


            // ==================================================
            // Djangoへ送信
            // ==================================================

            try {

                const response =
                    await fetch(
                        "/locations/update/",
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json",

                                "X-CSRFToken":
                                    csrfToken,

                            },

                            body:
                                JSON.stringify({

                                    latitude:
                                        latitude,

                                    longitude:
                                        longitude,

                                }),

                        }
                    );


                const data =
                    await response.json();


                console.log(
                    "📍 GPSサーバー応答:",
                    data
                );


                if (!response.ok) {

                    console.error(
                        "❌ GPS保存失敗",
                        data
                    );

                    return;
                }


                console.log(
                    "✅ GPS保存成功"
                );


            } catch (error) {

                console.error(
                    "❌ GPS送信エラー",
                    error
                );

            }

        },


        // ==================================================
        // GPS取得失敗
        // ==================================================

        (error) => {

            console.error(
                "❌ GPS取得失敗"
            );

            console.error(
                "code:",
                error.code
            );

            console.error(
                "message:",
                error.message
            );

        },


        // ==================================================
        // GPS設定
        // ==================================================

        {

            enableHighAccuracy: true,

            timeout: 10000,

            maximumAge: 60000,

        }

    );

});