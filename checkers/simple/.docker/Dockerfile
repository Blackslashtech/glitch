FROM python:latest

RUN apt update
RUN apt install -y iproute2

COPY ./.docker/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

WORKDIR /checker

COPY ./.docker/checkerserver.py /checker/checkerserver.py

CMD ["python3", "checkerserver.py"]