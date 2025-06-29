from features.strength import password_strength_feedback
from features.generate import generate_password
from datetime import datetime
from vault import load_vault, save_vault

def process_custom(args, ui, key=None, encrypted=False):
    try:
        entries = load_vault(key, encrypted)  # entries: list of dicts
    except Exception as e:
        ui.print_line(f"[X] Failed to load vault: {e}")
        return

    if not isinstance(entries, list):
        entries = []

    # Validate and normalize IDs input
    if args:
        if len(args) > 10:
            ui.print_line("[!] Maximum arguments is 10. Only the first 10 will be used.")
        ids = [id_.strip().lower() for id_ in args[:10]]
    else:
        entered = ui.prompt("[?] Enter up to 10 IDs (space-separated): ").strip().split()
        if len(entered) > 10:
            ui.print_line("[!] Maximum arguments is 10. Only the first 10 will be used.")
        ids = [id_.strip().lower() for id_ in entered[:10]]

    if not ids or not any(ids):
        ui.print_line("[X] ID is required to save passwords.")
        return

    for id_ in ids:
        if not id_:
            ui.print_line("[X] ID can't be empty.")
            return
        if ' ' in id_:
            ui.print_line("[X] ID can't contain spaces.")
            return

    # Password input for each ID
    for id_ in ids:
        while True:
            pwd = input(f"[?] Enter custom password for {id_}: ").strip()
            if not pwd:
                ui.print_line("[X] Password can't be empty.")
                continue
            if len(pwd) < 8 or len(pwd) > 64:
                ui.print_line("[!] Password length should be between 8 and 64 characters.")
                continue
            break

        feedback = password_strength_feedback(pwd)
        if feedback:
            ui.print_line(f"[!] Weak password: {'. '.join(feedback)}.")
            save_weak = ui.prompt("[?] Save this weak password? (y/n): ").strip().lower()
            if save_weak != "y":
                gen = ui.prompt("[?] Generate a strong password instead? (y/n): ").strip().lower()
                if gen == "y":
                    pwd = generate_password(12)
                    ui.print_line(f"[✓] Generated strong password: {pwd}")
                else:
                    ui.print_cancel()
                    return
        else:
            ui.print_line("[✓] Strong password")

        exist_ids = [entry['id'].lower() for entry in entries]
        unique_id = id_
        if unique_id in exist_ids:
            n = 1
            while f"{id_}_{n}" in exist_ids:
                n += 1
            unique_id = f"{id_}_{n}"
            ui.print_line(f"[i] ID '{id_}' exists, saved as '{unique_id}'.")

        entry = {
            "id": unique_id,
            "password": pwd,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
        entries.append(entry)
        ui.print_line(f"[✓] Saved: {unique_id}: {pwd} [{entry['last_updated']}]")

    try:
        save_vault(entries, key, encrypted)
        ui.print_line("\n[✓] Passwords saved successfully.")
        ui.print_line("[*] Use 'lockr -l' to list saved passwords.")
    except Exception as e:
        ui.print_line(f"[X] Failed to save vault: {e}")