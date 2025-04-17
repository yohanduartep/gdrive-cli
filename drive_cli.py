from dotenv import load_dotenv
import os
import io
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pathlib import Path

load_dotenv()

def authenticate():
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
    REDIRECT_URI = os.getenv('REDIRECT_URI')

    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri='https://oauth2.googleapis.com/token'
    )
    return build('drive', 'v3', credentials=creds)

def upload_file_or_folder(service, file_path, folder_id='root'):
    file_path = Path(file_path)
    try:
        if file_path.is_file():
            file_metadata = {'name': file_path.name, 'parents': [folder_id]}
            media = MediaFileUpload(file_path, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"File '{file_path.name}' uploaded successfully. File ID: {file.get('id')}")
        elif file_path.is_dir():
            folder_metadata = {
                'name': file_path.name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [folder_id]
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            print(f"Folder '{file_path.name}' created successfully. Folder ID: {folder.get('id')}")
            for child in file_path.iterdir():
                upload_file_or_folder(service, child, folder.get('id'))
        else:
            print("Invalid path. Please provide a valid file or folder path.")
    except Exception as e:
        print(f"Error uploading '{file_path}': {e}")

def list_files(service, folder_id='root'):
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=100,
            fields="files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def download_file(service, file_id, file_name):
    try:
        request = service.files().get_media(fileId=file_id)
        file_path = Path(file_name)
        with io.FileIO(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
        print(f"File downloaded to {file_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def delete_file_or_folder(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        print("File or folder deleted successfully.")
    except Exception as e:
        print(f"Error deleting file or folder: {e}")

def clear_terminal():
    os.system('clear')  # Use 'cls' for Windows if needed

def show_menu(service, folder_id='root', current_path='My Drive'):
    while True:
        clear_terminal()  # Clear the terminal at the start of the menu
        print(f"\n========== Google Drive Menu ==========\nCurrent Path: {current_path}\n")
        items = list_files(service, folder_id)
        item_map = {}
        index = 1

        print("Folders:")
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                print(f"  {index}. {item['name']} (Folder)")
                item_map[index] = item
                index += 1

        print("\nFiles:")
        for item in items:
            if item['mimeType'] != 'application/vnd.google-apps.folder':
                print(f"  {index}. {item['name']}")
                item_map[index] = item
                index += 1

        print("\nOptions:")
        print("  u. Upload a file or folder")
        print("  d. Delete this folder")
        print("  b. Back")
        print("  q. Quit")
        choice = input("\nSelect an option: ").strip().lower()

        if choice == 'q':
            clear_terminal()
            exit(0)
        elif choice == 'b':
            return
        elif choice == 'u':
            file_path = input("Enter the path of the file or folder to upload: ").strip()
            upload_file_or_folder(service, file_path, folder_id)
        elif choice == 'd':
            if folder_id == 'root':
                print("Cannot delete the root folder.")
            else:
                delete_file_or_folder(service, folder_id)
                return
        else:
            try:
                selected_index = int(choice)
                selected_item = item_map.get(selected_index)
                if selected_item:
                    if selected_item['mimeType'] == 'application/vnd.google-apps.folder':
                        show_menu(service, selected_item['id'], f"{current_path} > {selected_item['name']}")
                    else:
                        file_action_menu(service, selected_item, folder_id, current_path)
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please try again.")

def file_action_menu(service, file, folder_id, current_path):
    while True:
        clear_terminal()
        print(f"\n========== File Actions ==========\nFile: {file['name']} ({file['id']})\n")
        print("Options:")
        print("  1. Download")
        print("  2. Delete")
        print("  3. View and Edit in Neovim")
        print("  b. Back")
        choice = input("\nSelect an action: ").strip().lower()

        if choice == 'b':
            return
        elif choice == '1':
            download_file(service, file['id'], file['name'])
        elif choice == '2':
            delete_file_or_folder(service, file['id'])
            return
        elif choice == '3':
            download_file(service, file['id'], file['name'])
            try:
                subprocess.run(['nvim', file['name']])
                print(f"Re-uploading the file '{file['name']}' to Google Drive...")
                file_metadata = {'name': file['name']}
                media = MediaFileUpload(file['name'], resumable=True)
                updated_file = service.files().update(
                    fileId=file['id'],
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                print(f"File '{file['name']}' updated successfully. File ID: {updated_file.get('id')}")
            except Exception as e:
                print(f"Error editing or re-uploading file: {e}")
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    drive_service = authenticate()
    show_menu(drive_service)