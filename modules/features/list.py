from collections import defaultdict
import json
from vault import load_vault

def process_list(args, ui, key, encrypted, quiet=False):
    entries = load_vault(key, encrypted)
    if not entries:
        if not quiet:
            ui.print_line("[!] No saved passwords found.")
        return False  # No passwords
    if quiet:
        return True  # Passwords exist

    if "--json" in args:
        # Option 7: JSON pretty
        ui.print_line("Lockr - Saved Passwords (JSON)")
        ui.print_line("-" * 40)
        ui.print_line(json.dumps(entries, indent=2, ensure_ascii=False))
        return True

    if "--time" in args:
        # Option 10: with timestamps, close to ID
        ui.print_line("Lockr - Saved Passwords with Timestamps")
        ui.print_line("-" * 40)
        for idx, entry in enumerate(entries, 1):
            if not isinstance(entry, dict):
                continue
            id_ = entry.get("id", "")
            pwd = entry.get("password", "")
            ts = entry.get("last_updated", "")
            ui.print_line(f"{idx}. {id_}: {pwd}   [{ts}]")
        return True

    # Default: Option 8, grouped by base ID (duplicates under one group)
    ui.print_line("Lockr - Saved Passwords")
    ui.print_line("-" * 40)
    grouped = defaultdict(list)
    for entry in entries:
        if not isinstance(entry, dict) or "id" not in entry or "password" not in entry:
            continue
        id_ = entry["id"]
        pwd = entry["password"]
        base_id = id_.rsplit("_", 1)[0] if "_" in id_ and id_.rsplit("_", 1)[1].isdigit() else id_
        grouped[base_id].append(f"{id_}: {pwd}")
    idx = 1
    for base_id in sorted(grouped):
        group_entries = grouped[base_id]
        if len(group_entries) > 1:
            ui.print_line(f"{base_id}:")
            for entry in group_entries:
                ui.print_line(f"  {idx}. {entry.strip()}")
                idx += 1
        else:
            ui.print_line(f"{idx}. {group_entries[0].strip()}")
            idx += 1
    return True