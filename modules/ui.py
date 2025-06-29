def print_usage():
    """Prints usage instructions."""
    print("""Usage: lockr [options]

  -g, --generate [ID ...] [--N]   Generate passwords
  -c, --custom [ID ...]           Add custom passwords
  -l, --list                     List passwords
  -s, --search <ID ...>           Search passwords by ID
  -d, --delete <ID ...>           Delete passwords by ID
  -e, --edit [ID ...] [--g]       Edit/change passwords
      --encryption                Encryption settings
      --export                    Export passwords
  -b, --backup                   Backup/Restore passwords to configured cloud
  -u, --uninstall                Uninstall Lockr
  -h, --help                    Show help

Run 'lockr' without options for interactive menu.
""")

def print_main_menu():
    """Displays the main menu options."""
    print("""
+---------------------+
|        LOCKR        |
+---------------------+

[1] Generate passwords
[2] Add custom passwords
[3] List passwords
[4] Search IDs
[5] Delete passwords
[6] Edit/change passwords
[7] Export passwords
[8] Encryption options
[9] Backup/Restore
[0] Exit
""")

def get_menu_choice(prompt_msg="[?] Select option [0-9]: "):
    """Prompts the user for menu choice."""
    return input(prompt_msg).strip()

def prompt(msg):
    """Generic prompt function."""
    return input(msg)

def prompt_id(msg="[?] Enter ID for password: "):
    """Prompt for ID without spaces, retries up to 3 times."""
    attempts = 3
    while attempts > 0:
        id_ = input(msg).strip()
        if not id_:
            return ''
        if ' ' in id_:
            print("[X] ID can't contain spaces")
            attempts -= 1
            if attempts == 0:
                print("[X] Too many invalid attempts. Cancelled.")
                return ''
            continue
        return id_
    return ''

def print_line(line):
    """Prints a single line."""
    print(line)

def print_cancel():
    """Print cancel message."""
    print("[X] Operation cancelled.")

def print_keyboard_interrupt():
    """Print keyboard interrupt message."""
    print("\n[X] lockr aborted.")

def confirm(msg):
    """Simple yes/no confirmation."""
    return input(msg).strip().lower() == "y"

def print_goodbye():
    """Print goodbye message."""
    print("[✓] Lockr exited!")

def print_backup_restore_menu():
    print("""
=== Backup/Restore ===
1) Dropbox
2) Google Drive (coming soon)
3) Back
4) Exit
""")

def print_dropbox_menu():
    """Print Dropbox backup menu options."""
    print("""
=== Dropbox ===
1) Enable automatic backup
2) Backup
3) Restore
4) Delete backup
5) Disable Dropbox
6) Back
""")