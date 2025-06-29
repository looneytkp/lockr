import os
import json
import requests
import urllib.parse
import dropbox
from encrypt import encrypt_data, decrypt_data
from paths import DROPBOX_TOKEN_FILE

def print_dropbox_setup_instructions(ui):
    ui.print_line("""
=== Dropbox App Setup ===

1. Go to: https://www.dropbox.com/developers/apps/create
2. Choose:
   - Scoped access
   - "Full Dropbox" (or "App folder" for more privacy)
3. Name your app (e.g., lockr-backup-yourname)
4. Click "Create App"
5. On the permissions page, enable:
   - files.content.write
   - files.content.read
6. Click "Submit" to save permissions.
7. In the app's Settings tab:
   - Copy your App key and App secret
   - **Add the following to "Redirect URIs":**
     https://localhost/lockr
   - Click "Add" or "Save" to confirm

""")

def oauth_setup_flow(ui, key):
    print_dropbox_setup_instructions(ui)
    app_key = ui.prompt("[?] Enter your Dropbox APP KEY: ").strip()
    app_secret = ui.prompt("[?] Enter your Dropbox APP SECRET: ").strip()
    redirect_uri = "https://localhost/lockr"

    params = {
        "response_type": "code",
        "client_id": app_key,
        "redirect_uri": redirect_uri,
        "token_access_type": "offline",
        "scope": "files.content.write files.content.read"
    }
    auth_url = "https://www.dropbox.com/oauth2/authorize?" + urllib.parse.urlencode(params)
    ui.print_line("\n[*] Authorize Lockr to access Dropbox.")
    ui.print_line("Open this URL in your browser:")
    ui.print_line(auth_url)
    ui.print_line("\nSign in, allow access, and copy the 'code' value from the redirected URL (or just the code).")
    code = ui.prompt("[?] Paste the FULL redirected URL or just the 'code': ").strip()

    if code.startswith("http"):
        parsed = urllib.parse.urlparse(code)
        query = urllib.parse.parse_qs(parsed.query)
        code = query.get("code", [""])[0]

    if not code:
        ui.print_line("[X] No code provided.")
        return False

    token_url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": app_key,
        "client_secret": app_secret,
        "redirect_uri": redirect_uri,
    }
    ui.print_line("\n[*] Setting up Dropbox for Lockr, please wait...")
    try:
        resp = requests.post(token_url, data=data, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()
    except Exception as e:
        ui.print_line(f"[X] Token exchange failed: {e}")
        return False

    refresh_token = token_data.get("refresh_token")
    access_token = token_data.get("access_token")
    if not refresh_token:
        ui.print_line(f"[X] Failed to get refresh token: {token_data}")
        return False

    # Test token by uploading a dummy file
    dbx = dropbox.Dropbox(access_token)
    try:
        dbx.files_upload(b"lockr test", "/lockr_backup/test_oauth.txt", mode=dropbox.files.WriteMode.overwrite)
        dbx.files_delete_v2("/lockr_backup/test_oauth.txt")
    except Exception as e:
        ui.print_line(f"[X] Dropbox token test failed: {e}")
        return False

    creds = {
        "app_key": app_key,
        "app_secret": app_secret,
        "refresh_token": refresh_token
    }
    encrypted = encrypt_data(json.dumps(creds), key)
    os.makedirs(os.path.dirname(DROPBOX_TOKEN_FILE), exist_ok=True)
    with open(DROPBOX_TOKEN_FILE, "wb") as f:
        f.write(encrypted)

    ui.print_line("[✓] Dropbox credentials saved securely.")
    return True

def load_dropbox_creds(key):
    if not os.path.exists(DROPBOX_TOKEN_FILE):
        return None
    with open(DROPBOX_TOKEN_FILE, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = decrypt_data(encrypted, key)
        return json.loads(decrypted)
    except Exception:
        return None

def get_access_token_from_refresh(creds, ui):
    token_url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "refresh_token": creds.get("refresh_token"),
        "grant_type": "refresh_token",
        "client_id": creds.get("app_key"),
        "client_secret": creds.get("app_secret"),
    }
    try:
        resp = requests.post(token_url, data=data, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            ui.print_line("[X] Failed to obtain access token from refresh token.")
            raise Exception("No access token in response")
        return access_token
    except Exception as e:
        ui.print_line(f"[X] Error requesting Dropbox access token: {e}")
        raise