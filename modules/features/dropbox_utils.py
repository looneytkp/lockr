import os
import dropbox
from dropbox.exceptions import AuthError, ApiError

BACKUP_PATH = "/lockr_backup/passwords.gpg"

def validate_dropbox_token(token):
    try:
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        return True
    except AuthError:
        return False

def test_dropbox_upload(dbx):
    dummy_path = "/lockr_backup/test.txt"
    dummy_content = b"lockr test backup"
    try:
        dbx.files_upload(dummy_content, dummy_path, mode=dropbox.files.WriteMode.overwrite)
        dbx.files_delete_v2(dummy_path)
        return True
    except Exception as e:
        print(f"[X] Dropbox test upload failed: {e}")
        return False

def dropbox_backup(dbx, local_file_path, ui):
    ui.print_line("[*] Downloading existing backup (if any)...")
    cloud_data = None
    try:
        metadata, res = dbx.files_download(BACKUP_PATH)
        cloud_data = res.content
    except ApiError as e:
        if 'path/not_found/' in str(e):
            cloud_data = None
        else:
            ui.print_line(f"[X] Error downloading cloud backup: {e}")
            return False
    except Exception as e:
        ui.print_line(f"[X] Unexpected error downloading cloud backup: {e}")
        return False

    ui.print_line("[*] Reading local vault file...")
    try:
        with open(local_file_path, "rb") as f:
            local_data = f.read()
    except Exception as e:
        ui.print_line(f"[X] Failed to read local vault file: {e}")
        return False

    if cloud_data:
        ui.print_line("[*] Merging cloud backup with local vault...")
        merged_data = local_data + b"\n" + cloud_data
    else:
        merged_data = local_data

    ui.print_line("[*] Backing up - don't disconnect the Internet or abort.")
    try:
        dbx.files_upload(merged_data, BACKUP_PATH, mode=dropbox.files.WriteMode.overwrite)
    except Exception as e:
        ui.print_line(f"[X] Failed to upload backup: {e}")
        return False

    ui.print_line("[✓] Backup uploaded successfully to Dropbox.")
    return True

def dropbox_restore(dbx, local_file_path, ui):
    ui.print_line("[*] Downloading backup from Dropbox...")
    try:
        metadata, res = dbx.files_download(BACKUP_PATH)
        cloud_data = res.content
    except ApiError as e:
        if 'path/not_found/' in str(e):
            ui.print_line("[!] No backup found in Dropbox.")
            return False
        else:
            ui.print_line(f"[X] Error downloading backup: {e}")
            return False
    except Exception as e:
        ui.print_line(f"[X] Unexpected error downloading backup: {e}")
        return False

    if not cloud_data:
        ui.print_line("[!] No backup data found in Dropbox.")
        return False

    ui.print_line("[*] Restoring backup - don't disconnect the Internet or abort.")
    try:
        with open(local_file_path, "wb") as f:
            f.write(cloud_data)
    except Exception as e:
        ui.print_line(f"[X] Failed to write backup locally: {e}")
        return False

    ui.print_line("[✓] Backup restored successfully from Dropbox.")
    return True

def delete_backup(ui, dbx):
    try:
        dbx.files_delete_v2(BACKUP_PATH)
        ui.print_line("[✓] Backup deleted successfully from Dropbox.")
        return True
    except ApiError as e:
        if 'path_lookup/not_found' in str(e):
            ui.print_line("[!] No backup file found on Dropbox.")
            return True
        ui.print_line(f"[X] Failed to delete backup: {e}")
        return False
    except Exception as e:
        ui.print_line(f"[X] Unexpected error deleting backup: {e}")
        return False