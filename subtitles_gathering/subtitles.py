import os
import json
import math
from colorama import Fore, Style
import subprocess

class SubtitleGenerator:
    def __init__(self, languages: list[str], path: str):
        self._languages = languages
        self._path = path

    def _format_timestamp(self, seconds):
        """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
        hours = math.floor(seconds / 3600)
        seconds %= 3600
        minutes = math.floor(seconds / 60)
        seconds %= 60
        milliseconds = math.floor((seconds - math.floor(seconds)) * 1000)
        seconds = math.floor(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def _create_short_segments(self, json_path, output_srt_path, segment_duration=2.0):
        """Create short subtitle segments from whisper JSON output"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        segments = []
        current_segment = {"words": [], "start": None, "end": None, "text": ""}
        
        # Process each segment and its words
        for segment in data["segments"]:
            for word in segment.get("words", []):
                # If this is the first word in our segment, set the start time
                if current_segment["start"] is None:
                    current_segment["start"] = word["start"]
                
                # Add this word to our current segment
                current_segment["words"].append(word)
                current_segment["end"] = word["end"]
                
                # If we've reached our segment duration, finalize this segment
                if current_segment["end"] - current_segment["start"] >= segment_duration:
                    current_segment["text"] = " ".join(w["word"] for w in current_segment["words"])
                    segments.append(current_segment)
                    # Start a new segment
                    current_segment = {"words": [], "start": None, "end": None, "text": ""}
        
        # Don't forget the last segment if it has content
        if current_segment["words"]:
            current_segment["text"] = " ".join(w["word"] for w in current_segment["words"])
            segments.append(current_segment)
        
        # Write the SRT file
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments):
                # SRT format: index, timestamp, text, blank line
                f.write(f"{i+1}\n")
                f.write(f"{self._format_timestamp(segment['start'])} --> {self._format_timestamp(segment['end'])}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        
        return len(segments)

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
                    "--model", "turbo",
                    "--language", language,
                    "--device", "cpu",
                    "--output_dir", full_output_dir,
                    "--output_format", "srt",
                    # Settings to create shorter segments:
                    "--max_line_width", "20",     # Fewer characters per line
                    "--max_line_count", "1",      # Only one line per segment 
                    "--max_words_per_line", "3",  # 2-3 words per line maximum
                    "--word_timestamps", "True"   # Enable word-level timestamps
                ])
                
                print(Fore.GREEN + f"Subtitle generation for {language} completed." + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"Error generating subtitles for {language}: {e}" + Style.RESET_ALL)
