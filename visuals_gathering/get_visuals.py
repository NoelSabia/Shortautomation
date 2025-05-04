import os
import requests
import subprocess
import multiprocessing as mp
import asyncio
import aiohttp
from colorama import Fore, Style
from openai import OpenAI
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

# Load environment variables from .env file
load_dotenv()

class VideoDownloader:
	def __init__(self, output_path: list[str], script: str) -> None:
		self._output_path = output_path
		self._script = script
		self._number_of_picked_visuals = 0
		self._needed_visuals = self.calculate_visuals_needed()
		self._ai_generator_api_key = os.environ.get("STABLE_DIFFUSION_API_KEY")
	
	def calculate_visuals_needed(self) -> int:
		buffer = 2
		path = os.path.expanduser(self._output_path[1]) + "/audio/cleaned_output_german.mp3"
		result = subprocess.run(
			[
				"ffprobe",
				"-v", "error",
				"-show_entries", "format=duration",
				"-of", "default=noprint_wrappers=1:nokey=1",
				path			
			],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True
		)
		try:
			tmp_duration = float(result.stdout.strip())
			duration = int(int(tmp_duration) / 3) + buffer
			return duration
		except ValueError:
			print(Fore.YELLOW + "Could not retrieve duration." + Style.RESET_ALL)
	
	def get_quotes(self) -> list[str]:
		"""
		This organizes the description into a list

		Returns:
			list[str]: descrptions of what to create
		"""

		# list for the results
		description_list = []

		# read from the script file
		with open(os.path.expanduser(self._script), "r") as file:
			self._script = file.read()
		
		# chatgpt call to generate the descpritons
		client = OpenAI()
		completion = client.chat.completions.create(
			model="gpt-4o-mini-2024-07-18",
			messages=[
				{"role": "system", "content": "You are a professional in creating good and short descriptions for AI images."},
				{
					"role": "user",
					"content": f"Generate {self._needed_visuals} vivid, symbolic image prompts that visually represent the most important ideas and themes from the following script: '{self._script}'. Only create prompts that are directly related to the main topic or its core concepts.Each prompt should be a clear, concise sentence describing a visually striking image, separated by '|'."
				}
			]
		)

		# Extract the content from the completion object
		content = completion.choices[0].message.content
		
		# Split the content string with the delimiter and return the list
		description_list = content.split('|')
		print(f"{Fore.GREEN}Generate pictures with these descriptions: {description_list}{Style.RESET_ALL}")
		return description_list
	
	async def get_image(self, description: str, download_name: int) -> None:
		"""
		Used to make the api call to generate the image
		"""

		# prepare the form data
		form_data = aiohttp.FormData()
		form_data.add_field("prompt", description +", high quality, realistic, visually engaging, modern, cinematic lighting, professional, clean background, epic composition", content_type="text/plain; charset=utf-8")
		form_data.add_field("aspect_ratio", "9:16", content_type="text/plain; charset=utf-8")
		form_data.add_field("output_format", "png", content_type="text/plain; charset=utf-8")

		# call the api async
		async with aiohttp.ClientSession() as session:
			async with session.post(
				"https://api.stability.ai/v2beta/stable-image/generate/core",
				headers={
					"authorization": f"Bearer {self._ai_generator_api_key}",
					"accept": "image/*"
				},
				data=form_data
			) as response:
				if response.status == 200:
					image_data = await response.read()
					output_path = f"{self._output_path[1]}/visuals/final_images/image_{download_name}.png"
					output_path = os.path.expanduser(output_path)
					print(output_path)
					with open(output_path, 'wb') as file:
						file.write(image_data)
					print(f"{Fore.GREEN}Successfully saved image {download_name}{Style.RESET_ALL}")
				else:
					error_text = await response.text()
					print(f"{Fore.RED}Error generating image: {error_text}{Style.RESET_ALL}")
					raise Exception(error_text)
	
	async def orchastrate_image_getting(self) -> None:
		"""
		Takes care of the async gathering of the images
		"""

		# a few lists that are crucial for getting quotes for ai generation and the images
		description_ai_generation = []
		description_ai_generation = self.get_quotes()

		# start with image downloading async
		await asyncio.gather(*(self.get_image(description, index) for index, description in enumerate(description_ai_generation)))
