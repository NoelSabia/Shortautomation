from info_gathering.scraper import Scraper
from info_gathering.gpt_rewrite import GPTCaller
from colorama import Fore, Style, init
from voice_gathering.get_voice import VoiceCaller
from visuals_gathering.get_visuals import VideoDownloader
from shorts_fusion.capcut_merger import CapCutOrganizer
from music_selection.selection import MusicSelection
from shorts_fusion.upload_to_youtube import YoutubeUploader
from pathlib import Path
import shutil
import sys
import time

# What the color codes mean:
# WHITE: user input needed
# Fore.GREEN: Success
# Fore.YELLOW: Warning
# Fore.RED: Error

# Initialize colorama
init()

# This class will be used to organize the brainrot project and will only be used for cleaning, organizing and managing the project not storing any data
class Main_Organizer:
	def __init__(self, path: str, browser: str, websites_to_scrape: list[str]) -> None:
		self._path = path
		self._browser = browser
		self._websites_to_scrape = websites_to_scrape
	
	def get_keywords(self) -> None:
		# Ask the user for the keywords
		keywords = input("\nEnter topic related keywords or press ENTER to show every topic: ").lower()
		splitted_keywords = keywords.split(" ")
		return splitted_keywords
	
	def create_folders(self) -> None:
		"""
		Create folders for the output files.
		:return:
		"""
		print(Fore.GREEN + f"\nCreate folders for the output files called {self._path}/audio, {self._path}/visuals, {self._path}/visuals/images, {self._path}/visuals/videos {self._path}/script and {self._path}/upload" + Style.RESET_ALL)
		directory = Path(f"{self._path}/audio").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path(f"{self._path}/visuals").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path(f"{self._path}/visuals/images").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path(f"{self._path}/visuals/videos").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path(f"{self._path}/script").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path(f"{self._path}/upload").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
	
	def _get_sleep_duration(self) -> int:
		"""
		Get and validate sleep duration from user input
		:return: Sleep duration in seconds
		"""
		DEFAULT_SLEEP = 30 * 60  # 30 minutes in seconds
		MAX_SLEEP = 120 * 60     # 2 hours max sleep time
		
		try:
			sleep_input = input("\nTime to sleep before cleaning up the resources (in minutes) or ENTER for default (30 min): ").strip()
			
			# Handle empty input
			if not sleep_input:
				print(Fore.GREEN + "\nUsing default sleep time of 30 minutes." + Style.RESET_ALL)
				return DEFAULT_SLEEP
				
			# Convert and validate input
			minutes = float(sleep_input)
			if minutes <= 0:
				print(Fore.YELLOW + "\nInvalid sleep time. Using default of 30 minutes." + Style.RESET_ALL)
				return DEFAULT_SLEEP
			if minutes * 60 > MAX_SLEEP:
				print(Fore.YELLOW + f"\nSleep time too long. Limiting to {MAX_SLEEP//60} minutes." + Style.RESET_ALL)
				return MAX_SLEEP
				
			return int(minutes * 60)
			
		except ValueError:
			print(Fore.YELLOW + "\nInvalid input. Using default sleep time of 30 minutes." + Style.RESET_ALL)
			return DEFAULT_SLEEP

	def clean_up_everything(self) -> None:
		"""
		Clean up all the resources used by the brainrot project
		:return: 
		"""
		time_to_sleep = self._get_sleep_duration()
		
		try:
			print(Fore.GREEN + f"\nSleeping for {time_to_sleep//60} minute(s) before cleaning up resources..." + Style.RESET_ALL)
			time.sleep(time_to_sleep)
		except KeyboardInterrupt:
			print(Fore.YELLOW + "\nSleep interrupted. Starting cleanup..." + Style.RESET_ALL)
		except Exception as e:
			print(Fore.RED + f"\nError during sleep: {e}" + Style.RESET_ALL)

		print(Fore.GREEN + "\nCleaning up resources." + Style.RESET_ALL)
		
		# Clean the main brainrot output directory
		shutil.rmtree(Path(self._path).expanduser(), ignore_errors=True)
		
		# Remove all __pycache__ directories in voice_gathering and info_gathering and video_gathering
		for folder in ["voice_gathering", "info_gathering", "visuals_gathering", "shorts_fusion", "music_selection"]:
			for pycache_dir in Path(folder).rglob("__pycache__"):
				shutil.rmtree(pycache_dir, ignore_errors=True)
	
	def check_if_error_exit(self, returned_str: str) -> None:
		"""
		Exit the program with an error message
		:return:
		"""
		if returned_str is None:
			print(Fore.RED + "\nNothing->(None) returned. Exiting..." + Style.RESET_ALL)
			self.clean_up_everything()
			sys.exit(1)

	# Signal handler function to catch SIGINT and SIGTERM
	def signal_handler(self, sig, frame):
		"""
		Signal handler function to catch SIGINT and SIGTERM
		:param sig: signal number
		:param frame: current stack frame
		:return:
		"""
		print(Fore.GREEN + "\nSIGINT or SIGTERM received. Cleaning up resources." + Style.RESET_ALL)

		# Clean the main output directory
		shutil.rmtree(Path(self._path).expanduser(), ignore_errors=True)

		# Remove all __pycache__ directories in voice_gathering and info_gathering and video_gathering
		for folder in ["voice_gathering", "info_gathering", "visuals_gathering", "shorts_fusion", "music_selection"]:
			for pycache_dir in Path(folder).rglob("__pycache__"):
				shutil.rmtree(pycache_dir, ignore_errors=True)
		sys.exit(0)


