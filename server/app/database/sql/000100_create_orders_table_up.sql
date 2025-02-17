BEGIN;

CREATE TABLE IF NOT EXISTS orders (
	id SERIAL PRIMARY KEY,
	name VARCHAR(256) NOT NULL,
	description TEXT,
	blocked_until TIMESTAMP,
	is_blocked BOOL,
	creator_id INTEGER NOT NULL,
	performer_id INTEGER,
	FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (performer_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS images (
	id SERIAL PRIMARY KEY,
	image_link VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS orders_images (
	id SERIAL PRIMARY KEY,
	is_main BOOL,
	order_id INTEGER NOT NULL,
	image_id INTEGER NOT NULL,
	FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
	FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

COMMIT;
