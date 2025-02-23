import subprocess
from colorama import Fore, Style
import os
import time
from pathlib import Path

class CapCutOrganizer:
    def __init__(self, output_path: str, browser: str) -> None:
        self._browser = browser
        self._output_path = output_path

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

    def upload_to_youtube(self) -> None:
        """
        Upload the output files to YouTube.
        """
        print(Fore.GREEN + f"\nUploading output files to YouTube" + Style.RESET_ALL)
    
    def orchastrate_fusion(self) -> None:
        """
        Orchastrate the fusion of the CapCut output files.
        """
        print(Fore.GREEN + f"\nOrchastrating the fusion of the CapCut output files..." + Style.RESET_ALL)
        self.open_browser()
        self.mv_capcut_output_to_upload()
        self.upload_to_youtube()

def main() -> None:
    merger = CapCutOrganizer("~/Documents/brainrot/upload", "firefox")
    merger.orchastrate_fusion()

if __name__ == "__main__":
    main()