FROM alpine AS certificates

RUN apk add openssl

WORKDIR /app

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem -subj '/C=NL/ST=Noord-Brabant/L=Eindhoven/O=exm/OU=Beheer/emailAddress=john.doe@example.com/CN=avro-api'

FROM python:3.10 AS builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.10-slim AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=certificates /app/key.pem /app/cert.pem ./certs/

COPY data ./data
COPY routers ./routers
COPY main.py program.py ./

RUN mkdir -p /app/sqlite

ENTRYPOINT [ "python", "program.py" ]