# fastapi_backend/settings.py
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
# API_KEY is only used by ETL service, not by FastAPI backend for data serving
