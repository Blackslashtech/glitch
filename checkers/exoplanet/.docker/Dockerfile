FROM python:3.9

RUN apt update
RUN apt install -y iproute2

COPY ./.docker/requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /checker

COPY . /checker
COPY ./.docker/checkerserver.py /checker/checkerserver.py

CMD ["python3", "checkerserver.py"]