MINIO_USER=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 14 ; echo '')
MINIO_PASSWORD=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 28 ; echo '')

MINIO_APIKEY=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 14 ; echo '')
MINIO_APIKEY_SECRET=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 28 ; echo '')

echo "MINIO_ROOT_USER=$MINIO_USER" > .env
echo "MINIO_ROOT_PASSWORD=$MINIO_PASSWORD" >> .env

echo "BUCKET_KEY=$MINIO_APIKEY" >> .env
echo "ACCESS_KEY=$MINIO_APIKEY" >> .env

echo "BUCKET_SECRET=$MINIO_APIKEY_SECRET" >> .env
echo "ACCESS_KEY_SECRET=$MINIO_APIKEY_SECRET" >> .env

docker compose up -d --build