from concurrent.futures.thread import ThreadPoolExecutor
from typing import overload
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style
import os

# Load environment variables from .env file
load_dotenv()

class GPTCaller:
	def __init__(self, default_paths: list[str], languages: list[str]) -> None:
		self._default_paths = default_paths
		self._languages = languages
		self._rewritten_text = None

	def rewrite(self, scraped_str: str) -> list[str]:
		"""
		Rewrite the scraped text so that you can use it as your script
		:param scraped_str: The scraped text
		:param output_path: The path to save the rewritten text
		:return:
		"""

		# loop trough the list of path and language at the same time
		for i, (path, language) in enumerate(zip(self._default_paths, self._languages), start=1):
			expanded_output_path = os.path.expanduser(path)
			print(Fore.GREEN + f"\nGenerating script {i} of {len(self._default_paths)}." + Style.RESET_ALL)
			
			#generate the script
			while True:
				client = OpenAI()
				completion = client.chat.completions.create(
					model="gpt-4o-mini-2024-07-18",
					messages=[
						{"role": "system", "content": "Du bist ein professioneller Autor und haben die Aufgabe, den folgenden Text sachlich neu zu verfassen."},
						{
							"role": "user",
							"content": scraped_str + f"\n\n-Erstelle ein Skript auf {language} mit ca. 150 Wörtern zu dem technischen Thema. Der Einstieg sollte eine spannende Frage oder Aussage enthalten, um die Zuschauer direkt zu fesseln. Der Text muss informativ, klar und prägnant formuliert sein und sollte den Zuschauer mit 'Du'ansprechen. Kein überflüssiger Fülltext, sondern direkt auf den Punkt. Emojis sollen nicht verwendet werden, die Sprache jedoch alltaeglich sein. Der Text soll sachlich und informativ bleiben, ohne spekulative oder reißerische Abschlüsse."
						}
					]
				)

				# Print the generated text and ask the user if they want a rewrite
				print(Fore.GREEN + f"\nGenerated Text:\n\n{completion.choices[0].message.content}" + Style.RESET_ALL)
				user_input = input("\nDo you want a rewrite (y/ENTER) or rewrite it yourself(r)? (y/ENTER/r): ")

				# Check the user input if n then write the text to the file and break the loop
				if user_input.lower() == "":
					print(Fore.GREEN + f"\nAttemting to write it into {expanded_output_path}" + Style.RESET_ALL)
					self._rewritten_text = completion.choices[0].message.content
					with open(expanded_output_path, 'w') as file:
						file.write(completion.choices[0].message.content)
					print(Fore.GREEN + "\nScript saved to " + expanded_output_path + "" + Style.RESET_ALL)
					break
				# If the user wants to rewrite the text then ask for the rewritten text and write it to the file
				elif user_input.lower() == 'r':
					user_rewritten_text = input("Enter the rewritten text: ")
					self._rewritten_text = completion.choices[0].message.content
					with open(expanded_output_path, 'w') as file:
						file.write(user_rewritten_text)
					print(Fore.GREEN + "\nScript saved to " + expanded_output_path + "" + Style.RESET_ALL)
					break	
				# If the user enters something else then ask again
				elif user_input.lower() != "" and user_input.lower() != 'y':
					print(Fore.YELLOW + "\nInvalid input. Please enter 'y' or 'n'." + Style.RESET_ALL)
		return self._default_paths
