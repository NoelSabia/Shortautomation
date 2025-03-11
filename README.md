# Shortautomation

A command-line program that streamlines creating short videos, shorts for YouTube, TikTok or Instagram.

## Table of Contents
- [Preflight Check List](#preflight-check-list)
  - [How to Install Python](#how-to-install-python)
  - [How to Set Up a Virtual Environment](#how-to-set-up-a-virtual-environment)
  - [How and What to Install via pip](#how-and-what-to-install-via-pip)
  - [API Keys and How to Get Them](#api-keys-and-how-to-get-them)
  - [How to make a capcut account](#How-to-make-a-capcut-account)
  - [How to get the JSONs to autoupload youtube shorts](#How-to-get-the-JSONs-to-autoupload-youtube-shorts)
- [How to Use This Command-Line Program](#how-to-use-this-command-line-program)
- [How to Use the Master Command-Line Program](#how-to-use-the-master-command-line-program)
   - [How to change the program args file correctly](#how-to-change-the-program-args-file-correctly)


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
2. Install dependencies and ffmpeg on your system:  
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


### How to make a CapCut Account
You need a CapCut Account because this is the editor I choose to edit the video.
Go to https://www.capcut.com and make yourself an account. This is highly recommended.
The programm will eventually, after creating the script, audio and videos, open one of two browsers.
Chrome or Firefox, you can specifiy the browser used [here](#how-to-change-the-program-args-file-correctly). If you don't use either of those, get fucked.

### How to get the JSONs to autoupload youtube shorts
1. You need a Google account to upload to YouTube (https://www.google.com/intl/de/account/about/)
2. Go to: console.cloud.google.com/cloud-resource-manager
3. Check that you use the correct Google account
4. Click on "Create Project", give it a name and then click on create
5. Click on the Pop-Up on the top right that says: "Select Project"
6. Hover over "APIs & Services" and then click on "Enable APIs & services"
7. Then search for " YouTube Data API v3"
8. Enable it
9. Click on "OAuth consent screen"
10. Click on "Start"
11. Give a name, the support mail, click on external, then again your mail, and accept the terms and conditions, then create
12. Go to "Audience" and click on "Add Users" and add your mail
13. Go to "Clients" click on "Create Client" and select "Web Application"
14. Create URI1 and URI2 with http://localhost:8080/ and http://localhost:8080/oauth2callback and click on create
15. Now Download the JSON and your ready to go


## How to Use This Command-Line Program
1. Activate your virtual environment.
2. Run Python scripts from the terminal, for example:  
   ```bash
   python3 main.py <directory of where to write the output> <from here on only args are websites to scrape> ...
   ```
3. Follow the prompts.


## How to Use the Master Command-Line Program
1. Activate your virtual environment.
2. Change the file program_args.txt [accordingly](#how-to-change-the-program-args-file-correctly) or leave the default values.
3. Run Python scripts from the terminal, for example:  
   ```bash
   python3 master.py
   ```
4. Follow the prompts.

> [!NOTE]
> You will only need the master command-line program if you want to create multiple videos in one go.

### How to change the program args file correctly
The program_args.txt file has blocks that will have one directory of where to save all the output and as many websites to scrape as you want. It takes these parameters:

1. dir=<value in form of a string> -> this key-pair value shows where all the output will be downloaded (recommended "~/Documents/<projectname>)
2. browser=<value in form of a str> -> this key-pair value should either be chrome or firefox everything else is not supported
3. website=<value in form of a str> -> this key-pair value gives the website to scrape. You can have as many website key-value pairs as you like

The only problem is that if you don't use the default websites you either have to write your own python code to scrape or use the default scraper.
With that knowledge, the default scraper might be useless or deliver very poorly!

> [!NOTE]
> A 10-min-mail will also work here 😉