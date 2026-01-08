import os
from dotenv import load_dotenv

load_dotenv() 

# Flask app variables

DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DEBUG = True
TESTING = True

# API Client variable
API_KEY = os.getenv("API_KEY")