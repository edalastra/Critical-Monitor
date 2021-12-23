# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 3000:5000

RUN python3 -m flask db init

CMD python3 -m flask db migrate; python3 -m flask db upgrade; python3 run.py