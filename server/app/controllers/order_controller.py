from typing import Any

from server.app.models.order_model import Order
from server.app.models.image_model import Image
from server.app.models.order_image_model import OrderImage
from server.app.database.database import PostgresDatabase


class OrderController:
    @staticmethod
    def get_all_customer_orders(customer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            db.fetch(
                """
                    WITH customers_orders AS (
                        SELECT o.id AS id, o.name AS name, o.description AS description, o.customer_id AS customer_id, o.performer_id AS performer_id, i.image_link AS image_link, oi.is_main AS is_main
                        FROM orders o
                        JOIN orders_images oi ON o.id = oi.order_id
                        JOIN images i ON i.id = oi.image_id
                    )
                    SELECT id, name, description, customer_id, performer_id, image_link
                    FROM customers_orders
                    WHERE is_main IS TRUE;
                """,
                ( ),
                is_all=True,
            )

    @staticmethod
    def create_order(order_data: dict) -> dict[str, Any]:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    INSERT INTO orders (name, description, customer_id)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, description, customer_id, performer_id; 
                """
            )
