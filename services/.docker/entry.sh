#!/bin/sh

dockerd > /dev/null 2>&1 &
sleep 5
docker-compose up -d 2>/dev/null

# Set root password to ROOT_PASSWORD env var
echo "root:$ROOT_PASSWORD" | chpasswd

# Start sshd
/usr/sbin/sshd  > /dev/null 2>&1

# Hang forever so container doesn't exit
tail -f /dev/null