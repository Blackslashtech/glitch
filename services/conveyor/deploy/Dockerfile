FROM python:3.11.7-slim-bookworm

ENV \
  PYTHONUNBUFFERED=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_CREATE=false
WORKDIR /conveyor

RUN \
  --mount=type=cache,target=/root/.cache/pip \
  pip install -U pip setuptools && \
  pip install poetry==1.7.1

COPY pyproject.toml poetry.lock .
RUN \
  --mount=type=cache,target=/root/.cache/pip \
  --mount=type=cache,target=/root/.cache/pypoetry \
  poetry install --no-root --no-interaction --no-ansi

COPY conveyor/*.py ./conveyor/
COPY scripts/*.py ./scripts/
RUN \
  --mount=type=cache,target=/root/.cache/pip \
  --mount=type=cache,target=/root/.cache/pypoetry \
  poetry install --no-interaction --no-ansi

RUN mkdir ./data && \
  chmod -R 444 . && \
  chmod 555 . ./conveyor ./scripts && \
  chmod 777 ./data
USER nobody
CMD ["poetry", "run", "conveyor-server"]
