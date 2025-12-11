FROM python:3.11-slim

# Install Java (required for PySpark)
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command (can be overridden)
CMD ["python", "run_pipeline.py", "--companies-only"]