BEGIN;

ALTER TABLE orders DROP COLUMN execution_type;

COMMIT;
