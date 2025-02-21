from datetime import datetime
from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.order_model import Order


class OrderAdminController:
    @staticmethod
    def get_all_orders() -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_orders AS (
                        SELECT o.id AS id, o.name AS name, o.description AS description, o.customer_id AS customer_id, o.performer_id AS performer_id, i.image_link AS image_link
                        FROM orders o
                        JOIN orders_images oi ON o.id = oi.order_id
                        JOIN images i ON i.id = oi.image_id
                        WHERE oi.is_main IS TRUE
                    )
                    SELECT id, name, description, customer_id, performer_id, image_link
                    FROM selected_orders;
                """,
                is_all=True
            )

    @staticmethod
    def get_order_by_id(order_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_order AS (
                        SELECT o.id AS id, o.name AS name, o.description AS description, o.customer_id AS customer_id, o.performer_id AS performer_id, ARRAY_AGG(i.image_link) AS images_links
                        FROM orders o
                        JOIN orders_images oi ON o.id = oi.order_id
                        JOIN images i ON i.id = oi.image_id
                        WHERE o.id = %s
                        GROUP BY o.id
                    )
                    SELECT id, name, description, customer_id, performer_id, images_links
                    FROM selected_order;
                """,
                (order_id, )
            )

    @staticmethod
    def update_order_by_id(order_id: int, order_data: dict[str, Any] | None) -> dict[str, Any] | None:
        copy_keys = [key for key in order_data.keys()]
        for key in copy_keys:
            if not order_data[key]:
                order_data.pop(key)

        return Order.update_order_by_id(order_id, order_data)

    @staticmethod
    def delete_order_by_id(order_id: int) -> None:
        Order.delete_record_by_id(order_id)

    @staticmethod
    def block_order_by_id(order_id: int, block_timestamp: datetime) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    WITH blocked_order AS (
                        UPDATE orders
                        SET blocked_until = TIMESTAMP %s, is_blocked = TRUE
                        WHERE id = %s
                        RETURNING id, name, description, customer_id, performer_id, blocked_until, is_blocked
                    )    
                    SELECT bo.id AS id, bo.name AS name, bo.description AS description, bo.customer_id AS customer_id, bo.performer_id AS performer_id, ARRAY_AGG(i.image_link) AS images_links, bo.blocked_until AS blocked_until, bo.is_blocked AS is_blocked
                    FROM blocked_order bo
                    LEFT JOIN orders_images oi ON oi.order_id = bo.id
                    JOIN images i ON i.id = oi.image_id
                    GROUP BY bo.id, bo.name, bo.description, bo.customer_id, bo.performer_id, bo.blocked_until, bo.is_blocked
                """,
                (block_timestamp, order_id, )
            )
