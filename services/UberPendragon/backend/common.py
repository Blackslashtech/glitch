import psycopg2
import os

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

def get_connection():
    return psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD)