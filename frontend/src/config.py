import os

# Backend URL configuration
# Use localhost for local development, fastapi_backend for Docker
BACKEND_HOST = os.getenv('BACKEND_HOST', 'localhost')
BACKEND_PORT = os.getenv('BACKEND_PORT', '8000')
BACKEND_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# API endpoints
AGGREGATION_BY_SECTOR_URL = f"{BACKEND_BASE_URL}/api/v1/sectors"
SEARCH_SECTOR_URL = f"{BACKEND_BASE_URL}/api/v1/sectors/search"