from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return """
    <h1>🎬 MM Caption API</h1>
    <p>Backend is running successfully.</p>
    """

@app.post("/api/download")
def download():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "RedNote link ထည့်ပါ"
        }), 400

    return jsonify({
        "success": True,
        "message": "Link received",
        "url": url
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
