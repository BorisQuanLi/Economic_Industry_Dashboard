FROM python:3.12-slim
WORKDIR /app
COPY . ./tabular_intelligence/
ENV PYTHONPATH=/app USE_MOCK_ANALYTICS=true
ENV PATH="/usr/local/bin:${PATH}"
RUN pip install --no-cache-dir scikit-learn xgboost pydantic pytest numpy pandas scipy 2>&1 | tail -3 || true
CMD ["python", "-c", "import sys; sys.path.insert(0,\"/app\"); from tabular_intelligence.contracts import USE_MOCK_ANALYTICS; print(\"offline_mock=\", USE_MOCK_ANALYTICS); from tabular_intelligence.demo import main; main()"]
