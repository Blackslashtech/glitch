FROM linuxserver/wireguard:latest


# Install nppd
RUN apt update
RUN apt install -y ndppd


RUN apk --no-cache add --virtual .build-dependencies make g++ linux-headers patch wget ca-certificates \
	&& mkdir -p /usr/src \
	&& wget -qO- https://github.com/DanielAdolfsson/ndppd/archive/master.tar.gz | tar -xzC /usr/src \
	&& cd /usr/src/ndppd-master \
	&& make && make install \
	&& cd / && rm -rf /usr/src/ndppd-${NDPPD_VERSION} \
	&& apk del .build-dependencies

RUN apk --no-cache add libc6-compat libgcc libstdc++

# Enable forwarding
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
RUN echo "net.ipv6.conf.all.accept_ra=2" >> /etc/sysctl.conf
RUN echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
RUN echo "net.ipv6.conf.all.proxy_ndp=1" >> /etc/sysctl.conf
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf


# Set up nppd
COPY ./nppd.conf /etc/ndppd.conf
RUN chmod 777 /etc/ndppd.conf
RUN systemctl enable ndppd