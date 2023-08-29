#!/bin/sh

# Create randomized api key
API_KEY="$(openssl rand -hex 16)"
TEAM_COUNT=2
VPN_PER_TEAM=1
VPN_SERVER_URL="localhost"

source .env set

VPN_COUNT=$(expr $TEAM_COUNT \* $VPN_PER_TEAM)

echo "API KEY: $API_KEY"

echo "Starting range services..."
API_KEY=$API_KEY TEAM_COUNT=$TEAM_COUNT PEERS=$VPN_COUNT SERVERURL=$VPN_SERVER_URL docker-compose up -d --build --force-recreate > /dev/null

# Loop from 1 to $TEAM_COUNT
for TEAM_ID in $(seq 1 $TEAM_COUNT); do
  # Loop over every directory in /services
    # Create a counter for service IDs starting at 1
    SERVICE_ID=1
    for dir in ./services/*; do
        # Check if the file is named .docker or README.md
        if [ "$(basename "$dir")" = ".docker" ] || [ "$(basename "$dir")" = "README.md" ]; then
            # If it is, skip it
            continue
        fi
        # If the file is a directory
        if [ -d "$dir" ]; then
            # Start docker-compose in the /services directory with a volume mount of the directory
            # set the service environment variable to the directory name
            # Isolate the end of the directory name with the basename command
            SERVICE_NAME="$(basename "$dir")"
            # Generate a random root password
            ROOT_PASSWORD="$(openssl rand -hex 16)"
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
            IP=$(echo "10.100.$TEAM_ID.$SERVICE_ID" | tr '[:upper:]' '[:lower:]')
            echo "Starting $HOSTNAME, root password is $ROOT_PASSWORD ..."
            API_KEY=$API_KEY IP=$IP HOSTNAME=$HOSTNAME TEAM_ID=$TEAM_ID SERVICE_ID=$SERVICE_ID SERVICE_NAME=$SERVICE_NAME ROOT_PASSWORD=$ROOT_PASSWORD docker-compose -f ./services/docker-compose.yaml --project-name $HOSTNAME up -d --build > /dev/null
            SERVICE_ID=$(expr $SERVICE_ID + 1)
        fi
    done
done