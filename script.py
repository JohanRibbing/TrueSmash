import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
from googleapiclient.http import MediaIoBaseDownload
import io

from classes import *

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]
cloud_database_file_id = '149PKjQ7O1ynLFQ4MJA67jhTNv-Cg8fnk'
local_database_file_name = 'database.json'

    
    
def get_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds

def save_database(db):
    with open(local_database_file_name, 'w') as file:
        file.write(json.dumps(db, default=(lambda x: x.__dict__), indent=4))

def load_database():
    with open(local_database_file_name, 'r') as file:
        return Database(json.loads(file.read()))

def download_database(creds):
    ans = ''
    print('Downloading will overwrite any local data, do you want to continue?')
    while ans != 'yes' and ans != 'no':
        print('Input yes or no:')
        ans = input()
    if ans == 'yes':
        pass
    if ans == 'no':
        return False
    try:
        service = build("drive", "v3", credentials=creds)
        files = service.files()
        request = files.get_media(fileId=cloud_database_file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        db = Database(json.loads(file.getvalue()))
        save_database(db)
        return True

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")
        return False

def upload_database(creds):
    ans = ''
    print('Uploading will overwrite any cloud data, do you want to continue?')
    while ans != 'yes' and ans != 'no':
        print('Input yes or no:')
        ans = input()
    if ans == 'yes':
        pass
    if ans == 'no':
        return False
    try:
        service = build("drive", "v3", credentials=creds)
        files = service.files()
        files.update(uploadType='media',
                                media_body=local_database_file_name,
                                fileId=cloud_database_file_id).execute()
        return True

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")
        return False

def delete_player(name):
    db = load_database()
    db.delete_player(name)
    save_database(db)

def add_player(name):
    db = load_database()
    success = db.add_player(name)
    save_database(db)
    return success

def main():
    creds = get_creds() 
    download_database(creds)
    add_player('nokom')
    upload_database(creds)

if __name__ == "__main__":
    main()
