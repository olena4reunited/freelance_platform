from typing import Any
from concurrent.futures import ThreadPoolExecutor
import traceback
from server.app.utils.logger import logger

from psycopg2.extras import RealDictCursor

from server.app.database.database import PostgresDatabase


executor = ThreadPoolExecutor(max_workers=5)


class OrdersLogsController:
    @staticmethod
    def log_created_order(order_data: dict[str, Any]):
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO orders_logs (customer_id, order_id, change_type, new_price, order_name, order_tags)
                        VALUES (%s, %s, 'created', %s, %s, %s);
                    """,
                    (
                        order_data["customer_id"],
                        order_data["id"],
                        order_data["price"],
                        order_data["name"],
                        order_data["tags"]
                    )
                )

    @staticmethod
    def log_updated_order(order_data: dict[str, Any], percent: int | None = None):
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                        SELECT new_price
                        FROM orders_logs
                        WHERE order_id = %s
                        ORDER BY id DESC
                        LIMIT 1;
                    """,
                    (order_data["id"], )
                )
                price_row = cursor.fetchone()
                
                if not percent:
                    percent = abs(round(order_data["price"] / price_row["new_price"] - 1 * 100))
                
                cursor.execute(
                    """
                        INSERT INTO orders_logs (customer_id, order_id, change_type, old_price, new_price, price_change_percent, order_name, order_tags)
                        VALUES (%s, %s, 'updated', %s, %s, %s, %s, %s);
                    """,
                    (
                        order_data["customer_id"],
                        order_data["id"],
                        price_row["new_price"],
                        order_data["price"],
                        percent,
                        order_data["name"],
                        order_data["tags"]
                    )
                )

    @staticmethod
    def log_order_async(log_type: str, order_data: dict[str, Any], percent: int | None = None):
        def safe_call(fn, *args, **kwargs):
            try:
                fn(*args, **kwargs)
            except Exception as e:
                logger.error(
                    "Error was occured: \n%s\x1b[31m" \
                    "ERROR TRACEBACK:\x1b[0m\n%s",
                    " "*10,
                    traceback.format_exc()
                )

        if log_type == "created":
            executor.submit(safe_call, OrdersLogsController.log_created_order, order_data)
        elif log_type == "updated":
            executor.submit(safe_call, OrdersLogsController.log_updated_order, order_data, percent)
