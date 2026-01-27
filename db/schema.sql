CREATE TABLE IF NOT EXISTS flights (
    id VARCHAR(8) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    departure_airport VARCHAR(3) NOT NULL,
    arrival_airport VARCHAR(3) NOT NULL,
    departure_timezone VARCHAR(30) NOT NULL,
    arrival_timezone VARCHAR(30) NOT NULL,
    PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    passport_id VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);

CREATE UNIQUE INDEX IF EXISTS customers__passport_id_idx ON customers (passport_id);


CREATE TABLE IF NOT EXISTS passengers (
    flight_id VARCHAR(8) NOT NULL REFERENCES flights(id),
    customer_id INT NOT NULL REFERENCES customers(id),
    PRIMARY KEY (flight_id, customer_id)
);


INSERT INTO flights VALUES('AAA01', '2024-12-01T00:00:00Z', '2024-12-01T02:00:00Z', 'DMK', 'HYD', 'Asia/Bangkok', 'Asia/Bangkok')