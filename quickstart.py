import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
from googleapiclient.http import MediaIoBaseDownload
import io

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build("drive", "v3", credentials=creds)
        files = service.files()
    
        # examples
        #response = files.create(uploadType='media', media_body='upload_test.txt', body={'name': 'upload_test.txt'}).execute()
        #print(response)
        #response = files.update(uploadType='media', media_body='player.json', fileId='1wdYhAhNLgZQSkI2FyIf3A7ixS4USKuHE').execute()
        #print(response)

        request = files.get_media(fileId='1wdYhAhNLgZQSkI2FyIf3A7ixS4USKuHE')
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        player = (json.loads(file.getvalue()))
        player['rating'] += 10
        with open('player.json', 'w') as file:
            file.write(json.dumps(player, indent=4))
        response = files.update(uploadType='media', media_body='player.json', fileId='1wdYhAhNLgZQSkI2FyIf3A7ixS4USKuHE').execute()
        print(response)

      
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")
    


if __name__ == "__main__":
    main()
