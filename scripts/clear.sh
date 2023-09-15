#!/bin/bash

# Check if cwd is range
if [[ ! -d "./checkers" && -d "./services" && -d "./.docker" ]]; then
    echo "Please run this script from the range directory (i.e. sh scripts/clear.sh))"
    exit 1
fi

TEAM_TOKENS=""

source .env set

echo "Stopping all containers..."
sh scripts/down.sh

# Wait for all the docker stop commands to finish
sleep 5

echo "Deleting all containers..."

SERVICE_LIST=$(echo $SERVICES | tr ',' '\n')

# Loop from 1 to $TEAM_COUNT
for TEAM_ID in $(seq 1 $TEAM_COUNT); do
    # Loop over every service
    for SERVICE_NAME in $SERVICE_LIST; do
        dir="./services/$SERVICE_NAME"
        # If the file is a directory
        if [ -d "$dir" ]; then
            # Generate a random root password
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
            echo "Deleting $HOSTNAME..."
            docker rm $HOSTNAME > /dev/null &
        fi
    done
done

# Loop over every checker
for SERVICE_NAME in $SERVICE_LIST; do
    dir="./checkers/$SERVICE_NAME"
    # If the file is a directory
    if [ -d "$dir" ]; then
        # Generate a random root password
        HOSTNAME=$(echo "checker-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
        echo "Deleting $HOSTNAME..."
        docker rm $HOSTNAME > /dev/null &
    fi
done

# Delete all the vpn files
rm -rf ./.docker/vpn/* > /dev/null

# Delete all the teamdata files
rm ./teamdata.txt
rm -rf ./.docker/api/teamdata/* > /dev/null

# Wait to ensure all docker containers are down
sleep 2

# Prune dangling volumes
docker volume prune -f > /dev/null

# Prune dangling images
docker image prune -f -a > /dev/null