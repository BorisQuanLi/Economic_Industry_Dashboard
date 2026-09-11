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

COPY . .

# Offline-safe default: no live Neo4j or OpenAI calls without explicit env vars.
# Set USE_MOCK_GRAPH=false and provide NEO4J_URI / OPENAI_API_KEY for live mode.
ENV USE_MOCK_GRAPH=true \
    USE_FAKE_EMBEDDINGS=true

# Library service — no HTTP port exposed by default.
# Mount as a module: docker run graph_intelligence python -m graph_intelligence.company_search_tool
CMD ["python", "-c", "import graph_intelligence; print('graph_intelligence ready')"]
