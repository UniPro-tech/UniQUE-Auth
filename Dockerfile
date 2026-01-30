FROM ghcr.io/astral-sh/uv:python3.14-alpine

RUN apk add --no-cache \
  gcc \
  musl-dev \
  python3-dev \
  mariadb-dev \
  pkgconf \
  build-base \
  mysql-client \
  openssl

COPY . /app/unique_api

WORKDIR /app/unique_api

RUN uv venv .venv

RUN  uv sync --active

EXPOSE 8080

RUN chmod +x /app/unique_api/scripts/run.sh

CMD ["/app/unique_api/scripts/run.sh"]