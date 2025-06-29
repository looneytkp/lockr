import secrets
import string
import random
from datetime import datetime
from vault import load_vault, save_vault
import re

MIN_PWD_LEN = 8
MAX_PWD_LEN = 24

def generate_password(length,
                      include_lower=True,
                      include_upper=True,
                      include_digits=True,
                      include_special=True,
                      exclude_ambiguous=True):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = '!@#$%^&*_+-='
    ambiguous = 'O0l1I'
    pool = ''
    if include_lower:
        pool += lower
    if include_upper:
        pool += upper
    if include_digits:
        pool += digits
    if include_special:
        pool += special
    if exclude_ambiguous:
        pool = ''.join(ch for ch in pool if ch not in ambiguous)
    if length < (include_lower + include_upper + include_digits + include_special):
        raise ValueError("Length too short for required character sets")
    password_chars = []
    if include_lower:
        password_chars.append(secrets.choice([c for c in lower if c not in ambiguous]))
    if include_upper:
        password_chars.append(secrets.choice([c for c in upper if c not in ambiguous]))
    if include_digits:
        password_chars.append(secrets.choice([c for c in digits if c not in ambiguous]))
    if include_special:
        password_chars.append(secrets.choice(special))
    remaining_length = length - len(password_chars)
    password_chars.extend(secrets.choice(pool) for _ in range(remaining_length))
    random.shuffle(password_chars)
    return ''.join(password_chars)

def is_valid_id(id_):
    if not id_ or ' ' in id_ or ':' in id_ or '\n' in id_ or '\r' in id_:
        return False
    return True

def resolve_duplicate_id(id_, exist_ids):
    if id_ not in exist_ids:
        return id_
    n = 1
    while f"{id_}_{n}" in exist_ids:
        n += 1
    return f"{id_}_{n}"

def process_generate(args, ui, key, encrypted, DEFAULT_LEN=12):
    lines = load_vault(key, encrypted)
    if isinstance(lines, list) and lines and isinstance(lines[0], str):
        entries = []
        for line in lines:
            if ':' in line:
                id_, rest = line.split(':', 1)
                password = rest.strip().split(' ', 1)[0]
                entries.append({
                    "id": id_.strip(),
                    "password": password,
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                })
    else:
        entries = lines if isinstance(lines, list) else []

    ids = []
    pwlen = DEFAULT_LEN

    for arg in args:
        if arg.startswith("--") and arg[2:].isdigit():
            n = int(arg[2:])
            if n < MIN_PWD_LEN or n > MAX_PWD_LEN:
                ui.print_line(f"[X] Password length must be between {MIN_PWD_LEN} and {MAX_PWD_LEN}")
                return
            pwlen = n
        else:
            if len(ids) < 10:
                ids.append(arg)

    if len(ids) == 0:
        entered = ui.prompt("[?] Enter up to 10 IDs (space-separated): ").strip().split()
        if len(entered) > 10:
            ui.print_line("[!] Maximum arguments is 10. Only the first 10 will be used.")
        ids = entered[:10]
        if not ids or not any(ids):
            ui.print_line("[X] ID is required to generate passwords.")
            return

    if len(args) > 10:
        ui.print_line("[!] Maximum arguments is 10. Only the first 10 will be used.")

    max_id_len = max((len(id_) for id_ in ids), default=0)
    pad_len = max_id_len + 2

    exist_ids = [entry['id'] for entry in entries]

    for id_ in ids[:10]:
        if not is_valid_id(id_):
            ui.print_line(f"[X] Invalid ID '{id_}': IDs cannot contain spaces, colons, or newlines.")
            continue
        pwd = generate_password(pwlen)
        unique_id = resolve_duplicate_id(id_, exist_ids)
        exist_ids.append(unique_id)
        ui.print_line(f"[✓] {unique_id + ':':<{pad_len}} {pwd}")
        entries.append({
            "id": unique_id,
            "password": pwd,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        })

    save_vault(entries, key, encrypted)
    ui.print_line("\n[✓] Passwords have been generated and saved.")
    ui.print_line("[*] Execute 'lockr -l' to view saved passwords.")