FROM python:3.11-slim-bullseye

RUN apt update && apt install -y xxd
WORKDIR /app
ADD src/requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY app.env app.env

RUN sed -i  "s/JWT_KEY=.*/JWT_KEY=$(xxd -u -l 20 -p /dev/urandom)/g" app.env

COPY src .

CMD python3 main.py