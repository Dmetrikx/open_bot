import os
from dotenv import load_dotenv

# Load environment variables from .env in the parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_POLITICS_CHANNEL = os.getenv('DISCORD_POLITICS_CHANNEL', 'politics')
XAI_API_KEY = os.getenv('XAI_API_KEY')

# UNUSED: YouTube API credentials
# YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
# YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
# YOUTUBE_PROJECT_ID = os.getenv('YOUTUBE_PROJECT_ID')
# YOUTUBE_AUTH_URI = os.getenv('YOUTUBE_AUTH_URI')
# YOUTUBE_TOKEN_URI = os.getenv('YOUTUBE_TOKEN_URI')
# YOUTUBE_AUTH_PROVIDER_X509_CERT_URL = os.getenv('YOUTUBE_AUTH_PROVIDER_X509_CERT_URL')
# YOUTUBE_REDIRECT_URI = os.getenv('YOUTUBE_REDIRECT_URI')
# YOUTUBE_CHECK_INTERVAL = int(os.getenv('YOUTUBE_CHECK_INTERVAL', '600'))
