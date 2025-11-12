# keygen.py
import sqlite3
import secrets
import string
import hashlib
from datetime import datetime, timedelta
import pyperclip  # to copy keys

DB = "licenses.db"
SALT = "tHwaPGRtAk4K7mkS6XDCF2MWSrDEyX"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            type TEXT,
            created_at TEXT,
            expires_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_key(parts=4, part_len=4):
    alphabet = string.ascii_uppercase + string.digits
    return '-'.join(''.join(secrets.choice(alphabet) for _ in range(part_len)) for _ in range(parts))

def add_keys(n=10, key_type='infinite'):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    for _ in range(n):
        k = generate_key()
        created_at = datetime.utcnow().isoformat()
        expires_at = None
        if key_type == 'temporary':
            expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        try:
            c.execute("INSERT INTO licenses (key, type, created_at, expires_at) VALUES (?, ?, ?, ?)",
                      (k, key_type, created_at, expires_at))
            conn.commit()
            print(f"NEW {key_type.upper()} KEY: {k}")
            pyperclip.copy(k)  # copy last generated key to clipboard
        except sqlite3.IntegrityError:
            pass
    conn.close()

if __name__ == "__main__":
    init_db()
    add_keys(5, 'infinite')      # Generate 5 infinite keys
    add_keys(5, 'temporary')     # Generate 5 temporary 30-min keys
