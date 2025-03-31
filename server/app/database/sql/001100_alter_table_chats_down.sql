BEGIN;

ALTER TABLE chats
DROP CONSTRAINT fk_chats_orders,
DROP COLUMN order_id;

COMMIt;
