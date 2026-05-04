# A runtime-focused CUDA image for smaller footprint
FROM nvidia/cuda:12.1.0-base-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CUDA_VISIBLE_DEVICES=0

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install the CUDA-enabled torch binary
# We pin to cu121 to match our H100 hardware target defined in SKILL.md
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir torch==2.2.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

# Copy and install project dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory for staging
RUN mkdir -p /app/cache

# Standard entrypoint for a microservice
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8070"]
