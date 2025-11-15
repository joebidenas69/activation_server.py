import os
import json
import time
from flask import Flask, request, jsonify

app = Flask(__name__)
KEYS_FILE = "keys.json"
TEMP_KEY_DURATION = 3600  # 60 minutes in seconds

# Create keys.json if it doesn't exist
if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({}, f, indent=4)

# Load keys
with open(KEYS_FILE, "r") as f:
    keys = json.load(f)

# ---------------- Routes ----------------
@app.route("/add_key", methods=["POST"])
def add_key():
    data = request.get_json()
    key = data.get("key")
    key_type = data.get("type", "infinite")  # 'infinite' or 'temp'

    if not key:
        return jsonify({"error": "Missing key"}), 400

    if key_type == "temp":
        # Set expiry timestamp 60 minutes from now
        expiry = int(time.time()) + TEMP_KEY_DURATION
        keys[key] = {"type": "temp", "used": False, "expiry": expiry}
    else:
        keys[key] = {"type": "infinite", "used": False}

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
        current_time = int(time.time())
        expiry = key_info.get("expiry", 0)

        if current_time > expiry:
            return jsonify({"error": "Key expired"}), 400

        if key_info.get("used", False) and key_info.get("hwid") != hwid:
            return jsonify({"error": "Key already used"}), 400

        # Mark temp key as used for this HWID
        key_info["used"] = True
        key_info["hwid"] = hwid
        with open(KEYS_FILE, "w") as f:
            json.dump(keys, f, indent=4)

        return jsonify({"success": True, "type": "temp", "expiry": expiry}), 200

    if key_info["type"] == "infinite":
        # Infinite keys are always reusable
        return jsonify({"success": True, "type": "infinite"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
