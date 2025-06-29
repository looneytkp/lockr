import os
import sys
import shutil
import subprocess

def termux_install():
    print("[✓] ENV: Termux detected         [ OK ]")
    subprocess.run(
        ["pkg", "install", "-y", "python-cryptography"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("[✓] CRYPTOGRAPHY: Already found  [ OK ]")

    subprocess.run(
        ["pkg", "upgrade", "-y", "python-pip"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("[✓] PIP: Up-to-date              [ OK ]")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--user", "dropbox"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("[✓] Dropbox: Installed           [ OK ]")

def standard_install():
    print("[✓] ENV: Desktop/Shell detected  [ OK ]")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--user", "cryptography"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("[✓] CRYPTOGRAPHY: Already found  [ OK ]")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("[✓] PIP: Up-to-date              [ OK ]")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--user", "dropbox"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("[✓] Dropbox: Installed           [ OK ]")

def copy_files():
    home = os.path.expanduser("~")
    lockr_dir = os.path.join(home, ".lockr")
    modules_dir = os.path.join(lockr_dir, "modules")
    os.makedirs(modules_dir, exist_ok=True)
    shutil.copytree("modules", modules_dir, dirs_exist_ok=True)
    shutil.copy("install.py", os.path.join(lockr_dir, "install.py"))
    shutil.copy("uninstall.py", os.path.join(lockr_dir, "uninstall.py"))
    print("[✓] Files copied to: ~/.lockr/")

    local_bin = os.path.join(home, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    launcher = os.path.join(local_bin, "lockr")
    with open(launcher, "w") as f:
        f.write(f"#!/bin/sh\npython3 {os.path.join(lockr_dir, 'modules', 'lockr.py')} \"$@\"")
    os.chmod(launcher, 0o755)
    print("[✓] Launcher created: ~/.local/bin/lockr")
    print("[✓] PATH configured: ~/.local/bin")

def print_lockr_setup_ui():
    print("\n------------------ Lockr Setup ------------------")
    print("[!] INTERNET: Required during install")
    # The following will already have been printed above in order, so this section is just for grouping.
    print("-------------------------------------------------")
    print("[!] Restart your terminal to use Lockr.")
    print("[!] RUN: lockr -h")
    print("-------------------------------------------------\n")

def main():
    print("\n------------------ Lockr Setup ------------------")
    print("[!] INTERNET: Required during install")
    print("")

    # Detect Termux
    termux = "com.termux" in sys.executable or "termux" in sys.executable
    if termux or (os.path.exists("/data/data/com.termux/files/usr/bin/pkg")):
        termux_install()
    else:
        standard_install()

    copy_files()

    print("-------------------------------------------------")
    print("[!] Restart your terminal to use Lockr.")
    print("[!] RUN: lockr -h")
    print("-------------------------------------------------\n")

if __name__ == "__main__":
    main()