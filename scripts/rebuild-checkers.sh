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


export GAME_SUBNET_IPV6="fd10::100:0:0/31"
export GAME_SUBNET_IPV4="10.100.0.0/15"
export INFRA_SUBNET_IPV6="fd10::102:0:0/96"
export INFRA_SUBNET_IPV4="10.102.0.0/16"
export CHECKER_SUBNET_IPV6="fd10::103:0:0/96"
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

export SERVICE_ID=2
for SERVICE_NAME in $SERVICE_LIST; do
    dir="./checkers/$SERVICE_NAME/"
    # If the file is a directory
    if [ -d "$dir" ]; then
        export HOSTNAME=$(echo "checker-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
        export IPV4="10.103.2.$SERVICE_ID"
        export IPV6="fd10::103:2:$SERVICE_ID"
        export SERVICE_NAME
        echo "Restarting $HOSTNAME ..."
        docker stop $HOSTNAME > /dev/null 2>&1
        docker rm -f $HOSTNAME > /dev/null 2>&1
        docker rmi -f ${HOSTNAME}_checker > /dev/null 2>&1
        docker-compose --log-level ERROR -f ./checkers/docker-compose.yaml --project-name $HOSTNAME up -d > /dev/null
        export SERVICE_ID=$(expr $SERVICE_ID + 1)
    fi
done

docker-compose stop ticker > /dev/null
docker-compose rm -f ticker > /dev/null
docker rmi -f ticker > /dev/null
docker-compose build ticker > /dev/null
docker-compose start ticker > /dev/null