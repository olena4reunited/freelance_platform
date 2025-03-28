from typing import Any

from psycopg2 import sql

from server.app.database.database import PostgresDatabase
from server.app.models.order_model import Order


class OrderPerformerController:
    @staticmethod
    def get_orders(user_id: int) -> list[dict[str, Any]]:
        return Order.get_all_unassigned_orders(user_id)

    @staticmethod
    def assign_to_the_order(order_id: int, performer_id: int) -> dict[str, Any]:
        ...

    @staticmethod
    def get_assigned_orders(performer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT id, name, description, customer_id, performer_id
                    FROM orders
                    WHERE is_blocked IS NOT TRUE AND performer_id = %s
                """,
                (performer_id,),
                is_all=True
            )

    @staticmethod
    def get_all_performer_customers(performer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_customers_ids AS (
                        SELECT id, customer_id
                        FROM orders
                        WHERE performer_id = %s
                    )
                    SELECT sc.id AS order_id, u.id AS id, username, first_name, last_name, photo_link
                    FROM selected_customers_ids sc
                    Join users u on sc.customer_id = u.id
                """,
                (performer_id,),
                is_all=True
            )
