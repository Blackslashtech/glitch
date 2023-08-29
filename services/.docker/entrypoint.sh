#!/bin/sh

# Check in with API server
curl -s http://api/service/create?api_key=$API_KEY\&hostname=$HOSTNAME\&ip=$(hostname -i | tr -d '\n')\&status=starting

# Start docker daemon
echo "Starting docker daemon..."
dockerd --insecure-registry http://registry:5000 --registry-mirror http://registry:5000 &

# Wait for docker daemon to start
echo "Waiting for docker daemon to start..."
while ! docker info >/dev/null 2>&1; do sleep 1; done
echo "Docker daemon started."

# Update status with API server
curl -s http://api/service/update?api_key=$API_KEY\&hostname=$HOSTNAME\&status=building


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

# Update status with API server
curl -s http://api/service/update?api_key=$API_KEY\&hostname=$HOSTNAME\&status=up

# Set root password to ROOT_PASSWORD env var
echo "Setting root password..."
echo "root:$ROOT_PASSWORD" | chpasswd

# Start sshd
echo "Starting sshd..."
/usr/sbin/sshd  > /dev/null 2>&1

# Hang forever so container doesn't exit
echo "Hanging forever..."
tail -f /dev/null