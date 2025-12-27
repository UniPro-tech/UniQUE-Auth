FROM ghcr.io/astral-sh/uv:python3.13-alpine

RUN apk add --no-cache \
  gcc \
  musl-dev \
  python3-dev \
  mariadb-dev \
  pkgconf \
  build-base \
  mysql-client

COPY . /app/unique_api

RUN uv venv .venv

RUN  uv sync --active

EXPOSE 8080

CMD ["uv", "run", "--active", "unique_api/app/main.py"]