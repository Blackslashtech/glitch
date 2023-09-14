#!/bin/sh

API_KEY=""
TEAM_COUNT=2
VPN_PER_TEAM=1
VPN_SERVER_URL="localhost"
TEAM_TOKENS=""

source .env set

SERVICE_LIST=$(echo $SERVICES | tr ',' '\n')

# Loop from 1 to $TEAM_COUNT
for TEAM_ID in $(seq 1 $TEAM_COUNT); do
    # Loop over every checker in /checkers
    for SERVICE_NAME in $SERVICE_LIST; do
        dir="./checkers/$SERVICE_NAME"
        # If the file is a directory
        if [ -d "$dir" ]; then
            # Generate a random root password
            HOSTNAME=$(echo "checker-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
            echo "Stopping $HOSTNAME..."
            docker stop $HOSTNAME -t 1 > /dev/null &
        fi
    done
    # Loop over every directory in /services
    for SERVICE_NAME in $SERVICE_LIST; do
        dir="./services/$SERVICE_NAME"
        # If the file is a directory
        if [ -d "$dir" ]; then
            # Generate a random root password
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
            echo "Stopping $HOSTNAME..."
            docker stop $HOSTNAME -t 1 > /dev/null &
        fi
    done
done

sleep 2

echo "Stopping range services..."
API_KEY="" PEERS="" docker-compose down -t 2 > /dev/null