FROM ubuntu:latest
LABEL authors="13igor0241@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3 build-essential

COPY . /src
WORKDIR /src

RUN pip3 install --no-cache-dir -r requirements.txt
