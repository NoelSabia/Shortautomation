# Brainrot2.0

A command-line program that streamlines creating short, “brainrot” videos.

## Table of Contents
- [Preflight Check List](#preflight-check-list)
  - [How to Install Python](#how-to-install-python)
  - [How to Set Up a Virtual Environment](#how-to-set-up-a-virtual-environment)
  - [How and What to Install via pip](#how-and-what-to-install-via-pip)
  - [API Keys and How to Get Them](#api-keys-and-how-to-get-them)
- [How to Use This Command-Line Program](#how-to-use-this-command-line-program)
- [How to Use the Master Command-Line Program](#how-to-use-the-master-command-line-program)

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
   pip install <package>
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
   python3 main.py
   ```
3. Follow the prompts.
> [!WARNING]
> Using different websites than the default websites could result in bad results!

## How to Use the Master Command-Line Program
1. Activate your virtual environment.  
2. Run Python scripts from the terminal, for example:  
   ```bash
   python3 master.py
   ```
3. Follow the prompts.

> [!NOTE]
> You will only need the master command-line program if you want to create multiple videos in one go.
