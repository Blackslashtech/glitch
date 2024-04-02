#!/bin/bash

# Check if cwd is range
if [[ ! -d "./checkers" && -d "./services" && -d "./.docker" ]]; then
  echo "Please run this script from the range directory (i.e. sh scripts/up.sh))"
  exit 1
fi

# Set default values
TEAM_COUNT=2
VPN_PER_TEAM=1
FLAG_LIFETIME=5
SERVER_URL="localhost"
VPN_PORT=51820
API_PORT=8000
VPN_DNS="8.8.8.8"
SERVICES=""
TICK_SECONDS=60
# Use date if on unix, use gdate if on mac
if [[ "$(uname)" == "Darwin" ]]; then
  START_TIME=$(gdate -u +"%Y-%m-%dT%H:%M:%SZ")
  END_TIME=$(gdate -u +"%Y-%m-%dT%H:%M:%SZ" -d "+$(expr $TICK_SECONDS \* 100) seconds")
else
  START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ" -d "+$(expr $TICK_SECONDS \* 100) seconds")
fi
MEM_LIMIT="1G"
CPU_LIMIT="1"

source .env set

SERVICE_LIST=$(echo $SERVICES | tr ',' '\n')

SERVICE_ID=1
for SERVICE_NAME in $SERVICE_LIST; do
  dir="./checkers/$SERVICE_NAME/"
  # If the file is a directory
  if [ -d "$dir" ]; then
    HOSTNAME=$(echo "checker-$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
    IP=$(echo "10.103.2.$SERVICE_ID" | tr '[:upper:]' '[:lower:]')
    echo "Restarting $HOSTNAME ..."
    docker stop $HOSTNAME >/dev/null 2>&1
    docker rm -f $HOSTNAME >/dev/null 2>&1
    docker rmi -f ${HOSTNAME}_checker >/dev/null 2>&1
    IP=$IP GATEWAY="10.103.1.1" HOSTNAME=$HOSTNAME SERVICE_ID=$SERVICE_ID SERVICE_NAME=$SERVICE_NAME TICK_SECONDS=$TICK_SECONDS docker compose -f ./checkers/docker-compose.yaml --project-name $HOSTNAME up -d >/dev/null
    SERVICE_ID=$(expr $SERVICE_ID + 1)
  fi
done

docker compose restart ticker >/dev/null
