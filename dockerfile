FROM python:3.11.4

RUN mkdir /app
WORKDIR /app

ADD . /app/
ADD requirements.txt requirements.txt

RUN apt update -y
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
