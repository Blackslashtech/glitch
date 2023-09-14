#!/bin/bash

# Check if cwd is range
if [[ ! -d "./checkers" && -d "./services" && -d "./.docker" ]]; then
    echo "Please run this script from the range directory (i.e. sh scripts/rangemaster.sh))"
    exit 1
fi

docker exec -it rangemaster /bin/bash