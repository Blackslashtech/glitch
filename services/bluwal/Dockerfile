FROM golang:1.21-alpine as build

ENV CGO_ENABLED=0

WORKDIR /app
COPY go.* ./
COPY cmd cmd
COPY internal internal
COPY pkg pkg
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
        go build \
            -ldflags="-w -s" \
            -o bluwal \
            cmd/bluwal/main.go

FROM alpine

WORKDIR /app
COPY --from=build /app/bluwal bluwal
COPY front/dist front/dist

CMD ["./bluwal"]
