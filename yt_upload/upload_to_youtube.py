import os
import time
import pathlib
import subprocess
from colorama import Fore, Style
from pathlib import Path
from openai import OpenAI
import google_auth_httplib2
import google_auth_oauthlib
import googleapiclient.discovery
import datetime
import googleapiclient.errors
import googleapiclient.http
from dotenv import load_dotenv

#load the env variabled
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = 'token.json'

class YoutubeUploader:
    def __init__(self, output_path: str, name_of_client_json: list[str], script: str) -> None:
        self._output_path = output_path
        self._name_of_client_json = name_of_client_json
        self._script = script
    
    def authenticate_youtube(self, client_json_path: str, port_input: int):
        """
        Authenticate on youtube with google acc
        """
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            os.path.join(pathlib.Path().resolve() / "youtube_jsons" / client_json_path),
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        flow.redirect_uri = "http://localhost:" + str(port_input) + "/"
        credentials = flow.run_local_server(port=port_input)
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    
    def get_future_date(self) -> str:
        """
        Prompts the user for input between 0 and 6, where 0 represents today
        and 6 represents one week from today. Returns the corresponding date.
        """
        while True:
            try:
                days_input = input("Enter a number between 0 and 6 (0 for today, 6 for one week from today): ")
                days = int(days_input)
                if 0 <= days <= 6:
                    today = datetime.date.today()
                    future_date = today + datetime.timedelta(days=days)
                    return future_date
                else:
                    print(Fore.YELLOW + "Please enter a number between 0 and 6." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
                today = datetime.date.today()
                return today

    def upload_video(self, youtube, language, mp4_name) -> None:
        """
        Uploads the video to youtube
        """
        client = OpenAI()
        get_upload_date = self.get_future_date()
        script = Path(os.path.expanduser(self._script)).read_text()
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "Sie sind ein professioneller Autor und haben die Aufgabe, den folgenden Text sachlich neu zu verfassen."},
                {
                    "role": "user",
                    "content": script + f"\n\n-Fasse das Skript in eine interessante Überschrift zusammen. Der Text sollte nicht laenger als 10 Wörter sein. Es muss in der Sprache {language} sein!"
                }
            ]
        )
        request_body = {
            "snippet": {
                "categoryId": "24",
                "title": completion.choices[0].message.content,
                "description": "",
                "tags": ["shorts", "trending", "viral", "fyp", "breakingnews", "historyfacts","worldnews", "currentevents", "politicalnews", "headlines", "dailyupdate","historylovers", "didyouknow", "historybuff", "onthisday","traveltips", "travelvlog", "hiddenplaces", "amazingdestinations"]
            },
            "status":{
                "privacyStatus": "private",
                "publishAt": f"{get_upload_date}T06:00:00Z"
            }
        }
        #use "publishAt": "2023-12-31T10:00:00Z" to schedule the video. use it directly! under the privacyStatus in status

        # put the path of the video that you want to upload
        media_file = os.path.join(Path(self._output_path).expanduser(), mp4_name)

        # Create a request for the API
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=googleapiclient.http.MediaFileUpload(media_file, chunksize=-1, resumable=True)
        )

        # Upload the video
        response = None 
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(Fore.GREEN + f"\nUpload progress: {int(status.progress()*100)}%" + Style.RESET_ALL)
                time.sleep(2)
            print(Fore.GREEN + f"\nVideo succesfully uploaded with ID: {response['id']}" + Style.RESET_ALL)

    def upload_to_youtube(self) -> None:
        """
        Upload the output files to YouTube.
        """
        print(Fore.GREEN + f"\nUploading output files to YouTube" + Style.RESET_ALL)

        languages = ["german", "english"]
        mp4_names = ["german_video.mp4", "english_video.mp4"]
        ports = [8081, 8080]
        for i, (account, language, mp4_name, port) in enumerate(zip(self._name_of_client_json, languages, mp4_names, ports)):
            print(Fore.GREEN + f"\nUpload started for video {i + 1} of {len(languages)}." + Style.RESET_ALL)
            youtube = self.authenticate_youtube(account, port)
            self.upload_video(youtube, language, mp4_name)
