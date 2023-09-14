#!/bin/bash

# Generate all the schemas.d.ts from openapi.json endpoints

api_file=$(mktemp).json
auth_file=$(mktemp).json

npm exec --prefix api -- ts-node api/scripts/generate_openapi.ts > $api_file
sed -i 's/"\*\/\*":/"application\/json":/g' $api_file

if [ ! -d "auth/venv" ]; then
    virtualenv auth/venv
    . auth/venv/bin/activate
    cd auth/
    pip install -r requirements.txt 
    cd src/
else
    . auth/venv/bin/activate
    cd auth/src/
fi
DRY_RUN=1 flask spec > $auth_file
cd ../../
deactivate

npm exec --prefix frontend -- openapi-typescript $auth_file -o frontend/src/_cli/_api/auth_schema.d.ts
npm exec --prefix frontend -- openapi-typescript $api_file -o frontend/src/_cli/_api/api_schema.d.ts

npm exec --prefix api -- openapi-typescript $auth_file -o api/src/auth_api/schema.d.ts

# rm $api_file $auth_file