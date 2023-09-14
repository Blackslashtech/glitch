FROM golang:alpine3.17 AS builder
RUN apk update && apk add --no-cache git
ENV USER=appuser
ENV UID=10001 
RUN adduser \    
    --disabled-password \    
    --gecos "" \    
    --home "/nonexistent" \    
    --shell "/sbin/nologin" \    
    --no-create-home \    
    --uid "${UID}" \    
    "${USER}"
WORKDIR $GOPATH/src/auth_proxy
COPY src .
# RUN go get -d -v
RUN GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o /go/bin/auth_proxy


FROM scratch
# Import the user and group files from the builder.
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group
# Copy our static executable.
# COPY --from=builder /go/src/auth_proxy/public /go/bin/public
COPY --from=builder /go/bin/auth_proxy /go/bin/auth_proxy
# Use an unprivileged user.
USER appuser:appuser
WORKDIR /go/bin
# Run the conundrum binary.
ENTRYPOINT ["./auth_proxy"]