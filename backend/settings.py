import os
from dotenv import load_dotenv

load_dotenv() # read from .env file, which is saved at the same directory level as setting.py. /backend/
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DEBUG = True
TESTING = True
API_KEY = "f269391116fc672392f1a2d538e93171"
