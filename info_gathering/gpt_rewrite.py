import os
from concurrent.futures.thread import ThreadPoolExecutor
from typing import overload

from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style

# Load environment variables from .env file
load_dotenv()

class GPTCaller:
	def __init__(self, default_path: str | None) -> None:
		if not default_path:
			self._default_path = "~/Documents/brainrot/script/script.txt"
		else:
			self._default_path = default_path
		self._rewritten_text = None
			

	def rewrite(self, scraped_str: str, output_path: str = None) -> str:
		"""
		Rewrite the scraped text so that you can use it as your script
		:param scraped_str: The scraped text
		:param output_path: The path to save the rewritten text
		:return:
		"""
		if output_path is None or output_path == "":
			output_path = self._default_path
		expanded_output_path = os.path.expanduser(output_path)

		# Loop to ask the user if they want a rewrite
		while True:
			client = OpenAI()
			completion = client.chat.completions.create(
				model="gpt-4o-mini",
				messages=[
					{"role": "system", "content": "Sie sind ein professioneller Autor und haben die Aufgabe, den folgenden Text sachlich neu zu verfassen."},
					{
						"role": "user",
						"content": "\n\n-Erstelle ein Skript auf deutsch mit ca. 150 Wörtern zu dem technischen Thema. Der Einstieg sollte eine spannende Frage oder Aussage enthalten, um die Zuschauer direkt zu fesseln. Der Text muss informativ, klar und prägnant formuliert sein. Kein überflüssiger Fülltext, sondern direkt auf den Punkt. Emojis sollen nicht verwendet werden, die Sprache jedoch alltaeglich sein. Der Text soll sachlich und informativ bleiben, ohne spekulative oder reißerische Abschlüsse."
					}
				]
			)

			# Print the generated text and ask the user if they want a rewrite
			print(Fore.GREEN + f"\nGenerated Text:\n{completion.choices[0].message.content}\n" + Style.RESET_ALL)
			user_input = input("Do you want a rewrite or rewrite it yourself? (y/n/r): ")

			# Check the user input if n then write the text to the file and break the loop
			if user_input.lower() == 'n':
				print(Fore.GREEN + f"\nAttemting to write it into {expanded_output_path}" + Style.RESET_ALL)
				self._rewritten_text = completion.choices[0].message.content
				with open(expanded_output_path, 'w') as file:
					file.write(completion.choices[0].message.content)
				print(Fore.GREEN + "\nScript saved to " + expanded_output_path + Style.RESET_ALL)
				break
			# If the user wants to rewrite the text then ask for the rewritten text and write it to the file
			elif user_input.lower() == 'r':
				user_rewritten_text = input("Enter the rewritten text: ")
				self._rewritten_text = completion.choices[0].message.content
				with open(expanded_output_path, 'w') as file:
					file.write(user_rewritten_text)
				print(Fore.GREEN + "\nScript saved to " + expanded_output_path + Style.RESET_ALL)
				return user_rewritten_text
			# If the user enters something else then ask again
			elif user_input.lower() != 'n' and user_input.lower() != 'y':
				print(Fore.YELLOW + "Invalid input. Please enter 'y' or 'n'." + Style.RESET_ALL)

		# Return the rewritten text if the user didn't rewrite it themselves
		return completion.choices[0].message.content

	# def rewrite_multiple(self, scraped_strs: list[str], output_paths: list[str] = None) -> list[str]:
	# 	"""
	# 	Rewrite multiple scraped texts in parallel
	# 	:param scraped_strs:
	# 	:param output_paths:
	# 	:return:
	# 	"""
	# 	if len(scraped_strs) != len(output_paths):
	# 		raise ValueError("The length of scraped_strs and output_paths should be the same.")
	# 	elif len(set(output_paths)) != len(output_paths):
	# 		raise ValueError("Output paths must be unique.")
	# 	with ThreadPoolExecutor() as executor:
	# 		futures = [
	# 			executor.submit(self.rewrite, scraped_str, output_path) \
	# 			for scraped_str, output_path in zip(scraped_strs, output_paths)
	# 		]
	# 		return [future.result() for future in futures]
