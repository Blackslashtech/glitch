# Services

Place each service in its own directory, with the name of the directory equal to the name of the service.

Each service must have a `docker-compose.yml` file that defines the service, or a `deploy.sh` which starts the service. If both exist, only the `deploy.sh` script will be run.

Do not touch [`docker-compose.yml`](../docker-compose.yml) or [`.docker`](.docker). These are used to generate the host containers for each service.

Do not place anything in this directory that is not a directory containing a service - it will break the service generation.
