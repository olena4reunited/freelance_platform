BEGIN;

ALTER TABLE orders ADD COLUMN price NUMERIC(9, 2) NOT NULL;

COMMIT;
