# Range

A general purpose attack-defense range for zero-config deployment

## Usage

1. Drop each service into a folder in the [`./services`](services) directory.  Each service should have a `docker-compose.yml` file that defines the service, or a `deploy.sh` which starts the service. ([Services README](./services)).
3. Drop each checker script in the [`./checkers`](checkers) directory.  Each checker directory should be named the same as the service it corresponds to. ([Checkers README](./checkers)).
4. Modify the [`.env`](.env) as desired for all configuration options
5. Run `sh up.sh` to start the range.

To temporarily the range, run `sh down.sh`.
To delete all data associated with the range, run `sh clear.sh`.

> [!WARNING] 
> `clear.sh` runs a docker image and volume prune.  This can have unintended consequences if you have other docker containers on the host system.  Use with caution.


# License

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg