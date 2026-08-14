from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "/tmp/videos"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route("/")
def home():
    return "MM Caption API - RedNote Downloader is running"


@app.route("/api/download", methods=["POST"])
def download_video():

    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "RedNote link ထည့်ပါ"
        }), 400

    job_id = str(uuid.uuid4())

    output = os.path.join(
        DOWNLOAD_DIR,
        job_id + ".%(ext)s"
    )

    options = {
        "outtmpl": output,
        "format": "best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True
    }

    try:

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            filepath = ydl.prepare_filename(info)

        if not os.path.exists(filepath):

            return jsonify({
                "success": False,
                "error": "Video file မတွေ့ပါ"
            }), 500

        filename = os.path.basename(filepath)

        return jsonify({
            "success": True,
            "title": info.get(
                "title",
                "RedNote Video"
            ),
            "filename": filename,
            "video_url":
                "/api/video/" + filename
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/video/<filename>")
def get_video(filename):

    filename = os.path.basename(filename)

    filepath = os.path.join(
        DOWNLOAD_DIR,
        filename
    )

    if not os.path.isfile(filepath):

        return jsonify({
            "success": False,
            "error": "Video မတွေ့ပါ"
        }), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
