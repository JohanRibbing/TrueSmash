import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
from googleapiclient.http import MediaIoBaseDownload
import io
from prettytable import PrettyTable

from classes import *


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]
cloud_database_file_id = '149PKjQ7O1ynLFQ4MJA67jhTNv-Cg8fnk'
local_database_file_name = 'database.json'

    
def yes_or_no():
    ans = ''
    while ans != 'yes' and ans != 'no':
        print('Input yes or no:')
        ans = input()
    return ans == 'yes'
    
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
        file.write(json.dumps(db,
                              default=(lambda x: x.__dict__),
                              indent=4))
    return True

def load_database():
    with open(local_database_file_name, 'r') as file:
        return Database(json.loads(file.read()))

def download_database():
    creds = get_creds()
    print('Downloading will overwrite any local data, do you want to continue?')
    if yes_or_no():
        pass
    else:
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

def upload_database():
    creds = get_creds()
    print('Uploading will overwrite any cloud data, do you want to continue?')
    if yes_or_no():
        pass
    else:
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
    success = db.delete_player(name)
    save_database(db)
    return success

def add_player():
    db = load_database()
    name = ''
    sure = False
    while not sure:
        print('Player tag to add:')
        name = input()
        print(f'You input {name}, are you sure you want to add {name}?')
        sure = yes_or_no()

    success = db.add_player(name)
    save_database(db)
    return success

def reset_ratings():
    db = load_database()
    success = db.reset_ratings()
    save_database(db)
    return success

def play_match_singles():
    db = load_database()
    success = db.play_match_singles()
    save_database(db)
    return success

def play_singles():
    play_another = True
    while play_another:
        play_match_singles()
        print('Play another?')
        if yes_or_no():
            pass
        else:
            play_another = False

def play_match_doubles():
    db = load_database()
    success = db.play_match_doubles()
    save_database(db)
    return success

def play_doubles():
    play_another = True
    while play_another:
        play_match_doubles()
        ans = ''
        print('Play another?')
        if yes_or_no():
            pass
        else:
            play_another = False

def print_ladder():
    print('\n'*50)
    db = load_database()
    names_singles, ratings_singles = db.get_ladder_singles()
    names_doubles, ratings_doubles = db.get_ladder_doubles()
    tab = PrettyTable(['Singles', '+-+-+-', 'Doubles', '-+-+-+'])
    tab.add_row(['tag', 'rating', 'tag', 'rating'], divider=True)
    for i in range(len(names_singles)):
        tab.add_row([names_singles[i], ratings_singles[i],
                     names_doubles[i], ratings_doubles[i]])
    print(tab)

menu_dict = dict(download_database=download_database,
                 print_ladder=print_ladder,
                 add_player=add_player, 
                 play_singles=play_singles,
                 play_doubles=play_doubles,
                 upload_database=upload_database,
                 stop_playing=lambda: None)

def main():
    keys = menu_dict.keys()
    stop = False
    option = ''
    while not stop:
        option = ''
        print()
        print('-'*10)
        print('Menu')
        print('-'*10)
        for k in keys:
            print(k)
        print('-'*10)
        while option not in keys:
            print('Input menu option')
            option = input()
        menu_dict[option].__call__()
        if option == 'stop_playing':
            stop = True



if __name__ == "__main__":
    main()
