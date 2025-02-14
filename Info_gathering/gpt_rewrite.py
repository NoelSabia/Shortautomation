import os
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style

# Load environment variables from .env file
load_dotenv()

# This function will rewrite the scraped text so that you can use it as your script
def gpt_rewrite(scraped_str: str, output_path: str="~/Documents/brainrot/infos/script.txt") -> str:
	# TODO: Dont forget to add the .env file with the OPENAI_API_KEY
	api_key = os.getenv('OPENAI_API_KEY')
	if not api_key:
		raise ValueError(Fore.RED + "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable." + Style.RESET_ALL)
	
	# Expand the output path here to avoid doing it multiple times in the loop
	expanded_output_path = os.path.expanduser(output_path)

	# Initialize the client
	client = OpenAI(api_key=api_key)

	# Loop to ask the user if they want a rewrite
	while True:
		# Get the new text via API call to openai's 4o-mini model
		completion = client.chat.completions.create(
			model="gpt-4o-mini-2024-07-18",
			messages=[
				{"role": "developer", "content": "You are a professional writer and you have been given the task to rewrite the following text in a factual manner."},
				{
					"role": "user",
					"content": scraped_str + "\n\n-Erstelle ein Skript auf deutsch mit ca. 150 Wörtern zu dem technischen Thema. Der Einstieg sollte eine spannende Frage oder Aussage enthalten, um die Zuschauer direkt zu fesseln. Der Text muss informativ, klar und prägnant formuliert sein. Kein überflüssiger Fülltext, sondern direkt auf den Punkt. Emojis sollen nicht verwendet werden, die Sprache jedoch alltaeglich sein. Der Text soll sachlich und informativ bleiben, ohne spekulative oder reißerische Abschlüsse."
				}
			]
		)

		# Print the generated text and ask the user if they want a rewrite
		print(Fore.GREEN + f"\nGenerated Text:\n{completion.choices[0].message.content}\n" + Style.RESET_ALL)
		user_input = input("Do you want a rewrite or rewrite it yourself? (y/n/r): ")

		# Check the user input if n then write the text to the file and break the loop
		if user_input.lower() == 'n':
			print(Fore.GREEN + "\nAlright. Next step is to make the voiceover..." + Style.RESET_ALL)
			with open(expanded_output_path, 'w') as file:
				file.write(completion.choices[0].message.content)
			print(Fore.GREEN + "\nScript saved to " + expanded_output_path + Style.RESET_ALL)
			break

		# If the user wants to rewrite the text then ask for the rewritten text and write it to the file
		elif user_input.lower() == 'r':
			user_rewritte_text = input("Enter the rewritten text: ")
			with open(expanded_output_path, 'w') as file:
				file.write(user_rewritte_text)
			print(Fore.GREEN + "\nScript saved to " + expanded_output_path + Style.RESET_ALL)
			return user_rewritte_text
			
		# If the user enters something else then ask again
		elif user_input.lower() != 'n' and user_input.lower() != 'y':
			print(Fore.YELLOW + "Invalid input. Please enter 'y' for yes, 'n' for no or 'r' for rewrite." + Style.RESET_ALL)
	
	# Return the rewritten text if the user didn't rewrite it themselves
	return completion.choices[0].message.content
