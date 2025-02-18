from typing import Any

from server.app.database.database import PostgresDatabase


class OrderAdminController:
    @staticmethod
    def get_all_orders() -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_orders AS (
                        SELECT o.id AS id, o.name AS name, o.description AS description, o.customer_id AS customer_id, o.performer_id AS performer_id, i.image_link AS image_link, oi.is_main AS is_main
                        FROM orders o
                        JOIN orders_images oi ON o.id = oi.order_id
                        JOIN images i ON i.id = oi.image_id
                    )
                    SELECT id, name, description, customer_id, performer_id, image_link
                    FROM selected_orders
                    WHERE is_main IS TRUE;
                """,
                is_all=True
            )
