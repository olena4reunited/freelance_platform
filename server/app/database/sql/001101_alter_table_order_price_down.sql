BEGIN;

ALTER TABLE orders DROP COLUMN price;

COMMIT;
