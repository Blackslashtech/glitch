FROM php:8.3-cli

RUN apt update && apt install -y git libpng-dev libzip-dev
RUN docker-php-ext-install gd zip opcache sockets

WORKDIR /app

ENV COMPOSER_ALLOW_SUPERUSER=1
COPY --from=composer:2.3 /usr/bin/composer /usr/bin/composer
COPY backend/composer.* .
RUN composer config --no-plugins allow-plugins.spiral/composer-publish-plugin false && \
    composer install --optimize-autoloader --no-dev

COPY --from=spiralscout/roadrunner:2023.3.10 /usr/bin/rr /app

COPY backend/ .
COPY conf/rr.yml rr.yaml
COPY conf/backend.env .env
COPY backend-entry.sh ./entry.sh

CMD ["./entry.sh"]