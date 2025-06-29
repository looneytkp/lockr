import sys
import os
import logging
from config import get_encryption_status, set_encryption_status
from encrypt import prompt_key, derive_key
from vault import load_vault, save_vault
from paths import HINT_FILE, SALT_FILE
import ui

from features.generate import process_generate
from features.custom import process_custom
from features.list import process_list
from features.search import process_search
from features.delete import process_delete
from features.edit import process_edit
from features.export import process_export
from features.encryption import encryption_menu
from features.dropbox_backup import dropbox_backup_menu

VALID_FLAGS = {
    "-g", "--generate",
    "-c", "--custom",
    "-l", "--list",
    "-s", "--search",
    "-d", "--delete",
    "-e", "--edit",
    "--export",
    "--encryption",
    "-b", "--backup",
    "-u", "--uninstall",
    "-h", "--help",
}

VALID_MENU_CHOICES = {str(i) for i in range(10)}

LOG_FILE = os.path.expanduser("~/.lockr/system/lockr.log")

# Ensure the log directory exists before logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

def ensure_dirs():
    from paths import LOCKR_DIR
    os.makedirs(LOCKR_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def initial_setup():
    from paths import CONFIG_FILE, PASS_FILE
    if not os.path.exists(CONFIG_FILE) or not os.path.exists(PASS_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        print("=== Lockr: First time setup ===")
        key_input = prompt_key(setup=True)
        if key_input == "":
            set_encryption_status(False)
            save_vault([], None, False)
            if os.path.exists(HINT_FILE):
                os.remove(HINT_FILE)
            print("[*] Vault created WITHOUT encryption.")
            logging.info("Vault created without encryption on first setup.")
        else:
            set_encryption_status(True)
            key = derive_key(key_input)
            save_vault([], key, True)
            print("[*] Vault created and ENCRYPTED.")
            logging.info("Vault created with encryption on first setup.")
        return True
    return False

def get_master_key():
    user_key = prompt_key()
    if not user_key:
        ui.print_line("[X] Key is required.")
        logging.warning("User failed to provide master key.")
        return None
    return derive_key(user_key)

def interactive_menu():
    while True:
        ui.print_main_menu()
        choice = ui.get_menu_choice()
        if choice not in VALID_MENU_CHOICES:
            break
        encrypted = get_encryption_status()
        key = None
        if encrypted and choice in "1234567":
            key = get_master_key()
            if key is None:
                continue
        try:
            if choice == "1":
                process_generate([], ui, key, encrypted)
            elif choice == "2":
                process_custom([], ui, key, encrypted)
            elif choice == "3":
                process_list([], ui, key, encrypted)
            elif choice == "4":
                process_search([], ui, key, encrypted)
            elif choice == "5":
                process_delete([], ui, key, encrypted)
            elif choice == "6":
                process_edit([], ui, key, encrypted)
            elif choice == "7":
                process_export([], ui, key, encrypted)
            elif choice == "8":
                encryption_menu(ui, load_vault, save_vault, SALT_FILE)
            elif choice == "9":
                dropbox_backup_menu(ui, key)
            elif choice == "0":
                break
        except Exception as e:
            ui.print_line(f"[X] Error: {e}")
            logging.error(f"Error processing menu choice {choice}: {e}")
    ui.print_line("Goodbye!")
    logging.info("User exited interactive menu.")

def main():
    if initial_setup():
        return
    ensure_dirs()
    args = sys.argv
    if len(args) < 2:
        interactive_menu()
        return

    flag = args[1]
    if flag in ("-h", "--help"):
        ui.print_usage()
        return

    if flag not in VALID_FLAGS:
        ui.print_line("[X] Invalid flag provided.")
        ui.print_usage()
        logging.warning(f"Invalid flag used: {flag}")
        return

    if flag in ("-u", "--uninstall"):
        import subprocess
        ui.print_line("[*] Running uninstall script...")
        uninstall_script = os.path.expanduser("~/.lockr/uninstall.py")
        if os.path.exists(uninstall_script):
            try:
                subprocess.run([sys.executable, uninstall_script], check=True)
                ui.print_line("[✓] Uninstallation complete.")
            except Exception as e:
                ui.print_line(f"[X] Uninstallation failed: {e}")
                logging.error(f"Uninstallation failed: {e}")
        else:
            ui.print_line("[X] Uninstall script not found.")
        return

    encrypted = get_encryption_status()
    key = None

    if encrypted and flag in ("-g", "--generate", "-c", "--custom", "-l", "--list", "-s", "--search", "-d", "--delete", "-e", "--edit"):
        key = get_master_key()
        if key is None:
            return

    try:
        if flag in ("-g", "--generate"):
            process_generate(args[2:], ui, key, encrypted)
        elif flag in ("-c", "--custom"):
            process_custom(args[2:], ui, key, encrypted)
        elif flag in ("-l", "--list"):
            process_list(args[2:], ui, key, encrypted)
        elif flag in ("-s", "--search"):
            process_search(args[2:], ui, key, encrypted)
        elif flag in ("-d", "--delete"):
            process_delete(args[2:], ui, key, encrypted)
        elif flag in ("-e", "--edit"):
            process_edit(args[2:], ui, key, encrypted)
        elif flag == "--export":
            process_export(args[2:], ui, key, encrypted)
        elif flag == "--encryption":
            encryption_menu(ui, load_vault, save_vault, SALT_FILE)
        elif flag in ("-b", "--backup"):
            key = get_master_key()
            if key is None:
                return
            dropbox_backup_menu(ui, key)
    except Exception as e:
        ui.print_line(f"[X] Error executing flag {flag}: {e}")
        logging.error(f"Error executing flag {flag}: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.print_keyboard_interrupt()
        logging.info("User aborted with keyboard interrupt.")