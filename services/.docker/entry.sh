#!/bin/sh

dockerd > /dev/null 2>&1 &
sleep 5
docker-compose up -d --force-recreate > /dev/null 2>&1

# Set root password to ROOT_PASSWORD env var
echo "root:$ROOT_PASSWORD" | chpasswd

# Start sshd
/usr/sbin/sshd  > /dev/null 2>&1

# Register with the API server
curl api/service/register?service_id=${SERVICE_ID}\&ip=$(hostname -i | tr -d '\n')

# Hang forever so container doesn't exit
tail -f /dev/null