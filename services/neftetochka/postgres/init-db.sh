#!/bin/sh

psql --username app --dbname app <<-EOSQL
    CREATE TABLE IF NOT EXISTS users (
        id          VARCHAR(32) PRIMARY KEY,
        username    VARCHAR(100) NOT NULL,
        password    VARCHAR(100) NOT NULL,
        balance     INTEGER
    );

    CREATE TABLE IF NOT EXISTS stations (
        port        INTEGER PRIMARY KEY,
        x           INTEGER,
        y           INTEGER
    );

    CREATE TABLE IF NOT EXISTS links (
        port1   INTEGER REFERENCES stations(port),
        port2   INTEGER REFERENCES stations(port),
        CONSTRAINT port1_port2_pkey PRIMARY KEY (port1, port2)
    );

    CREATE TABLE IF NOT EXISTS oil (
        id          VARCHAR(32) PRIMARY KEY,
        sender_id   VARCHAR(32) REFERENCES users(id),
        receiver_id VARCHAR(32) REFERENCES users(id),
        message     VARCHAR(100),
        station_id  INTEGER REFERENCES stations(port),
        time        BIGINT
    );

    INSERT INTO stations (port, x, y) values
        (16001,  1,  2),
        (16002,  3,  5),
        (16003, 15,  2),
        (16005,  5, 13),
        (16006, 15, 14),
        (16007,  3,  9),
        (16008,  9,  3),
        (16009, 20,  4),
        (16011, 11, 20),
        (16012,  8, 17),
        (16013,  2, 19),
        (16014, 10, 11),
        (16015, 19, 19),
        (16016, 13,  4),
        (16017,  6,  1),
        (16018,  0, 12),
        (16019,  7,  8),
        (16020, 18,  1),
        (16021,  3, 16),
        (16022, 13, 16),
        (16024, 16,  7),
        (16023, 14,  9),
        (16010, 19, 10),
        (16004, 10,  5),
        (16025, 17, 11),
        (16026, 11, 17),
        (16027, 16, 18),
        (16028, 17, 16),
        (16029,  6,  5),
        (16030,  7, 11),
        (16031, 14, 12),
        (16032, 17,  4),
        (16033, 12, 14),
        (16034,  9, 15);

    INSERT INTO links (port1, port2) values
        (16001, 16017),
        (16001, 16002),
        (16017, 16008),
        (16016, 16003),
        (16002, 16007),
        (16018, 16007),
        (16019, 16004),
        (16020, 16003),
        (16020, 16009),
        (16019, 16007),
        (16013, 16021),
        (16005, 16021),
        (16005, 16012),
        (16021, 16012),
        (16008, 16004),
        (16008, 16016),
        (16011, 16026),
        (16022, 16026),
        (16022, 16006),
        (16024, 16023),
        (16015, 16027),
        (16028, 16027),
        (16028, 16006),
        (16025, 16010),
        (16025, 16023),
        (16012, 16026),
        (16002, 16029),
        (16008, 16029),
        (16014, 16019),
        (16014, 16030),
        (16005, 16030),
        (16006, 16031),
        (16025, 16031),
        (16009, 16032),
        (16024, 16032),
        (16012, 16034),
        (16033, 16022),
        (16033, 16031);

EOSQL