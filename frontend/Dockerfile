FROM python:3.7

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

CMD ["streamlit", "run", "src/index.py"]