# In the main function we ask the user for the keywords and then call the scrape function
def main() -> None:
	"""
	Main function to run the brainrot project
	:return:
	"""
	try:
		#read the args and safe them in the main organizer object. Create the main organizer object that helps to organize the main func. 
		args = sys.argv[1:]
		if len(args) < 2:
			print(Fore.RED + "Usage of the program: python3 main.py <path_of_where_to_safe_it> <from here on websites to scrape> ..." + Style.RESET_ALL)
			return
		main_org = Main_Organizer(sys.argv[1], sys.argv[2], sys.argv[4:])
		
		# Call the create_folders function
		main_org.create_folders()

		# Create the scraper object that scrapes the websites. Then call the scrape function and check for return value
		scraper = Scraper(main_org._websites_to_scrape, main_org.get_keywords())
		script = scraper.scrape()
		main_org.check_if_error_exit(script)
		
		# Call the gpt_rewrite function and check for return value
		gpt = GPTCaller([main_org._path + "/script/script_german.txt", main_org._path + "/script/script_english.txt"], ["deutsch", "englisch"])
		paths_to_scripts = gpt.rewrite(script)

		# Call the get_voice function and call the get_song function for all the audio related stuff
		try:
			audio = VoiceCaller(paths_to_scripts, [main_org._path + "/audio/output_german.mp3", main_org._path + "/audio/output_english.mp3"])
			audio.get_voice()
			music = MusicSelection(main_org._path + "/audio")
			music.get_song()
		except Exception as e:
			print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
			main_org.check_if_error_exit(None)
			return
		
		# Call the get_cc_vids function
		try:
			visual = VideoDownloader([main_org._path + "/visuals", main_org._path] , paths_to_scripts[1])
			visual.download_visuals()
			visual.select_visuals()
		except Exception as e:
			print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
			main_org.check_if_error_exit(None)
			return
		
		# Call the capcut_merger function (if full autiomation with videos are doable (is doable) this will be deprecated)
		try:
			merger = CapCutOrganizer(main_org._path + "/uploads", main_org._browser)
			merger.orchastrate_fusion()
		except Exception as e:
			print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
			main_org.check_if_error_exit(None)
			return
		
		# Call the upload_to_youtube functions that automatically uploads the video as you like
		try:
			uploader = YoutubeUploader(main_org._path + "/uploads", sys.argv[3])
			uploader.upload_to_youtube
		except:
			print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
			main_org.check_if_error_exit(None)
			return
		
		# Clean up the resources
		main_org.clean_up_everything()

	except KeyboardInterrupt:
		pass
	
# Call the main function
if __name__ == "__main__":
	main()