FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip3 install -r requirements.txt

COPY backend/ .
COPY .env .

ENV FLASK_APP=api.src
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api.src:create_app()"]
