FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN echo $SPOTIPY_CACHE > .cache-whatAGoodBot

CMD [ "python3", "src/main.py"]