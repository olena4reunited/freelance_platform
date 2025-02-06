BEGIN;

DELETE FROM plans WHERE name IN ('admin', 'moderator', 'customer', 'performer');

COMMIT;