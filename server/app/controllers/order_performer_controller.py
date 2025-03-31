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
        return Order.assign_single_performer_to_order(order_id, performer_id)

    @staticmethod
    def get_assigned_orders(performer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        return Order.get_assigned_orders_by_performer(performer_id)

    @staticmethod
    def get_all_performer_customers(performer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        return Order.get_customers_by_performer(performer_id)
