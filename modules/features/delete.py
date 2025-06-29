from vault import load_vault, save_vault

def process_delete(args, ui, key=None, encrypted=False):
    ids_to_delete = args[:10]
    if not ids_to_delete:
        ids_to_delete = ui.prompt("[?] Enter up to 10 IDs to delete (space-separated): ").strip().split()[:10]

    if not ids_to_delete or not any(ids_to_delete):
        ui.print_line("[X] ID is required to delete passwords.")
        return

    if len(args) > 10:
        ui.print_line("[!] Maximum arguments is 10. Only the first 10 will be used.")

    # Validate and normalize IDs: strip, no spaces
    ids_to_delete = [id_.strip() for id_ in ids_to_delete if id_.strip() and ' ' not in id_]
    if not ids_to_delete:
        ui.print_line("[X] No valid IDs to delete (IDs cannot contain spaces).")
        return

    entries = load_vault(key, encrypted)
    if not isinstance(entries, list) or not entries:
        ui.print_line("[!] No saved passwords found.")
        return

    deleted = []
    new_entries = []

    for entry in entries:
        if not isinstance(entry, dict) or "id" not in entry or "password" not in entry:
            continue  # skip malformed
        if entry["id"] in ids_to_delete:
            deleted.append(entry)
        else:
            new_entries.append(entry)

    for del_id in ids_to_delete:
        matched = [e for e in deleted if e["id"] == del_id]
        if matched:
            for e in matched:
                ui.print_line(f"[✓] Deleted entry for ID: {del_id} ({e['password']})")
        else:
            ui.print_line(f"[!] No entry found for ID: {del_id}")

    if deleted:
        try:
            save_vault(new_entries, key, encrypted)
        except Exception as e:
            ui.print_line(f"[X] Failed to save vault: {e}")