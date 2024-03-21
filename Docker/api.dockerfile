FROM python:3.11-slim

WORKDIR /usr/src/app


RUN apt-get update

COPY requirements.txt /usr/src/app
RUN pip install -r requirements.txt

COPY . /usr/src/app



CMD [ "gunicorn" , "-k" , "uvicorn.workers.UvicornWorker","-w", "2", "-b" , ":8000",  "backend.app:app" ]