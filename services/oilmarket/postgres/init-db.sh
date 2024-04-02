#!/bin/sh

psql --username oilmarket --dbname oilmarket  <<-EOSQL
        CREATE TABLE IF NOT EXISTS buyers (
                id SERIAL PRIMARY KEY,
                name VARCHAR UNIQUE NOT NULL,
                flag VARCHAR NOT NULL,
                api_key uuid UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS attesters (
                id SERIAL PRIMARY KEY,
                name VARCHAR UNIQUE NOT NULL,
                api_key uuid UNIQUE NOT NULL,
                key TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS buyer_attester (
                buyer_id INTEGER REFERENCES buyers(id),
                attester_id  INTEGER REFERENCES attesters(id),
                PRIMARY KEY(buyer_id, attester_id)
        );

        CREATE TABLE IF NOT EXISTS sellers (
                id SERIAL PRIMARY KEY,
                name VARCHAR UNIQUE NOT NULL,
                api_key uuid UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS barrels (
                id SERIAL PRIMARY KEY,
                seller_id INTEGER REFERENCES sellers(id)
        );

EOSQL

