FROM python:3.10

RUN mkdir /app

WORKDIR /app

ADD . /app

RUN pip install poetry

RUN poetry install

EXPOSE 8027

CMD poetry run gunicorn -w 2 -b 127.0.0.1:8027 wsgi:app