import requests
import uuid
import random
import string

SERVER_URL = "https://activation-server-py-1.onrender.com"
ADD_KEY_ENDPOINT = f"{SERVER_URL}/add_key"

def generate_key(length=16):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def add_key_to_server(key, key_type="infinite"):
    payload = {"key": key, "type": key_type}
    r = requests.post(ADD_KEY_ENDPOINT, json=payload)
    if r.status_code == 200:
        print(f"✅ Key {key} added successfully ({key_type})")
    else:
        print(f"❌ Failed to add key: {r.status_code} {r.text}")

def main():
    print("🔑 PAPISALKA HUB Key Generator")
    print("1. Infinite Key (reusable)")
    print("2. 30-minute Key (single-use)")
    choice = input("Choose key type: ")

    key_type = "infinite" if choice == "1" else "temp"
    key = generate_key()
    add_key_to_server(key, key_type)

if __name__ == "__main__":
    main()
