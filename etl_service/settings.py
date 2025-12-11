# etl_service/settings.py
# Database settings
DB_USER = "postgres"
DB_NAME = "postgres"
DB_HOST = "postgres" # For Docker Compose environment
DB_PASSWORD = "postgres" # Replace with actual password from .env or secrets for production

# Financial Modeling Prep API Key
API_KEY = "YOUR_FMP_API_KEY" # Replace with your actual API key