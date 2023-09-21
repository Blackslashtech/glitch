#!/bin/bash

# Check if cwd is range
if [[ ! -d "./checkers" && -d "./services" && -d "./.docker" ]]; then
    echo "Please run this script from the range directory (i.e. sh scripts/clear.sh))"
    exit 1
fi

TEAM_TOKENS=""

source .env set

echo "Stopping all containers..."
bash scripts/down.sh

# Wait for all the docker stop commands to finish
sleep 5

echo "Deleting all containers..."

docker rm -f range-api > /dev/null
docker rm -f range-ticker > /dev/null
docker rmi -f range_api > /dev/null
docker rmi -f range_ticker > /dev/null

SERVICE_LIST=$(echo $SERVICES | tr ',' '\n')

# Loop from 1 to $TEAM_COUNT
for TEAM_ID in $(seq 2 $(expr $TEAM_COUNT + 1)); do
    # Loop over every service
    echo "Deleting team $TEAM_ID..."
    for SERVICE_NAME in $SERVICE_LIST; do
        dir="./services/$SERVICE_NAME"
        # If the file is a directory
        if [ -d "$dir" ]; then
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
            echo "Deleting $HOSTNAME..."
            docker rm -f $HOSTNAME > /dev/null 2>&1
            docker rmi -f ${HOSTNAME}_service > /dev/null 2>&1
        fi
    done
done

# Loop over every checker
for SERVICE_NAME in $SERVICE_LIST; do
    dir="./checkers/$SERVICE_NAME"
    # If the file is a directory
    if [ -d "$dir" ]; then
        echo "Deleting $SERVICE_NAME checker..."
        HOSTNAME=$(echo "checker-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
        echo "Deleting $HOSTNAME..."
        docker rm -f $HOSTNAME > /dev/null 2>&1
        docker rmi -f ${HOSTNAME}_checker > /dev/null 2>&1
    fi
done

# Delete all the vpn files
rm -rf ./.docker/vpn/* > /dev/null

# Delete all the teamdata files
rm ./teamdata.txt
rm -rf ./.docker/api/teamdata/* > /dev/null

# Prune docker networks
docker network prune -f > /dev/null