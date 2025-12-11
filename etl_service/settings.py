# etl_service/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Database settings (from environment variables)
DB_USER = os.getenv("DB_USER", "postgres")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PASSWORD = os.getenv("DB_PASS", "postgres")

# Financial Modeling Prep API Key
API_KEY = os.getenv("FMP_API_KEY", "YOUR_FMP_API_KEY")