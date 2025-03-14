import os
from pathlib import Path
from colorama import Fore, Style
import subprocess

class MusicSelection:
	def __init__(self, output_path: str) -> None:
		self._output_path = Path(output_path).expanduser()
	
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

	def cut_song_len(self, song: str) -> None:
		"""
		Get the duration of the voice_audio and cut the song accordingly.
		:return: None
		"""
		voice_files = [self._output_path / "cleaned_output_german.mp3", self._output_path / "cleaned_output_english.mp3"]
		output_file_names = ["cut_song_german.mp3", "cut_song_english.mp3"]
		duration = 0

		# Get the duration of the voice_audio to then cut the song to the same length
		for voice_file, output_file_name in zip(voice_files, output_file_names):
			result = subprocess.run(
				[
					"ffprobe",
					"-v", "error",
					"-show_entries", "format=duration",
					"-of", "default=noprint_wrappers=1:nokey=1",
					voice_file
				],
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True
			)
			try:
				tmp_duration = float(result.stdout.strip())
				duration = int(tmp_duration)
			except ValueError:
				print("Could not retrieve duration.")
			
			# Cut the song to the duration of the voice_audio
			command = [
				"ffmpeg",
				"-i", str(self._output_path / song),
				"-t", str(duration),
				"-y",
				str(self._output_path / output_file_name)
			]
			try:
				subprocess.run(command, check=True)
				# Delete original file only after successful cut
				if os.path.exists(self._output_path / song):
					os.remove(self._output_path / song)
					print(Fore.GREEN + f"\nDeleted original file: {self._output_path / song}" + Style.RESET_ALL)
			except subprocess.CalledProcessError as e:
				print(Fore.RED + f"\nFailed to cut {song} to {duration} seconds." + Style.RESET_ALL)
		
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
				choice = input("\nEnter the number of the song to select or press ENTER for default music: ")
				if (choice == ""):
					choice = len(songs) - 1
				index = int(choice)
				if 0 <= index < len(songs):
					selected_song = music_folder / songs[index]
					self.cp_song_to_output(selected_song)
					self.cut_song_len(songs[index])
					break
				else:
					print("\nInvalid selection. Please choose a valid number.")
			except ValueError:
				print("\nPlease enter a number.")
