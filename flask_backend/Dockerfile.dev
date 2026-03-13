FROM python:3.7-alpine
# use miniconda instead?
# https://discuss.streamlit.io/t/how-to-use-streamlit-in-docker/1067/4

WORKDIR /usr/src/app

COPY ./requirements.txt . 

# To enable pip install psycopg2-binary, listed in requirements.txt
# Below, from https://stackoverflow.com/questions/62715570/failing-to-install-psycopg2-binary-on-new-docker-container


RUN apk update --no-cache \
    && apk add build-base postgresql-dev libpq --no-cache --virtual .build-deps \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt \
    && apk del .build-deps \
    && apk add --no-cache libstdc++ \
    && apk add postgresql-libs libpq --no-cache \
    && apk add bind-tools

# Above, from https://stackoverflow.com/questions/62715570/failing-to-install-psycopg2-binary-on-new-docker-container

RUN pip install -r requirements.txt

COPY ./ ./

CMD ["flask", "run", "--host=0.0.0.0"]
