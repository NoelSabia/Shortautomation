import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize colorama
init()

class Scraper:
	"""
	Web scraper class to scrape websites for keywords
	"""
	def __init__(self, targets: list[str], keywords: list[str]) -> None:
		"""
		:param targets: target websites to scrape
		:param keywords: keywords to search for in the websites
		"""
		self._targets = targets
		self._keywords = keywords

	def add_keywords(self, keywords: list[str]) -> None:
		"""
		Add keywords to the list of keywords
		:param keywords: list of keywords to add
		:return:
		"""
		self._keywords.extend(keywords)

	def scrape(self) -> str:
		"""
		Scrape the websites for the keywords provided
		:return: string of the scraped text
		"""
		# List to store the sublinks to a specific topic
		scrape_sublinks_result = []
		# List to store the results that will be used to generate the script with chatgpt
		scrape_text_results = []

		# Loop through the websites in parallel
		with ThreadPoolExecutor() as executor:
			futures = [
				executor.submit(self.__fetch_links_, website)
				for website in self._targets
			]
			for future in as_completed(futures):
				scrape_sublinks_result.extend(future.result())

		# If no sublinks are found then return
		if len(scrape_sublinks_result) == 0:
			print(Fore.RED + "\nNo sublinks found. Please check your keywords." + Style.RESET_ALL)
			return

		# List all the scraped sublinks
		print("")
		for count, sublink in enumerate(scrape_sublinks_result):
			print(Fore.GREEN + f"{count}: {sublink}" + Style.RESET_ALL)
		print("")

		# Ask the user if they which sublinks should be scraped
		user_sublinks_result = []
		while True:
			try:
				user_input = int(input(
					f"Enter the number of the sublink to scrape (0-{len(scrape_sublinks_result) - 1}), or -1 to finish: "))
				if user_input == -1:
					break
				if 0 <= user_input < len(scrape_sublinks_result):
					user_sublinks_result.append(scrape_sublinks_result[user_input])
				else:
					print(
						Fore.RED + f"Please enter a number between 0 and {len(scrape_sublinks_result) - 1}." + Style.RESET_ALL)
			except ValueError:
				print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)

		# Loop through the sublinks in parallel and get the text from the paragraphs
		with ThreadPoolExecutor() as executor:
			futures = [
				executor.submit(self.__fetch_texts_, sublink) \
				for sublink in user_sublinks_result
			]
			for future in as_completed(futures):
				scrape_text_results.extend(future.result())

		# Send the scraped text to gpt_rewrite and then return the finished script
		return "\n".join(scrape_text_results)

	def __fetch_links_(self, link: str) -> list[str]:
		"""
		Fetch and process the link to extract sublinks.
		:param link:
		:param keywords:
		:return:
		"""
		sublinks: list[str] = []
		raw_html = requests.get(link)
		if raw_html.status_code == 200:
			soup = BeautifulSoup(raw_html.text, 'html.parser')
			links = soup.find_all('a')
			for link in links:
				href = link.get('href')
				if href and any(keyword in href for keyword in self._keywords) and href not in sublinks:
					sublinks.append(href)
		return sublinks

	def __fetch_texts_(self, sublink: str) -> list[str]:
		"""
        Fetch and process the sublink to extract paragraphs.
        :param sublink: URL of the sublink to fetch
        :return: List of paragraphs' text
        """
		paragraphs_text = []
		raw_html = requests.get(sublink)
		if raw_html.status_code == 200:
			soup = BeautifulSoup(raw_html.text, 'html.parser')
			main_content = soup.find('main')					#TODO: the main tag might only be specific to techcrunch! change accordingly
			if main_content:
				paragraphs = main_content.find_all('p')
				for paragraph in paragraphs:
					paragraphs_text.append(paragraph.get_text(separator="\n", strip=True))
		return paragraphs_text
