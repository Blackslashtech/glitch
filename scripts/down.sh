#!/bin/bash

# Check if cwd is range
if [[ ! -d "./checkers" && -d "./services" && -d "./.docker" ]]; then
    echo "Please run this script from the range directory (i.e. sh scripts/down.sh))"
    exit 1
fi

source .env set

export VPN_COUNT=$(expr $TEAM_COUNT \* $VPN_PER_TEAM)
export SERVICE_LIST=$(echo $SERVICES | tr ',' '\n')

# Prep ipv4 or ipv6 for range services
if [ "$IPV6_ENABLED" = "true" ]; then
    export GAME_SUBNET="fd10:100::/31"
    export INFRA_SUBNET="fd10:102::/32"
    export CHECKER_SUBNET="fd10:103::/32"

    export VPN_GAME_IPV4=""
    export VPN_GAME_IPV6="fd10:101::1:2"
    export VPN_CHECKER_IPV4=""
    export VPN_CHECKER_IPV6="fd10:103::1:2"

    export API_GAME_IPV4=""
    export API_GAME_IPV6="fd10:101::1:3"
    export API_INFRA_IPV4=""
    export API_INFRA_IPV6="fd10:102::1:3"

    export REGISTRY_GAME_IPV4=""
    export REGISTRY_GAME_IPV6="fd10:101::1:4"
    export REGISTRY_CHECKER_IPV4=""
    export REGISTRY_CHECKER_IPV6="fd10:103::1:4"

    export RANGEMASTER_GAME_IPV4=""
    export RANGEMASTER_GAME_IPV6="fd10:101::1:6"
    export RANGEMASTER_INFRA_IPV4=""
    export RANGEMASTER_INFRA_IPV6="fd10:102::1:6"
    export RANGEMASTER_CHECKER_IPV4=""
    export RANGEMASTER_CHECKER_IPV6="fd10:103::1:6"

    export TICKER_INFRA_IPV4=""
    export TICKER_INFRA_IPV6="fd10:102::1:5"
    export TICKER_CHECKER_IPV4=""
    export TICKER_CHECKER_IPV6="fd10:103::1:5"

    export DB_INFRA_IPV4=""
    export DB_INFRA_IPV6="fd10:102::1:4"
else
    export GAME_SUBNET="10.100.0.0/15"
    export INFRA_SUBNET="10.102.0.0/16"
    export CHECKER_SUBNET="10.103.0.0/16"

    export VPN_GAME_IPV4="10.101.1.2"
    export VPN_GAME_IPV6=""
    export VPN_CHECKER_IPV4="10.103.1.2"
    export VPN_CHECKER_IPV6=""

    export API_GAME_IPV4="10.101.1.3"
    export API_GAME_IPV6=""
    export API_INFRA_IPV4="10.102.1.3"
    export API_INFRA_IPV6=""

    export REGISTRY_GAME_IPV4="10.101.1.4"
    export REGISTRY_GAME_IPV6=""
    export REGISTRY_CHECKER_IPV4="10.103.1.4"
    export REGISTRY_CHECKER_IPV6=""

    export RANGEMASTER_GAME_IPV4="10.101.1.6"
    export RANGEMASTER_GAME_IPV6=""
    export RANGEMASTER_INFRA_IPV4="10.102.1.6"
    export RANGEMASTER_INFRA_IPV6=""
    export RANGEMASTER_CHECKER_IPV4="10.103.1.6"
    export RANGEMASTER_CHECKER_IPV6=""

    export TICKER_INFRA_IPV4="10.102.1.5"
    export TICKER_INFRA_IPV6=""
    export TICKER_CHECKER_IPV4="10.103.1.5"
    export ICKER_CHECKER_IPV6=""

    export DB_INFRA_IPV4="10.102.1.4"
    export DB_INFRA_IPV6=""
fi

source .env set

export API_KEY
# Set default values
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

export GAME_SUBNET
export INFRA_SUBNET
export CHECKER_SUBNET
export VPN_GAME_IPV6
export VPN_CHECKER_IPV6
export API_GAME_IPV6
export API_INFRA_IPV6
export REGISTRY_GAME_IPV6
export REGISTRY_CHECKER_IPV6
export RANGEMASTER_GAME_IPV6
export RANGEMASTER_INFRA_IPV6
export RANGEMASTER_CHECKER_IPV6
export TICKER_INFRA_IPV6
export TICKER_CHECKER_IPV6
export DB_INFRA_IPV6
export VPN_GAME_IPV4
export VPN_CHECKER_IPV4
export API_GAME_IPV4
export API_INFRA_IPV4
export REGISTRY_GAME_IPV4
export REGISTRY_CHECKER_IPV4
export RANGEMASTER_GAME_IPV4
export RANGEMASTER_INFRA_IPV4
export RANGEMASTER_CHECKER_IPV4
export TICKER_INFRA_IPV4
export TICKER_CHECKER_IPV4
export DB_INFRA_IPV4

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

# Loop from 1 to $TEAM_COUNT
for TEAM_ID in $(seq 2 $(expr $TEAM_COUNT + 1)); do
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
API_KEY="" PEERS="" TEAM_TOKENS="" docker-compose down -t 2 > /dev/null