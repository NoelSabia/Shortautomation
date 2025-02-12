import requests
from bs4 import BeautifulSoup
from Info_gathering.gpt_rewrite import gpt_rewrite
from colorama import Fore, Style, init

# Initialize colorama
init()

# This function will scrape the web for the keywords provided
# In detail we scrape the hole website for important sublinks and then ask the user which sublinks should be scraped. We then scrape them and send this to gpt_rewrite()
def scrape(keywords):
	# List of websites to scrape TODO: change website accordingly
	websites_to_scrape = ["https://techcrunch.com/"]
	# List to store the sublinks to a specific topic
	scrape_sublinks_result = []
	# List to store the results that will be used to generate the script with chatgpt
	scrape_text_results = []

	# Loop through the websites
	for website in websites_to_scrape:
		raw_html = requests.get(website)
		# If the request is successful then get every link that corresponds to the keywords
		if raw_html.status_code == 200:
			soup = BeautifulSoup(raw_html.text, 'html.parser')
			links = soup.find_all('a')
			for link in links:
				href = link.get('href')
				if href and any(keyword in href for keyword in keywords) and href not in scrape_sublinks_result:
					scrape_sublinks_result.append(href)
				
	# If no sublinks are found then return
	if (len(scrape_sublinks_result) == 0):
		print(Fore.RED + "No sublinks found. Please check your keywords." + Style.RESET_ALL)
		return

	#List all the scraped sublinks
	count = 0
	print("\n")
	for sublink in scrape_sublinks_result:
		print(Fore.GREEN + f"{count}: {sublink}" + Style.RESET_ALL)
		count += 1
	print("\n")

	# Ask the user if they which sublinks should be scraped
	user_sublinks_result = []
	while True:
		try:
			user_input = int(input(Fore.YELLOW + f"Enter the number of the sublink to scrape (0-{len(scrape_sublinks_result)-1}), or -1 to finish: " + Style.RESET_ALL))
			if user_input == -1:
				break
			if 0 <= user_input < len(scrape_sublinks_result):
				user_sublinks_result.append(scrape_sublinks_result[user_input])
			else:
				print(Fore.YELLOW + f"Please enter a number between 0 and {len(scrape_sublinks_result)-1}." + Style.RESET_ALL)
		except ValueError:
			print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)

	# Loop through the sublinks and get the text from the paragraphs (specified for techcrunch just delete everything that is related to main_content TODO: change this accordingly)
	for sublink in user_sublinks_result:
		raw_html = requests.get(sublink)
		if raw_html.status_code == 200:
			soup = BeautifulSoup(raw_html.text, 'html.parser')
			main_content = soup.find('main')
			if main_content:
				paragraphs = main_content.find_all('p')
				for paragraph in paragraphs:
					scrape_text_results.append(paragraph.get_text(separator="\n", strip=True))
	
	# Send the scraped text to gpt_rewrite
	combined_text = "\n".join(scrape_text_results)
	gpt_rewrite(combined_text)
