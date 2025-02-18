from info_gathering.scraper import Scraper
from info_gathering.gpt_rewrite import GPTCaller
from colorama import Fore, Style, init
from voice_gathering.get_voice import VoiceCaller
from video_gathering.get_cc_vids import VideoDownloader
from pathlib import Path
import shutil
import signal
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
	def __init__(self) -> None:
		pass
	
	def get_keywords(self) -> None:
		# Ask the user for the keywords
		keywords = input("Enter topic related keywords: ").lower()
		splitted_keywords = keywords.split(" ")
		return splitted_keywords
	
	def create_folders(self) -> None:
		"""
		Create folders for the output files called brainrot/voiceover, brianrot/videos, brainrot/infos.
		:return:
		"""
		print(Fore.GREEN + "\nCreate folders for the output files called brainrot/voiceover, brianrot/videos, brainrot/script." + Style.RESET_ALL)
		directory = Path("~/Documents/brainrot/voiceover").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path("~/Documents/brainrot/videos").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
		directory = Path("~/Documents/brainrot/script").expanduser()
		directory.mkdir(parents=True, exist_ok=True)
	
	# This function will clean up all the resources used by the brainrot project
	def clean_up_everything(self) -> None:
		"""
		Clean up all the resources used by the brainrot project
		:return: 
		"""
		try:
			sleep_input = input("\nTime to sleep before cleaning up the resources (in minutes): ")
			time_to_sleep = int(sleep_input) * 60
			try:
				print(Fore.GREEN + f"\nSleeping for {sleep_input} minute(s) before cleaning up resources..." + Style.RESET_ALL)
				time.sleep(time_to_sleep)
			except Exception as e:
				print(Fore.RED + f"\nError during sleep: {e}" + Style.RESET_ALL)
		except ValueError:
			print(Fore.RED + "\nInvalid time provided. Starting to clean up resources..." + Style.RESET_ALL)

		print(Fore.GREEN + "\nCleaning up resources." + Style.RESET_ALL)
		
		# Clean the main brainrot output directory
		shutil.rmtree(Path("~/Documents/brainrot").expanduser(), ignore_errors=True)
		
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
	@staticmethod
	def signal_handler(sig, frame):
		"""
		Signal handler function to catch SIGINT and SIGTERM
		:param1: signal number
		:param2: current stack frame
		:return:
		"""
		print(Fore.GREEN + "\nSIGINT or SIGTERM received. Cleaning up resources." + Style.RESET_ALL)
		
		# Clean the main brainrot output directory
		shutil.rmtree(Path("~/Documents/brainrot").expanduser(), ignore_errors=True)
		
		# Remove all __pycache__ directories in voice_gathering and info_gathering and video_gathering
		for folder in ["voice_gathering", "info_gathering", "video_gathering"]:
			for pycache_dir in Path(folder).rglob("__pycache__"):
				shutil.rmtree(pycache_dir, ignore_errors=True)
		sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, Main_Organizer.signal_handler)
signal.signal(signal.SIGTERM, Main_Organizer.signal_handler)

# In the main function we ask the user for the keywords and then call the scrape function
def main() -> None:
	"""
	Main function to run the brainrot project
	:return:
	"""

	# Create the main organizer object that helps to organize the main func and the scraper object that scrapes the websites
	main_org = Main_Organizer()
	scraper = Scraper(["https://techcrunch.com/"], main_org.get_keywords())

	# Call the create_folders function
	main_org.create_folders()

	# Call the scrape function and check for return value
	script = scraper.scrape()
	main_org.check_if_error_exit(script)
	
	# Call the gpt_rewrite function and check for return value
	user_input_path = input("\nEnter the output path for the script or press ENTER to use default value (default: ~/Documents/brainrot/script/): ")
	output_path = user_input_path if user_input_path != "" else "~/Documents/brainrot/script/script.txt"
	gpt = GPTCaller(output_path)
	rewritten_script = gpt.rewrite(script)
	main_org.check_if_error_exit(rewritten_script)

	# # Call the get_voice function
	# try:
	# 	user_input_path = input("\nEnter the output path for the audio or press ENTER to use default value (default: ~/Documents/brainrot/voiceover/): ")
	# 	output_path = user_input_path if user_input_path != "" else "~/Documents/brainrot/voiceover/output.mp3"
	# 	voiceover = VoiceCaller()
	# 	voiceover.get_voice(rewritten_script, output_path)
	# except Exception as e:
	# 	print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
	# 	main_org.check_if_error_exit(None)
	# 	return
	
	# Call the get_cc_vids function
	try:
		user_input_path = input("\nEnter the output path for the audio or press ENTER to use default value (default: ~/Documents/brainrot/videos/): ")
		output_path = user_input_path if user_input_path != "" else "~/Documents/brainrot/videos/"
		video = VideoDownloader(output_path)
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