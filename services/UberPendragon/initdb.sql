CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS places (
    addr_id UUID DEFAULT uuid_generate_v4(),
    public BOOLEAN,
    station BOOLEAN,
    addr_label TEXT,
    placeX INTEGER,
    placeY INTEGER,
    PRIMARY KEY (addr_id)
);

CREATE TABLE IF NOT EXISTS homes (
    home_id SERIAL,
    homeX INTEGER,
    homeY INTEGER,
    PRIMARY KEY (home_id)
);

CREATE TABLE IF NOT EXISTS users (
    username TEXT NOT NULL,
    pubkey TEXT,
    addr_id UUID,
    PRIMARY KEY (username),
    FOREIGN KEY (addr_id) REFERENCES places(addr_id)
);

CREATE TABLE IF NOT EXISTS doorbells (
    doorb_id SERIAL,
    addr_id UUID,
    doorb_label TEXT,
    PRIMARY KEY (doorb_id),
    FOREIGN KEY (addr_id) REFERENCES places(addr_id)
);

CREATE TABLE IF NOT EXISTS rides (
    ride_id SERIAL,
    start_addr UUID,
    end_addr UUID,
    ride_creation TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (ride_id),
    FOREIGN KEY (start_addr) REFERENCES places(addr_id),
    FOREIGN KEY (end_addr) REFERENCES places(addr_id)
);

INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000000', 'TRUE', 'FALSE', 'Mysterious Forest', 25, 0);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000001', 'TRUE', 'FALSE', 'Enchanted Mountain', 65, 30);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000002', 'TRUE', 'FALSE', 'Magic Lake', 25, 81);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000003', 'TRUE', 'FALSE', 'Dangerous Volcano', 100, 100);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000004', 'TRUE', 'FALSE', 'Whispering Cave', 100, 30);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000005', 'FALSE', 'TRUE', 'Station 1',  70, 10);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000006', 'FALSE', 'TRUE', 'Station 2',  40, 20);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000007', 'FALSE', 'TRUE', 'Station 3', 100, 50);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000008', 'FALSE', 'TRUE', 'Station 4',  12, 70);
INSERT INTO places (addr_id, public, station, addr_label, placeX, placeY) VALUES ('00000000-0000-0000-0000-000000000009', 'FALSE', 'TRUE', 'Station 5',  60, 80);

INSERT INTO homes (homeX, homeY) VALUES (60, 2);
INSERT INTO homes (homeX, homeY) VALUES (91, 18);
INSERT INTO homes (homeX, homeY) VALUES (55, 37);
INSERT INTO homes (homeX, homeY) VALUES (72, 45);
INSERT INTO homes (homeX, homeY) VALUES (35, 52);
INSERT INTO homes (homeX, homeY) VALUES (80, 70);
INSERT INTO homes (homeX, homeY) VALUES (38, 75);
INSERT INTO homes (homeX, homeY) VALUES (75, 90);
INSERT INTO homes (homeX, homeY) VALUES (12, 95);

INSERT INTO doorbells (addr_id, doorb_label) VALUES ('00000000-0000-0000-0000-000000000000', E'Welcome to the\nMysterious Forest!');
INSERT INTO doorbells (addr_id, doorb_label) VALUES ('00000000-0000-0000-0000-000000000001', E'Welcome to the\nEnchanted Mountain!');
INSERT INTO doorbells (addr_id, doorb_label) VALUES ('00000000-0000-0000-0000-000000000002', E'Welcome to the\nMagic Lake!');
INSERT INTO doorbells (addr_id, doorb_label) VALUES ('00000000-0000-0000-0000-000000000003', E'Welcome to the\nDangerous Volcano!');
INSERT INTO doorbells (addr_id, doorb_label) VALUES ('00000000-0000-0000-0000-000000000004', E'Welcome to the\nWhispering Cave!');