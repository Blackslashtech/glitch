FROM python:3.11-bookworm

RUN apt update && apt upgrade -y && apt install -y dumb-init g++

RUN useradd web && usermod -a -G web web

WORKDIR /app
COPY requirements.txt .

RUN apt install -y libmariadb-dev
RUN pip install -r requirements.txt
RUN pip install pybind11

COPY src .
RUN chown -R web:web .

EXPOSE 5000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["gunicorn", "-w", "4", "-b", ":5000", "app:app", "--user", "web", "--group", "web"]