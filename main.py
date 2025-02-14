from info_gathering.scraper import scrape
from colorama import Fore, Style, init
from voice_gathering.get_voice import get_voice
from video_gathering.get_cc_vids import get_cc_vids
from pathlib import Path
import shutil
import signal
import sys

# What the color codes mean:
# WHITE: user input needed
# Fore.GREEN: Success
# Fore.YELLOW: Warning
# Fore.RED: Error

# Initialize colorama
init()

def clean_up_everything() -> None:
    print(Fore.GREEN + "\nCleaning up resources..." + Style.RESET_ALL)
    
    # Clean the main brainrot output directory
    shutil.rmtree(Path("~/Documents/brainrot").expanduser(), ignore_errors=True)
    
    # Remove all __pycache__ directories in voice_gathering and info_gathering and video_gathering
    for folder in ["voice_gathering", "info_gathering", "video_gathering"]:
        for pycache_dir in Path(folder).rglob("__pycache__"):
            shutil.rmtree(pycache_dir, ignore_errors=True)

# Signal handler function to catch SIGINT and SIGTERM
def signal_handler(sig, frame):
	clean_up_everything()
	sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# In the main function we ask the user for the keywords and then call the scrape function
def main() -> None:

	# Ask the user for the keywords
	keywords = input("Enter topic related keywords: ").lower()
	splitted_keywords = keywords.split(" ")

	#Generate the directorys for the output files
	print(Fore.GREEN + "\nCreate folders for the output files called brainrot/voiceover, brianrot/videos, brainrot/infos." + Style.RESET_ALL)
	directory = Path("~/Documents/brainrot/voiceover").expanduser()
	directory.mkdir(parents=True, exist_ok=True)
	directory = Path("~/Documents/brainrot/videos").expanduser()
	directory.mkdir(parents=True, exist_ok=True)
	directory = Path("~/Documents/brainrot/infos").expanduser()
	directory.mkdir(parents=True, exist_ok=True)

	# Call the scrape function and check for return value
	script = scrape(splitted_keywords)
	if script is None:
		print(Fore.RED + "\nNo script generated. Exiting...\n" + Style.RESET_ALL)
		clean_up_everything()
		return

	# Call the get_voice function
	try:
		output_path = input("\nEnter the output path for the audio or press ENTER to use default value (default: ~/Documents/brainrot/voiceover/): ")
		if output_path == "":
			get_voice(script)
		else:
			get_voice(script, output_path)
	except Exception as e:
		print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
		clean_up_everything()
		return
	
	# Call the get_cc_vids function
	try:
		get_cc_vids(script)
	except Exception as e:
		print(Fore.RED + f"\n{e}\n" + Style.RESET_ALL)
		clean_up_everything()
		return
	
# Call the main function
if __name__ == "__main__":
	main()
