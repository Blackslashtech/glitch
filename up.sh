#!/bin/sh

source .env set

echo "Starting range services..."
docker-compose up -d --build --force-recreate > /dev/null

# Sleep for 5 seconds to allow range services to come up
sleep 5

# Loop from 1 to $TEAM_COUNT
for TEAM_ID in $(seq 1 $TEAM_COUNT); do
  # Loop over every directory in /services
    for dir in ./services/*; do
        # Check if the file is named .docker
        if [ "$(basename "$dir")" = ".docker" ]; then
            # If it is, skip it
            continue
        fi
        # If the file is a directory
        if [ -d "$dir" ]; then
            # Start docker-compose in the /services directory with a volume mount of the directory
            # set the service environment variable to the directory name
            # Isolate the end of the directory name with the basename command
            SERVICE_ID="$(basename "$dir")"
            # Generate a random root password
            ROOT_PASSWORD="$(openssl rand -hex 16)"
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_ID" | tr '[:upper:]' '[:lower:]')
            echo "Starting $HOSTNAME, root password is $ROOT_PASSWORD ..."
            HOSTNAME=$HOSTNAME SERVICE_ID=$SERVICE_ID ROOT_PASSWORD=$ROOT_PASSWORD docker-compose -f services/docker-compose.yaml --project-name $HOSTNAME up -d --build --force-recreate
        fi
    done
done