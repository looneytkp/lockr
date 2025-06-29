import json
from typing import Dict, Optional
from paths import CONFIG_FILE

def load_config() -> Dict:
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(data: Dict) -> None:
    try:
        tmp_file = CONFIG_FILE + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(data, f)
        # Atomic rename
        import os
        os.replace(tmp_file, CONFIG_FILE)
    except Exception as e:
        print(f"[X] Failed to save config: {e}")

def get_encryption_status() -> bool:
    data = load_config()
    return data.get("encrypted", False)

def set_encryption_status(encrypted: bool) -> None:
    try:
        data = load_config()
        data["encrypted"] = encrypted
        save_config(data)
    except Exception as e:
        print(f"[X] Failed to update encryption status: {e}")

def get_dropbox_token_encrypted() -> Optional[str]:
    config = load_config()
    return config.get("dropbox_token_encrypted")

def set_dropbox_token_encrypted(enc_token: str) -> None:
    config = load_config()
    config["dropbox_token_encrypted"] = enc_token
    save_config(config)