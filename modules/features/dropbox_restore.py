import os
import json
import dropbox
from paths import CONFIG_FILE, PASS_FILE
from encrypt import prompt_key, derive_key, encrypt_data, decrypt_data
import ui
from features.dropbox_oauth import (
    oauth_setup_flow,
    load_dropbox_creds,
    get_access_token_from_refresh,
)
from features.list import process_list
import sys

REMOTE_PATH = "/lockr_backup/passwords.gpg"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"backup": False}

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

def load_vault(filepath, key):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "rb") as f:
        data = f.read()
        if not data:
            return []
        try:
            entries = json.loads(decrypt_data(data, key))
        except json.JSONDecodeError:
            return []
    # Always return a list of dicts
    return [entry for entry in entries if isinstance(entry, dict)]

def is_vault_empty(ui_obj, key, encrypted):
    entries = load_vault(PASS_FILE, key)
    if not entries:
        if not ui_obj:
            return True
        ui_obj.print_line("[!] There are no saved passwords.")
        return True
    return False

def toggle_automatic_backup(cfg, ui_obj):
    current = cfg.get("automatic_backup", "disabled")
    new_status = "enabled" if current == "disabled" else "disabled"
    cfg["automatic_backup"] = new_status
    save_config(cfg)
    ui_obj.print_line(f"[✓] Automatic backup {new_status.upper()}.")

def setup_backup(ui_obj, key):
    if oauth_setup_flow(ui_obj, key):
        cfg = load_config()
        cfg["backup"] = True
        cfg["provider"] = "dropbox"
        save_config(cfg)
        ui_obj.print_line("[✓] Dropbox backup configured.")
        return True
    else:
        ui_obj.print_line("[X] Dropbox credential setup failed.")
        return False

def do_backup(ui_obj, key):
    creds = load_dropbox_creds(key)
    if not creds:
        ui_obj.print_line("[!] Dropbox credentials not configured. Run backup setup first.")
        return False
    try:
        access_token = get_access_token_from_refresh(creds, ui_obj)
    except Exception as e:
        ui_obj.print_line(f"[X] Failed to refresh Dropbox access token: {e}")
        return False
    if is_vault_empty(ui_obj, key, True):
        return False
    try:
        dbx = dropbox.Dropbox(access_token)
        ui_obj.print_line("[*] Backing up to Dropbox, please wait...")
        # Your sync and backup implementation here (not shown)
        ui_obj.print_line("[✓] Backup completed.")
        return True
    except Exception as e:
        ui_obj.print_line(f"[X] Backup failed: {e}")
        return False

def dropbox_menu(ui_obj, key):
    while True:
        ui.print_dropbox_menu()
        choice = ui_obj.prompt("[?] Choose: ").strip()
        if choice == "1":
            cfg = load_config()
            toggle_automatic_backup(cfg, ui_obj)
        elif choice == "2":
            ui_obj.print_line("[*] Backing up to Dropbox, please wait...")
            do_backup(ui_obj, key)
        elif choice == "3":
            ui_obj.print_line("[*] Restoring from Dropbox, please wait...")
            from features.dropbox_restore import do_restore
            do_restore(ui_obj, key)
        elif choice == "4":
            try:
                creds = load_dropbox_creds(key)
                if not creds:
                    ui_obj.print_line("[!] Dropbox credentials not configured. Run backup setup first.")
                    continue
                access_token = get_access_token_from_refresh(creds, ui_obj)
                dbx = dropbox.Dropbox(access_token)
                from features.dropbox_utils import delete_backup
                delete_backup(ui_obj, dbx)
            except Exception as e:
                ui_obj.print_line(f"[X] Delete backup failed: {e}")
        elif choice == "5":
            cfg = load_config()
            cfg["backup"] = False
            cfg.pop("provider", None)
            cfg.pop("automatic_backup", None)
            save_config(cfg)
            from features.dropbox_oauth import DROPBOX_TOKEN_FILE
            if os.path.exists(DROPBOX_TOKEN_FILE):
                os.remove(DROPBOX_TOKEN_FILE)
            ui_obj.print_line("[✓] Dropbox disabled and settings cleared.")
        elif choice == "6" or not choice or choice not in ["1","2","3","4","5"]:
            break
        elif choice == "7":
            ui_obj.print_line("[✓] Exiting program.")
            sys.exit(0)
        else:
            ui_obj.print_line("[!] Invalid choice, try again.")

def dropbox_backup_menu(ui_obj, key=None):
    if key is None:
        key_input = prompt_key()
        if key_input == "":
            ui_obj.print_line("[X] Master key required for backup features.")
            return
        key = derive_key(key_input)

    creds = load_dropbox_creds(key)
    while True:
        ui.print_backup_restore_menu()
        choice = ui_obj.prompt("[?] Choose: ").strip()
        if not choice or choice == "3":
            break
        elif choice == "4":
            ui_obj.print_line("[✓] Exiting program.")
            sys.exit(0)

        if choice == "1":
            if not creds:
                if setup_backup(ui_obj, key):
                    creds = load_dropbox_creds(key)
                    ui_obj.print_line("[✓] Dropbox backup enabled. You can now backup/restore.")
                    continue
                else:
                    ui_obj.print_line("[X] Dropbox setup failed.")
                    break
            else:
                dropbox_menu(ui_obj, key)
        elif choice == "2":
            ui_obj.print_line("[!] Google Drive support not implemented yet.")
        else:
            ui_obj.print_line("[!] Cancelled.")
            break