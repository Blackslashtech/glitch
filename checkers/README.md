# Services - Work in Progress

Place each checker in its own directory, with the name of the directory equal to the name of the service which the checker checks.  Only checkers matching names in the list of services in the top level `.env` file will be deployed.

Each checker must have a `deploy.sh`, `docker-compose.yaml`, or `Dockerfile` which starts the checker (searched for in that order)

Templates for checker interfaces are in [`.templates`](.templates).  Some tweaking may be required depending on the checker implementation, but ideally most are plug-and-play.

To use a template, copy the .docker directory from the template into the checker directory, alongside the checker source code.  The checker will be run inside a docker container defined by `Dockerfile`, using an XML-RPC wrapper handled in `checkeradapter.py`, and called periodically by the ticker.