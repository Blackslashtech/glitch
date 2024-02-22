#!/bin/sh

chown nobody:nogroup -R /users

exec socat 'TCP-LISTEN:1337,reuseaddr,fork,keepalive,su=nobody' EXEC:./martian
