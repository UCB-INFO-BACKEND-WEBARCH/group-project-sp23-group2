CREATE TABLE IF NOT EXISTS census_request_history (
    id SERIAL PRIMARY KEY,
    county VARCHAR(40),
    state VARCHAR(20),
    email VARCHAR(100)
);