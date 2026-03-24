# etl_service/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Database settings — accept both POSTGRES_* (docker-compose) and DB_* (legacy) env var names
DB_USER = os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres"))
DB_NAME = os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "postgres"))
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PASSWORD = os.getenv("DB_PASS", os.getenv("POSTGRES_PASSWORD", "postgres"))

# Financial Modeling Prep API Key
API_KEY = os.getenv("FMP_API_KEY", "YOUR_FMP_API_KEY")
