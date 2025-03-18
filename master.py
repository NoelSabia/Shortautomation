import re
import signal
import subprocess
import sys
import shutil
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init()

class MasterOrganizer:
	def __init__(self) -> None:
		self._directory = []
		self._browser = []
		self._youtube_german = []
		self._youtube_english = []
		self._websites = []

	# Load the program arguments into the master organizer object
	def load_args_into_master_org(self) -> None:
		"""
		Load the program arguments into the master organizer object.
		Each block must have exactly one dir="" and can have multiple website="" entries.
		It's invalid to define the same dir more than once across all blocks.
		"""
		# Read the program arguments from the file
		with open("program_args.txt", "r") as f:
			blocks = f.read().strip().split("\n\n")
			for block in blocks:
				block_dir = None
				block_browser = None
				block_youtube_german = None
				block_youtube_english = None
				block_websites = []

				# Parse each line with the regex
				for line in block.strip().splitlines():
					match = re.match(r'(\w+)="([^"]*)"', line.strip())
					if match:
						key, value = match.groups()
						if key == "dir":
							# Ensure only one dir per block
							if block_dir is not None:
								raise ValueError("Error: Block contains more than one 'dir'.")
							block_dir = value
						elif key == "browser":
							if block_browser is not None:
								raise ValueError("Error: Block contains more than one 'browser'.")
							block_browser = value
						elif key == "website":
							block_websites.append(value)
						elif key == "youtube1" or key == "youtube_german":  # Accept both formats
							if block_youtube_german is not None:
								raise ValueError("Error: Block contains more than one YouTube German parameter.")
							block_youtube_german = value
						elif key == "youtube2" or key == "youtube_english":  # Accept both formats
							if block_youtube_english is not None:
								raise ValueError("Error: Block contains more than one YouTube English parameter.")
							block_youtube_english = value

				# Check for missing dir
				if block_dir is None:
					raise ValueError("Error: Block missing 'dir' key-value pair.")

				# Check for duplicate dir
				if block_dir in self._directory:
					raise ValueError(f"Error: Duplicate 'dir' found: {block_dir}")

				# Append to internal lists
				self._directory.append(block_dir)
				self._browser.append(block_browser)
				self._youtube_german.append(block_youtube_german)
				self._youtube_english.append(block_youtube_english)
				self._websites.append(block_websites)

	# Signal handler function to catch SIGINT and SIGTERM
	def signal_handler(self, sig, frame):
		"""
		Signal handler function to catch SIGINT and SIGTERM
		:param sig: signal number
		:param frame: current stack frame
		:return:
		"""
		print(Fore.GREEN + "\n\nSIGINT or SIGTERM received. Cleaning up resources." + Style.RESET_ALL)

		# Clean the directories from self._directory
		for directory in self._directory:
			try:
				shutil.rmtree(Path(directory).expanduser())
				print(Fore.GREEN + f"\nDeleted directory: {directory}" + Style.RESET_ALL)
			except FileNotFoundError:
				print(Fore.YELLOW + f"\nDirectory not found: {directory}, skipping." + Style.RESET_ALL)
			except PermissionError:
				print(Fore.RED + f"\nInsufficient permissions to delete: {directory}" + Style.RESET_ALL)

		# Remove __pycache__ directories
		for folder in ["voice_gathering", "info_gathering", "visuals_gathering", "shorts_fusion", "music_selection", "subtitles_gathering", "yt_upload"]:
			for pycache_dir in Path(folder).rglob("__pycache__"):
				shutil.rmtree(pycache_dir, ignore_errors=True)

		sys.exit(0)

def master() -> None:

    # Create an instance of the MasterOrganizer class
    master_org = MasterOrganizer()
    master_org.load_args_into_master_org()

    # Register signal handlers using the instance method
    signal.signal(signal.SIGINT, master_org.signal_handler)
    signal.signal(signal.SIGTERM, master_org.signal_handler)

    # Run main.py with the paths, browser, YouTube links and websites
    for i, path in enumerate(master_org._directory):
        print(Fore.GREEN + f"\nRunning main.py with path={path},\nbrowser={master_org._browser[i]},\nYouTube German={master_org._youtube_german[i]},\nYouTube English={master_org._youtube_english[i]}\nand website(s)={master_org._websites[i]}" + Style.RESET_ALL)
        
        # Build command with all parameters
        command = [
            "python3", 
            "main.py", 
            path, 
            master_org._browser[i] or "",
            master_org._youtube_german[i] or "",
            master_org._youtube_english[i] or ""
        ]
        
        # Add all websites
        command.extend(master_org._websites[i])
        
        # Run command
        subprocess.run(command)
        
        print(Fore.GREEN + f"\nmain.py finished processing {path}." + Style.RESET_ALL)

if __name__ == "__main__":
	master()