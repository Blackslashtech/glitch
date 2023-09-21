#!/bin/bash

# Check if cwd is range
if [[ ! -d "./checkers" && -d "./services" && -d "./.docker" ]]; then
    echo "Please run this script from the range directory (i.e. sh scripts/up.sh))"
    exit 1
fi

# Create randomized api key
API_KEY="$(openssl rand -hex 16)"
# Set default values
TEAM_COUNT=2
VPN_PER_TEAM=1
FLAG_LIFETIME=5
SERVER_URL="localhost"
VPN_PORT=51820
API_PORT=8000
VPN_DNS="8.8.8.8"
IPV6_ENABLED="false"
SERVICES=""
TICK_SECONDS=60
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
END_TIME=$(gdate -u +"%Y-%m-%dT%H:%M:%SZ" -d "+$(expr $TICK_SECONDS \* 100) seconds")
MEM_LIMIT="1G"
CPU_LIMIT="1"

source .env set

VPN_COUNT=$(expr $TEAM_COUNT \* $VPN_PER_TEAM)
SERVICE_LIST=$(echo $SERVICES | tr ',' '\n')

# Create empty teamdata directory
rm -rf ./.docker/api/teamdata
mkdir ./.docker/api/teamdata
echo "Team data download links (distribute one link to each team):" > ./teamdata.txt

# Generate team tokens
TEAM_TOKENS=""
for TEAM_ID in $(seq 1 $TEAM_COUNT); do
    # Generate team token
    TEAM_TOKEN="$(openssl rand -hex 16)"
    TEAM_TOKENS="$TEAM_TOKENS,$TEAM_TOKEN"
    # Create teamdata directory and credentials file
    mkdir ./.docker/api/teamdata/$TEAM_TOKEN
    mkdir ./.docker/api/teamdata/$TEAM_TOKEN/vpn
    echo -e "Team $TEAM_ID Range Credentials:\n" > ./.docker/api/teamdata/$TEAM_TOKEN/creds.txt
    echo -e "API Token: $TEAM_TOKEN\n" >> ./.docker/api/teamdata/$TEAM_TOKEN/creds.txt
    echo "Team $TEAM_ID: http://$SERVER_URL:$API_PORT/teamdata/$TEAM_TOKEN/rangedata.zip" >> ./teamdata.txt
done
# Strip leading comma
TEAM_TOKENS="${TEAM_TOKENS:1}"

echo "Starting range services..."
API_KEY=$API_KEY TEAM_COUNT=$TEAM_COUNT PEERS=$VPN_COUNT FLAG_LIFETIME=$FLAG_LIFETIME TICK_SECONDS=$TICK_SECONDS SERVERURL=$SERVER_URL API_PORT=$API_PORT VPN_PORT=$VPN_PORT VPN_DNS=$VPN_DNS IPV6_ENABLED=$IPV6_ENABLED TEAM_TOKENS=$TEAM_TOKENS docker-compose up -d --force-recreate > /dev/null

echo "Waiting 5 seconds for VPN to start..."
sleep 5

# Loop from 1 to $TEAM_COUNT - 1
for TEAM_ID in $(seq 1 $TEAM_COUNT); do
    echo "Starting team $TEAM_ID..."
    TEAM_TOKEN="$(echo $TEAM_TOKENS | cut -d',' -f$TEAM_ID)"
    # Copy vpn files
    for VPN_ID in $(seq 1 $VPN_PER_TEAM); do
        VPN_NAME="peer$(expr $VPN_ID + $(expr $(expr $TEAM_ID - 1) \* $VPN_PER_TEAM))"
        cp ./.docker/vpn/$VPN_NAME/$VPN_NAME.conf ./.docker/api/teamdata/$TEAM_TOKEN/vpn/wg$VPN_ID.conf
    done
    # Create a counter for service IDs starting at 1
    SERVICE_ID=1
    for SERVICE_NAME in $SERVICE_LIST; do
        dir="./services/$SERVICE/"
        # If the file is a directory
        if [ -d "$dir" ]; then
            # Start docker-compose in the /services directory with a volume mount of the directory
            # Generate a random root password
            ROOT_PASSWORD="$(openssl rand -hex 16)"
            HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
            # check if ipv6 is enabled
            if [ "$IPV6_ENABLED" = "true" ]; then
                IP=""
                IP6="fd00:1000:$TEAM_ID::$SERVICE_ID"
            else
                IP="10.100.$TEAM_ID.$SERVICE_ID"
                IP6=""
            fi
            # Write creds to creds.txt
            echo "$IP$IP6 ($SERVICE_NAME) - root : $ROOT_PASSWORD" >> ./.docker/api/teamdata/$TEAM_TOKEN/creds.txt
            IP=$IP IP6=$IP6 HOSTNAME=$HOSTNAME TEAM_ID=$TEAM_ID SERVICE_ID=$SERVICE_ID SERVICE_NAME=$SERVICE_NAME ROOT_PASSWORD=$ROOT_PASSWORD CPU_LIMIT=$CPU_LIMIT MEM_LIMIT=$MEM_LIMIT docker-compose -f ./services/docker-compose.yaml --project-name $HOSTNAME up -d > /dev/null
            SERVICE_ID=$(expr $SERVICE_ID + 1)
        fi
    done
    # Zip teamdata directory
    pushd ./.docker/api/teamdata > /dev/null
    zip -r $TEAM_TOKEN.zip $TEAM_TOKEN > /dev/null
    popd > /dev/null
done

SERVICE_ID=1
for SERVICE_NAME in $SERVICE_LIST; do
    dir="./checkers/$SERVICE_NAME/"
    # If the file is a directory
    if [ -d "$dir" ]; then
        HOSTNAME=$(echo "checker-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
        # check if ipv6 is enabled
        if [ "$IPV6_ENABLED" = "true" ]; then
            IP=""
            IP6="fd00:1003:2::$SERVICE_ID"
            GATEWAY="fd00:1003:1::100"
        else
            IP="10.103.2.$SERVICE_ID"
            IP6=""
            GATEWAY="10.103.1.100"
        fi
        echo "Starting $HOSTNAME ..."
        IP=$IP IP6=$IP6 GATEWAY=$GATEWAY HOSTNAME=$HOSTNAME SERVICE_ID=$SERVICE_ID SERVICE_NAME=$SERVICE_NAME TICK_SECONDS=$TICK_SECONDS docker-compose -f ./checkers/docker-compose.yaml --project-name $HOSTNAME up -d > /dev/null
        SERVICE_ID=$(expr $SERVICE_ID + 1)
    fi
done

# Print teamdata download links
echo "*******************************************************"
echo -e "\nAdmin API KEY: $API_KEY\n"
cat ./teamdata.txt
echo -e "\n(Team data stored in ./teamdata.txt)"