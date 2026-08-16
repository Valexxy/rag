# Multi-stage Dockerfile: Golang Engine + Embedded 24/7 Baileys WhatsApp Gateway
FROM golang:1.22-alpine AS go-builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o server .

FROM node:20-alpine AS runner
WORKDIR /app

# Install ca-certificates, tzdata, supervisor, git, openssl, and libstdc++
RUN apk add --no-cache ca-certificates tzdata supervisor git openssl libstdc++

# Copy Golang compiled binary
COPY --from=go-builder /app/server /app/server

# Copy Baileys WhatsApp Gateway & install dependencies at both /app/gateway and /app
COPY gateway /app/gateway
RUN cd /app/gateway && npm install --production && cp -r node_modules /app/node_modules

# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisord.conf

EXPOSE 8080 8081
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
