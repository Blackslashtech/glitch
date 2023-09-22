FROM ubuntu:latest

# Update apt
RUN apt update

# Install docker
RUN apt install -y docker docker-compose

# Install ssh server
RUN apt install -y openssh-server

# Generate host keys
RUN ssh-keygen -A

# Install curl
RUN apt install -y curl

# Configure docker
RUN echo '\
{\
    "experimental": true,\
    "ip6tables": true,\
    "fixed-cidr-v6": "2001:db8:d0ca:d0ca::/64",\
    "default-address-pools": [\
        {"base": "172.31.0.0/16", "size": 24},\
        {"base": "2001:db8:d0ca::/49", "size": 64}\
    ],\
    "dns" : [\
        "8.8.8.8",\
        "8.8.4.4"\
    ]\
}\
' > /etc/docker/daemon.json



ARG SERVICE_NAME

# Copy service directory
COPY ./$SERVICE_NAME /service

# Copy entrypoint script
COPY ./.docker/entrypoint.sh /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]