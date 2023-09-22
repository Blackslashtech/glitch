FROM docker:latest

# Install ssh server
RUN apk add openssh-server

# Generate host keys
RUN ssh-keygen -A

# Install curl
RUN apk add curl

ARG SERVICE_NAME

# Copy service directory
COPY ./$SERVICE_NAME /service

# Copy entrypoint script
COPY ./.docker/entrypoint.sh /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]