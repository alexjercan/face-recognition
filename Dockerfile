# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN apt-get update && apt-get -y install g++ cmake

WORKDIR /app

COPY requirements-server.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY server.py server.py
COPY whitelist whitelist

CMD [ "python3", "server.py" ]
