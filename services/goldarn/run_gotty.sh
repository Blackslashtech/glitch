#!/usr/bin/env bash

while true; do
    /gotty --once --port "$1" --permit-write --tls --tls-crt /gotty.crt --tls-key /gotty.key /runner /usr/local/cargo/bin/cargo run -q --release --target-dir
done
