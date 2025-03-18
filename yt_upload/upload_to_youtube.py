import os
import time
import pathlib
from colorama import Fore, Style
from pathlib import Path
from openai import OpenAI
import google_auth_httplib2
import google_auth_oauthlib
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from dotenv import load_dotenv

#load the env variabled
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = 'token.json'

class YoutubeUploader:
    def init(self, output_path: str, path_to_client_json: list[str]) -> None:
        self._output_path = output_path
        self._path_to_client_json = path_to_client_json
    
    def authenticate_youtube(self, client_json_path):
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            pathlib.Path().resolve() + "/youtube_jsons/" + client_json_path,
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        flow.redirect_uri = "http://localhost:8080/"
        credentials = flow.run_local_server(port=8080)
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    def upload_video(self, youtube, language, mp4_name) -> None:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "Sie sind ein professioneller Autor und haben die Aufgabe, den folgenden Text sachlich neu zu verfassen."},
                {
                    "role": "user",
                    "content": self._script + f"\n\n-Fasse das Skript in eine interessante Überschrift zusammen. Der Text sollte nicht laenger als 10 Wörter sein. Es muss in der Sprache {language} sein!"
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
                "privacyStatus": "private"
            }
        }
        #use "publishAt": "2023-12-31T12:00:00Z" to schedule the video. use it directly! under the privacyStatus in status

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

        languages = ["deutsch", "englisch"]
        mp4_names = ["german_output.mp4", "english_output.mp4"]
        for i, account, language, mp4_name in enumerate(zip(self._path_to_client_json, languages, mp4_names)):
            print(Fore.GREEN + f"\nUpload started for video {i} of {len(languages)}." + Style.RESET_ALL)
            youtube = self.authenticate_youtube(account)
            self.upload_video(youtube, language, mp4_name)
