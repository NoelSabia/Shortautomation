import os
import subprocess
from colorama import Fore, Style

class ShortFusion:
	def __init__(self, path: str):
		self._path = os.path.expanduser(path)
		self._output_dir = os.path.join(self._path, "upload")
		self._videos_dir = os.path.join(self._path, "visuals", "final_videos")
		self._images_dir = os.path.join(self._path, "visuals", "final_images")
		self._subtitles_dir = os.path.join(self._path, "subtitles")
		self._audio_dir = os.path.join(self._path, "audio")
	
	def get_all_images(self) -> list[str]:
		"""
		Get all images.
		:return: list of strings to the path of each video
		"""
		directory_images = self._images_dir

		image_extensions = {'.jpg'}

		image_count = [
			f for f in os.listdir(directory_images)
			if os.path.isfile(os.path.join(directory_images, f)) and os.path.splitext(f)[1].lower() in image_extensions
		]
		return image_count

	def get_all_videos(self) -> list[str]:
		"""
		Gets all videos.
		:return: list of string to the path of each image
		"""
		
		directory_videos = self._videos_dir
		video_extension = {'.mp4'}
		
		# Get all video files
		video_files = [
			f for f in os.listdir(directory_videos)
			if os.path.isfile(os.path.join(directory_videos, f)) and os.path.splitext(f)[1].lower() in video_extension
		]
		return video_files
	
	def video_fusion(self) -> str:
		"""
		Fuses videos and images into a single video with transitions
		:return: str - paths to the final video files
		"""
		# Get all images and videos
		images = self.get_all_images()
		videos = self.get_all_videos()
	
		final_visual_output = os.path.join(self._videos_dir, "final_visual.mp4")
		
		# Target vertical video format (for shorts/reels)
		target_width = 720
		target_height = 1280
		
		# make the command to concatenate all videos
		all_videos = []
		for video in videos:
			all_videos.extend(["-i", os.path.join(self._videos_dir, video)])
		
		# Apply filters and concatenate the scaled videos only (no audio)
		filter_complex = ""
		for i in range(len(videos)):
			filter_complex += f"[{i}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2[v{i}];"
		for i in range(len(videos)):
			filter_complex += f"[v{i}]"
		filter_complex += f"concat=n={len(videos)}:v=1:a=0[outv]"  # a=0 means no audio output
		
		# Construct the complete ffmpeg command
		command = [
			"ffmpeg", "-y",
			*all_videos,
			"-filter_complex", filter_complex,
			"-map", "[outv]",
			# Remove "-map", "[outa]" line completely
			"-c:v", "libx264",
			"-an",  # This disables audio
			final_visual_output
		]

		# Execute the command
		print(Fore.GREEN + "\nExecuting ffmpeg command..." + Style.RESET_ALL)
		video = subprocess.run(
			command,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)
	
		# Logging to check if it worked or not
		if video.returncode != 0:
			print(Fore.RED + f"\nError concatinating video and images!" + Style.RESET_ALL)
		else:
			print(Fore.GREEN + f"\nSuccessfully created video!" + Style.RESET_ALL)
		
		return final_visual_output

	def audio_fusion(self) -> list[str]:
		"""
		Fuses the audio in one audio where the music is a little quieter than the ai voice
		:return: list[str]
		"""
		voiceover_filenames = [os.path.join(self._audio_dir,"cleaned_output_german.mp3"), os.path.join(self._audio_dir,"cleaned_output_english.mp3")]
		music_filenames = [os.path.join(self._audio_dir,"cut_song_german.mp3"), os.path.join(self._audio_dir,"cut_song_english.mp3")]
		final_audio_output = [os.path.join(self._audio_dir, "merged_german.mp3"), os.path.join(self._audio_dir, "merged_english.mp3")]

		# iterate trough the ai voices and music files at the same time
		for voice, music, final_audio in zip(voiceover_filenames, music_filenames, final_audio_output):

			# this is the command that helps 
			command = [
				"ffmpeg", "-y",
				"-i", voice,
				"-i", music,
				"-filter_complex", 
				"[1:a]volume=0.05[music];[0:a][music]amix=inputs=2:duration=longest",
				"-c:a", "libmp3lame", "-q:a", "2",
				final_audio
			]

			audio = subprocess.run(
				command,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True
			)

			if audio.returncode != 0:
				print(Fore.RED + f"\nError mixing audio: {audio.stderr}!" + Style.RESET_ALL)
		
		return final_audio_output
	
	def orchestrate_fusion(self) -> None:
		"""
		Simplified orchestration that only processes videos and images
		:return:
		"""
		print(Fore.GREEN + "\nStarting video fusion..." + Style.RESET_ALL)
		video = self.video_fusion()
		print(Fore.GREEN + "\nFinished video fusion." + Style.RESET_ALL)
		print(Fore.GREEN + "\nStarting audio fusion..." + Style.RESET_ALL)
		audio = self.audio_fusion()
		print(Fore.GREEN + "\nFinished audio fusion." + Style.RESET_ALL)		

def main() -> None:
	fusion = ShortFusion("~/Documents/technews")
	fusion.orchestrate_fusion()

if __name__ == "__main__":
	main()

# geschnittene videos und bilder entsprechend drueber legen,
# zwischen videos und bildern auch immer eine entsprechende ueberleitung
# und dann noch subtitles die ich im .srt format habe einspielen mit entsprechenden effekten.
# das alles dann als mp4 verpacken und in ein entsprechenden ordner verschieben
