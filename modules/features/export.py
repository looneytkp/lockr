import os
import sys
from vault import load_vault

def get_downloads_folder():
    if os.name == "nt" or sys.platform.startswith("win"):
        return os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")

def process_export(args, ui, key=None, encrypted=False):
    downloads_folder = get_downloads_folder()
    os.makedirs(downloads_folder, exist_ok=True)
    filename = os.path.join(downloads_folder, "lockr_export.txt")
    proceed = ui.prompt(f"[!] Exporting will save all passwords as plain text to {filename}. Proceed? (y/n): ").strip().lower()
    if proceed != "y":
        ui.print_line("[!] Cancelled.")
        return

    entries = load_vault(key, encrypted)
    if not entries:
        ui.print_line("[!] Vault is empty.")
        return
    if os.path.exists(filename):
        overwrite = ui.prompt(f"[?] File {filename} exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != "y":
            ui.print_line("[!] Export cancelled to prevent overwrite.")
            return
    try:
        with open(filename, "w") as f:
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                id_ = entry.get("id", "")
                pwd = entry.get("password", "")
                ts = entry.get("last_updated", "")
                f.write(f"{id_}: {pwd}     {ts}\n")
        ui.print_line(f"[✓] Passwords exported to {filename}")
    except Exception as e:
        ui.print_line(f"[X] Failed to export passwords: {e}")