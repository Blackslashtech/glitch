#!/usr/bin/env bash

mkdir -p /home/ctf/.parallel && echo -j 512 -k > /home/ctf/.parallel/run_profile && chmod 400 /home/ctf/.parallel/run_profile

seq 14141 14652 | parallel -J run_profile /run_gotty.sh
