/opt/bitnami/scripts/minio/run.sh &

sleep 5
mc config host add myminio http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
mc mb myminio/bucket
mc anonymous set-json /opt/bucket_policy.json myminio/bucket
mc admin user svcacct add --access-key "$ACCESS_KEY" --secret-key "$ACCESS_KEY_SECRET" --policy /opt/accesskey_policy.json myminio $MINIO_ROOT_USER

wait