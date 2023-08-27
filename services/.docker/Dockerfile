FROM docker:latest

# Install ssh server
RUN apk add openssh-server

# Generate host keys
RUN ssh-keygen -A

# Install curl
RUN apk add curl

# Append local docker registry to daemon.json
RUN mkdir -p /etc/docker
RUN echo '{ "insecure-registries":["registry:5000"] }' >> /etc/docker/daemon.json