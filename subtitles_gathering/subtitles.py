import os
import json
import math
from colorama import Fore, Style
import subprocess

class SubtitleGenerator:
    def __init__(self, languages: list[str], path: str):
        self._languages = languages
        self._path = path

    def get_subtitles(self):
        """
        Gets the subtitles of the videos in German and English using whisper
        :return:
        """
        input_paths = ["/audio/cleaned_output_german.mp3", "/audio/cleaned_output_english.mp3"]
        output_paths = ["/subtitles/german.srt", "/subtitles/english.srt"]

        for i, (language, input_path, output_path) in enumerate(zip(self._languages, input_paths, output_paths)):
            print(Fore.GREEN + f"\nGetting subtitles {i+1}/{len(self._languages)}." + Style.RESET_ALL)
            
            # Build the full input and output paths
            full_input_path = os.path.expanduser(self._path + input_path)
            full_output_dir = os.path.dirname(os.path.expanduser(self._path + output_path))
            
            # Create output directory if it doesn't exist
            os.makedirs(full_output_dir, exist_ok=True)
            
            try:
                # Run whisper with parameters to create shorter segments
                subprocess.run([
                    "whisper", 
                    full_input_path,
                    "--model", "small",
                    "--language", language,
                    "--device", "cuda",
                    "--output_dir", full_output_dir,
                    "--output_format", "srt",
                    # Settings to create shorter segments:
                    "--max_line_width", "15",     # Reduced character limit to force shorter lines
                    "--max_line_count", "1",      # Only one line per segment 
                    "--word_timestamps", "True"   # Enable word-level timestamps for more precise segmentation
                ])
                
                
                print(Fore.GREEN + f"Subtitle generation for {language} completed." + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"Error generating subtitles for {language}: {e}" + Style.RESET_ALL)