#!/bin/sh

# Check if script is run as root
if [ "$(id -u)" != "0" ]; then
    echo "Please run this script as root (i.e. sudo sh scripts/install.sh)"
    exit 1
fi


# Install docker
curl -fsSL https://get.docker.com | sh

echo -e '{ "experimental": true, "ip6tables": true, "dns" : [ "8.8.8.8" , "8.8.4.4" ] }' >/etc/docker/daemon.json

systemctl enable docker
systemctl restart docker

# Install zip
sudo apt-get install -y zip

# Copy sample.env to .env if it doesn't already exist
cp -n sample.env .env
