import os
from dotenv import load_dotenv

load_dotenv()
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")
LOGIN = os.getenv("LOGIN").encode("utf-8")
