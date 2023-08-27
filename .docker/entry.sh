#!/bin/sh

dockerd & > /dev/null 2>&1
sleep 5


# Loop over every directory in /services
for dir in /services/*; do
  # If the directory is a directory
  if [ -d "$dir" ]; then
    # Start docker-compose in the /services directory with a volume mount of the directory
    # set the service environment variable to the directory name
    # Isolate the end of the directory name with the basename command
    export SERVICE_NAME="$(basename "$dir")"
    # Generate a random root password
    export ROOT_PASSWORD="$(openssl rand -hex 16)"
    echo "Starting $SERVICE_NAME, root password is $ROOT_PASSWORD"
    SERVICE_NAME=$SERVICE_NAME docker-compose --project-name $SERVICE_NAME up -d --force-recreate > /dev/null 2>&1
  fi
done

# Hang forever so container doesn't exit
tail -f /dev/null