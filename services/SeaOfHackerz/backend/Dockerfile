FROM python:3.11-slim-buster

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app.py /code/app.py

CMD ["gunicorn", "--workers=32", "--bind", "0.0.0.0:5000", "app:app", "--log-level", "debug"]