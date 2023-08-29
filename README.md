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

## Connecting to the Range
Credentials for all services are printed to STDOUT during the range startup.

For local testing, you can get a shell inside the range environment with the command `docker exec -it user sh`.

As long as the `VPN_SERVER_URL` is properly set and port forwarding is enabled for UDP 51820, you can connect to the range from anywhere with the Wireguard client.
Wireguard configs are stored in the [`.docker/vpn`](..docker/vpn) directory, or can be downloaded from the API at `http://api/vpn/<team_id>/wg<vpn_id>.conf`. (i.e. `http://api/vpn/1/wg1.conf`)

> [!NOTE]
> Team IDs, Service IDs, and VPN IDs are all 1-indexed.  This is to avoid subnetting/IP confusion.

# Network

The range network is defined in [`docker-compose.yaml`](docker-compose.yaml):
- Range network: `10.100.0.0/15`
  - Infrastructure subnet: `10.101.0.0/16`
    - VPN Server (NAT source for all traffic): `10.101.0.1` (hostname `vpn`)
    - API: `10.101.0.2` (hostname `api`)
    - (WIP) Checker: `10.101.0.3` (hostname `checker`)
    - (WIP) DB: `10.101.0.4` (hostname `db`)
    - (WIP) Frontend: `10.101.0.5` (hostname `api`)
    - Docker Registry: `10.101.0.6` (hostname `registry`)
    - Rangemaster troubleshooting container: `10.101.0.7` (hostname `rangemaster`)
  - Team subnet: `10.100.<team_id>.0/24`
    - Service host: `10.100.<team_id>.<service_id>` (hostname `team<team_id>-<service_name>` - i.e. `team1-web`)


# License

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg