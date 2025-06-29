import os
import json
import dropbox
from dropbox.exceptions import ApiError
from paths import CONFIG_FILE, PASS_FILE
from encrypt import prompt_key, derive_key
import ui
from features.dropbox_oauth import (
    prompt_and_save_creds,
    load_dropbox_creds,
    get_access_token_from_refresh,
)
import sys

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"backup": False}

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

def delete_backup(ui, dbx):
    try:
        dbx.files_delete_v2("/lockr_backup/passwords.gpg")
        ui.print_line("[✓] Backup deleted successfully from Dropbox.")
        return True
    except ApiError as e:
        if 'path_lookup/not_found' in str(e):
            ui.print_line("Failed to delete backup: No backup found.")
            return True
        ui.print_line(f"[X] Failed to delete backup: {e}")
        return False
    except Exception as e:
        ui.print_line(f"[X] Unexpected error deleting backup: {e}")
        return False

def dropbox_menu(ui_obj, key):
    while True:
        ui.print_dropbox_menu()
        choice = ui_obj.prompt("[?] Choose: ").strip()
        if choice == "1":
            cfg = load_config()
            toggle_automatic_backup(cfg, ui_obj)
        elif choice == "2":
            from features.dropbox_backup import do_backup
            ui_obj.print_line("[*] Backing up to Dropbox, please wait...")
            do_backup(ui_obj, key)
        elif choice == "3":
            from features.dropbox_restore import do_restore
            ui_obj.print_line("[*] Restoring from Dropbox, please wait...")
            do_restore(ui_obj, key)
        elif choice == "4":
            try:
                creds = load_dropbox_creds(key)
                if not creds:
                    ui_obj.print_line("[!] Dropbox credentials not configured. Run backup setup first.")
                    continue
                access_token = get_access_token_from_refresh(creds, ui_obj)
                dbx = dropbox.Dropbox(access_token)
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