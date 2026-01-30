#!/bin/sh

if [ ! -f /app/keys/rsa_private.pem ] || [ ! -f /app/keys/rsa_public.pem ]; then \
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out /app/keys/rsa_private.pem && \
  openssl rsa -pubout -in /app/keys/rsa_private.pem -out /app/keys/rsa_public.pem && \
  chmod 600 /app/keys/rsa_private.pem && chmod 644 /app/keys/rsa_public.pem; \
fi

uv run --active unique_api/app/main.py