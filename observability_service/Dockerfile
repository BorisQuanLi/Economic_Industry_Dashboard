FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY observability_service/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . ./observability_service/
ENV PYTHONPATH=/app USE_MOCK_ANALYTICS=true
RUN python -m pytest observability_service/tests/ -v
CMD ["python", "-m", "observability_service.main"]
