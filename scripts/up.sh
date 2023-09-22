#!/bin/bash

# Check if cwd is range
if [[ ! -d "./checkers" && -d "./services" && -d "./.docker" ]]; then
    echo "Please run this script from the range directory (i.e. sh scripts/up.sh))"
    exit 1
fi

# Create randomized api key
export API_KEY="$(openssl rand -hex 16)"
# Set default values
export TEAM_COUNT=2
export VPN_PER_TEAM=1
export FLAG_LIFETIME=5
export SERVER_URL="localhost"
export VPN_PORT=51820
export API_PORT=8000
export VPN_DNS="8.8.8.8"
export IPV6_ENABLED="false"
export SERVICES=""
export TICK_SECONDS=60
export START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ" -d "+$(expr $TICK_SECONDS \* 100) seconds")
export MEM_LIMIT="1G"
export CPU_LIMIT="1"


export GAME_SUBNET_IPV6="fd10::100:/95"
export GAME_SUBNET_IPV4="10.100.0.0/15"
export INFRA_SUBNET_IPV6="fd10::102:/96"
export INFRA_SUBNET_IPV4="10.102.0.0/16"
export CHECKER_SUBNET_IPV6="fd10::103:/96"
export CHECKER_SUBNET_IPV4="10.103.0.0/16"

export VPN_GAME_IPV4="10.101.1.2"
export VPN_GAME_IPV6="fd10::101:1:2"
export VPN_CHECKER_IPV4="10.103.1.2"
export VPN_CHECKER_IPV6="fd10::103:1:2"

export API_GAME_IPV4="10.101.1.3"
export API_GAME_IPV6="fd10::101:1:3"
export API_INFRA_IPV4="10.102.1.3"
export API_INFRA_IPV6="fd10::102:1:3"

export REGISTRY_GAME_IPV4="10.101.1.4"
export REGISTRY_GAME_IPV6="fd10::101:1:4"
export REGISTRY_CHECKER_IPV4="10.103.1.4"
export REGISTRY_CHECKER_IPV6="fd10::103:1:4"

export RANGEMASTER_GAME_IPV4="10.101.1.6"
export RANGEMASTER_GAME_IPV6="fd10::101:1:6"
export RANGEMASTER_INFRA_IPV4="10.102.1.6"
export RANGEMASTER_INFRA_IPV6="fd10::102:1:6"
export RANGEMASTER_CHECKER_IPV4="10.103.1.6"
export RANGEMASTER_CHECKER_IPV6="fd10::103:1:6"

export TICKER_INFRA_IPV4="10.102.1.5"
export TICKER_INFRA_IPV6="fd10::102:1:5"
export TICKER_CHECKER_IPV4="10.103.1.5"
export TICKER_CHECKER_IPV6="fd10::103:1:5"

export DB_INFRA_IPV4="10.102.1.4"
export DB_INFRA_IPV6="fd10::102:1:4"



source .env set

export VPN_COUNT=$(expr $TEAM_COUNT \* $VPN_PER_TEAM)
export SERVICE_LIST=$(echo $SERVICES | tr ',' '\n')

export API_KEY
export TEAM_COUNT
export VPN_PER_TEAM
export FLAG_LIFETIME
export SERVER_URL
export VPN_PORT
export API_PORT
export VPN_DNS
export IPV6_ENABLED
export SERVICES
export TICK_SECONDS
export START_TIME
export END_TIME
export MEM_LIMIT
export CPU_LIMIT

export GAME_SUBNET_IPV6
export GAME_SUBNET_IPV4
export INFRA_SUBNET_IPV6
export INFRA_SUBNET_IPV4
export CHECKER_SUBNET_IPV6
export CHECKER_SUBNET_IPV4

export VPN_GAME_IPV4
export VPN_GAME_IPV6
export VPN_CHECKER_IPV4
export VPN_CHECKER_IPV6

export API_GAME_IPV4
export API_GAME_IPV6
export API_INFRA_IPV4
export API_INFRA_IPV6

export REGISTRY_GAME_IPV4
export REGISTRY_GAME_IPV6
export REGISTRY_CHECKER_IPV4
export REGISTRY_CHECKER_IPV6

export RANGEMASTER_GAME_IPV4
export RANGEMASTER_GAME_IPV6
export RANGEMASTER_INFRA_IPV4
export RANGEMASTER_INFRA_IPV6
export RANGEMASTER_CHECKER_IPV4
export RANGEMASTER_CHECKER_IPV6

