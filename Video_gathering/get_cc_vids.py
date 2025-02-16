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

def get_cc_vids(script: str, output_path: str = "~/Documents/brainrot/videos/") -> None:
	"""
	get_cc_vids downloads youtube videos that were published under the creative commons license

	:param 1: script: str: The script that is being used to find videos
	:return: None
	"""

	api_key = os.getenv('OPENAI_API_KEY')
	if not api_key:
		raise ValueError(Fore.RED + "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable." + Style.RESET_ALL)
	
	# Initialize the client and user_rewritten_url_parameters
	client = OpenAI(api_key=api_key)
	user_rewritten_url_parameters = ""

	# Loop to ask if the url parameter that is returned from chatgpt is what the user wants
	while True:
		# Get the new url-parameters via API call to openai's 4o-mini model
		completion = client.chat.completions.create(
			model="gpt-4o-mini-2024-07-18",
			messages=[
				{"role": "developer", "content": "You are an assistant that extracts the most relevant keywords from a given script. Your response must contain only 2 to 4 words, separated by a `+` symbol, and nothing else. Do not include any punctuation other than `+`. Prioritize nouns and key terms."},
				{
					"role": "user",
					"content": script
				}
			]
		)

		# Print the generated url_parameters and ask the user if they are fine with the result, want something else or want to rewrite it themselves
		print(Fore.GREEN + f"\nGenerated URL-parameter:\n{completion.choices[0].message.content}\n" + Style.RESET_ALL)
		user_input = input("Do you want a rewrite or rewrite it yourself? (y/n/r): ")

		# Check the user input if n then create the url and break the loop
		if user_input.lower() == 'n':
			break

		# If the user wants to rewrite the text then ask for the rewritten text and write it to the file
		elif user_input.lower() == 'r':
			user_rewritten_url_parameters = input("\nEnter the rewritten URL-parameters like <word1+word2+word3+word4>: ")
			break
		
		# If the user enters something else then ask again
		elif user_input.lower() != 'n' and user_input.lower() != 'y':
			print(Fore.YELLOW + "Invalid input. Please enter 'y' for yes, 'n' for no or 'r' for rewrite." + Style.RESET_ALL)

	# Make the url to scrape
	url_params = user_rewritten_url_parameters if user_rewritten_url_parameters != "" else completion.choices[0].message.content
	url_to_scrape = f"https://www.youtube.com/results?search_query={url_params}&sp=EgIwAQ%253D%253D"
	
	# List to store the sublinks to a specific topic 
	scrape_vidlinks_result = get_video_links(url_to_scrape)
				
	#List all the scraped sublinks
	count = 0
	print("")
	for count, sublink in enumerate(scrape_vidlinks_result):
		print(Fore.GREEN + f"{count}: {sublink}" + Style.RESET_ALL)
	print("")

	# Ask the user if they which sublinks should be scraped
	user_vidlinks_result = []
	while True:
		try:
			user_input = input(f"Enter the number of the sublink to scrape (0-{len(scrape_vidlinks_result)-1}), -1 to finish or ENTER to download all: ")
			if user_input == "":
				# Download all videos as no specific sublink is given
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

	# expand the output path
	output_path = os.path.expanduser(output_path)

	# Loop trough the vidlinks and download the videos
	for vidlink in user_vidlinks_result:
	    ydl_opts = {
	        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
	        'restrictfilenames': True,
	        'quiet': False
	    }

	    with YoutubeDL(ydl_opts) as ydl:
	        ydl.download([vidlink])

	    print(Fore.GREEN + f"\nVideo downloaded from {vidlink} to {output_path}\n" + Style.RESET_ALL)

# Replace the requests/BeautifulSoup scraping with Selenium:
def get_video_links(url_to_scrape: str) -> list:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.get(url_to_scrape)
    
    # Wait until elements are loaded; here we wait for at least one ytd-video-renderer to appear
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
    except Exception as e:
        driver.quit()
        raise ValueError("Timeout waiting for video elements to load") from e
    
    # Now, get all ytd-video-renderer elements (which contain the <a> tags)
    video_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
    scrape_vidlinks_result = []
    
    # Iterate over the video elements. For each, find the first <a> element and get its href.
    for count, video in enumerate(video_elements):
        if count > 5:
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
