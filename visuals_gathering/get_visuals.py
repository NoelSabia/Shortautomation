import os
import requests
from colorama import Fore, Style
from openai import OpenAI
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

# Load environment variables from .env file
load_dotenv()

class VideoDownloader:
	def __init__(self, output_path: str, script: str) -> None:
		self._output_path = output_path
		self._script = script
		self._query = None
		self._rapid_api_key = os.environ['RAPIDAPI-KEY']
	
	def get_query(self) -> None:
		"""
		Get the search query from the user and set it as the query attribute.
		:return:
		"""
		client = OpenAI()

		# At first we get the search query in this format <word>%20<word2>%20<word3>
		while True:
			completion = client.chat.completions.create(
				model="gpt-4o-mini-2024-07-18",
				messages=[
					{"role": "system", "content": "You are someone who can summarize texts well."},
					{
						"role": "user",
						"content": self._script + "\n\n-Summarize the text in one english word! No more, no less!"
					}
				]
			)

			# Print the generated search query
			print(Fore.GREEN + f"\nSearch query:\n{completion.choices[0].message.content}\n" + Style.RESET_ALL)
			user_input = input("Do you want a rewrite (y/n) or rewrite it yourself(r)? (y/n/r): ")

			# Check the user input if n then write the search query break the loop
			if user_input.lower() == 'n':
				print(Fore.GREEN + f"\nScraping video links in list" + Style.RESET_ALL)
				query = completion.choices[0].message.content
				self._query = query
				break
			# If the user wants to rewrite the query
			elif user_input.lower() == 'r':
				user_rewritten_text = input("Enter the rewritten text in format <word>%20<word2>: ")
				query = user_rewritten_text
				self._query = query
				break
			# If the user enters something else then ask again
			elif user_input.lower() != 'n' and user_input.lower() != 'y':
				print(Fore.YELLOW + "Invalid input. Please enter 'y', 'n' or 'r'." + Style.RESET_ALL)


	def get_video_urls(self) -> list:
		"""
		Get video URLs from the Twitter API.
		:return: List of video URLs
		"""
		video_urls = []

		# Prepare the request with search query and api key and then get the json data for videos
		url = f"https://twttrapi.p.rapidapi.com/search-videos?query={self._query}"
		headers = {
			"x-rapidapi-key": f"{self._rapid_api_key}",
			"x-rapidapi-host": "twttrapi.p.rapidapi.com"
		}

		#get video via requests
		video_response = requests.get(url, headers=headers)
		video_json_data = video_response.json()

		# Get the entries array for videos
		entries = video_json_data["data"]["search"]["timeline_response"]["timeline"]["instructions"][0]["entries"]

		# Loop through each entry for videos 
		for i, entry in enumerate(entries):
			try:
				# Try to access the same path as before for each entry
				variants = entry["content"]["content"]["tweetResult"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["variants"]
				# Get the last variant -> highest resolution
				last_variant = variants[-1]
				content_type = last_variant.get("content_type")
				if content_type == "video/mp4":
					url = last_variant.get("url")
					video_urls.append(url)

			# Skip entries that don't have the expected structure
			except (KeyError, TypeError, IndexError):
				print(Fore.YELLOW + "No video found in this entry" + Style.RESET_ALL)

		# return the list with all the links in them
		return video_urls
	
	def get_image_urls(self) -> list:
		"""
		Get image URLs from the Twitter API.
		:return: List of image URLs
		"""
		image_urls = []

		#Prepare the request with search query and api key and then get the json data for images
		url = f"https://twttrapi.p.rapidapi.com/search-images?query={self._query}"
		headers = {
			"x-rapidapi-key": f"{self._rapid_api_key}",
			"x-rapidapi-host": "twttrapi.p.rapidapi.com"
		}

		#get video via requests
		image_response = requests.get(url, headers=headers)
		image_json_data = image_response.json()

		# Get the entries array for videos
		entries = image_json_data["data"]["search"]["timeline_response"]["timeline"]["instructions"][0]["entries"]

		# Loop through each entry for videos 
		for i, entry in enumerate(entries):
			try:
				# Try to access the same path as before for each entry
				media = entry["content"]["content"]["tweetResult"]["result"]["legacy"]["extended_entities"]["media"]
				# Loop through each media item
				for j, media_item in enumerate(media):
					image_urls.append(media_item.get("media_url_https"))

			# Skip entries that don't have the expected structure
			except (KeyError, TypeError, IndexError):
				print(Fore.YELLOW + "No image found in this entry" + Style.RESET_ALL)

		# return the list with all the links in them
		return image_urls
	
	def download_visuals(self) -> None:
		"""
		Download videos and images from the URLs.
		:return:
		"""
		self.get_query()
		
		# Use descriptive variables instead of a list
		video_urls = self.get_video_urls()
		image_urls = self.get_image_urls()
		
		# have correct path for the files
		directory_videos = os.path.expanduser(f"{self._output_path}/videos")
		directory_images = os.path.expanduser(f"{self._output_path}/images")
		
		# Download videos
		print(Fore.GREEN + f"\nDownloading {len(video_urls)} videos" + Style.RESET_ALL)
		for i, video in enumerate(video_urls):
			if i == 15:
				break
			try:
				ydl_opts = {'outtmpl': f'{directory_videos}/%(title)s.%(ext)s'}
				with YoutubeDL(ydl_opts) as ydl:
					ydl.download([video])
			except Exception as e:
				print(Fore.YELLOW + f"Error downloading video {video}: {e}" + Style.RESET_ALL)
		
		# Download images
		print(Fore.GREEN + f"\nDownloading {len(image_urls)} images" + Style.RESET_ALL)
		for i, image in enumerate(image_urls):
			if i == 15:
				break
			try:
				image_data = requests.get(image).content
				filename = f"{directory_images}/{i}_{image.split('/')[-1]}"
				with open(filename, "wb") as handler:
					handler.write(image_data)
			except Exception as e:
				print(Fore.YELLOW + f"Error downloading image {image}: {e}" + Style.RESET_ALL)