export TICKER_INFRA_IPV4
export TICKER_INFRA_IPV6
export TICKER_CHECKER_IPV4
export TICKER_CHECKER_IPV6

export DB_INFRA_IPV4
export DB_INFRA_IPV6


echo "Configuration:"
echo "API_KEY: $API_KEY"
echo "TEAM_COUNT: $TEAM_COUNT"
echo "VPN_PER_TEAM: $VPN_PER_TEAM"
echo "FLAG_LIFETIME: $FLAG_LIFETIME"
echo "SERVER_URL: $SERVER_URL"
echo "VPN_PORT: $VPN_PORT"
echo "API_PORT: $API_PORT"
echo "VPN_DNS: $VPN_DNS"
echo "IPV6_ENABLED: $IPV6_ENABLED"
echo "SERVICES: $SERVICES"
echo "TICK_SECONDS: $TICK_SECONDS"
echo "START_TIME: $START_TIME"
echo "END_TIME: $END_TIME"
echo "MEM_LIMIT: $MEM_LIMIT"
echo "CPU_LIMIT: $CPU_LIMIT"

echo "GAME_SUBNET_IPV6: $GAME_SUBNET_IPV6"
echo "GAME_SUBNET_IPV4: $GAME_SUBNET_IPV4"
echo "INFRA_SUBNET_IPV6: $INFRA_SUBNET_IPV6"
echo "INFRA_SUBNET_IPV4: $INFRA_SUBNET_IPV4"
echo "CHECKER_SUBNET_IPV6: $CHECKER_SUBNET_IPV6"
echo "CHECKER_SUBNET_IPV4: $CHECKER_SUBNET_IPV4"

echo "VPN_GAME_IPV4: $VPN_GAME_IPV4"
echo "VPN_GAME_IPV6: $VPN_GAME_IPV6"
echo "VPN_CHECKER_IPV4: $VPN_CHECKER_IPV4"
echo "VPN_CHECKER_IPV6: $VPN_CHECKER_IPV6"

echo "API_GAME_IPV4: $API_GAME_IPV4"
echo "API_GAME_IPV6: $API_GAME_IPV6"
echo "API_INFRA_IPV4: $API_INFRA_IPV4"
echo "API_INFRA_IPV6: $API_INFRA_IPV6"

echo "REGISTRY_GAME_IPV4: $REGISTRY_GAME_IPV4"
echo "REGISTRY_GAME_IPV6: $REGISTRY_GAME_IPV6"
echo "REGISTRY_CHECKER_IPV4: $REGISTRY_CHECKER_IPV4"
echo "REGISTRY_CHECKER_IPV6: $REGISTRY_CHECKER_IPV6"

echo "RANGEMASTER_GAME_IPV4: $RANGEMASTER_GAME_IPV4"
echo "RANGEMASTER_GAME_IPV6: $RANGEMASTER_GAME_IPV6"
echo "RANGEMASTER_INFRA_IPV4: $RANGEMASTER_INFRA_IPV4"
echo "RANGEMASTER_INFRA_IPV6: $RANGEMASTER_INFRA_IPV6"
echo "RANGEMASTER_CHECKER_IPV4: $RANGEMASTER_CHECKER_IPV4"
echo "RANGEMASTER_CHECKER_IPV6: $RANGEMASTER_CHECKER_IPV6"

echo "TICKER_INFRA_IPV4: $TICKER_INFRA_IPV4"
echo "TICKER_INFRA_IPV6: $TICKER_INFRA_IPV6"
echo "TICKER_CHECKER_IPV4: $TICKER_CHECKER_IPV4"
echo "TICKER_CHECKER_IPV6: $TICKER_CHECKER_IPV6"

echo "DB_INFRA_IPV4: $DB_INFRA_IPV4"
echo "DB_INFRA_IPV6: $DB_INFRA_IPV6"

echo "*******************************************************"

# Create empty teamdata directory
rm -rf ./.docker/api/teamdata
mkdir ./.docker/api/teamdata
echo "Team data download links (distribute one link to each team):" > ./teamdata.txt

# Generate team tokens
export TEAM_TOKENS=""
for TEAM_ID in $(seq 2 $(expr $TEAM_COUNT + 1)); do
    # Generate team token
    export TEAM_TOKEN="$(openssl rand -hex 16)"
    export TEAM_TOKENS="$TEAM_TOKENS,$TEAM_TOKEN"
    # Create teamdata directory and credentials file
    mkdir ./.docker/api/teamdata/$TEAM_TOKEN
    mkdir ./.docker/api/teamdata/$TEAM_TOKEN/vpn
    echo -e "Team $TEAM_ID Range Credentials:\n" > ./.docker/api/teamdata/$TEAM_TOKEN/creds.txt
    echo -e "API Token: $TEAM_TOKEN\n" >> ./.docker/api/teamdata/$TEAM_TOKEN/creds.txt
    echo "Team $TEAM_ID: http://$SERVER_URL:$API_PORT/teamdata/$TEAM_TOKEN/rangedata.zip" >> ./teamdata.txt
