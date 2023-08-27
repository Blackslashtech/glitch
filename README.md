# Range

A general purpose attack-defense range for zero-config deployment

## Usage

1. Drop each service into a folder in the [`./services`](services) directory.  Each service should have a `docker-compose.yml` file that defines the service.
2. Modify the [`.env`](.env) as desired for all configuration options.
3. Run `docker-compose up -d` to start the range.