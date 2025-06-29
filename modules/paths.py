import os

HOME = os.path.expanduser("~")
LOCKR_DIR = os.path.join(HOME, ".lockr")
PASS_FILE = os.path.join(LOCKR_DIR, "passwords.enc")
CONFIG_FILE = os.path.join(LOCKR_DIR, "config.json")
SALT_FILE = os.path.join(LOCKR_DIR, "salt.bin")
HINT_FILE = os.path.join(LOCKR_DIR, "hint_key.txt")
TOKEN_FILE = os.path.expanduser("~/.lockr/token.enc")
DROPBOX_TOKEN_FILE = os.path.expanduser("~/.lockr/system/dropbox_token.gpg")