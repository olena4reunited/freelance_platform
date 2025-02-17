BEGIN;

CREATE UNIQUE INDEX unique_main_order
ON orders_images (order_id)
WHERE is_main = TRUE;

COMMIT;