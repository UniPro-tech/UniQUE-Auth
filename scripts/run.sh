if [ ! -f /app/unique_api/rsa_private.pem ] || [ ! -f /app/unique_api/rsa_public.pem ]; then \
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out /app/unique_api/rsa_private.pem && \
  openssl rsa -pubout -in /app/unique_api/rsa_private.pem -out /app/unique_api/rsa_public.pem && \
  chmod 600 /app/unique_api/rsa_private.pem && chmod 644 /app/unique_api/rsa_public.pem; \
fi

uv run --active unique_api/app/main.py