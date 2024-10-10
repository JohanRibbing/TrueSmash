import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
from googleapiclient.http import MediaIoBaseDownload
import io
import random
import trueskill as ts

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

def play_match_singles():
    db = load_database()
    p1, p2 = random.sample(db.players, 2)
    vs_dict = {p1.name: p1, p2.name: p2}
    print(p1.name, ' vs ', p2.name)
    print('Who won?')
    winner_name = ''
    while winner_name != p1.name and winner_name != p2.name:
        print('Input player tag:')
        winner_name = input()
    winner = vs_dict.pop(winner_name)
    loser = list(vs_dict.values())[0]
    w_rating = ts.Rating(mu=winner.mu_singles,
                      sigma=winner.sigma_singles)
    l_rating = ts.Rating(mu=loser.mu_singles,
                      sigma=loser.sigma_singles)
    w_rating, l_rating = ts.rate_1vs1(w_rating, l_rating,
            env=ts.TrueSkill(draw_probability=0.0))

    winner.mu_singles = w_rating.mu
    winner.sigma_singles = w_rating.sigma
    loser.mu_singles = l_rating.mu
    loser.sigma_singles = l_rating.sigma
    save_database(db)

def main():
    creds = get_creds() 
    download_database(creds)
    play_another = True
    while play_another:
        print()
        play_match_singles()
        print()
        ans = ''
        print('Play another?')
        while ans != 'yes' and ans != 'no':
            print('Input yes or no:')
            ans = input()
        if ans == 'yes':
            pass
        if ans == 'no':
            play_another = False
        print()
    upload_database(creds)


if __name__ == "__main__":
    main()
