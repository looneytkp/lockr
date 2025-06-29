import sys
from config import get_encryption_status, set_encryption_status
from encrypt import derive_key, prompt_key
import os
from paths import HINT_FILE, SALT_FILE

def encryption_menu(ui, load_vault, save_vault, SALT_FILE):
    while True:
        encrypted = get_encryption_status()
        ui.print_line("\n=== Encryption Menu ===")
        if encrypted:
            ui.print_line("[✓] Encryption is currently ENABLED.")
            ui.print_line("1) Change encryption key")
            ui.print_line("2) Disable encryption (store as plaintext)")
            ui.print_line("3) Back")
            ui.print_line("4) Exit")
            choice = ui.prompt("[?] Choose: ").strip()
            if choice == "1":
                old_key_input = prompt_key()
                old_key = derive_key(old_key_input)
                try:
                    lines = load_vault(old_key, encrypted=True)
                except Exception:
                    ui.print_line("[X] Incorrect key or vault is corrupted.")
                    continue
                new_key = prompt_key(setup=True)
                if new_key == "":
                    ui.print_line("[X] Encryption key cannot be blank.")
                    continue
                salt = os.urandom(16)
                try:
                    with open(SALT_FILE, "wb") as f:
                        f.write(salt)
                    new_key_derived = derive_key(new_key)
                    save_vault(lines, key=new_key_derived, encrypted=True)
                    set_encryption_status(True)
                    ui.print_line("[✓] Key changed successfully.")
                except Exception as e:
                    ui.print_line(f"[X] Failed to change key: {e}")
                    continue
            elif choice == "2":
                key_input = prompt_key()
                key = derive_key(key_input)
                try:
                    lines = load_vault(key, encrypted=True)
                except Exception:
                    ui.print_line("[X] Incorrect key or vault is corrupted.")
                    continue
                try:
                    save_vault(lines, key=None, encrypted=False)
                    set_encryption_status(False)
                    if os.path.exists(HINT_FILE):
                        os.remove(HINT_FILE)
                    if os.path.exists(SALT_FILE):
                        os.remove(SALT_FILE)
                    ui.print_line("[✓] Encryption disabled. Vault is now plaintext.")
                except Exception as e:
                    ui.print_line(f"[X] Failed to disable encryption: {e}")
                    continue
            elif choice == "3" or choice not in ("1", "2", "4"):
                # Back - exit encryption menu loop
                return
            elif choice == "4":
                # Exit entire program
                sys.exit(0)
        else:
            ui.print_line("[!] Encryption is currently DISABLED.")
            ui.print_line("1) Enable encryption (set new key)")
            ui.print_line("3) Back")
            ui.print_line("4) Exit")
            choice = ui.prompt("[?] Choose: ").strip()
            if choice == "1":
                lines = load_vault()
                new_key = prompt_key(setup=True)
                if new_key == "":
                    ui.print_line("[X] Encryption key cannot be blank.")
                    continue
                salt = os.urandom(16)
                try:
                    with open(SALT_FILE, "wb") as f:
                        f.write(salt)
                    new_key_derived = derive_key(new_key)
                    save_vault(lines, key=new_key_derived, encrypted=True)
                    set_encryption_status(True)
                    ui.print_line("[✓] Key enabled. Vault is now encrypted.")
                except Exception as e:
                    ui.print_line(f"[X] Failed to enable encryption: {e}")
                    continue
            elif choice == "3" or choice not in ("1", "4"):
                # Back - exit encryption menu loop
                return
            elif choice == "4":
                # Exit entire program
                sys.exit(0)