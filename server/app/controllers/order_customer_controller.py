from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.order_model import Order


class OrderCustomerController:
    @staticmethod
    def get_all_customer_orders(customer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH customers_orders AS (
                        SELECT o.id AS id, o.name AS name, o.description AS description, o.customer_id AS customer_id, o.performer_id AS performer_id, i.image_link AS image_link, oi.is_main AS is_main
                        FROM orders o
                        JOIN orders_images oi ON o.id = oi.order_id
                        JOIN images i ON i.id = oi.image_id
                    )
                    SELECT id, name, description, customer_id, performer_id, image_link
                    FROM customers_orders
                    WHERE is_main IS TRUE AND customer_id = %s;
                """,
                (customer_id, ),
                is_all=True,
            )

    @staticmethod
    def get_all_customer_performers(customer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_performers_ids AS (
                        SELECT id, performer_id
                        FROM orders
                        WHERE customer_id = %s
                    )
                    SELECT spf.id AS order_id, u.id AS id, username, first_name, last_name, photo_link
                    FROM selected_performers_ids spf
                    JOIN users u ON spf.performer_id = u.id
                """,
                (customer_id, ),
                is_all=True,
            )

    @staticmethod
    def get_single_customer_order(order_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_images AS (
                        SELECT oi.order_id AS order_id, ARRAY_AGG(i.image_link) AS images_links
                        FROM images i
                        JOIN orders_images oi ON oi.image_id = i.id
                        WHERE oi.order_id = %s
                        GROUP BY oi.order_id
                    )
                    SELECT o.id AS id, name, description, customer_id, performer_id, si.images_links AS images_links
                    FROM selected_images si
                    JOIN orders o ON o.id = si.order_id
                    WHERE id = %s
                """,
                (order_id, )
            )


    @staticmethod
    def create_order(order_data: dict) -> dict[str, Any]:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    INSERT INTO orders (name, description, customer_id)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, description, customer_id, performer_id; 
                """,
                (order_data["name"], order_data["description"], order_data["customer_id"]),
            )

    @staticmethod
    def update_order(
            order_id: int,
            order_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            if order_data["images_links"]:
                db.execute_query("DELETE FROM orders_images WHERE order_id = %s", (order_id,))

                for link in order_data["images_links"]:
                    image_id = db.execute_query(
                        """
                            INSERT INTO images (image_link)
                            VALUES (%s)
                            RETURNING id
                        """,
                        (link,),
                    )

                    db.execute_query(
                        """
                            WITH inserted_images AS (
                                INSERT INTO orders_images (order_id, image_id)
                                VALUES (%s, %s)
                            ),
                            selected_main AS (
                                SELECT image_id
                                FROM orders_images
                                WHERE order_id = %s
                                LIMIT 1
                            )                        
                            UPDATE orders_images 
                            SET is_main = TRUE 
                            WHERE order_id = selected_main.image_id
                        """,
                        (order_id, image_id),
                    )

            return db.fetch(
                """
                    WITH selected_images AS (
                        SELECT oi.order_id AS order_id, ARRAY_AGG(i.image_link) AS images_links
                        FROM images i
                        JOIN orders_images oi ON oi.image_id = i.id
                        WHERE oi.order_id = %s
                        GROUP BY oi.order_id
                    )
                    SELECT o.id AS id, name, description, customer_id, performer_id, si.images_links AS images_links
                    FROM selected_images si
                    JOIN orders o ON o.id = si.order_id
                    WHERE id = %s
                """,
                (order_id, order_id),
            )

    @staticmethod
    def delete_order(order_id: int) -> None:
        Order.delete_record_by_id(order_id)
