FROM python:3.9
MAINTAINER THE MLEXCHANGE TEAM

WORKDIR /app/work

COPY docker/requirements.txt ./requirements.txt
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

ENV HOME /app/work
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["bash"]
