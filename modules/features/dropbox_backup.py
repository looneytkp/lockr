import os
import json
import dropbox
from paths import CONFIG_FILE, PASS_FILE, DROPBOX_TOKEN_FILE
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

def is_vault_empty(ui_obj, key, encrypted):
    return not process_list([], ui_obj, key, encrypted, quiet=True)

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

def sync_and_backup(ui_obj, key, local_path, dbx, remote_path=REMOTE_PATH):
    # Download & merge cloud
    try:
        _, res = dbx.files_download(remote_path)
        cloud_data = res.content
        cloud_entries = json.loads(decrypt_data(cloud_data, key))
        cloud_dict = {e["id"]: e for e in cloud_entries if isinstance(e, dict)}
    except dropbox.exceptions.ApiError:
        cloud_dict = {}
    except Exception as e:
        ui_obj.print_line(f"[X] Failed to load Dropbox vault: {e}")
        return False

    try:
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                local_entries = json.loads(decrypt_data(f.read(), key))
                local_dict = {e["id"]: e for e in local_entries if isinstance(e, dict)}
        else:
            local_dict = {}
    except Exception as e:
        ui_obj.print_line(f"[X] Failed to load local vault: {e}")
        return False

    merged = {}
    for entry_id in set(local_dict.keys()) | set(cloud_dict.keys()):
        l = local_dict.get(entry_id)
        c = cloud_dict.get(entry_id)
        if l and c:
            merged[entry_id] = l if l['last_updated'] >= c['last_updated'] else c
        elif l:
            merged[entry_id] = l
        elif c:
            merged[entry_id] = c

    try:
        with open(local_path, "wb") as f:
            f.write(encrypt_data(json.dumps(list(merged.values())), key))
        dbx.files_upload(
            encrypt_data(json.dumps(list(merged.values())), key),
            remote_path,
            mode=dropbox.files.WriteMode.overwrite,
        )
        ui_obj.print_line("[✓] Vault merged and synced with Dropbox.")
        return True
    except Exception as e:
        ui_obj.print_line(f"[X] Failed to save/upload merged vault: {e}")
        return False

def do_backup(ui_obj, key):
    creds = load_dropbox_creds(key)
    if not creds:
        ui_obj.print_line("[!] Dropbox credentials not configured. Run backup setup first.")
        return False
    try:
        access_token = get_access_token_from_refresh(creds, ui_obj)
    except Exception:
        return False
    try:
        dbx = dropbox.Dropbox(access_token)
        ui_obj.print_line("[*] Backing up to Dropbox...")
        return sync_and_backup(ui_obj, key, PASS_FILE, dbx)
    except Exception as e:
        ui_obj.print_line(f"[X] Backup/sync failed: {e}")
        return False

def dropbox_menu(ui_obj, key):
    while True:
        ui.print_dropbox_menu()
        choice = ui_obj.prompt("[?] Choose: ").strip()
        if choice == "1":
            cfg = load_config()
            toggle_automatic_backup(cfg, ui_obj)
        elif choice == "2":
            do_backup(ui_obj, key)
        elif choice == "3":
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
            if os.path.exists(DROPBOX_TOKEN_FILE):
                os.remove(DROPBOX_TOKEN_FILE)
            ui_obj.print_line("[✓] Dropbox disabled and settings cleared.")
        elif choice == "6" or not choice or choice not in ["1", "2", "3", "4", "5"]:
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