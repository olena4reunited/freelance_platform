BEGIN;

ALTER TABLE orders 
DROP COLUMN performer_team_id;

DROP TABLE IF EXISTS teams_users;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS users_specialities;
DROP TABLE IF EXISTS orders_tags;
DROP TABLE IF EXISTS specialities_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS specialities;

COMMIT;
