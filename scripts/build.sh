#!/bin/sh

swag i -g cmd/server/main.go

# if --dev flag is provided, set gin to debug mode
if [ "$1" = "--dev" ]; then
  export DB_DSN="root:rootpass123@tcp(localhost:3306)/devdb?parseTime=true"
  export GIN_MODE=debug
  go run cmd/server/main.go
else
  export GIN_MODE=release
  go build cmd/server/main.go
fi
