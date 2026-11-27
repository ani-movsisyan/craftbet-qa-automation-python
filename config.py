import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://craftbet.com"
TIMEOUT = 20  # seconds for explicit waits
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

USERNAME = os.getenv("CRAFTBET_USERNAME", "")
PASSWORD = os.getenv("CRAFTBET_PASSWORD", "")