done
# Strip leading comma
export TEAM_TOKENS="${TEAM_TOKENS:1}"

echo "Starting range services..."
docker-compose --log-level ERROR up -d --force-recreate > /dev/null

echo "Waiting 5 seconds for VPN to start..."
sleep 5

# Loop from 1 to $TEAM_COUNT - 1
for TEAM_ID in $(seq 2 $(expr $TEAM_COUNT + 1)); do
    echo "Starting team $TEAM_ID..."
    TEAM_TOKEN="$(echo $TEAM_TOKENS | cut -d',' -f$(expr $TEAM_ID - 1))"
    # Copy vpn files
    for VPN_ID in $(seq 1 $VPN_PER_TEAM); do
        VPN_NAME="peer$(expr $VPN_ID + $(expr $(expr $TEAM_ID - 2) \* $VPN_PER_TEAM))"
        cp ./.docker/vpn/config/$VPN_NAME/$VPN_NAME.conf ./.docker/api/teamdata/$TEAM_TOKEN/vpn/wg$VPN_ID.conf
    done
    # Create a counter for service IDs starting at 1
    export SERVICE_ID=2
    for SERVICE_NAME in $SERVICE_LIST; do
        dir="./services/$SERVICE/"
        # If the file is a directory
        if [ -d "$dir" ]; then
            # Start docker-compose in the /services directory with a volume mount of the directory
            # Generate a random root password
            export ROOT_PASSWORD="$(openssl rand -hex 16)"
            export HOSTNAME=$(echo "team$TEAM_ID-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
            export IPV4="10.100.$TEAM_ID.$SERVICE_ID"
            export IPV6="fd10::100:$TEAM_ID:$SERVICE_ID"
            # Write creds to creds.txt
            if [ "$IPV6_ENABLED" = "true" ]; then
                echo "$IPV6 ($SERVICE_NAME) - root : $ROOT_PASSWORD" >> ./.docker/api/teamdata/$TEAM_TOKEN/creds.txt
                echo "Starting $HOSTNAME at $IPV6..."
            else
                echo "$IPV4 ($SERVICE_NAME) - root : $ROOT_PASSWORD" >> ./.docker/api/teamdata/$TEAM_TOKEN/creds.txt
                echo "Starting $HOSTNAME at $IPV4..."
            fi
            export TEAM_ID=$TEAM_ID
            export SERVICE_NAME=$SERVICE_NAME
            docker-compose --log-level ERROR -f ./services/docker-compose.yaml --project-name $HOSTNAME up -d > /dev/null
            export SERVICE_ID=$(expr $SERVICE_ID + 1)
        fi
    done
    # Zip teamdata directory
    pushd ./.docker/api/teamdata > /dev/null
    zip -r $TEAM_TOKEN.zip $TEAM_TOKEN > /dev/null
    popd > /dev/null
done

export GATEWAY_IPV4=$VPN_CHECKER_IPV4
export GATEWAY_IPV6=$VPN_CHECKER_IPV6
export SERVICE_ID=2
for SERVICE_NAME in $SERVICE_LIST; do
    dir="./checkers/$SERVICE_NAME/"
    # If the file is a directory
    if [ -d "$dir" ]; then
        export HOSTNAME=$(echo "checker-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
        export CHECKER_IPV4="10.103.2.$SERVICE_ID"
        export CHECKER_IPV6="fd10::103:2:$SERVICE_ID"
        export GAME_IPV4="10.101.2.$SERVICE_ID"
        export GAME_IPV6="fd10::101:2:$SERVICE_ID"
        echo "Starting $HOSTNAME ..."
        docker-compose --log-level ERROR -f ./checkers/docker-compose.yaml --project-name $HOSTNAME up -d > /dev/null
        export SERVICE_ID=$(expr $SERVICE_ID + 1)
    fi
done

# Print teamdata download links
echo "*******************************************************"
echo -e "\nAdmin API KEY: $API_KEY\n"
cat ./teamdata.txt
echo -e "\n(Team data stored in ./teamdata.txt)"