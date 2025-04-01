BEGIN;

CREATE TABLE IF NOT EXISTS orders_logs (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_id INTEGER NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    old_price DECIMAL(10,2) NULL,
    new_price DECIMAL(10,2) NULL,
    price_change_percent INTEGER NULL,
    order_name VARCHAR(256) NOT NULL
    order_tags TEXT[] NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE SET NULL
);

ALTER TABLE orders_logs 
ADD CHECK (
	change_type = ANY(ARRAY['created', 'updated', 'completed'])
);

COMMIT;
