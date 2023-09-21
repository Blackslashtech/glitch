FROM linuxserver/wireguard:latest


# Install nppd
RUN apt update
RUN apt install -y ndppd

# Enable ipv4 forwarding
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
# Enable ipv6 forwarding
RUN echo "net.ipv6.conf.all.accept_ra=2" >> /etc/sysctl.conf
RUN echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
RUN echo "net.ipv6.conf.all.proxy_ndp=1" >> /etc/sysctl.conf
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf


# Set up nppd
COPY ./nppd.conf /etc/ndppd.conf
RUN chmod 777 /etc/ndppd.conf
RUN systemctl enable ndppd