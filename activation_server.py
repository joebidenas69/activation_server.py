@app.route("/activate", methods=["POST"])
def activate():
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid")

    if not key or not hwid:
        return jsonify({"error": "Missing key or hwid"}), 400

    with open("keys.json", "r") as f:
        keys = json.load(f)

    if key not in keys:
        return jsonify({"error": "Invalid key"}), 400

    key_info = keys[key]

    # TEMPORARY KEY (single-use)
    if key_info["type"] == "temp":
        if key_info.get("used", False):
            return jsonify({"error": "Key already used"}), 400

        # Mark temp key as used
        key_info["used"] = True
        key_info["hwid"] = hwid

        with open("keys.json", "w") as f:
            json.dump(keys, f, indent=4)

        return jsonify({"success": True, "type": "temp"}), 200

    # INFINITE KEY (reusable)
    if key_info["type"] == "infinite":
        # Do NOT mark as used
        return jsonify({"success": True, "type": "infinite"}), 200
