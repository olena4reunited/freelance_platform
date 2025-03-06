from typing import Any

from psycopg2 import sql

from server.app.models._base_model import BaseModel
from server.app.database.database import PostgresDatabase


class Order(BaseModel):
    table_name = "orders"

    @staticmethod
    def get_orders_by_customer(
            customer_id: int
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH customers_orders AS (
                        SELECT 
                            o.id AS id, 
                            o.name AS name, 
                            o.description AS description, 
                            o.customer_id AS customer_id, 
                            COALESCE(o.performer_id, NULL) AS performer_id, 
                            COALESCE(i.image_link, NULL) AS image_link, 
                            COALESCE(oi.is_main, NULL) AS is_main
                        FROM orders o
                        LEFT JOIN orders_images oi 
                            ON o.id = oi.order_id
                        LEFT JOIN images i 
                            ON i.id = oi.image_id
                        WHERE customer_id = %s AND (oi.is_main IS TRUE OR NULL)
                    )
                    SELECT 
                        id, 
                        name, 
                        description, 
                        customer_id, 
                        performer_id, 
                        image_link
                    FROM customers_orders;
                """,
                (customer_id, ),
                is_all=True,
            )

    @staticmethod
    def get_performers_by_customer(
            customer_id: int
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_performers_ids AS (
                        SELECT 
                            ARRAY_AGG(id) AS order_ids, 
                            performer_id
                        FROM orders
                        WHERE customer_id = %s
                        GROUP BY performer_id 
                    )
                    SELECT 
                        spf.order_ids AS order_ids, 
                        u.id AS id,
                        username,
                        first_name, 
                        last_name, 
                        photo_link
                    FROM selected_performers_ids spf
                    JOIN users u 
                        ON spf.performer_id = u.id
                """,
                (customer_id, ),
                is_all=True,
            )

    @staticmethod
    def get_order_details(order_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_images AS (
                        SELECT 
                            oi.order_id AS order_id, 
                            COALESCE(ARRAY_AGG(i.image_link), '{}') AS images_links
                        FROM orders_images oi 
                        LEFT JOIN images i 
                            ON oi.image_id = i.id 
                        GROUP BY oi.order_id
                    )
                    SELECT 
                        o.id AS id, 
                        name, 
                        description, 
                        customer_id, 
                        performer_id, 
                        si.images_links AS images_links
                    FROM orders o
                    LEFT JOIN selected_images si 
                        ON o.id = si.order_id
                    WHERE o.id = %s;
                """,
                (order_id,)
            )

    @staticmethod
    def create_order(
            customer_id: int,
            order_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO orders 
                            (name, description, customer_id)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """,
                    (order_data["name"], order_data["description"], customer_id),
                )
                order_id = cursor.fetchone()
                counter = 1

                for image_link in order_data["images_links"]:
                    cursor.execute(
                        """
                            INSERT INTO images (image_link)
                            VALUES (%s)
                            RETURNING id;
                        """,
                        (image_link,),
                    )
                    image_id = cursor.fetchone()

                    cursor.execute(
                        """
                            INSERT INTO orders_images 
                                (order_id, image_id, is_main)
                            VALUES (%s, %s, %s)
                        """,
                        (order_id, image_id, True if counter == 1 else False),
                    )
                    counter += 1

            return db.fetch(
                """
                    WITH selected_images AS (
                        SELECT 
                            oi.order_id AS order_id, 
                            COALESCE(ARRAY_AGG(i.image_link), '{}') AS images_links
                        FROM orders_images oi 
                        LEFT JOIN images i 
                            ON oi.image_id = i.id 
                        GROUP BY oi.order_id
                    )
                    SELECT 
                        o.id AS id, 
                        name, 
                        description, 
                        customer_id, 
                        performer_id, 
                        COALESCE(si.images_links, '{}') AS images_links
                    FROM orders o
                    LEFT JOIN selected_images si 
                        ON o.id = si.order_id
                    WHERE o.id = %s;
                """,
                (order_id,)
            )

    @staticmethod
    def update_order_by_id(
            order_id: int,
            order_data: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor() as cursor:
                if order_data.get("images_links"):
                    cursor.execute(
                        """
                            DELETE FROM orders_images
                            WHERE order_id = %s
                        """,
                        (order_id,)
                    )

                    counter = 1

                    for image_link in order_data["images_links"]:
                        cursor.execute(
                            """
                                INSERT INTO images (image_link)
                                VALUES (%s)
                                RETURNING id;
                            """,
                            (image_link,),
                        )
                        image_id = cursor.fetchone()

                        cursor.execute(
                            """
                                INSERT INTO orders_images 
                                    (order_id, image_id, is_main)
                                VALUES (%s, %s, %s)
                            """,
                            (order_id, image_id, True if counter == 1 else False),
                        )
                        counter += 1

                order_data.pop("images_links", None)

                set_clause = sql.SQL(", ").join(
                    sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder(k))
                    for k in order_data.keys()
                )
                cursor.execute(
                    sql.SQL("""
                        UPDATE orders 
                        SET {set_clause} 
                        WHERE id = {id_placeholder}
                    """).format(
                        set_clause=set_clause,
                        id_placeholder=sql.Placeholder("order_id"),
                    ),
                    {"order_id": order_id, **order_data},
                )

                cursor.execute(
                    """
                        WITH selected_images AS (
                            SELECT 
                                oi.order_id AS order_id, 
                                COALESCE(ARRAY_AGG(i.image_link), '{}') AS images_links
                            FROM orders_images oi 
                            LEFT JOIN images i 
                                ON oi.image_id = i.id 
                            GROUP BY oi.order_id
                        )
                        SELECT 
                            o.id AS id, 
                            name, 
                            description, 
                            customer_id, 
                            performer_id, 
                            COALESCE(si.images_links, '{}') AS images_links
                        FROM orders o
                        LEFT JOIN selected_images si 
                            ON o.id = si.order_id
                        WHERE o.id = %s;
                    """,
                    (order_id,)
                )
                return cursor.fetchone()
