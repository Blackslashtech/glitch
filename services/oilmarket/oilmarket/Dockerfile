FROM rust:1.73-bookworm AS builder

RUN --mount=type=cache,target=/usr/local/rustup \
  rustup toolchain install nightly-2023-12-02 && \
  rustup default nightly-2023-12-02

RUN apt update && apt install -y protobuf-compiler libprotobuf-dev

WORKDIR /build
RUN mkdir dir

COPY build.rs build.rs
COPY proto proto
COPY Cargo.lock Cargo.toml .
COPY src src
COPY .sqlx .sqlx

RUN \
  --mount=type=cache,target=/usr/local/cargo/registry \
  --mount=type=cache,target=/build/target \
  cargo build --release && \
  cp target/release/oilmarket .

FROM ubuntu:22.04

RUN echo "nobody:x:1000:1000:::" > /etc/passwd
RUN echo "nobody::1000:nobody" > /etc/group

COPY --from=builder --chown=nobody:nobody --chmod=500 /build/oilmarket /oilmarket

USER nobody

ENTRYPOINT [ "/oilmarket" ]
