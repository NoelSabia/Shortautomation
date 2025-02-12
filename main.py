from Info_gathering.scraper import scrape
from colorama import Fore, Style, init

# Initialize colorama
init()

# In the main function we ask the user for the keywords and then call the scrape function
def main():

	# Ask the user for the keywords
	keywords = input(Fore.YELLOW + "Enter topic related keywords: " + Style.RESET_ALL).lower()
	splitted_keywords = keywords.split(" ")

	# Call the scrape function
	scrape(splitted_keywords)

# Call the main function
if __name__ == "__main__":
	main()