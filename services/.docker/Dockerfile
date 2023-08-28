FROM docker:latest

# Install ssh server
RUN apk add openssh-server

# Generate host keys
RUN ssh-keygen -A

# Install curl
RUN apk add curl