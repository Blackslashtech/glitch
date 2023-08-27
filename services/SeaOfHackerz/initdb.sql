CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL,
  username varchar(30) NOT NULL UNIQUE,
  password varchar(120),
  PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS items (
  item_id INTEGER,
  name varchar(30) UNIQUE,
  description varchar(250),
  PRIMARY KEY (item_id)
);

CREATE TABLE IF NOT EXISTS inventory (
  user_id integer,
  item_id integer,
  personal_description varchar(50),
  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (item_id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, item_id)
);

CREATE TABLE IF NOT EXISTS styles (
  style_id integer,
  type varchar(15),
  name varchar(15),
  PRIMARY KEY (type, style_id)
);

CREATE TABLE IF NOT EXISTS ships (
  style_type varchar(15),
  user_id integer,
  style_id integer,
  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
  FOREIGN KEY (style_type, style_id) REFERENCES styles (type, style_id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, style_type)
);

CREATE TABLE IF NOT EXISTS attacks (
  attack_id SERIAL,
  victim_id integer,
  attacker_id integer,
  ship_damage integer,
  attacker_damage integer,
  salt text,
  ac_key text,
  w text,
  x text,
  y text,
  z text,
  FOREIGN KEY (victim_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (attacker_id) REFERENCES users(user_id) ON DELETE CASCADE,
  PRIMARY KEY (attack_id)
);

INSERT INTO items (item_id, name, description) VALUES ( 0, 'Treasure', 'Store here your secrets!');
INSERT INTO items (item_id, name, description) VALUES ( 1, 'Cannon', 'The perfect weapon to bring on your boat');
INSERT INTO items (item_id, name, description) VALUES ( 2, 'Blunderbuss', 'Intimidate your enemies with this one');
INSERT INTO items (item_id, name, description) VALUES ( 3, 'Coin', 'A journey of a thousand miles begins with a single step...');
INSERT INTO items (item_id, name, description) VALUES ( 4, 'Compass', 'I will never lose my path again');
INSERT INTO items (item_id, name, description) VALUES ( 5, 'Map', 'What is the meaning of your life without this?');
INSERT INTO items (item_id, name, description) VALUES ( 6, 'Parrot', 'A truly loyal friend');
INSERT INTO items (item_id, name, description) VALUES ( 7, 'Flag', 'Not the one you are looking for, if you are a CTF player');
INSERT INTO items (item_id, name, description) VALUES ( 8, 'Hat', 'To protect you from the sun');
INSERT INTO items (item_id, name, description) VALUES ( 9, 'Swords', 'Less noisy than the blunderbuss');
INSERT INTO items (item_id, name, description) VALUES (10, 'Skull', 'Just to intimidate your enemies');
INSERT INTO items (item_id, name, description) VALUES (11, 'Telescope', 'Useful to see exploits from far away');
INSERT INTO items (item_id, name, description) VALUES (12, 'Banner', 'I swear, it is not an advertisement');
INSERT INTO items (item_id, name, description) VALUES (13, 'Eye patch', 'It blocks exploits against your eye');
INSERT INTO items (item_id, name, description) VALUES (14, 'Black flag', 'Again, you might be disappointed');
INSERT INTO items (item_id, name, description) VALUES (15, 'Rum', 'Wait, are you old enough to drink?');
INSERT INTO styles (type, style_id, name) VALUES ('Ship', 0, 'Anchor');
INSERT INTO styles (type, style_id, name) VALUES ('Ship', 1, 'Skull');
INSERT INTO styles (type, style_id, name) VALUES ('Ship', 2, 'Compass');
INSERT INTO styles (type, style_id, name) VALUES ('Sail', 0, 'Square');
INSERT INTO styles (type, style_id, name) VALUES ('Sail', 1, 'Rumble');
INSERT INTO styles (type, style_id, name) VALUES ('Sail', 2, 'Default');
INSERT INTO styles (type, style_id, name) VALUES ('Sail', 3, 'Blunt');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 0, '0');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 1, '1');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 2, '2');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 3, '3');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 4, '4');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 5, '5');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 6, '6');
INSERT INTO styles (type, style_id, name) VALUES ('Sail color', 7, '7');
INSERT INTO styles (type, style_id, name) VALUES ('Porthole', 0, 'Square');
INSERT INTO styles (type, style_id, name) VALUES ('Porthole', 1, 'Blunt');
INSERT INTO styles (type, style_id, name) VALUES ('Porthole', 2, 'Double');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 0, '0');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 1, '1');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 2, '2');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 3, '3');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 4, '4');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 5, '5');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 6, '6');
INSERT INTO styles (type, style_id, name) VALUES ('Flag color', 7, '7');