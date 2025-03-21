import os
import requests
import subprocess
import multiprocessing as mp
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
		with open(os.path.expanduser(self._script), "r") as file:
			script_content = file.read()

		# At first we get the search query in this format <word>%20<word2>%20<word3>
		while True:
			completion = client.chat.completions.create(
				model="gpt-4o-mini-2024-07-18",
				messages=[
					{"role": "system", "content": "You are someone who can summarize texts well."},
					{
						"role": "user",
						"content": script_content + "\n\n-Summarize the text in one english word! No more, no less!"
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
		Download videos in parallel and images sequentially.
		:return:
		"""
		self.get_query()
		
		# Use descriptive variables instead of a list
		video_urls = self.get_video_urls()
		image_urls = self.get_image_urls()
		
		# Create directories
		directory_videos = os.path.expanduser(f"{self._output_path[0]}/videos")
		directory_images = os.path.expanduser(f"{self._output_path[0]}/images")
		os.makedirs(directory_videos, exist_ok=True)
		os.makedirs(directory_images, exist_ok=True)
		
		# Download videos in parallel
		print(Fore.GREEN + f"\nDownloading {min(len(video_urls), 15)} videos in parallel" + Style.RESET_ALL)
		
		# Limit to 15 videos and prepare processes
		videos_to_download = video_urls[:15]
		processes = []
		
		# Start a process for each video
		for i, video in enumerate(videos_to_download):
			p = mp.Process(
				target=self.download_video_worker,
				args=(video, directory_videos, i)
			)
			processes.append(p)
			p.start()
		
		# Wait for all video downloads to complete
		for p in processes:
			p.join()
		
		print(Fore.GREEN + f"\nVideo downloads complete. Now downloading images..." + Style.RESET_ALL)
		
		# Download images sequentially (as they're faster)
		print(Fore.GREEN + f"\nDownloading {min(len(image_urls), 15)} images" + Style.RESET_ALL)
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
		
		print(Fore.GREEN + f"\nAll downloads completed!" + Style.RESET_ALL)
	
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
	
	def get_all_images(self) -> list[str]:
		directory_images = os.path.expanduser(f"{self._output_path[0]}/images")

		image_extensions = {'.jpg', '.jpeg', '.png'}

		image_count = [
			f for f in os.listdir(directory_images)
			if os.path.isfile(os.path.join(directory_images, f)) and os.path.splitext(f)[1].lower() in image_extensions
		]
		return image_count

	def get_all_videos(self) -> list[list[str]]:
		"""
		Gets all videos and cuts them into 3-second segments sequentially.
		:return: List of lists, where each inner list contains segments from one original video
		"""
		
		directory_videos = os.path.expanduser(f"{self._output_path[0]}/videos")
		video_extension = {'.mp4'}
		
		# Get all video files
		video_files = [
			f for f in os.listdir(directory_videos)
			if os.path.isfile(os.path.join(directory_videos, f)) and os.path.splitext(f)[1].lower() in video_extension
		]
		
		# Create a directory for cut videos if it doesn't exist
		cut_directory = os.path.join(directory_videos, "segments")
		if not os.path.exists(cut_directory):
			os.makedirs(cut_directory)
		
		# Process videos sequentially
		print(Fore.GREEN + f"\nProcessing {len(video_files)} videos sequentially..." + Style.RESET_ALL)
		
		results = []
		for video_file in video_files:
			# Process each video one at a time
			segments = self.process_video_segments(video_file, directory_videos, cut_directory)
			results.append(segments)
		
		# Filter out empty lists (failed videos)
		all_segments = [segments for segments in results if segments]
		
		# Return list of lists, where each inner list contains segments from one original video
		if not all_segments and video_files:
			# If no segments were created, return the original video files
			return [video_files]
		
		return all_segments

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
			destination_path = os.path.expanduser(self._output_path[1]) + "/visuals/final_images/"
			subprocess.run(["mv", source_path, destination_path])

	def select_videos(self) -> None:
		"""
		Allowed to select video segments that the user wants to use in the final video
		:return:
		"""
		# Get list of available video segments from get_all_videos
		video_segments_by_source = self.get_all_videos()
		number_of_source_videos = len(video_segments_by_source)
		final_segments_list = []

		print(Fore.GREEN + f"\nYou can now pick video segments. There are segments from {number_of_source_videos} source videos." + Style.RESET_ALL)

		# Generate unique terminal identifier
		terminal_id = f"terminal_{os.getpid()}"

		# Iterate through each source video's segments
		for source_idx, segments in enumerate(video_segments_by_source):
			print(Fore.BLUE + f"\nViewing segments from source video {source_idx + 1}/{number_of_source_videos}" + Style.RESET_ALL)
			print(Fore.BLUE + f"This source video has {len(segments)} segments" + Style.RESET_ALL)
			
			 # Flag to check if we should skip this source video
			skip_source = False
			
			# Iterate through each segment for this source video
			for segment_idx, segment in enumerate(segments):
				# Skip the rest of this loop if we're skipping this source
				if skip_source:
					break
					
				# Path to segment is in the segments subdirectory
				segment_path = os.path.join(os.path.expanduser(f"{self._output_path[0]}/videos/segments"), segment)
				
				print(Fore.GREEN + f"\nSegment {segment_idx + 1}/{len(segments)} from source {source_idx + 1}. Needed visuals: {self._number_of_picked_visuals}/{self._needed_visuals}" + Style.RESET_ALL)
				print(f"Segment file: {segment}")
				
				# Tag current terminal window
				subprocess.run(["wmctrl", "-T", terminal_id, "-r", ":ACTIVE:"])

				# Open the video segment in mpv with focus control flags
				video_proc = subprocess.Popen(
					["mpv", "--no-focus-on-open", "--force-window=immediate", segment_path],
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

				user_input = input(Fore.GREEN + "\nUse this segment(y), skip it(n), or skip all segments from this source(s)? (y/n/s): " + Style.RESET_ALL)
				while True:
					if user_input.lower() == 'y':
						final_segments_list.append(segment)
						video_proc.terminate()
						self._number_of_picked_visuals += 1
						break
					elif user_input.lower() == 'n':
						video_proc.terminate()
						break
					elif user_input.lower() == 's':
						video_proc.terminate()
						skip_source = True
						print(Fore.YELLOW + f"Skipping all remaining segments from source {source_idx + 1}" + Style.RESET_ALL)
						break
					else:
						print(Fore.YELLOW + f"\nInput '{user_input}' not recognized as a command, use y, n, or s." + Style.RESET_ALL)
						user_input = input(Fore.GREEN + "\nUse segment(y), skip it(n), or skip all segments from this source(s)? (y/n/s): " + Style.RESET_ALL)

		# Move the selected segments to the final_videos folder
		for final_segment in final_segments_list:
			source_path = os.path.join(os.path.expanduser(f"{self._output_path[0]}/videos/segments"), final_segment)
			destination_path = os.path.expanduser(self._output_path[1]) + "/visuals/final_videos/"
			subprocess.run(["cp", source_path, destination_path])
			print("")
			print(Fore.GREEN + f"Copied segment {final_segment} to final videos folder" + Style.RESET_ALL)

	def download_video_worker(self, video_url, directory_videos, idx) -> bool:
		"""Worker function for downloading a single video in a separate process"""
		try:
			ydl_opts = {'outtmpl': f'{directory_videos}/%(title)s.%(ext)s'}
			with YoutubeDL(ydl_opts) as ydl:
				ydl.download([video_url])
			return True
		except Exception as e:
			print(Fore.YELLOW + f"Error downloading video {idx}: {video_url}: {e}" + Style.RESET_ALL)
			return False

	def process_video_segments(self, video_file, directory_videos, cut_directory) -> list[str]:
		"""
		Worker function to process a single video into segments
		:return: list[str]
		"""
		
		video_path = os.path.join(directory_videos, video_file)
		video_name = os.path.splitext(video_file)[0]
		segments_for_video = []
		
		# Get video duration using ffprobe
		result = subprocess.run([
			"ffprobe", 
			"-v", "error",
			"-show_entries", "format=duration",
			"-of", "default=noprint_wrappers=1:nokey=1",
			video_path
		], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
		
		try:
			duration = float(result.stdout.strip())
			# Calculate number of 3-second segments
			num_segments = int(duration / 3)
			
			# Cut video into 3-second segments
			for i in range(num_segments):
				start_time = i * 3
				segment_name = f"{video_name}_segment_{i}.mp4"
				output_path = os.path.join(cut_directory, segment_name)
				
				# Use ffmpeg to cut the segment
				subprocess.run([
					"ffmpeg",
					"-y",  # Overwrite output file if it exists
					"-ss", str(start_time),
					"-i", video_path,
					"-t", "3",  # 3-second duration
					"-c:v", "libx264",
					"-c:a", "aac",
					"-loglevel", "error",
					output_path
				], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
				
				segments_for_video.append(segment_name)
			
			print(Fore.GREEN + f"\nCut {video_file} into {len(segments_for_video)} segments." + Style.RESET_ALL)
			return segments_for_video
			
		except (ValueError, subprocess.SubprocessError) as e:
			print(Fore.YELLOW + f"\nError processing video {video_file}: {e}" + Style.RESET_ALL)
			return []

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
			elif enough_visuals.lower() == "":
				break
			enough_visuals = input(Fore.GREEN + f"\nDo you have enough visuals(ENTER) or want to look again over the materials(n)? (ENTER/n): ")
