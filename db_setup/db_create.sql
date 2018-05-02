  CREATE TABLE country (
  country TEXT NOT NULL,
  city TEXT NOT NULL UNIQUE,
  PRIMARY KEY (country, city)
);


CREATE TABLE sys_user (
     user_id SERIAL PRIMARY KEY,
     email TEXT NOT NULL UNIQUE,
     password TEXT NOT NULL,
     role TEXT NOT NULL
);

CREATE TABLE hotel_admin (
    person_id INTEGER PRIMARY KEY REFERENCES sys_user (user_id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT NOT NULL
);

CREATE TABLE hotel (
    hotel_id SERIAL PRIMARY KEY,
    city TEXT NOT NULL REFERENCES country (city),
    address TEXT NOT NULL,
    name TEXT NOT NULL,
    stars INTEGER NOT NULL,
    description TEXT NOT NULL,
    img TEXT NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES hotel_admin (person_id) ON DELETE CASCADE
);

CREATE TABLE room_config (
    config_id SERIAL PRIMARY KEY,
    single_bed INTEGER,
    double_bed INTEGER,
    sofa_bed INTEGER
);

CREATE TABLE customer (
   person_id INTEGER PRIMARY KEY REFERENCES sys_user (user_id) ON DELETE CASCADE,
   first_name TEXT NOT NULL,
   last_name TEXT NOT NULL,
   phone_number TEXT NOT NULL,
   payment_info TEXT
);

CREATE TABLE admin (
    person_id INTEGER PRIMARY KEY REFERENCES sys_user (user_id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT NOT NULl
);

CREATE TABLE receptionist (
  person_id INTEGER PRIMARY KEY REFERENCES sys_user (user_id) ON DELETE CASCADE,
  hotel_id INTEGER NOT NULL REFERENCES hotel (hotel_id) ON DELETE CASCADE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone_number TEXT NOT NULL,
  salary INTEGER NOT NULL
);

CREATE TABLE transaction (
    transaction_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer (person_id),
    payment_method TEXT NOT NULL,
    amount REAL NOT NULL
);

CREATE TABLE room_option (
    option_id SERIAL PRIMARY KEY,
    is_bathroom BOOLEAN NOT NULL,
    is_tv BOOLEAN NOT NULL,
    is_wifi BOOLEAN NOT NULL,
    is_bathhub BOOLEAN NOT NULL,
    is_airconditioniring BOOLEAN NOT NULL
);

CREATE TABLE room (
    room_id SERIAL PRIMARY KEY,
    hotel_id INTEGER NOT NULL REFERENCES hotel (hotel_id) ON DELETE CASCADE,
    config_id INTEGER NOT NULL REFERENCES room_config (config_id),
    option_id INTEGER NOT NULL REFERENCES room_option (option_id),
    quantity INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    cost REAL NOT NULL
);

CREATE TABLE booking (
  room_id INTEGER REFERENCES room (room_id) ON DELETE CASCADE,
  customer_id INTEGER REFERENCES customer (person_id),
  transaction_id INTEGER NOT NULL REFERENCES transaction (transaction_id) ON DELETE CASCADE,
  quantity INTEGER NOT NULL,
  checkin_date DATE NOT NULL,
  checkout_date DATE NOT NULL,
  PRIMARY KEY (room_id, customer_id, transaction_id)
);

CREATE VIEW vw_hotels AS
  SELECT *
  FROM hotel
    JOIN country USING (city);

CREATE VIEW vw_customers AS
  SELECT
    person_id,
    first_name,
    last_name,
    phone_number,
    payment_info,
    email
  FROM sys_user
    JOIN customer ON (user_id = person_id);

CREATE VIEW vw_booked_rooms AS
  SELECT
    room_id,
    hotel_id,
    title,
    r.config_id,
    r.option_id,
    description,
    cost,
    b.quantity,
    checkin_date,
    checkout_date,
    single_bed,
    double_bed,
    sofa_bed,
    is_bathroom,
    is_tv,
    is_wifi,
    is_bathhub,
    is_airconditioniring,
    first_name,
    last_name,
    phone_number,
    amount
  FROM room r
    JOIN booking b USING (room_id)
    JOIN room_config rc USING (config_id)
    JOIN room_option ro USING (option_id)
    JOIN customer c ON (c.person_id = b.customer_id)
    JOIN transaction t ON (b.transaction_id = t.transaction_id);

INSERT INTO sys_user VALUES (DEFAULT, 'admin', '$2b$12$iBcgVwBvy/7NvLAw1oJ36OY9aYsK02eKPlHepY/0vCruDWdiysV6a', 'admin');
INSERT INTO admin VALUES (1, 'admin', 'admin', '789783113')