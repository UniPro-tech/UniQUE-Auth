FROM ghcr.io/astral-sh/uv:python3.13-alpine

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
# ビルド時に RSA 鍵が存在しなければ生成する
# config.py のデフォルトが rsa_private.pem / rsa_public.pem の場合、
# /app/unique_api 以下に鍵を作ることでアプリがそのまま利用できるようにする
RUN if [ ! -f rsa_private.pem ] || [ ! -f rsa_public.pem ]; then \
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out rsa_private.pem && \
  openssl rsa -pubout -in rsa_private.pem -out rsa_public.pem && \
  chmod 600 rsa_private.pem && chmod 644 rsa_public.pem; \
  fi

RUN uv venv .venv

RUN  uv sync --active

EXPOSE 8080

CMD ["uv", "run", "--active", "unique_api/app/main.py"]