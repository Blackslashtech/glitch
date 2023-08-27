# Range

A general purpose attack-defense range for zero-config deployment

## Usage

1. Drop each service into a folder in the [`./services`](services) directory.  Each service should have a `docker-compose.yml` file that defines the service.
2. Modify the [`.env`](.env) as desired for all configuration options.
3. Run `docker-compose up -d` to start the range.


## Structure



## IPs:

* user: 192.168.128.2
* team-1: 192.168.128.6
    * ping-host-1: 172.19.0.2
    * web-host-1:  172.20.0.2
* team-2: 192.168.128.4
    * ping-host-1: 172.18.0.2
    * web-host-1:  172.19.0.2
* team-3: 192.168.128.3
    * ping-host-1: 172.18.0.2
    * web-host-1:  172.19.0.2
* team-4: 192.168.128.5
    * ping-host-1: 172.18.0.2
    * web-host-1: 172.19.0.2
* team-5: 192.168.128.7
    * ping-host-1: 172.18.0.2
    * web-host-1: 172.19.0.2
