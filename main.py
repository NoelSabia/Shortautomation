from info_gathering.scraper import Scraper
from info_gathering.gpt_rewrite import GPTCaller
from colorama import Fore, Style, init
from voice_gathering.get_voice import VoiceCaller
from video_gathering.get_cc_vids import VideoDownloader
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
	def __init__(self, path: str, websites_to_scrape: list[str]) -> None:
		self._path = path
		self._websites_to_scrape = websites_to_scrape
	
	def get_keywords(self) -> None:
		# Ask the user for the keywords
		keywords = input("\nEnter topic related keywords: ").lower()
		splitted_keywords = keywords.split(" ")
		return splitted_keywords
	
	def create_folders(self) -> None:
		"""
		Create folders for the output files called brainrot/voiceover, brianrot/videos, brainrot/infos.
		:return:
		"""
		print(Fore.GREEN + f"\nCreate folders for the output files called {self._path}/voiceover, {self._path}/videos, {self._path}/script and {self._path}/upload" + Style.RESET_ALL)
		directory = Path(f"{self._path}/voiceover").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path(f"{self._path}/videos").expanduser()
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
		for folder in ["voice_gathering", "info_gathering", "video_gathering"]:
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
		for folder in ["voice_gathering", "info_gathering", "video_gathering"]:
			for pycache_dir in Path(folder).rglob("__pycache__"):
				shutil.rmtree(pycache_dir, ignore_errors=True)
		sys.exit(0)


# In the main function we ask the user for the keywords and then call the scrape function
def main() -> None:
	"""
	Main function to run the brainrot project
	:return:
	"""
	#read the args and safe them in the main organizer object. Create the main organizer object that helps to organize the main func. 
	args = sys.argv[1:]
	if len(args) < 2:
		return "Usage of the program: python3 main.py <path_of_where_to_safe_it> <from here on websites to scrape> ..."
	main_org = Main_Organizer(sys.argv[1], sys.argv[2:])
	
	# Call the create_folders function
	main_org.create_folders()

	# Create the scraper object that scrapes the websites. Then call the scrape function and check for return value
	scraper = Scraper(main_org._websites_to_scrape, main_org.get_keywords())
	script = scraper.scrape()
	main_org.check_if_error_exit(script)
	
	# Call the gpt_rewrite function and check for return value
	gpt = GPTCaller(main_org._path + "/script/script.txt")
	rewritten_script = gpt.rewrite(script)
	main_org.check_if_error_exit(rewritten_script)

	# Call the get_voice function
	try:
		voiceover = VoiceCaller(rewritten_script, main_org._path + "/voiceover/output.mp3")
		voiceover.get_voice()
	except Exception as e:
		print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
		main_org.check_if_error_exit(None)
		return
	
	# Call the get_cc_vids function
	try:
		video = VideoDownloader(main_org._path + "/video/output.mp3")
		video.get_cc_vids(rewritten_script)
	except Exception as e:
		print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
		main_org.check_if_error_exit(None)
		return
	
	# Clean up the resources
	main_org.clean_up_everything()
	
# Call the main function
if __name__ == "__main__":
	main()