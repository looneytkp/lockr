import os
import sys
from paths import PASS_FILE
import ui
from features.dropbox_backup import do_backup
from features.export import process_export
from vault import load_vault

def uninstall_flow():
    ui.print_line("[?] Backup passwords before uninstall? (y/n): ")
    choice = input().strip().lower()
    if choice == "y":
        # Check if vault has passwords
        try:
            vault_data = load_vault(None, False)  # No encryption, just check if file exists and load plaintext
            if not vault_data:
                ui.print_line("[!] No passwords found to backup.")
                return True  # Proceed uninstall
        except Exception:
            ui.print_line("[!] Could not load vault to backup.")

        # Try Dropbox backup if configured
        ui.print_line("[*] Attempting Dropbox backup...")
        key_input = ui.prompt("[?] Enter master key for backup: ")
        if not key_input:
            ui.print_line("[!] No master key provided. Skipping Dropbox backup.")
            export_prompt()
            return True  # Proceed uninstall

        key = None
        try:
            from encrypt import derive_key
            key = derive_key(key_input)
        except Exception:
            ui.print_line("[X] Invalid master key.")
            export_prompt()
            return True

        if not do_backup(ui, key):
            ui.print_line("[X] Dropbox backup failed or not configured.")
            export_prompt()
            return True  # Proceed uninstall
        ui.print_line("[✓] Dropbox backup successful.")
        return True

    elif choice == "n":
        ui.print_line("[!] Uninstalling without backup. All saved passwords will be lost.")
        return True
    else:
        ui.print_line("[X] Invalid choice. Cancelled uninstall.")
        return False

def export_prompt():
    export_choice = ui.prompt("[?] Export passwords to plaintext file before uninstall? (y/n): ").strip().lower()
    if export_choice == "y":
        try:
            vault_lines = []
            try:
                vault_lines = load_vault(None, False)
            except Exception:
                ui.print_line("[!] Failed to load vault for export.")
            process_export(vault_lines, ui)
        except Exception as e:
            ui.print_line(f"[X] Export failed: {e}")
    else:
        ui.print_line("[!] Continuing uninstall without export.")

def uninstall():
    if not uninstall_flow():
        ui.print_line("[!] Uninstall cancelled.")
        return
    # Proceed with uninstall
    import shutil
    from paths import LOCKR_DIR
    try:
        if os.path.exists(LOCKR_DIR):
            shutil.rmtree(LOCKR_DIR)
        # Remove launcher script if any
        launcher_path = os.path.expanduser("~/.local/bin/lockr")
        if os.path.exists(launcher_path):
            os.remove(launcher_path)
        ui.print_line("[✓] Lockr uninstalled successfully.")
    except Exception as e:
        ui.print_line(f"[X] Uninstall failed: {e}")

if __name__ == "__main__":
    uninstall()