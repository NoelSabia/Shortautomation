from elevenlabs import generate
from elevenlabs import set_api_key
from dotenv import load_dotenv

# Load environment variables from .env file and initialize the api key
load_dotenv()
set_api_key('ELEVEN_LABS_API')

def get_voice(str_to_voice):
	audio = generate(text=str_to_voice, voice="Voice name")

