import json
import uuid
import os

DB_FILE = "keys.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"keys": {}}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


def generate_key(type="normal"):
    db = load_db()

    key = str(uuid.uuid4()).upper()

    db["keys"][key] = {
        "type": type,       # "normal" or "infinite"
        "used": False,
        "hwid": None,
        "activated_at": None
    }

    save_db(db)
    return key


if __name__ == "__main__":
    print("1. Normal key")
    print("2. Infinite key")
    ch = input("> ")

    if ch == "1":
        print("Normal key:", generate_key("normal"))
    else:
        print("Infinite key:", generate_key("infinite"))
