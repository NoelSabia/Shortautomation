import requests
import random
from random import randint
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

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
		for target in self._targets:
			sublinks = self.__fetch_links_(target)
			scrape_sublinks_result.extend(sublinks)

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
				executor.submit(self.__fetch_texts_, self._targets, sublink) \
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
		sublinks = []
		visited = set()
		raw_html = requests.get(link)
		if raw_html.status_code == 200:
			print(Fore.GREEN + f"\nStatus Code of {raw_html.status_code} received." + Style.RESET_ALL)
		else:
			print(Fore.RED + f"\nStatus Code of {raw_html.status_code} received." + Style.RESET_ALL)
		if raw_html.status_code == 200:
			soup = BeautifulSoup(raw_html.text, 'html.parser')

			# for techcrunch
			if link == "https://techcrunch.com/":
				main_section = soup.select_one("main")
				if main_section:
					links = main_section.find_all('a')
					for a in links:
						href = a.get('href')
						if href and not href.startswith("http"):
							href = urljoin(link, href)
						if href and "/author" not in href and "/category" not in href and href not in sublinks and len(sublinks) < 20:
							sublinks.append(href)

			# for historydaily
			elif not self._keywords and link == "https://www.historydaily.com/episodes/":
				page_url = f"{link}?page={randint(1, 42)}"
				if page_url not in visited:
					visited.add(page_url)
					raw_html = requests.get(page_url)
					if raw_html.status_code == 200:
						soup = BeautifulSoup(raw_html.text, 'html.parser')
						div = soup.select_one("div.row-wrapper")
						if div:
							links = div.find_all('a')
							for a in links:
								href = a.get('href')
								if href and not href.startswith("http"):
									href = urljoin(link, href)
								if href and href not in visited and len(sublinks) < 20:
									visited.add(href)
									sub_html = requests.get(href)
									if sub_html.status_code == 200:
										sub_soup = BeautifulSoup(sub_html.text, 'html.parser')
										transcript_anchor = sub_soup.find('a', href='#transcript')
										if transcript_anchor:
											sublinks.append(href)

			elif not self._keywords and link == "https://www.politico.eu/":
					main_section = soup.select_one("main#main.main--front-page")
					if main_section:
						links = main_section.find_all('a')
						for a in links:
							href = a.get('href')
							if href and href not in sublinks and len(sublinks) < 20:
								sublinks.append(href)
								
			elif not self._keywords and link == "https://www.neverendingfootsteps.com/travel-guides/":
				main_section = soup.select_one("main.vw-content-main")
				if main_section:
					links = main_section.find_all('a')
					for link in links:
						href = link.get('href')
						sublinks.append(href)

			else:
				print(Fore.RED + "\nNo known website found. Please write your own scraper." + Style.RESET_ALL)

		return sublinks

	def __fetch_texts_(self, website: list[str], sublink: str) -> list[str]:
		"""
        Fetch and process the sublink to extract paragraphs.
        :param sublink: URL of the sublink to fetch
        :return: List of paragraphs' text
        """
		paragraphs_text = []

		if sublink == "https://techcrunch.com/":
			raw_html = requests.get(sublink)
			if raw_html.status_code == 200:
				soup = BeautifulSoup(raw_html.text, 'html.parser')
				main_content = soup.find('main')
				if main_content:
					paragraphs = main_content.find_all('p')
					for paragraph in paragraphs:
						paragraphs_text.append(paragraph.get_text(separator="\n", strip=True))

		elif website[0] == "https://www.historydaily.com/episodes/":
			raw_html = requests.get(sublink)
			if raw_html.status_code == 200:
				soup = BeautifulSoup(raw_html.text, 'html.parser')
				parapgraphs = soup.find_all('p')
				for paragraph in paragraphs:
						paragraphs_text.append(paragraph.get_text(separator="\n", strip=True))

		elif website[0] == "https://www.politico.eu/":
			raw_html = requests.get(sublink)
			if raw_html.status_code == 200:
				soup = BeautifulSoup(raw_html.text, 'html.parser')
				parapgraphs = soup.find_all('p')
				for paragraph in paragraphs:
						paragraphs_text.append(paragraph.get_text(separator="\n", strip=True))

		elif website[0] == "https://www.neverendingfootsteps.com/travel-guides/":
			raw_html = requests.get(sublink)
			if raw_html.status_code == 200:
				soup = BeautifulSoup(raw_html.text, 'html.parser')
				links = soup.find_all('a')
				anchor_hrefs = [a.get('href') for a in links if a.get('href')]
				if anchor_hrefs:
					chosen_href = random.choice(anchor_hrefs)
					sub_html = requests.get(chosen_href)
					if sub_html.status_code == 200:
						sub_soup = BeautifulSoup(sub_html.text, 'html.parser')
						paragraphs = sub_soup.find_all('p')
						for paragraph in paragraphs:
							paragraphs_text.append(paragraph.get_text(separator="\n", strip=True))

		else:
			raw_html = requests.get(sublink)
			if raw_html.status_code == 200:
				soup = BeautifulSoup(raw_html.text, 'html.parser')
				# You could scrape a variety of elements; here we collect all <p> tags
				paragraphs = soup.find_all('p')
				for paragraph in paragraphs:
					text = paragraph.get_text(separator="\n", strip=True)
					if text:
						paragraphs_text.append(text)

		return paragraphs_text
