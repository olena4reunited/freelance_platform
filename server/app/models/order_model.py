from typing import Any

from psycopg2 import sql

from server.app.models._base_model import BaseModel
from server.app.database.database import PostgresDatabase


class Order(BaseModel):
    table_name = "orders"

    @staticmethod
    def update_order_by_id(order_id: int, order_data: dict[str, Any] | None) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor() as cursor:
                if order_data.get("images_links"):
                    cursor.execute("DELETE FROM orders_images WHERE order_id = %s", (order_id,))

                    for image_link in order_data["images_links"]:
                        counter = 1
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
                                INSERT INTO orders_images (order_id, image_id, is_main)
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
                            SELECT oi.order_id AS order_id, COALESCE(ARRAY_AGG(i.image_link), '{}') AS images_links
                            FROM orders_images oi 
                            LEFT JOIN images i ON oi.image_id = i.id 
                            GROUP BY oi.order_id
                        )
                        SELECT o.id AS id, name, description, customer_id, performer_id, COALESCE(si.images_links, '{}') AS images_links
                        FROM orders o
                        LEFT JOIN selected_images si ON o.id = si.order_id
                        WHERE o.id = %s;
                    """,
                    (order_id,)
                )

                return cursor.fetchone()
