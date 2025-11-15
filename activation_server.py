from flask import Flask, request, jsonify
import json, os, time

app = Flask(__name__)

KEYS_FILE = "keys.json"
HWID_FILE = "hwids.json"

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

    data = keys[key]

    # ------------- Check expiration -------------
    if data["expires_after_activation"] > 0:  
        # key has time limit
        if data["activated_at"] != 0:
            # key has been activated before
            if time.time() > data["activated_at"] + data["expires_after_activation"]:
                return False, "Key expired"

    # ------------- Check if already used -------------
    if data["activated"] == True:
        return False, "Key already used"

    # ------------- Bind HWID -------------
    if key in hwids:
        return False, "Key already activated on another machine"

    # Mark activation time
    data["activated"] = True
    data["activated_at"] = time.time()

    hwids[key] = hwid
    save_keys(keys)
    save_hwids(hwids)

    return True, "Key activated successfully"

@app.route("/activate", methods=["POST"])
def activate():
    data = request.get_json()
    if not data or "key" not in data or "hwid" not in data:
        return jsonify({"error": "Missing key or hwid"}), 400

    key = data["key"].strip()
    hwid = data["hwid"].strip()

    valid, msg = is_key_valid(key, hwid)

    if valid:
        return jsonify({"success": True, "message": msg})
    return jsonify({"error": msg}), 400

@app.route("/add_key", methods=["POST"])
def add_key():
    data = request.get_json()
    if "key" not in data:
        return jsonify({"error": "Missing key"}), 400

    key = data["key"].strip()
    expires = data.get("expires", 0)   # 0 = infinite key

    keys = load_keys()
    if key in keys:
        return jsonify({"error": "Key already exists"}), 400

    keys[key] = {
        "activated": False,
        "activated_at": 0,                 # when key gets activated
        "expires_after_activation": expires # 0 = infinite
    }

    save_keys(keys)
    return jsonify({"success": True, "message": f"Key {key} added"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
