from datetime import datetime
from features.generate import generate_password
from features.strength import password_strength_feedback
from vault import load_vault, save_vault

def process_edit(args, ui, key=None, encrypted=False):
    use_generate = False
    ids = []
    for arg in args:
        if arg in ("--g", "--generate"):
            use_generate = True
        elif len(ids) < 10:
            ids.append(arg)
    if not ids:
        ids = ui.prompt("[?] Enter up to 10 IDs to edit (space-separated): ").strip().split()[:10]
        if not ids or not any(ids):
            ui.print_line("[X] ID is required to edit passwords.")
            return
    if len(args) > 10:
        ui.print_line("[!] Maximum arguments is 10. Only the first 10 will be used.")

    entries = load_vault(key, encrypted)
    if not isinstance(entries, list):
        entries = []

    for id_ in ids[:10]:
        found = False
        changed = False
        for entry in entries:
            if entry["id"] == id_:
                found = True
                if use_generate:
                    new_pwd = generate_password(12)
                    entry["password"] = new_pwd
                    entry["last_updated"] = datetime.utcnow().isoformat() + "Z"
                    changed = True
                else:
                    new_pwd = ui.prompt(f"[?] Change password for {id_} (visible): ").strip()
                    if not new_pwd:
                        ui.print_line(f"[X] Password is required to update {id_}. Skipping.")
                        continue
                    if len(new_pwd) < 8 or len(new_pwd) > 24:
                        ui.print_line("[!] Password length should be between 8 and 24 characters.")
                        continue
                    feedback = password_strength_feedback(new_pwd)
                    if feedback:
                        ui.print_line(f"[!] Weak password: {'. '.join(feedback)}.")
                        save_weak = ui.prompt("[?] Save this weak password? (y/n): ").strip().lower()
                        if save_weak != "y":
                            gen = ui.prompt("[?] Generate a strong password instead? (y/n): ").strip().lower()
                            if gen == "y":
                                new_pwd = generate_password(12)
                                ui.print_line(f"[✓] Generated strong password: {new_pwd}")
                            else:
                                ui.print_cancel()
                                continue
                    else:
                        ui.print_line("[✓] Strong password")
                    entry["password"] = new_pwd
                    entry["last_updated"] = datetime.utcnow().isoformat() + "Z"
                    changed = True
        if found and changed:
            ui.print_line(f"[✓] Password for {id_} updated.")
        elif not found:
            ui.print_line(f"[!] No entry found for ID: {id_}")
    save_vault(entries, key, encrypted)