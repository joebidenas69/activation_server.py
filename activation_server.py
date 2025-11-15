from flask import Flask, request, jsonify
import json
import time
import uuid
import os

DB_FILE = "keys.json"

app = Flask(__name__)

# Load or create database
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"keys": {}}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


@app.post("/activate")
def activate():
    db = load_db()
    req = request.get_json()

    key = req.get("key")
    hwid = req.get("hwid")

    if key not in db["keys"]:
        return jsonify({"success": False, "error": "Invalid key"}), 400

    k = db["keys"][key]

    # Infinite key → unlimited activations
    if k["type"] == "infinite":
        return jsonify({"success": True, "message": "Infinite key activated"}), 200

    # Normal key
    if k["used"]:
        return jsonify({"success": False, "error": "Key already used"}), 400

    # Bind HWID
    k["used"] = True
    k["hwid"] = hwid
    k["activated_at"] = time.time()

    save_db(db)
    return jsonify({"success": True, "message": "Key activated"}), 200


@app.post("/validate")
def validate():
    db = load_db()
    req = request.get_json()

    key = req.get("key")
    hwid = req.get("hwid")

    if key not in db["keys"]:
        return jsonify({"success": False, "error": "Invalid key"}), 400

    k = db["keys"][key]

    if k["type"] == "infinite":
        return jsonify({"success": True}), 200

    if not k["used"]:
        return jsonify({"success": False, "error": "Key not activated yet"}), 400

    if k["hwid"] != hwid:
        return jsonify({"success": False, "error": "Wrong device"}), 400

    return jsonify({"success": True}), 200


if __name__ == "__main__":
    app.run(port=5000)
