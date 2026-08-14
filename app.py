from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

# Render ရဲ့ temporary storage
DOWNLOAD_DIR = "/tmp/videos"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# =========================================================
# WEB UI
# =========================================================

HTML = """
<!DOCTYPE html>
<html lang="my">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>MM Caption - RedNote</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #0b0d10;
    color: #ffffff;
    font-family: Arial, sans-serif;
}

.page {
    width: 100%;
    max-width: 600px;
    min-height: 100vh;
    margin: auto;
    padding: 24px;
}

.logo {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    margin-top: 45px;
    margin-bottom: 45px;
}

h1 {
    text-align: center;
    margin: 10px 0;
}

.subtitle {
    text-align: center;
    color: #8f97a3;
    margin-bottom: 30px;
}

input {
    width: 100%;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #303640;
    background: #15181d;
    color: white;
    font-size: 15px;
    outline: none;
}

input:focus {
    border-color: #ffffff;
}

button {
    width: 100%;
    padding: 16px;
    margin-top: 14px;
    border: none;
    border-radius: 12px;
    background: white;
    color: #111111;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.back {
    background: transparent;
    color: #a0a6af;
    text-align: left;
    padding: 5px 0;
    margin: 0 0 20px 0;
}

.card {
    background: #15181d;
    border: 1px solid #292e36;
    border-radius: 16px;
    padding: 18px;
    margin-top: 22px;
}

.status {
    text-align: center;
    color: #9da5b0;
    margin-top: 20px;
    line-height: 1.6;
}

.error {
    color: #ff7373;
}

.success {
    color: #7ee787;
}

.hidden {
    display: none !important;
}

video {
    width: 100%;
    max-height: 520px;
    border-radius: 12px;
    background: #000000;
    display: block;
}

.progress-box {
    margin-top: 20px;
}

.progress-background {
    width: 100%;
    height: 10px;
    background: #292e36;
    border-radius: 20px;
    overflow: hidden;
}

.progress-bar {
    width: 0%;
    height: 100%;
    background: #ffffff;
    transition: width 0.3s ease;
}

.progress-text {
    text-align: center;
    margin-top: 10px;
    color: #9da5b0;
}

</style>

</head>


<body>


<div class="page">


    <!-- ================================================= -->
    <!-- PAGE 1 -->
    <!-- ================================================= -->

    <section id="page1">

        <div class="logo">
            🎬 MM Caption
        </div>

        <h1>
            RedNote Video
        </h1>

        <p class="subtitle">
            RedNote Link ထည့်ပြီး စတင်ပါ
        </p>


        <input
            id="url"
            type="text"
            placeholder="RedNote Video Link..."
            autocomplete="off"
        >


        <button
            id="continueBtn"
            onclick="startDownload()"
        >
            Continue →
        </button>


        <div
            id="status"
            class="status"
        ></div>


        <div
            id="progressBox"
            class="progress-box hidden"
        >

            <div class="progress-background">

                <div
                    id="progressBar"
                    class="progress-bar"
                ></div>

            </div>

            <div
                id="progressText"
                class="progress-text"
            >
                0%
            </div>

        </div>

    </section>



    <!-- ================================================= -->
    <!-- PAGE 2 -->
    <!-- ================================================= -->

    <section
        id="page2"
        class="hidden"
    >

        <button
            class="back"
            onclick="goBack()"
        >
            ← Back
        </button>


        <h1 id="videoTitle">
            🎬 Video
        </h1>


        <div class="card">

            <video
                id="video"
                controls
                playsinline
            ></video>


            <button
                id="downloadBtn"
                onclick="downloadVideo()"
            >
                ⬇️ Download Video
            </button>


            <div
                id="downloadStatus"
                class="status"
            ></div>

        </div>

    </section>


</div>



<script>


let videoURL = "";

let downloadedFilename = "";


// ========================================================
// START DOWNLOAD
// ========================================================

async function startDownload() {

    const url =
        document
        .getElementById("url")
        .value
        .trim();


    const button =
        document
        .getElementById("continueBtn");


    const status =
        document
        .getElementById("status");


    const progressBox =
        document
        .getElementById("progressBox");


    const progressBar =
        document
        .getElementById("progressBar");


    const progressText =
        document
        .getElementById("progressText");


    if (!url) {

        status.className =
            "status error";

        status.textContent =
            "❌ RedNote Link ထည့်ပါ";

        return;
    }


    button.disabled = true;

    button.textContent =
        "⏳ Download လုပ်နေပါတယ်...";


    status.className =
        "status";

    status.textContent =
        "🔎 RedNote Video ရှာနေပါတယ်...";


    progressBox.classList.remove(
        "hidden"
    );


    progressBar.style.width =
        "10%";

    progressText.textContent =
        "10%";


    try {


        const response =
            await fetch(
                "/api/download",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        url: url
                    })

                }
            );


        progressBar.style.width =
            "30%";

        progressText.textContent =
            "30%";


        let data;


        try {

            data =
                await response.json();

        } catch {

            throw new Error(
                "Server က မှန်ကန်တဲ့ response မပေးပါ"
            );

        }


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Video Download မအောင်မြင်ပါ"
            );

        }


        progressBar.style.width =
            "100%";

        progressText.textContent =
            "100%";


        videoURL =
            data.video_url;


        downloadedFilename =
            data.filename || "RedNote-Video";


        document
            .getElementById("videoTitle")
            .textContent =
            "🎬 " +
            (
                data.title ||
                "RedNote Video"
            );


        const video =
            document
            .getElementById("video");


        video.src =
            data.video_url;


        video.load();


        document
            .getElementById("page1")
            .classList
            .add("hidden");


        document
            .getElementById("page2")
            .classList
            .remove("hidden");


        status.textContent = "";


    } catch (error) {


        console.error(error);


        progressBar.style.width =
            "0%";

        progressText.textContent =
            "0%";


        status.className =
            "status error";


        status.textContent =
            "❌ " +
            error.message;


    } finally {


        button.disabled = false;

        button.textContent =
            "Continue →";

    }

}



// ========================================================
// DOWNLOAD FILE
// ========================================================

function downloadVideo() {


    if (!videoURL) {

        alert(
            "Video မရသေးပါ"
        );

        return;

    }


    const link =
        document.createElement("a");


    link.href =
        videoURL;


    link.download =
        downloadedFilename ||
        "RedNote-Video";


    document
        .body
        .appendChild(link);


    link.click();


    link.remove();


    document
        .getElementById(
            "downloadStatus"
        )
        .className =
        "status success";


    document
        .getElementById(
            "downloadStatus"
        )
        .textContent =
        "✅ Download စတင်ပါပြီ";

}



// ========================================================
// BACK
// ========================================================

function goBack() {


    document
        .getElementById("page2")
        .classList
        .add("hidden");


    document
        .getElementById("page1")
        .classList
        .remove("hidden");


    document
        .getElementById("video")
        .pause();

}


</script>


</body>

</html>
"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template_string(
        HTML
    )


# =========================================================
# REDNOTE DOWNLOAD
# =========================================================

@app.route(
    "/api/download",
    methods=["POST"]
)
def download_video():


    data =
        request.get_json(
            silent=True
        ) or {}


    url =
        data.get(
            "url",
            ""
        ).strip()


    if not url:

        return jsonify({

            "success": False,

            "error":
                "RedNote link ထည့်ပါ"

        }), 400


    job_id =
        str(
            uuid.uuid4()
        )


    output =
        os.path.join(
            DOWNLOAD_DIR,
            job_id + ".%(ext)s"
        )


    options = {

        "outtmpl":
            output,

        "format":
            "best",

        "noplaylist":
            True,

        "quiet":
            True,

        "no_warnings":
            True,

        "restrictfilenames":
            True

    }


    try:


        with yt_dlp.YoutubeDL(
            options
        ) as ydl:


            info =
                ydl.extract_info(
                    url,
                    download=True
                )


            filepath =
                ydl.prepare_filename(
                    info
                )


        # ------------------------------------------------
        # တချို့ extractor တွေမှာ extension ပြောင်းနိုင်တာကြောင့်
        # prepare_filename မတွေ့ရင် job_id နဲ့ရှာမယ်
        # ------------------------------------------------

        if not os.path.isfile(
            filepath
        ):


            possible_files = [

                os.path.join(
                    DOWNLOAD_DIR,
                    filename
                )

                for filename
                in os.listdir(
                    DOWNLOAD_DIR
                )

                if filename.startswith(
                    job_id
                )

            ]


            if not possible_files:

                return jsonify({

                    "success":
                        False,

                    "error":
                        "Video file မတွေ့ပါ"

                }), 500


            filepath =
                possible_files[0]


        filename =
            os.path.basename(
                filepath
            )


        return jsonify({

            "success":
                True,

            "title":
                info.get(
                    "title",
                    "RedNote Video"
                ),

            "filename":
                filename,

            "video_url":
                "/api/video/" +
                filename

        })


    except Exception as e:


        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500



# =========================================================
# VIDEO FILE
# =========================================================

@app.route(
    "/api/video/<path:filename>"
)
def get_video(filename):


    filename =
        os.path.basename(
            filename
        )


    filepath =
        os.path.join(
            DOWNLOAD_DIR,
            filename
        )


    if not os.path.isfile(
        filepath
    ):

        return jsonify({

            "success":
                False,

            "error":
                "Video မတွေ့ပါ"

        }), 404


    return send_file(

        filepath,

        as_attachment=True,

        download_name=filename

    )



# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":


    port =
        int(
            os.environ.get(
                "PORT",
                10000
            )
        )


    app.run(

        host="0.0.0.0",

        port=port

    )
