from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv
from colorama import Fore, Style

# Load environment variables from .env file
load_dotenv()

class VoiceCaller:
	def __init__(self) -> None:
		pass
	# This function will convert the text to speech using the Eleven Labs API
	def get_voice(self, str_to_voice: str, output_path: str) -> None:

		#Check if output_path is None
		if output_path == "":
			output_path = "~/Documents/brainrot/voiceover/output.mp3"

		# Cycle through all API keys and check for validity
		api_keys = [os.getenv('ELEVEN_LABS_API_1'), os.getenv('ELEVEN_LABS_API_2'), os.getenv('ELEVEN_LABS_API_2'), os.getenv('ELEVEN_LABS_API_4')]
		valid_api_keys = [key for key in api_keys if key]
		if not valid_api_keys:
			raise ValueError(Fore.RED + "Eleven Labs API key not found. Please set the ELEVEN_LABS_API_X environment variables." + Style.RESET_ALL)

		# Cycle trough all the keys and try each one of them until one works (needed if you only use the free api keys)
		for api_key in valid_api_keys:
			client = ElevenLabs(api_key=api_key)
			try:
				audio_generator = client.text_to_speech.convert(
					voice_id= "JBFqnCBsd6RMkjVDRZzb", # this is the voice of George
					output_format="mp3_44100_128",
					text=str_to_voice,
					model_id="eleven_multilingual_v2",
					voice_settings={"stability": 1.0, "similarity_boost": 0.25, "style": 0.1}
				)
				# Save the audio content to a file
				expanded_output_path = os.path.expanduser(output_path)
				with open(expanded_output_path, 'wb') as audio_file:
					for chunk in audio_generator:
						audio_file.write(chunk)
				print(Fore.GREEN + f"Audio saved to {output_path} using API key: {api_key}" + Style.RESET_ALL)
				return
			except Exception as e:
				if e.status_code == 429:
					print(Fore.YELLOW + f"\nAPI key {api_key} exhausted (429). Trying next key." + Style.RESET_ALL)
					continue
				elif e.status_code == 401:
					print(Fore.YELLOW + f"\nThe API key {api_key} is not authorized. No urgent action needed, fallback to other API keys!" + Style.RESET_ALL)
					continue
				elif e.status_code == 422:
					raise ValueError(Fore.RED + "\nThe text provided is invalid. Please check the text and try again." + Style.RESET_ALL) from e
				else:
					raise ValueError(Fore.RED + "\nAn unidentified error occurred while trying to convert the text to speech. Please try again later." + Style.RESET_ALL) from e

		# If all keys returned a 429 error
		raise ValueError(Fore.RED + "\nAll API keys are exhausted! Make a new API key or wait." + Style.RESET_ALL)
