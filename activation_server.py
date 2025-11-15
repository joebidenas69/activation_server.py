import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
KEYS_FILE = "keys.json"

# Create keys.json if it doesn't exist
if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({}, f, indent=4)

# Load keys
with open(KEYS_FILE, "r") as f:
    keys = json.load(f)

@app.route("/add_key", methods=["POST"])
def add_key():
    data = request.get_json()
    key = data.get("key")
    key_type = data.get("type", "infinite")  # 'infinite' or 'temp'

    if not key:
        return jsonify({"error": "Missing key"}), 400

    keys[key] = {"type": key_type, "used": False}
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

    return jsonify({"success": True, "key": key, "type": key_type}), 200

@app.route("/activate", methods=["POST"])
def activate():
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid")

    if not key or not hwid:
        return jsonify({"error": "Missing key or hwid"}), 400

    if key not in keys:
        return jsonify({"error": "Invalid key"}), 400

    key_info = keys[key]

    if key_info["type"] == "temp":
        if key_info.get("used", False):
            return jsonify({"error": "Key already used"}), 400

        # Mark temp key as used
        key_info["used"] = True
        key_info["hwid"] = hwid
        with open(KEYS_FILE, "w") as f:
            json.dump(keys, f, indent=4)
        return jsonify({"success": True, "type": "temp"}), 200

    if key_info["type"] == "infinite":
        # Infinite keys are always reusable
        return jsonify({"success": True, "type": "infinite"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
