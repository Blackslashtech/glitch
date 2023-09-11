FROM python:3.9

WORKDIR /checker

COPY ./.docker/requirements.txt /checker/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /checker/requirements.txt

COPY ./.docker/interface.py /checker/interface.py
COPY ./.docker/checkeradapter.py /checker/checkeradapter.py

COPY . /checker/src

CMD ["python3", "interface.py"]