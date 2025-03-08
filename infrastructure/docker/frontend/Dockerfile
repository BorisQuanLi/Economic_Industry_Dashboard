FROM python:3.10-slim

WORKDIR /app
COPY frontend/requirements.txt .
RUN pip3 install -r requirements.txt

COPY frontend/ .
COPY .env .

EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py"]
