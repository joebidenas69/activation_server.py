import random
import string
import requests

# Replace with your server URL
SERVER = "https://activation-server-py-1.onrender.com"

def generate_key():
    """Generate a random key like ABCD-1234-EFGH-5678"""
    parts = []
    for _ in range(4):
        part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        parts.append(part)
    return '-'.join(parts)

def add_key_to_server(key, temporary=False):
    """Send the key to your server to register it as unused or a temp key"""
    try:
        resp = requests.post(
            SERVER + "/add_key",
            json={"key": key, "temporary": temporary},
            timeout=10
        )
        if resp.status_code == 200:
            print(f"[SUCCESS] Key added: {key}")
        else:
            print(f"[ERROR] Could not add key: {key}, reason: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Server request failed: {e}")

if __name__ == "__main__":
    num_keys = int(input("How many keys to generate? "))
    temp = input("Temporary 30-minute keys? (y/n): ").lower() == "y"

    for _ in range(num_keys):
        key = generate_key()
        add_key_to_server(key, temporary=temp)
