from collections import defaultdict
from vault import load_vault

def process_search(args, ui, key=None, encrypted=False):
    try:
        entries = load_vault(key, encrypted)
    except Exception as e:
        ui.print_line(f"[X] Error loading vault: {e}")
        return

    queries = [q.strip().lower() for q in args[:10] if q.strip()]
    while not queries:
        input_str = ui.prompt("[?] Enter up to 10 IDs to search (space-separated): ").strip()
        queries = [q.strip().lower() for q in input_str.split() if q.strip()]
        if not queries:
            ui.print_line("[X] ID is required to search for passwords.")

    for q in queries:
        if ' ' in q:
            ui.print_line(f"[X] Query '{q}' is invalid: no spaces allowed.")
            return

    if len(queries) > 10:
        ui.print_line("[!] Maximum search arguments is 10. Only the first 10 will be used.")
        queries = queries[:10]

    found_any = False
    for q in queries:
        matches = [
            entry for entry in entries
            if isinstance(entry, dict) and "id" in entry and "password" in entry and q in entry["id"].lower()
        ]
        if not matches:
            ui.print_line(f"[!] No matching entries found for ID: {q}")
        else:
            found_any = True
            ui.print_line(f"[i] Found {len(matches)} entries for '{q}':")
            grouped = defaultdict(list)
            for entry in matches:
                id_ = entry["id"]
                pwd = entry["password"]
                base_id = id_.rsplit("_", 1)[0] if "_" in id_ and id_.rsplit("_", 1)[1].isdigit() else id_
                grouped[base_id].append(f"{id_}: {pwd}")
            for base_id in sorted(grouped):
                group_entries = grouped[base_id]
                if len(group_entries) > 1:
                    ui.print_line(f"{base_id}:")
                    for ent in group_entries:
                        ui.print_line(f"  - {ent.strip()}")
                else:
                    ui.print_line(f"- {group_entries[0].strip()}")

    if not found_any:
        ui.print_line("[!] No entries found for given queries.")