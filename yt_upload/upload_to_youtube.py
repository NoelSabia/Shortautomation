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
    def init(self, output_path: str, path_to_client_json: str) -> None:
        self._output_path = output_path
        self._path_to_client_json = path_to_client_json
    
    def authenticate_youtube(self):
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            pathlib.Path().resolve() + "/youtube_jsons/" + self._path_to_client_json,
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        flow.redirect_uri = "http://localhost:8080/"
        credentials = flow.run_local_server(port=8080)
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    def upload_video(self, youtube) -> None:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "Sie sind ein professioneller Autor und haben die Aufgabe, den folgenden Text sachlich neu zu verfassen."},
                {
                    "role": "user",
                    "content": self._script + "\n\n-Fasse das Skript in eine interessante Überschrift zusammen. Der Text sollte nicht laenger als 10 Wörter sein."
                }
            ]
        )
        request_body = {
            "snippet": {
                "categoryId": "24",
                "title": completion.choices[0].message.content,
                "description": "", # here you could give credit for the videos used under cc license
                "tags": ["short"]
            },
            "status":{
                "privacyStatus": "private"
            }
        }
        #use "publishAt": "2023-12-31T12:00:00Z" to schedule the video. use it directly! under the privacyStatus in status

        # put the path of the video that you want to upload
        media_file = os.path.join(Path(self._output_path).expanduser(), "output.mp4")

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
                print(f"\nUpload {int(status.progress()*100)}%")
                time.sleep(2)
            print(f"\nVideo uploaded with ID: {response['id']}")

    def upload_to_youtube(self) -> None:
        """
        Upload the output files to YouTube.
        """
        print(Fore.GREEN + f"\nUploading output files to YouTube" + Style.RESET_ALL)
        youtube = self.authenticate_youtube()
        self.upload_video(youtube)
