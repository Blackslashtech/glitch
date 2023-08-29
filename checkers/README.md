# Services - Work in Progress

Place each checker in its own directory, with the name of the directory equal to the name of the service which the checker checks.  These names must match the names of the services in the [`services`](..services) directory.

Each checker must have a `deploy.sh`, `docker-compose.yaml`, or `Dockerfile` which starts the checker (searched for in that order)

Do not touch [`docker-compose.yml`](../docker-compose.yml) or [`.docker`](.docker).  These are used to generate the host containers for each service.

Do not place anything in this directory that is not a directory containing a checker - it will break the checker generation.