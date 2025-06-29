import os
import getpass
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from paths import SALT_FILE, HINT_FILE

def remove_hint_and_salt():
    for file in (HINT_FILE, SALT_FILE):
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception:
            pass

def prompt_key(setup=False, changing_key=False):
    """
    If setup=True: prompt for new key + hint with checks.
    If changing_key=True: prompt new key + hint without generating new salt.
    Else: prompt for existing key with optional hint shown.
    """
    if setup or changing_key:
        attempts = 2
        for attempt in range(attempts):
            k1 = getpass.getpass("[?] Set master key (leave blank for no encryption): ")
            if k1 != "" and len(k1) <= 5:
                print("[X] Key must be longer than 5 characters or blank for no encryption.")
                continue
            k2 = getpass.getpass("[?] Confirm key: ")
            if k1 != k2:
                print("[X] Keys do not match.")
                continue
            if k1 == "":
                remove_hint_and_salt()
                return ""
            hint = input("[?] (Optional) Set a hint for your master key (leave blank to skip): ").strip()
            if hint and hint == k1:
                print("[X] Hint cannot be the same as the master key.")
                if attempt == 0:
                    continue
                else:
                    print("[!] Aborting encryption setup. Vault will not be encrypted.")
                    remove_hint_and_salt()
                    return ""
            if hint:
                with open(HINT_FILE, "w") as f:
                    f.write(hint)
            else:
                remove_hint_and_salt()
            return k1
        print("[!] Proceeding without encryption.")
        remove_hint_and_salt()
        return ""
    else:
        if os.path.exists(HINT_FILE):
            with open(HINT_FILE) as f:
                hint = f.read().strip()
            if hint:
                print(f"💡 Hint: {hint}")
        return getpass.getpass("[?] Enter master key: ")

def get_salt():
    if os.path.exists(SALT_FILE):
        return open(SALT_FILE, "rb").read()
    salt = os.urandom(16)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    return salt

def derive_key(key):
    salt = get_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(key.encode()))

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(token, key):
    f = Fernet(key)
    return f.decrypt(token).decode()