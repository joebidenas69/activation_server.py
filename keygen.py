import random, string, requests

SERVER = "https://activation-server-py-1.onrender.com"

def generate_key():
    parts = []
    for _ in range(4):
        part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        parts.append(part)
    return '-'.join(parts)

def add_key_to_server(key, expires):
    try:
        resp = requests.post(
            SERVER + "/add_key",
            json={"key": key, "expires": expires},
            timeout=10
        )
        if resp.status_code == 200:
            print(f"[SUCCESS] Key added: {key}")
        else:
            print(f"[ERROR] Could not add key: {key}, reason: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Server request failed: {e}")

if __name__ == "__main__":
    t = input("30 min key? (y/n): ").strip().lower()
    expires = 1800 if t == "y" else 0
    key = generate_key()
    add_key_to_server(key, expires)
