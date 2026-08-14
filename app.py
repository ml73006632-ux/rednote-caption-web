from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "/tmp/videos"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return """
    <h1>🎬 MM Caption API</h1>
    <p>RedNote Downloader is ready.</p>
    """


@app.post("/api/download")
def download_video():

    data = request.get_json(silent=True) or {}

    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "RedNote link ထည့်ပါ"
        }), 400

    filename = str(uuid.uuid4())

    output = os.path.join(
        DOWNLOAD_DIR,
        filename
    )

    ydl_opts = {
        "outtmpl": output + ".%(ext)s",
        "format": "best",
        "noplaylist": True,
        "quiet": True
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            filepath = ydl.prepare_filename(info)

        return jsonify({
            "success": True,
            "title": info.get("title", "RedNote Video"),
            "video_url": "/api/video/" + os.path.basename(filepath)
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.get("/api/video/<filename>")
def get_video(filename):

    filepath = os.path.join(
        DOWNLOAD_DIR,
        filename
    )

    if not os.path.exists(filepath):

        return jsonify({
            "success": False,
            "error": "Video မတွေ့ပါ"
        }), 404

    return send_file(
        filepath,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
