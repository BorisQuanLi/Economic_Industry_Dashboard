FROM python:3.12-slim-bookworm

# Install Java 17 (LTS) for PySpark
# Added mkdir fix to ensure successful installation on slim images
RUN mkdir -p /usr/share/man/man1 && \
    apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into a subdirectory matching the package name
COPY . ./etl_service/

# Default command (can be overridden)
CMD ["python", "etl_service/pipelines/standard_pipeline.py", "--companies-only"]