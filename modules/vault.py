import os
import sys
import json
from paths import PASS_FILE
from encrypt import encrypt_data, decrypt_data

def load_vault(key=None, encrypted=False):
    if not os.path.exists(PASS_FILE):
        return []
    try:
        with open(PASS_FILE, "rb") as f:
            content = f.read()
        if not content:
            return []
        if encrypted:
            if not key:
                raise ValueError("Encryption enabled but no key provided")
            data = decrypt_data(content, key)
        else:
            data = content.decode()
        # Return as list of dicts (JSON)
        return json.loads(data)
    except Exception:
        print("[X] Incorrect passphrase or vault corrupted.")
        sys.exit(1)

def save_vault(entries, key=None, encrypted=False):
    data = json.dumps(entries)
    if encrypted:
        if not key:
            raise ValueError("Encryption enabled but no key provided")
        enc = encrypt_data(data, key)
        with open(PASS_FILE, "wb") as f:
            f.write(enc)
    else:
        with open(PASS_FILE, "w") as f:
            f.write(data)