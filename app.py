import os
import time

from flask import Flask, jsonify, render_template, request

from cipher import decode_message, encode_message, get_pokemon_tokens_info, num_regions

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", num_regions=num_regions)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "num_regions": num_regions})


@app.route("/api/encode", methods=["POST"])
def api_encode():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify(
            {"error": "Please enter text to encrypt.", "encoded": "", "tokens": []}
        ), 400

    start_time = time.time()
    encoded_text = encode_message(text)
    tokens = get_pokemon_tokens_info(encoded_text)
    elapsed = time.time() - start_time

    return jsonify({"encoded": encoded_text, "tokens": tokens, "elapsed": elapsed})


@app.route("/api/decode", methods=["POST"])
def api_decode():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify(
            {"error": "Please enter Pokémon names to decrypt.", "decoded": ""}
        ), 400

    start_time = time.time()
    decoded_text = decode_message(text)
    elapsed = time.time() - start_time

    return jsonify({"decoded": decoded_text, "elapsed": elapsed})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    app.run(host="0.0.0.0", port=port, debug=False)
