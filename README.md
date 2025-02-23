# Shortautomation

A command-line program that streamlines creating short, “brainrot” videos.

## Table of Contents
- [Preflight Check List](#preflight-check-list)
  - [How to Install Python](#how-to-install-python)
  - [How to Set Up a Virtual Environment](#how-to-set-up-a-virtual-environment)
  - [How and What to Install via pip](#how-and-what-to-install-via-pip)
  - [API Keys and How to Get Them](#api-keys-and-how-to-get-them)
- [How to Use This Command-Line Program](#how-to-use-this-command-line-program)
- [How to Use the Master Command-Line Program](#how-to-use-the-master-command-line-program)
   - [How to change the program args file accordingly](#how-to-change-the-program-args-file-accordingly)

---

## Preflight Check List

### How to Install Python
1. Visit the official Python website or use your package manager.  
2. Verify installation with:  
   ```bash
   python --version
   ```

### How to Set Up a Virtual Environment
1. Navigate to the project folder in your terminal.  
2. Create and activate a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

### How and What to Install via pip
1. Ensure you’re in the virtual environment.  
2. Install dependencies with:  
   ```bash
   pip install colorama openai dotenv requests bs4 selenium webdriver_manager yt-dlp ffmpeg-python elevenlabs google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```
3. Alternative you can use a requirements file and just add all the packages in there and install all of them at once with:
   ```bash
   pip install -r requirements.txt
   ```

### API Keys and How to Get Them
1. Sign up for the necessary APIs (Eleven Labs, OpenAI).  
2. Add the keys to your .env file:
   ```
   OPENAI_API_KEY=your_openai_key
   ELEVEN_LABS_API_X=your_elevenlabs_key
   ```
> [!TIP]
> You can use a 10-min-mail to create endless free eleven labs api-keys. The more the better.

---

## How to Use This Command-Line Program
1. Activate your virtual environment.
2. Run Python scripts from the terminal, for example:  
   ```bash
   python3 main.py <directory of where to write the output> <from here on only args are websites to scrape> ...
   ```
3. Follow the prompts.


## How to Use the Master Command-Line Program
1. Activate your virtual environment.
2. Change the file program_args.txt [accordingly](#how-to-change-the-program-args-file-accordingly) or leave the default values.
3. Run Python scripts from the terminal, for example:  
   ```bash
   python3 master.py
   ```
4. Follow the prompts.

### How to change the program args file accordingly
The program_args.txt file has blocks that will have one directory of where to save all the output and as many websites to scrape as you want.
The only problem is that if you don't use the default websites you either have to write your own python code to scrape or use the default scraper.
Though the default scraper might be useless or deliver very poorly!

> [!NOTE]
> You will only need the master command-line program if you want to create multiple videos in one go.
