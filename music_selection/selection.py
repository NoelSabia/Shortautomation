import os
from pathlib import Path
from colorama import Fore, Style
import subprocess

class MusicSelection:
	def __init__(self, output_path: str) -> None:
		self._output_path = Path(output_path).expanduser()

	def get_song(self) -> str:
		"""
		Lists all songs in the music folder and asks the user to select one.
		Returns the full path of the selected song.
		"""
		# Define the music folder path relative to this file
		music_folder = Path(__file__).resolve().parent / "music"
		if not music_folder.exists():
			print(Fore.YELLOW + f"\nMusic folder {music_folder} does not exist." + Style.RESET_ALL)
			return ""

		# Get list of songs (e.g., .mp3 files)
		songs = [song for song in os.listdir(music_folder) if song.lower().endswith('.mp3')]
		if not songs:
			print(Fore.YELLOW + "\nNo songs found in the music folder." + Style.RESET_ALL)
			return ""

		# Display the songs with index numbers
		print(Fore.GREEN + "\nAvailable songs:\n" + Style.RESET_ALL)
		for idx, song in enumerate(songs):
			print(Fore.GREEN + f"{idx}. {song}" + Style.RESET_ALL)

		# Ask user for selection
		while True:
			try:
				choice = input("\nEnter the number of the song to select: ")
				index = int(choice)
				if 0 <= index < len(songs):
					selected_song = music_folder / songs[index]
					self.cp_song_to_output(selected_song)
					break
				else:
					print("\nInvalid selection. Please choose a valid number.")
			except ValueError:
				print("\nPlease enter a number.")
	
	def cp_song_to_output(self, music_file: str) -> None:
		"""
		Copy the selected song to the output path.
		"""
		# Copy the selected song to the output path
		command = [
			"cp",
			music_file,
			self._output_path
		]
		try:
			subprocess.run(command, check=True)
		except subprocess.CalledProcessError as e:
			print(Fore.RED + f"\nFailed to copy {music_file} to {self._output_path}." + Style.RESET_ALL)
			return
		print(Fore.GREEN + f"\nSong copied: {music_file} -> {self._output_path}" + Style.RESET_ALL)
