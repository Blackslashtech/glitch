#!/bin/sh

API_KEY=""
TEAM_COUNT=2
VPN_PER_TEAM=1
VPN_SERVER_URL="localhost"

source .env set


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
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_ID" | tr '[:upper:]' '[:lower:]')
            echo "Stopping $HOSTNAME..."
            docker stop $HOSTNAME -t 1 > /dev/null &
        fi
    done
done

echo "Stopping range services..."
API_KEY="" PEERS="" docker-compose down -t 2 > /dev/null
