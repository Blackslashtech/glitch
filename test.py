#!/usr/bin/env python3
# Netcat into 10.0.13.37 1337

from pwn import *
import sys

context.log_level='error'

r = remote('range2.strider.one', 666)

r.recvuntil(b'\n\n')

flags = sys.argv[1:]

for flag in flags:
    try:
        r.sendline(flag.encode('utf-8'))
        status = ' '.join(r.recvline().decode('utf-8').strip().split(' ')[1:])
        print(flag + "," + status)
    except Exception as e:
        print(flag + "," + "ERR submitter: " + str(e))