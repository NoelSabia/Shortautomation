import os
import time
import subprocess
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

class CapCutOrganizer:
    def __init__(self, output_path: str, browser: str, script: str) -> None:
        self._browser = browser
        self._output_path = output_path
        self._script = script

    def open_browser(self) -> None:
        """
        Open the browser with the given browser name also check that it's only firefox or chrome
        """
        try:
            print(Fore.GREEN + f"\nOpening {self._browser} browser..." + Style.RESET_ALL)
            subprocess.run([self._browser, "https://www.capcut.com/editor?start_tab=video&__action_from=my_draft&position=my_draft&from_page=work_space&enter_from=create_new&scenario=tiktok_ads&scale=9%3A16"], check=True)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"\nError opening browser: {e}" + Style.RESET_ALL)
        except FileNotFoundError:
            print(Fore.RED + f"\nBrowser '{self._browser}' not found" + Style.RESET_ALL)
    
    def mv_capcut_output_to_upload(self) -> None:
        """
        Move output files from Downloads to output folder.
        Checks Downloads folder every second for new .mp4 files to move the finished product to the output folder where it can be uploaded to YouTube.
        """
        downloads = str(Path.home() / "Downloads")
        location = Path(self._output_path).expanduser()

        print(Fore.GREEN + f"\nWatching Downloads folder for new .mp4 files." + Style.RESET_ALL)
        print(Fore.GREEN + f"\nWill move the output_file from {downloads} to {self._output_path}." + Style.RESET_ALL)

        try:
            while True:
                for file in os.listdir(downloads):
                    if file.endswith(".mp4"):
                        src = os.path.join(downloads, file)
                        dst = os.path.join(location, file)
                        try:
                            subprocess.run(["mv", src, dst], check=True)
                            print(Fore.GREEN + f"\nMoved {file} to {self._output_path}" + Style.RESET_ALL)
                            return
                        except subprocess.CalledProcessError as e:
                            print(Fore.RED + f"Error moving file: {e}" + Style.RESET_ALL)
                time.sleep(1)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nStopped watching Downloads folder" + Style.RESET_ALL)

    def authenticate_youtube(self):
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            "./yt-api-requirements/client.json",
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
            print(f"\nVideo uploaded with ID: {response['id']}")

    def upload_to_youtube(self) -> None:
        """
        Upload the output files to YouTube.
        """
        print(Fore.GREEN + f"\nUploading output files to YouTube" + Style.RESET_ALL)
        youtube = self.authenticate_youtube()
        self.upload_video(youtube)
    
    def orchastrate_fusion(self) -> None:
        """
        Orchastrate the fusion of the CapCut output files.
        """
        print(Fore.GREEN + f"\nOrchastrating the fusion of the CapCut output files..." + Style.RESET_ALL)
        self.open_browser()
        self.mv_capcut_output_to_upload()
        self.upload_to_youtube()

def main() -> None:
    merger = CapCutOrganizer("~/Documents/brainrot/upload", "/Applications/Firefox.app/Contents/MacOS/firefox", "Du willst wissen, was die Zukunft bringt? Hier sind die heißesten Tech-News in 60 Sekunden! Künstliche Intelligenz wird immer smarter – Google, Apple und Co. bringen neue KI-Features, die unseren Alltag revolutionieren. Faltbare Handys sind auf dem Vormarsch. Samsung und andere Hersteller zeigen, dass die Zukunft flexibel ist. Neue Akkus laden in unter 10 Minuten. Nie wieder stundenlang warten. Welche Tech-Innovation interessiert dich am meisten? Schreib es in die Kommentare. Für mehr Tech-Updates abonnieren und liken.")
    merger.upload_to_youtube()

if __name__ == "__main__":
    main()