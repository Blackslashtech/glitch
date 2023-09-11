#!/bin/sh

source .env set

echo "Stopping all containers..."
sh down.sh

echo "Deleting all containers..."

# Loop from 1 to $TEAM_COUNT
for TEAM_ID in $(seq 1 $TEAM_COUNT); do
    # Loop over every checker in /checkers
    for dir in ./checkers/*; do
        # Check if the file is named .templates or README.md
        if [ "$(basename "$dir")" = ".templates" ] || [ "$(basename "$dir")" = "README.md" ]; then
            # If it is, skip it
            continue
        fi
        # If the file is a directory
        if [ -d "$dir" ]; then
            SERVICE_ID="$(basename "$dir")"
            # Generate a random root password
            HOSTNAME=$(echo "checker-$SERVICE_ID" | tr '[:upper:]' '[:lower:]')
            echo "Deleting $HOSTNAME..."
            docker rm $HOSTNAME > /dev/null &
        fi
    done
    # Loop over every directory in /services
    for dir in ./services/*; do
        # Check if the file is named .docker
        if [ "$(basename "$dir")" = ".docker" ]; then
            # If it is, skip it
            continue
        fi
        # If the file is a directory
        if [ -d "$dir" ]; then
            SERVICE_ID="$(basename "$dir")"
            # Generate a random root password
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_ID" | tr '[:upper:]' '[:lower:]')
            echo "Deleting $HOSTNAME..."
            docker rm $HOSTNAME > /dev/null &
        fi
    done
done

# Prune dangling images
docker image prune -f > /dev/null

# Prune dangling volumes
docker volume prune -f > /dev/null

# Delete all the vpn files
rm -rf ./.docker/vpn/* > /dev/null