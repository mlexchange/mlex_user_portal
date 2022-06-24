FROM python:3.9
MAINTAINER THE MLEXCHANGE TEAM

RUN ls
COPY docker/requirements.txt requirements.txt
COPY docker/wait-for-it.sh ./wait-for-it.sh
COPY docker/docker-entrypoint.sh ./docker-entrypoint.sh

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    python3-pip \
    ffmpeg \
    libsm6 \
    libxext6 \
    python3-tk

RUN pip3 install --upgrade pip &&\
    pip3 install -r requirements.txt 

WORKDIR /app/api
ENV HOME /app/api
COPY src src

ENV PYTHONUNBUFFERED=1
WORKDIR /app/api/src

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD uvicorn user_api:app --host 0.0.0.0 --port 5000 --reload
