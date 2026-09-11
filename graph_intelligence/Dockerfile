FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the package under /app/graph_intelligence/ so import paths resolve:
#   from graph_intelligence.neo4j_client import Neo4jClient
COPY . ./graph_intelligence/

# /app must be on PYTHONPATH so `graph_intelligence` is a top-level package.
ENV PYTHONPATH=/app \
    USE_MOCK_GRAPH=true \
    USE_FAKE_EMBEDDINGS=true \
    USE_MOCK_SCREENER=true

# Default: self-contained quick-start demo — offline, no credentials needed.
# Run tests instead:
#   docker run <image> python -m pytest graph_intelligence/tests/ -v
CMD ["python", "graph_intelligence/demo.py"]
