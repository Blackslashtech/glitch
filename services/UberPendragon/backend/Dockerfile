FROM python:3.9

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app.py /code/app.py
COPY ./common.py /code/common.py
COPY ./crypto.py /code/crypto.py
COPY ./places.py /code/places.py
COPY ./rides.py /code/rides.py
COPY ./users.py /code/users.py

CMD ["gunicorn", "--workers=8", "--bind", "0.0.0.0:5000", "app:app", "--log-level", "debug"]