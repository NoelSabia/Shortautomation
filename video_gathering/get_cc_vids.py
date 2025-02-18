import os
from colorama import Fore, Style
from openai import OpenAI
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from yt_dlp import YoutubeDL

# Load environment variables from .env file
load_dotenv()

class VideoDownloader:
	def __init__(self, default_path: str | None) -> None:
		if not default_path:
			self._default_path = "~/Documents/brainrot/script/script.txt"
		else:
			self._default_path = default_path

	def gather_url_params(self, script: str) -> str:
		"""
		Queries the user (via AI or direct input) for URL parameters built from the script.
		:param1: The script to generate URL parameters from.
		:return: The generated URL parameters.
		"""
		api_key = os.getenv('OPENAI_API_KEY')
		if not api_key:
			raise ValueError(Fore.RED + "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable." + Style.RESET_ALL)

		client = OpenAI(api_key=api_key)
		user_rewritten_url_parameters = ""

		while True:
			completion = client.chat.completions.create(
				model="gpt-4o-mini-2024-07-18",
				messages=[
					{"role": "developer",
					"content": "You are an assistant that extracts the most relevant keywords from a given script. Prioritize keywords that indicate products, companies, or organizations rather than individuals. Your response must contain only 2 to 4 words, separated by a `+` symbol, and nothing else. Do not include any punctuation other than `+`. Answer in english!"
					},
					{"role": "user", "content": script}
				]
			)

			print(Fore.GREEN + f"\nGenerated URL-parameter:\n{completion.choices[0].message.content}\n" + Style.RESET_ALL)
			user_input = input("Do you want a rewrite (y/n) or rewrite it yourself(r)? (y/n/r): ")


			if user_input.lower() == 'n':
				return completion.choices[0].message.content
			elif user_input.lower() == 'r':
				user_rewritten_url_parameters = input("\nEnter the rewritten URL-parameters like <word1+word2+word3+word4>: ")
				return user_rewritten_url_parameters
			elif user_input.lower() != 'y' and user_input.lower() != 'n' and user_input.lower() != 'r':
				print(Fore.YELLOW + "Invalid input. Please enter 'y' for yes, 'n' for no or 'r' for rewrite." + Style.RESET_ALL)

	def ask_user_for_video_selection(self, scrape_vidlinks_result: list[str]) -> list[str]:
		"""
		Lets the user decide which links to download.
		:param1: A list of video links to choose from.
		:return: A list of video links to download.
		"""
		user_vidlinks_result = []
		while True:
			try:
				user_input = input(
					f"Enter the number of the sublink to scrape (0-{len(scrape_vidlinks_result)-1}), "
					"-1 to finish or ENTER to download all: "
				)
				if user_input == "":
					# Download all videos as no specific link is given
					for sublink in scrape_vidlinks_result:
						if sublink.startswith("http"):
							user_vidlinks_result.append(sublink)
						else:
							user_vidlinks_result.append("https://www.youtube.com" + sublink)
					break
				else:
					num = int(user_input)
					if num == -1:
						break
					elif 0 <= num < len(scrape_vidlinks_result):
						user_vidlinks_result.append(scrape_vidlinks_result[num])
					else:
						print(Fore.RED + f"Please enter a number between 0 and {len(scrape_vidlinks_result)-1}." + Style.RESET_ALL)
			except ValueError:
				print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)

		return user_vidlinks_result

	def download_videos(self, vidlinks: list[str], output_path: str) -> None:
		"""
		Downloads each video link in vidlinks to the specified output_path using yt_dlp.
		:param1: A list of video links to download.
		:param2: The output path to save the videos to.
		:return: 
		"""
		for vidlink in vidlinks:
			ydl_opts = {
				'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
				'restrictfilenames': True,
				'quiet': False
			}
			with YoutubeDL(ydl_opts) as ydl:
				ydl.download([vidlink])
			print(Fore.GREEN + f"\nVideo downloaded from {vidlink} to {output_path}\n" + Style.RESET_ALL)

	def get_video_links(self, url_to_scrape: str) -> list[str]:
		"""
		Uses Selenium to retrieve video links from a given YouTube results page.
		:param1: The URL of the YouTube search results page to scrape.
		:return: A list of video links.
		"""
		chrome_options = Options()
		chrome_options.add_argument("--headless")
		chrome_options.add_argument("--disable-gpu")
		chrome_options.add_argument("--no-sandbox")

		driver = webdriver.Chrome(
			service=Service(ChromeDriverManager().install()),
			options=chrome_options
		)
		driver.get(url_to_scrape)
		
		try:
			WebDriverWait(driver, 15).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
			)
		except Exception as e:
			driver.quit()
			raise ValueError("Timeout waiting for video elements to load") from e
		
		video_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
		scrape_vidlinks_result = []
		
		# Limit to 6 items for brevity.
		for count, video in enumerate(video_elements):
			if count > 2:
				break
			try:
				link_element = video.find_element(By.CSS_SELECTOR, "a")
				href = link_element.get_attribute("href")
				if href and href not in scrape_vidlinks_result:
					scrape_vidlinks_result.append(href)
			except Exception as e:
				print("Failed to get link from a video element.", e)
		
		driver.quit()
		return scrape_vidlinks_result

	def get_cc_vids(self, script: str, output_path: str = None) -> None:
		"""
		Main function to gather URL parameters, retrieve video links, prompt user selection, and download videos.
		:param1: The script to generate URL parameters from.
		:param2: The output path to save the videos to.
		:return:
		"""
		if output_path is None or output_path == "":
			output_path = self._default_path
		expanded_output_path = os.path.expanduser(output_path)

		# Gather user-chosen URL parameters:
		url_params = self.gather_url_params(script)

		# Build the YouTube search URL:
		url_to_scrape = f"https://www.youtube.com/results?search_query={url_params}&sp=EgIwAQ%253D%253D"
		print(f"\nScraping videos from: {url_to_scrape}")

		# Retrieve video links:
		scrape_vidlinks_result = self.get_video_links(url_to_scrape)

		# Show the scraped links and let the user select specific ones to download:
		print("")  # spacing
		for count, sublink in enumerate(scrape_vidlinks_result):
			print(Fore.GREEN + f"{count}: {sublink}" + Style.RESET_ALL)
		print("")
		user_vidlinks_result = self.ask_user_for_video_selection(scrape_vidlinks_result)

		# Expand and download videos:
		output_path = os.path.expanduser(output_path)
		self.download_videos(user_vidlinks_result, output_path)
