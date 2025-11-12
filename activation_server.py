from flask import Flask, request, jsonify
import json
import os
import hashlib
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

KEYS_FILE = "keys.json"
HWID_FILE = "hwids.json"

# ---------------- Helper Functions ----------------
def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def load_hwids():
    if os.path.exists(HWID_FILE):
        with open(HWID_FILE, "r") as f:
            return json.load(f)
    return {}

def save_hwids(hwids):
    with open(HWID_FILE, "w") as f:
        json.dump(hwids, f, indent=4)

def is_key_valid(key, hwid):
    keys = load_keys()
    hwids = load_hwids()

    if key not in keys:
        return False, "Key does not exist"

    key_data = keys[key]

    # Check if key is already used
    if key_data.get("used"):
        return False, "Key already used"

    # Check temporary key expiration
    if key_data.get("expires_at"):
        expire_time = datetime.fromisoformat(key_data["expires_at"])
        if datetime.utcnow() > expire_time:
            return False, "Temporary key expired"

    # Bind HWID
    hwids[key] = hwid
    key_data["used"] = True
    save_keys(keys)
    save_hwids(hwids)
    return True, f"Key activated successfully ({'Temporary' if key_data.get('expires_at') else 'Infinite'})"

# ---------------- Routes ----------------
@app.route("/activate", methods=["POST"])
def activate():
    data = request.get_json()
    if not data or "key" not in data or "hwid" not in data:
        return jsonify({"error": "Missing key or hwid"}), 400

    key = data["key"].strip()
    hwid = data["hwid"].strip()
    valid, message = is_key_valid(key, hwid)

    if valid:
        keys = load_keys()
        payload = keys[key]
        return jsonify({"success": True, "message": message, "expires_at": payload.get("expires_at")})
    else:
        return jsonify({"error": message}), 400

@app.route("/add_key", methods=["POST"])
def add_key():
    data = request.get_json()
    if not data or "key" not in data or "type" not in data:
        return jsonify({"error": "Missing key or type"}), 400

    key = data["key"].strip()
    key_type = data["type"]  # 'infinite' or 'temporary'

    keys = load_keys()
    if key in keys:
        return jsonify({"error": "Key already exists"}), 400

    key_data = {"used": False}
    if key_type == "temporary":
        key_data["expires_at"] = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    keys[key] = key_data
    save_keys(keys)
    return jsonify({"success": True, "message": f"Key {key} added ({key_type})"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
