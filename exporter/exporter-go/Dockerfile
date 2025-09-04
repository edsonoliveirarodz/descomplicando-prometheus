FROM golang:1.23-alpine3.20 AS build

WORKDIR /app
COPY . /app

RUN go mod init exporter || true
RUN go mod tidy

RUN go build exporter.go


FROM alpine:3.16

COPY --from=build /app/exporter /app/exporter
EXPOSE 7788
WORKDIR /app
CMD ["./exporter"]