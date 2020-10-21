FROM python:3.7

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install -U pip

WORKDIR /home/chatdb

COPY ./chatdb ./chatdb
COPY ./setup.py ./README.md ./

RUN pip install --progress-bar off -e .
