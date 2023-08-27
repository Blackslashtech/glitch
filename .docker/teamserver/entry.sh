#!/bin/sh

dockerd > /dev/null 2>&1 &
sleep 5



# Loop over every directory in /services
for dir in /team/*; do
  # Check if the directory is named .docker
  if [ "$(basename "$dir")" = ".docker" ]; then
    # If it is, skip it
    continue
  fi
  # If the directory is a directory
  if [ -d "$dir" ]; then
    # Start docker-compose in the /services directory with a volume mount of the directory
    # set the service environment variable to the directory name
    # Isolate the end of the directory name with the basename command
    SERVICE_ID="$(basename "$dir")"
    # Generate a random root password
    ROOT_PASSWORD="$(openssl rand -hex 16)"
    # Register with the API server
    echo "Starting $SERVICE_ID, root password is $ROOT_PASSWORD"
    SERVICE_ID=$SERVICE_ID ROOT_PASSWORD=$ROOT_PASSWORD docker-compose --project-name $SERVICE_ID up -d --build --force-recreate
  fi
done

# Hang forever so container doesn't exit
tail -f /dev/null