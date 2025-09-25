# Build stage
FROM golang:1.19-alpine AS builder
WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY . .
RUN go build -o /tubehosting-attack-notifier cmd/notifier/main.go

# Final stage
FROM alpine:latest
WORKDIR /
COPY --from=builder /tubehosting-attack-notifier .
EXPOSE 8080
ENTRYPOINT ["/tubehosting-attack-notifier"]