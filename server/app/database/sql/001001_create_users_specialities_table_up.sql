BEGIN;

CREATE TABLE IF NOT EXISTS specialities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS specialities_tags (
    id SERIAL PRIMARY KEY,
    speciality_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (speciality_id) REFERENCES specialities(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE (speciality_id, tag_id)
);

CREATE TABLE IF NOT EXISTS orders_tags (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE (order_id, tag_id)
);

CREATE TABLE IF NOT EXISTS users_specialities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    speciality_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (speciality_id) REFERENCES specialities(id) ON DELETE CASCADE,
    UNIQUE (user_id, speciality_id)
);

CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    lead_id INTEGER,
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (lead_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS teams_users (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (team_id, user_id)
);

ALTER TABLE orders 
ADD COLUMN performer_team_id INTEGER NULL;
ALTER TABLE orders 
ADD CONSTRAINT fk_performer_team 
FOREIGN KEY (performer_team_id) REFERENCES teams(id) ON DELETE SET NULL;

COMMIT;
