FROM ubuntu:22.04 as setup

RUN apt -y update && apt -y install wget libseccomp-dev gcc

WORKDIR /
RUN wget https://github.com/yudai/gotty/releases/download/v1.0.1/gotty_linux_amd64.tar.gz
RUN tar xvf gotty_linux_amd64.tar.gz

ADD runner/main.c .
RUN gcc main.c -lseccomp -o runner

FROM rust:1.72 as app

RUN apt -y update && apt -y install parallel psmisc

WORKDIR /app
ADD app/Cargo.toml app/Cargo.lock app/rust-toolchain ./
RUN mkdir -p src && echo "//" > src/lib.rs
RUN cargo build  --release
RUN rm -rf src

ADD app/src ./src

COPY --from=setup /gotty /gotty
COPY --from=setup /runner /runner

RUN chmod u+s,g+s /runner

ADD gotty.crt /
ADD gotty.key /

RUN useradd -m -s /bin/false -u 1337 ctf

RUN mkdir -p /files && chmod 777 /files
RUN mkdir -p /cache && chmod 777 /cache

ADD run.sh run_gotty.sh /
RUN chmod +x /run.sh /run_gotty.sh

USER ctf

CMD [ "/run.sh" ]
