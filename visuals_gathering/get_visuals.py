import os
import requests
import subprocess
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
		self._query = None
		self._rapid_api_key = os.environ['RAPIDAPI-KEY']
		self._number_of_picked_visuals = 0
		self._needed_visuals = self.calculate_visuals_needed()
	
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
		directory_videos = os.path.expanduser(f"{self._output_path[0]}/videos")
		directory_images = os.path.expanduser(f"{self._output_path[0]}/images")
		
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
	
	def calculate_visuals_needed(self) -> int:
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
			duration = int(tmp_duration)
			return duration
		except ValueError:
			print(Fore.YELLOW + "Could not retrieve duration." + Style.RESET_ALL)
	
	def get_all_images(self) -> list[str]:
		directory_images = os.path.expanduser(f"{self._output_path[0]}/images")

		image_extensions = {'.jpg', '.jpeg', '.png'}

		image_count = [
			f for f in os.listdir(directory_images)
			if os.path.isfile(os.path.join(directory_images, f)) and os.path.splitext(f)[1].lower() in image_extensions
		]
		return image_count

	def get_all_videos(self) -> list[list[str]]:
		directory_videos = os.path.expanduser(f"{self._output_path[0]}/videos")
		video_extention = {'.mp4'}

		video_count = [
			f for f in os.listdir(directory_videos)
			if os.path.isfile(os.path.join(directory_videos, f)) and os.path.splitext(f)[1].lower() in video_extention
		]

		#here implement the cutting of the videos

		return video_count

	def select_images(self) -> None:
		"""
		Allowed to select the images that the user want's to use in the video
		:return:
		"""
		preliminary_image_list = self.get_all_images()
		number_of_images = len(preliminary_image_list)
		final_image_list = []
	
		# the counter of how many visuals are needed and how many we currently have
		print(Fore.GREEN + f"\nPick around {self._needed_visuals} visuals." + Style.RESET_ALL)

		#display the images first
		print(Fore.GREEN + f"\nYou can now pick images. There is a total of {number_of_images} images." + Style.RESET_ALL)
		
		# Generate unique terminal identifier
		terminal_id = f"terminal_{os.getpid()}"
		
		for i, image in enumerate(preliminary_image_list):
			directory_images = os.path.expanduser(f"{self._output_path[0]}/images/")
			print(directory_images + image)
			print(Fore.GREEN + f"\nPicture {i + 1} of {number_of_images}. Needed visuals: {self._number_of_picked_visuals}/{self._needed_visuals}" + Style.RESET_ALL)
			
			# Tag current terminal window then open image with feh
			subprocess.run(["wmctrl", "-T", terminal_id, "-r", ":ACTIVE:"])
			image_window = subprocess.Popen(
				["feh", directory_images + image],
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
				start_new_session=True
			)
			
			# Short pause to allow feh to open then force focus back to terminal
			subprocess.run(["sleep", "0.1"])
			subprocess.run(["wmctrl", "-a", terminal_id])
			
			user_input = input(Fore.GREEN + "\nUse image(y) or delete image(n)? (y/n): " + Style.RESET_ALL)
			while True:
				if user_input.lower() == 'y':
					final_image_list.append(image)
					image_window.terminate()
					self._number_of_picked_visuals += 1
					break
				elif user_input.lower() == 'n':
					image_window.terminate()
					break
				else:
					print(Fore.YELLOW + f"\nInput '{user_input}' not recognized as a command use y or n." + Style.RESET_ALL)
					user_input = input(Fore.GREEN + "\nUse image(y) or delete image(n)? (y/n): " + Style.RESET_ALL)
		
		for final_image in final_image_list:
			source_path = os.path.join(os.path.expanduser(f"{self._output_path[0]}/images"), final_image)
			destination_path = os.path.expanduser(self._output_path[1]) + "/final_images/"
			subprocess.run(["mv", source_path, destination_path])

	def select_videos(self) -> None:
		"""
		Allowed to select the videos that the user wants to use in the video
		:return:
		"""
		# Get list of available video files from get_all_videos
		preliminary_video_list = self.get_all_videos()
		number_of_videos = len(preliminary_video_list)
		final_video_list = []

		print(Fore.GREEN + f"\nYou can now pick videos. There is a total of {number_of_videos} videos." + Style.RESET_ALL)

		# Generate unique terminal identifier
		terminal_id = f"terminal_{os.getpid()}"

		for i, video in enumerate(preliminary_video_list):
			directory_videos = os.path.expanduser(f"{self._output_path[0]}/videos/")
			print(directory_videos + video)
			print(Fore.GREEN + f"\nVideo {i + 1} of {number_of_videos}. Needed visuals: {self._number_of_picked_visuals}/{self._needed_visuals}" + Style.RESET_ALL)

			# Tag current terminal window
			subprocess.run(["wmctrl", "-T", terminal_id, "-r", ":ACTIVE:"])

			# Open the video in mpv with focus control flags
			video_proc = subprocess.Popen(
				["mpv", "--no-focus-on-open", "--force-window=immediate", directory_videos + video],
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
				start_new_session=True
			)
			
			# Longer pause to allow mpv to fully initialize
			subprocess.run(["sleep", "0.3"])
			
			# Force focus back to terminal - repeat to ensure it takes effect
			subprocess.run(["wmctrl", "-a", terminal_id])
			subprocess.run(["sleep", "0.1"])
			subprocess.run(["wmctrl", "-a", terminal_id])

			user_input = input(Fore.GREEN + "\nUse video(y) or delete video(n)? (y/n): " + Style.RESET_ALL)
			while True:
				if user_input.lower() == 'y':
					final_video_list.append(video)
					video_proc.terminate()
					self._number_of_picked_visuals += 1
					break
				elif user_input.lower() == 'n':
					video_proc.terminate()
					break
				else:
					print(Fore.YELLOW + f"\nInput '{user_input}' not recognized as a command, use y or n." + Style.RESET_ALL)
					user_input = input(Fore.GREEN + "\nUse video(y) or delete video(n)? (y/n): " + Style.RESET_ALL)

		# We move the selected videos to the final_video folder to later process only the selected videos
		for final_video in final_video_list:
			source_path = os.path.join(os.path.expanduser(f"{self._output_path[0]}/videos"), final_video)
			destination_path = os.path.expanduser(self._output_path[1]) + "/final_videos/"
			subprocess.run(["mv", source_path, destination_path])

	def select_visuals(self) -> None:
		"""
		Orchastrated the selection of the visuals
		:return:
		"""
		enough_visuals = None

		#this loop will allow the user to select other images and video if the threshold of needed visuals are not passed
		while True:
			if enough_visuals == None or enough_visuals.lower() == 'n':
				self.select_images()
				self.select_videos()
			elif enough_visuals.lower() == 'y':
				break
			enough_visuals = input(Fore.GREEN + f"\nDo you have enough visuals(y) or want to look again over the materials(n)? (y/n): ")


def main() -> None:
	video = VideoDownloader(["~/Documents/test" + "/visuals", "~/Documents/test"], "Elon Musk, geboren 1971 in Südafrika, ist ein Visionär, der Tesla zur führenden Marke für Elektroautos machte. Tesla wurde 2003 gegründet, doch erst mit Musks Einstieg 2004 gewann das Unternehmen an Bedeutung. Mit dem Tesla Roadster (2008) zeigte Tesla, dass Elektroautos leistungsstark sein können. Später folgten Modelle wie S, X, 3 und Y, die Elektromobilität massentauglich machten. Neben Autos entwickelt Tesla auch Batteriespeicher und Solartechnologien. Trotz Produktionsengpässen und Kritik bleibt Tesla ein Innovationsführer, der traditionelle Autobauer zum Umdenken zwingt. Die Gigafactory sorgt für nachhaltige Batterien, und Musks Ziel bleibt eine emissionsfreie Zukunft. Elon Musk treibt mit Tesla die Energiewende voran. Seine Vision und unkonventionelle Art machen ihn zu einer der einflussreichsten Persönlichkeiten der Technologiebranche.")
	# video.download_visuals()
	video.select_visuals()

if __name__ == "__main__":
	main()
