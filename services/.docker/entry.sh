#!/bin/sh

# Start docker daemon
dockerd --insecure-registry http://registry:5000 --registry-mirror http://registry:5000 &

# Check in with API server
curl -s http://api/services/create?api_key=$API_KEY\&hostname=$HOSTNAME\&ip=$(hostname -i | tr -d '\n')

docker-compose up -d 2>/dev/null

# Update status with API server
curl -s http://api/services/update?api_key=$API_KEY\&hostname=$HOSTNAME\&status=up

# Set root password to ROOT_PASSWORD env var
echo "root:$ROOT_PASSWORD" | chpasswd

# Start sshd
/usr/sbin/sshd  > /dev/null 2>&1

# Hang forever so container doesn't exit
tail -f /dev/null