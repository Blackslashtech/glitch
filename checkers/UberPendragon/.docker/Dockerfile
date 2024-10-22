FROM python:3.12

RUN apt update
RUN apt install -y iproute2

WORKDIR /checker

COPY . /checker
COPY ./.docker/adapter.py /checker/adapter.py
COPY ./.docker/checkerserver.py /checker/checkerserver.py

RUN bash ./setup.sh

CMD ["python3", "checkerserver.py"]
