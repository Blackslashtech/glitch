#!/bin/sh

# Configure docker daemon
mkdir /etc/docker
echo -e '{ "dns" : [ "8.8.8.8" , "8.8.4.4" ] }' > /etc/docker/daemon.json

# Start docker daemon
echo "Starting docker daemon..."
dockerd --insecure-registry http://registry:5000 --registry-mirror http://registry:5000 &

# Wait for docker daemon to start
echo "Waiting for docker daemon to start..."
while ! docker info >/dev/null 2>&1; do sleep 1; done
echo "Docker daemon started."

# Check if there is a deploy.sh script in the service directory
if [ -f deploy.sh ]; then
    # If there is, run it
    echo "Running deploy.sh..."
    sh deploy.sh
else
    # Start docker-compose
    echo "Running docker-compose..."
    docker-compose up -d >/dev/null
fi

# Set root password to ROOT_PASSWORD env var
echo "Setting root password to $ROOT_PASSWORD..."
echo "root:$ROOT_PASSWORD" | chpasswd

# Enable root login via ssh
echo "Enabling root login via ssh..."
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# Start sshd
echo "Starting sshd..."
/usr/sbin/sshd  > /dev/null 2>&1

# Hang forever so container doesn't exit
echo "Hanging forever..."
tail -f /dev/null