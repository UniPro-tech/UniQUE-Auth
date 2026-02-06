## Multi-stage Dockerfile
##  - builder: build the Go server binary
##  - runtime: minimal Alpine with openssl and mysql client, runs `scripts/run.sh`

FROM golang:1.24.4-alpine AS builder
RUN apk add --no-cache git ca-certificates
WORKDIR /src
COPY . .

RUN export COMMIT=$(git rev-parse --short HEAD)
RUN export BRANCH=$(git branch --show-current)


# Build the Go server (static, no cgo)
RUN cd src && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /app/server ./cmd/server

FROM alpine:3.19 AS runtime
RUN apk add --no-cache openssl mysql-client ca-certificates

WORKDIR /app
RUN mkdir -p /app/keys/private /app/keys/public /app/unique_api

# Copy built server and scripts
COPY --from=builder /app/server /app/server
COPY --from=builder /src/scripts /app/unique_api/scripts

# Copy any config or internal packages needed at runtime (optional)
COPY --from=builder /src/src/internal /app/unique_api/internal

EXPOSE 8080

RUN chmod +x /app/unique_api/scripts/run.sh

CMD ["/app/unique_api/scripts/run.sh"]