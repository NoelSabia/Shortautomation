import os
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style
from Voice_gathering.get_voice import get_voice

# Load environment variables from .env file
load_dotenv()

# This function will rewrite the scraped text so that you can use it as your script
def gpt_rewrite(scraped_str):
	# Dont forget to add the .env file with the OPENAI_API_KEY
	api_key = os.getenv('OPENAI_API_KEY')
	if not api_key:
		raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
	
	# Initialize the client
	client = OpenAI(api_key=api_key)

	# Loop to ask the user if they want a rewrite
	while True:
		completion = client.chat.completions.create(
			model="gpt-4o-mini-2024-07-18",
			messages=[
				{"role": "developer", "content": "You are a professional writer and you have been given the task to rewrite the following text in a exciting manner."},
				{
					"role": "user",
					"content": scraped_str + "\n\n-Fasse diesen Text zusammen, dass es 2 Absaetze sind. Dabei ist der erste Absatz als Hook verstanden um das Interesse vom Leser zu wecken. Der zweite Absatz soll dann die restliche Geschichte versuchen spannend zu erzaehlen. Deine Antwort sollte in etwa 150 Woerter haben. Der Text soll auf deutsch sein."
				}
			]
		)

		print(Fore.GREEN + "\nGenerated Text:\n" + Style.RESET_ALL)
		print(Fore.GREEN + completion.choices[0].message.content + Style.RESET_ALL)
		print("\n")

		user_input = input(Fore.YELLOW + "Do you want/need a rewrite? (y/n): " + Style.RESET_ALL)
		if user_input.lower() == 'n':
			print(Fore.GREEN + "Alright. Next step is to make the voiceover..." + Style.RESET_ALL)
			get_voice(completion.choices[0].message.content)
			break
		elif user_input.lower() != 'n' and user_input.lower() != 'y':
			print(Fore.RED + "Invalid input. Please enter 'y' or 'n'." + Style.RESET_ALL)
