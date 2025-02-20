import os
import subprocess
import ffmpeg
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from colorama import Fore, Style

# Load environment variables from .env file
load_dotenv()

class VoiceCaller:
	def __init__(self, script_to_voice: str, output_path: str) -> None:
		self._script_to_voice = script_to_voice
		self._output_path = output_path
	
	def cut_silence(self, input_path: str, output_path: str) -> None:
		"""
		Removes every silence period longer than 0.2 seconds->(stop_duration) from an audio file using ffmpeg.
		:param input_path: The input audio file path.
		:param output_path: The output file path for the processed audio.
		"""
		command = [
			"ffmpeg",
			"-i", input_path,
			"-af", "silenceremove=stop_periods=-1:stop_duration=0.2:stop_threshold=-50dB",
			"-y",  # Overwrite output file if exists
			output_path
		]
		try:
			subprocess.run(command, check=True)
		except subprocess.CalledProcessError as e:
			print(f"Failed to remove silence from {input_path}.")
		print(f"Silence removed: {input_path} -> {output_path}")

	# This function will convert the text to speech using the Eleven Labs API
	def get_voice(self) -> None:

		# Cycle through all API keys and check for validity
		api_keys = [os.getenv('ELEVEN_LABS_API_1'), os.getenv('ELEVEN_LABS_API_2'), os.getenv('ELEVEN_LABS_API_2'), os.getenv('ELEVEN_LABS_API_4')]
		valid_api_keys = [key for key in api_keys if key]
		if not valid_api_keys:
			raise ValueError(Fore.RED + "Eleven Labs API key not found. Please set the ELEVEN_LABS_API_X environment variables." + Style.RESET_ALL)

		# Cycle trough all the keys and try each one of them until one works (needed if you only use the free api keys)
		failed_api_keys = 0
		for api_key in valid_api_keys:
			client = ElevenLabs(api_key=api_key)
			try:
				audio_generator = client.text_to_speech.convert(
					voice_id= "JBFqnCBsd6RMkjVDRZzb", # this is the voice of George
					output_format="mp3_44100_128",
					text=self._script_to_voice,
					model_id="eleven_multilingual_v2",
					voice_settings={"stability": 1.0, "similarity_boost": 0.25, "style": 0.1}
				)
				# Save the audio content to a file
				expanded_output_path = os.path.expanduser(self._output_path)
				with open(expanded_output_path, 'wb') as audio_file:
					for chunk in audio_generator:
						audio_file.write(chunk)
				print(Fore.GREEN + f"Audio saved to {self._output_path} using API key: {api_key}" + Style.RESET_ALL)
				break
			except Exception as e:
				if e.status_code == 429:
					print(Fore.YELLOW + f"\nAPI key {api_key} exhausted (429). Trying next key." + Style.RESET_ALL)
					failed_api_keys += 1
					continue
				elif e.status_code == 401:
					print(Fore.YELLOW + f"\nThe API key {api_key} is not authorized. No urgent action needed, fallback to other API keys!" + Style.RESET_ALL)
					failed_api_keys += 1
					continue
				elif e.status_code == 422:
					raise ValueError(Fore.RED + "\nThe text provided is invalid. Please check the text and try again." + Style.RESET_ALL) from e
				else:
					raise ValueError(Fore.RED + "\nAn unidentified error occurred while trying to convert the text to speech. Please try again later." + Style.RESET_ALL) from e

		# If all keys returned a 429 error
		if (failed_api_keys == len(valid_api_keys)):
			raise ValueError(Fore.RED + "\nAll API keys are exhausted! Make a new API key or wait." + Style.RESET_ALL)


		# call to remove the silence from the audio file
		cleaned_output_path = input("\nEnter the path to save the cleaned audio file or ENTER to go with the default (~/Documents/brainrot/voiceover/cleaned_output.mp3): ") or self._output_path + "/voiceover/cleaned_output.mp3"
		expanded_output_path = os.path.expanduser(self._output_path)
		expanded_cleaned_output_path = os.path.expanduser(cleaned_output_path)
		self.cut_silence(expanded_output_path, expanded_cleaned_output_path)

		# After successfully processing and creating the cleaned file:
		if os.path.exists(expanded_output_path):
			os.remove(self._output_path)
			print(f"\nDeleted original file: {self._output_path}")
