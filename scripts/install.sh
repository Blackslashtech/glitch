#!/bin/sh

# Check if script is run as root
if [ "$(id -u)" != "0" ]; then
    echo "Please run this script as root (i.e. sudo sh scripts/install.sh)"
    exit 1
fi

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" |
    sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update

# Install docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo -e '{ "experimental": true, "ip6tables": true, "dns" : [ "8.8.8.8" , "8.8.4.4" ] }' >/etc/docker/daemon.json

systemctl enable docker
systemctl restart docker

# Install zip
sudo apt-get install -y zip

# Copy sample.env to .env if it doesn't already exist
cp -n sample.env .env
