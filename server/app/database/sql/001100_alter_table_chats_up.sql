BEGIN;

ALTER TABLE chats 
ADD COLUMN order_id INT,
ADD CONSTRAINT fk_chats_order
FOREIGN KEY (order_id) REFERENCES orders(id)
ON DELETE CASCADE;

COMMIT;
