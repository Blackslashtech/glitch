FROM python:latest

RUN apt update
RUN apt install -y iproute2

WORKDIR /checker

COPY ./.docker/checkerserver.py /checker/checkerserver.py

CMD ["python3", "checkerserver.py"]