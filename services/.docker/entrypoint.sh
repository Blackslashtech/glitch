#!/bin/sh

# Start docker daemon
echo "Starting docker daemon..."
dockerd --insecure-registry http://registry:5000 --registry-mirror http://registry:5000 &

# Wait for docker daemon to start
echo "Waiting for docker daemon to start..."
while ! docker info >/dev/null 2>&1; do sleep 1; done
echo "Docker daemon started."

# Check if ./docker-compose.yaml exists
if [ -f ./docker-compose.yaml ]; then
    sed '/cpus:/s/^/#/' ./docker-compose.yaml > ./docker-compose.yaml.tmp
    sed '/pids_limit:/s/^/#/' ./docker-compose.yaml > ./docker-compose.yaml.tmp
    sed '/mem_limit:/s/^/#/' ./docker-compose.yaml > ./docker-compose.yaml.tmp
    mv ./docker-compose.yaml.tmp ./docker-compose.yaml
else if [ -f ./docker-compose.yml ]; then
    sed '/cpus:/s/^/#/' ./docker-compose.yml > ./docker-compose.yml.tmp
    sed '/pids_limit:/s/^/#/' ./docker-compose.yml > ./docker-compose.yml.tmp
    sed '/mem_limit:/s/^/#/' ./docker-compose.yml > ./docker-compose.yml.tmp
    mv ./docker-compose.yml.tmp ./docker-compose.yml
fi

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