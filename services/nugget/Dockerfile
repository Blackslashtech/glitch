FROM golang:1.21 as build-env

ENV CGO_ENABLED=0

WORKDIR /app
COPY cmd cmd
COPY internal internal
COPY go.* ./

RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
        go build \
            -ldflags="-w -s" \
            -o /nugget \
            ./cmd/nugget/main.go

CMD ["/nugget"]
