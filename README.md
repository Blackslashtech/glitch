# Range

A general purpose attack-defense range for zero-config deployment

## Usage

1. Drop each service into a folder in the [`./services`](services) directory.  Each service should have a `docker-compose.yml` file that defines the service.
2. Modify the [`.env`](.env) as desired for all configuration options.
3. Run `sh up.sh` to start the range.

To stop the range, run `sh down.sh`.

**Warning** `clean.sh` runs a docker image and volume prune.  This can have unintended consequences if you have other docker containers on the host system.  Use with caution.


# License

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg