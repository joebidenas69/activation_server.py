# keygen.py
import sqlite3
import secrets
import string
import hashlib
from datetime import datetime

DB = "licenses.db"
SALT = "tHwaPGRtAk4K7mkS6XDCF2MWSrDEyX"  # change to a long random string

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT UNIQUE,
            created_at TEXT,
            used INTEGER DEFAULT 0,
            used_by TEXT,
            used_at TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_key(parts=4, part_len=4):
    alphabet = string.ascii_uppercase + string.digits
    return '-'.join(''.join(secrets.choice(alphabet) for _ in range(part_len)) for _ in range(parts))

def hash_key(raw_key):
    return hashlib.sha256((SALT + raw_key).encode()).hexdigest()

def add_keys(n=10):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    for _ in range(n):
        k = generate_key()
        hk = hash_key(k)
        try:
            c.execute("INSERT INTO licenses (key_hash, created_at) VALUES (?, ?)", (hk, datetime.utcnow().isoformat()))
            conn.commit()
            print("NEW KEY:", k)
        except sqlite3.IntegrityError:
            # collision (very unlikely) — skip
            pass
    conn.close()

if __name__ == "__main__":
    init_db()
    add_keys(20)  # change to how many keys you want
