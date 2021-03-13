# https://github.com/jigsawlabs-student/docker-streamlit-lab/blob/main/foursquare/api/Dockerfile
FROM python:3.7-alpine
WORKDIR /usr/src/app

COPY ./ ./


# RUN apk update \
#    && apk add postgresql-dev gcc python3-dev musl-dev

# Chris Slacked this:
# https://github.com/analytics-ufcg/python3.7-pandas-psycopg2-alpine/blob/master/Dockerfile
RUN apk --no-cache add musl-dev linux-headers g++ postgresql-dev python3-dev openblas-dev


RUN pip3 install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]