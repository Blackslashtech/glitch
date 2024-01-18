FROM python:3.9

RUN apt update
RUN apt install -y iproute2

WORKDIR /checker

COPY . /checker
COPY ./.docker/checkerserver.py /checker/checkerserver.py

RUN bash ./setup.sh

CMD ["python3", "checkerserver.py"]