# ETL Service Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and pandas
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY etl_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the etl_service package
COPY etl_service/ ./etl_service/

# Create data directory for CSV files
RUN mkdir -p /app/data

ENV PYTHONPATH=/app

# Default command runs the full pipeline with DB init
CMD ["python", "-m", "etl_service.run_pipeline", "--init-db"]
