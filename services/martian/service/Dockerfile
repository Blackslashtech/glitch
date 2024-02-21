FROM ubuntu:latest

RUN apt-get update && apt-get upgrade -yyq
RUN apt-get install socat libstdc++6 build-essential -yyq

ADD ./entrypoint.sh /entrypoint.sh
ADD ./martian /martian
ADD ./items.txt /items.txt
ADD ./libstdc++.so.6 /usr/lib/x86_64-linux-gnu/libstdc++.so.6

WORKDIR /

CMD ["/entrypoint.sh"]

