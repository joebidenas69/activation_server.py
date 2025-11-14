from flask import Flask, request, jsonify
import json
import os
import hashlib
import uuid
import time

app = Flask(__name__)

# ---------------- Configuration ----------------
KEYS_FILE = "keys.json"  # stores keys and their status
HWID_FILE = "hwids.json" # optional: to bind keys to a machine

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

    # Support old format: "used" or "unused"
    if isinstance(keys[key], str):
        key_data = {"status": keys[key], "expires": None}
    else:
        key_data = keys[key]

    # NEW: Expiration check
    if key_data.get("expires") and time.time() > key_data["expires"]:
        return False, "Key expired"

    if key_data["status"] == "used":
        return False, "Key already used"

    if key in hwids:
        return False, "Key already activated on another machine"

    # Mark key as used
    key_data["status"] = "used"
    keys[key] = key_data
    hwids[key] = hwid

    save_keys(keys)
    save_hwids(hwids)

    return True, "Key activated successfully"

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
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"error": message}), 400

# ---------------- Admin Endpoint to Add Keys ----------------
@app.route("/add_key", methods=["POST"])
def add_key():
    data = request.get_json()
    if not data or "key" not in data:
        return jsonify({"error": "Missing key"}), 400

    key = data["key"].strip()
    keys = load_keys()

    if key in keys:
        return jsonify({"error": "Key already exists"}), 400

    # NEW: Add expiration if temporary
    if data.get("temporary"):
        expires = int(time.time()) + 1800  # 30 min
        keys[key] = {"status": "unused", "expires": expires}
    else:
        keys[key] = {"status": "unused", "expires": None}

    save_keys(keys)
    return jsonify({"success": True, "message": f"Key {key} added"}), 200

# ---------------- Run Server ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
