from typing import Any

from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from server.app.models._base_model import BaseModel
from server.app.database.database import PostgresDatabase
from server.app.utils.exceptions import GlobalException
from server.app.utils.team_naming import generate_team_name


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
                            o.execution_type AS execution_type,
                            COALESCE(o.performer_id, NULL) AS performer_id,
                            COALESCE(o.performer_team_id, NULL) AS performer_team_id,
                            COALESCE(i.image_link, NULL) AS image_link, 
                            COALESCE(oi.is_main, NULL) AS is_main
                        FROM orders o
                        LEFT JOIN orders_images oi 
                            ON o.id = oi.order_id
                        LEFT JOIN images i 
                            ON i.id = oi.image_id
                        WHERE 
                            customer_id = %s
                            AND (oi.is_main IS TRUE OR oi.is_main IS NULL)
                    ),
                    selected_tags AS (
                        SELECT ot.order_id AS order_id, ARRAY_AGG(t.name) AS tags
                        FROM orders_tags ot
                        JOIN tags t
                            ON ot.tag_id = t.id
                        GROUP BY ot.order_id
                    )
                    SELECT 
                        id, 
                        name, 
                        description, 
                        customer_id, 
                        execution_type,
                        performer_id,
                        performer_team_id,
                        image_link,
                        st.tags AS tags
                    FROM customers_orders co
                    JOIN selected_tags st
                        ON st.order_id = co.id;
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
    def get_performer_teams_by_customer(
        customer_id: int
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                        SELECT
                            ARRAY_AGG(id) AS order_ids,
                            performer_team_id
                        FROM orders
                        WHERE customer_id = %s AND performer_team_id IS NOT NULL
                        GROUP BY performer_team_id
                    """,
                    (customer_id, )
                )
                order_teams = cursor.fetchall()

                for order_team in order_teams:
                    cursor.execute(
                        """
                            SELECT 
                                name,
                                lead_id
                            FROM teams
                            WHERE id = %s 
                        """,
                        (order_team.get("performer_team_id"), )
                    )
                    team = cursor.fetchone()

                    cursor.execute(
                        """
                            SELECT
                                username,
                                first_name,
                                last_name,
                                photo_link
                            FROM users
                            WHERE id = %s
                        """,
                        (team.get("lead_id"), )
                    )
                    team_lead = cursor.fetchone()

                    cursor.execute(
                        """
                            WITH selected_team AS (
                                SELECT user_id
                                FROM teams_users
                                WHERE team_id = %s
                            ),
                            selected_users AS (
                                SELECT 
                                    username,
                                    first_name,
                                    last_name,
                                    photo_link
                                FROM users
                                WHERE id = ANY (SELECT user_id FROM selected_team)
                            )
                            SELECT 
                                username, 
                                first_name,
                                last_name,
                                photo_link
                            FROM selected_users
                        """,
                        (order_team.get("performer_team_id"), )
                    )
                    performers = cursor.fetchall()

                    order_team.pop("performer_team_id")
                    order_team["name"] = team.get("name")
                    order_team["lead"] = team_lead
                    order_team["performers"] = performers

            return order_teams

    @staticmethod
    def get_order_details(order_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT 
                        o.id AS id,
                        o.name AS name,
                        o.description AS description,
                        o.customer_id AS customer_id,
                        o.execution_type AS execution_type,
                        o.performer_id AS performer_id,
                        o.performer_team_id AS performer_team_id,
                        ARRAY_AGG(DISTINCT i.image_link) 
                            FILTER 
                                (WHERE i.image_link IS NOT NULL) 
                            AS images_links,
                        ARRAY_AGG(t.name) AS tags
                    FROM orders o
                    LEFT JOIN orders_images oi
                        ON oi.order_id = o.id
                    LEFT JOIN images i
                        ON oi.image_id = i.id
                    LEFT JOIN orders_tags ot
                        ON ot.order_id = o.id
                    LEFT JOIN tags t
                        ON ot.tag_id = t.id
                    WHERE o.id = %s
                    GROUP BY 
                        o.id, 
                        o.name, 
                        o.description, 
                        o.customer_id,
                        o.performer_id, 
                        o.performer_team_id;
                """,
                (order_id, )
            )

    @staticmethod
    def create_order(
            customer_id: int,
            order_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                        INSERT INTO orders 
                            (name, description, customer_id, execution_type, price)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """,
                    (
                        order_data["name"], 
                        order_data["description"], 
                        customer_id, 
                        order_data["execution_type"],
                        order_data["price"]
                    ),
                )
                order = cursor.fetchone()

                if order_data["images_links"]:
                    cursor.executemany(
                        """
                        INSERT INTO images (image_link)
                        VALUES (%s)
                        RETURNING id;
                        """,
                        [(link,) for link in order_data["images_links"]]
                    )

                    image_ids = [row["id"] for row in cursor.fetchall()]

                    order_images_data = [
                        (order["id"], image_id, index == 0) for index, image_id in enumerate(image_ids)
                    ]

                    cursor.executemany(
                        """
                            INSERT INTO orders_images (order_id, image_id, is_main)
                            VALUES (%s, %s, %s);
                        """,
                        order_images_data
                    )

                cursor.executemany(
                    """
                        INSERT INTO orders_tags (order_id, tag_id)
                        VALUES (%s, %s);
                    """,
                    [(order["id"], tag) for tag in order_data["tags"]]
                )

                cursor.execute(
                    """
                        SELECT 
                            o.id AS id,
                            o.name AS name,
                            o.description AS description,
                            o.customer_id AS customer_id,
                            o.execution_type AS execution_type,
                            o.performer_id AS performer_id,
                            o.performer_team_id AS performer_team_id,
                            ARRAY_AGG(DISTINCT i.image_link) 
                                FILTER 
                                    (WHERE i.image_link IS NOT NULL) 
                                AS images_links,
                            ARRAY_AGG(t.name) AS tags
                        FROM orders o
                        LEFT JOIN orders_images oi
                            ON oi.order_id = o.id
                        LEFT JOIN images i
                            ON oi.image_id = i.id
                        LEFT JOIN orders_tags ot
                            ON ot.order_id = o.id
                        LEFT JOIN tags t
                            ON ot.tag_id = t.id
                        WHERE o.id = %s
                        GROUP BY 
                            o.id, 
                            o.name, 
                            o.description, 
                            o.customer_id,
                            o.performer_id, 
                            o.performer_team_id;
                    """,
                    (order["id"], )
                )
                return cursor.fetchone()

    @staticmethod
    def update_order_by_id(
            order_id: int,
            order_data: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if order_data.get("images_links"):
                    cursor.execute(
                        """
                            DELETE FROM orders_images
                            WHERE order_id = %s
                        """,
                        (order_id, )
                    )

                    cursor.executemany(
                        """
                        INSERT INTO images (image_link)
                        VALUES (%s)
                        RETURNING id;
                        """,
                        [(link,) for link in order_data["images_links"]]
                    )

                    image_ids = [row["id"] for row in cursor.fetchall()]

                    order_images_data = [
                        (order_id, image_id, index == 0) for index, image_id in enumerate(image_ids)
                    ]

                    cursor.executemany(
                        """
                            INSERT INTO orders_images (order_id, image_id, is_main)
                            VALUES (%s, %s, %s);
                        """,
                        order_images_data
                    )

                    order_data.pop("images_links")

                if order_data.get("tags"):
                    cursor.execute(
                        """
                            DELETE FROM orders_tags
                            WHERE order_id = %s
                        """,
                        (order_id, )
                    )

                    cursor.executemany(
                        """
                            INSERT INTO orders_tags (order_id, tag_id)
                            VALUES (%s, %s);
                        """,
                        [(order_id, tag) for tag in order_data["tags"]]
                    )


                    order_data.pop("tags")

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
                        SELECT 
                            o.id AS id,
                            o.name AS name,
                            o.description AS description,
                            o.customer_id AS customer_id,
                            o.execution_type AS execution_type,
                            o.performer_id AS performer_id,
                            o.performer_team_id AS performer_team_id,
                            ARRAY_AGG(DISTINCT i.image_link) 
                                FILTER 
                                    (WHERE i.image_link IS NOT NULL) 
                                AS images_links,
                            ARRAY_AGG(t.name) AS tags
                        FROM orders o
                        LEFT JOIN orders_images oi
                            ON oi.order_id = o.id
                        LEFT JOIN images i
                            ON oi.image_id = i.id
                        LEFT JOIN orders_tags ot
                            ON ot.order_id = o.id
                        LEFT JOIN tags t
                            ON ot.tag_id = t.id
                        WHERE o.id = %s
                        GROUP BY 
                            o.id, 
                            o.name, 
                            o.description, 
                            o.customer_id,
                            o.performer_id, 
                            o.performer_team_id;
                    """,
                    (order_id,)
                )

                return cursor.fetchone()


    @staticmethod
    def get_all_unassigned_orders(user_id: int) -> dict[str, Any]:
        with PostgresDatabase() as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                        WITH selected_order_ids AS (
                            SELECT DISTINCT(ot.order_id) AS order_id
                            FROM users_specialities usp
                            JOIN specialities_tags spt
                                ON spt.speciality_id = usp.speciality_id
                            JOIN orders_tags ot
                                ON ot.tag_id = spt.tag_id
                            WHERE usp.user_id = %s
                        )
                        SELECT 
                            o.id AS id,
                            o.name AS name,
                            o.description AS description,
                            o.customer_id AS customer_id,
                            o.execution_type AS execution_type,
                            ARRAY_AGG(DISTINCT i.image_link) 
                                FILTER 
                                    (WHERE i.image_link IS NOT NULL) 
                                AS images_links,
                            ARRAY_AGG(t.name) AS tags
                        FROM orders o
                        LEFT JOIN orders_images oi
                            ON oi.order_id = o.id
                        LEFT JOIN images i
                            ON oi.image_id = i.id
                        LEFT JOIN orders_tags ot
                            ON ot.order_id = o.id
                        LEFT JOIN tags t
                            ON ot.tag_id = t.id
                        WHERE 
                            o.id = ANY(SELECT order_id FROM selected_order_ids)
                            AND o.is_blocked IS NOT TRUE
                            AND o.blocked_until IS NULL
                            AND o.performer_id IS NULL
                            AND o.performer_team_id IS NULL
                        GROUP BY 
                            o.id, 
                            o.name, 
                            o.description, 
                            o.customer_id,
                            o.execution_type,
                            o.performer_id, 
                            o.performer_team_id;
                    """,
                    (user_id, )
                )
                return cursor.fetchall()

    @staticmethod
    def assign_single_performer_to_order(order_id: int, performer_id: int) -> dict[str, Any]:
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                        SELECT DISTINCT
                            o.execution_type AS execution_type,
                            o.customer_id AS customer_id,
                            o.performer_id AS performer_id,
                            o.performer_team_id AS performer_team_id,
                            ARRAY_AGG(t.name) AS tags
                        FROM orders o
                        JOIN orders_tags ot
                            ON ot.order_id = o.id
                        JOIN specialities_tags spt
                            ON spt.tag_id = ot.tag_id
                        JOIN users_specialities usp
                            ON usp.speciality_id = spt.speciality_id
                        JOIN tags t
                            ON t.id = ot.tag_id
                        WHERE o.id = %s
                            AND usp.user_id = %s
                            AND o.is_blocked IS NOT TRUE
                            AND o.blocked_until IS NULL
                        GROUP BY 
                            o.execution_type,
                            o.customer_id,
                            o.performer_id,
                            o.performer_team_id
                    """,
                    (order_id, performer_id, )
                )
                order = cursor.fetchone()

                if not order:
                    GlobalException.CustomHTTPException.raise_exception(
                        status_code=403,
                        detail=(
                            "Order is inaccessable for accepting to work"
                        )
                    )

                    return
                if order["execution_type"] == "single":
                    if order.get("performer_id"):
                        if order.get("performer_id") == performer_id:
                            GlobalException.CustomHTTPException.raise_exception(
                                status_code=400,
                                detail=(
                                    "You already assign yourself to selected order"
                                )
                            )
                        
                            return
                        GlobalException.CustomHTTPException.raise_exception(
                            status_code=403,
                            detail=(
                                "You are not allowed to assign yourself to selected order. " \
                                "The order is already accepted to work by another user"
                            )
                        )

                        return
                    else:
                        cursor.execute(
                            """
                                WITH updated_order AS (
                                    UPDATE orders
                                    SET performer_id = %s
                                    WHERE id = %s
                                    RETURNING 
                                        id,
                                        name,
                                        description,
                                        customer_id,
                                        execution_type
                                )
                                SELECT 
                                    uo.id AS id,
                                    uo.name AS name,
                                    uo.description AS description,
                                    uo.customer_id AS customer_id,
                                    uo.execution_type AS execution_type,
                                    ARRAY_AGG(DISTINCT i.image_link) 
                                        FILTER 
                                            (WHERE i.image_link IS NOT NULL) 
                                        AS images_links,
                                    ARRAY_AGG(t.name) AS tags
                                FROM updated_order uo
                                LEFT JOIN orders_images oi
                                    ON oi.order_id = uo.id
                                LEFT JOIN images i
                                    ON oi.image_id = i.id
                                LEFT JOIN orders_tags ot
                                    ON ot.order_id = uo.id
                                LEFT JOIN tags t
                                    ON ot.tag_id = t.id
                                GROUP BY 
                                    uo.id,
                                    uo.name,
                                    uo.description,
                                    uo.customer_id,
                                    uo.execution_type;
                            """,
                            (performer_id, order_id, )
                        )
                        result_order = cursor.fetchone()

                        cursor.execute(
                            """
                                SELECT 
                                    username,
                                    first_name,
                                    last_name,
                                    photo_link
                                FROM users
                                WHERE id = %s;
                            """,
                            (performer_id, )
                        )
                        performer = cursor.fetchone()

                        result_order["performer"] = performer

                        return result_order
                    
                if order["execution_type"] == "team":
                    if order.get("performer_team_id"):
                        cursor.execute(
                            """
                                SELECT id
                                FROM teams
                                WHERE id = %s
                                    AND lead_id IS NULL;
                            """,
                            (order["performer_team_id"], )
                        )
                        team_accessable = cursor.fetchone()

                        if not team_accessable:
                            GlobalException.CustomHTTPException.raise_exception(
                                status_code=403,
                                detail=(
                                    "Order is inaccessable for accepting to work"
                                )                                
                            )
                        else:
                            cursor.execute(
                                """
                                    SELECT 
                                        o.id AS id,
                                        o.name AS name,
                                        o.description AS description,
                                        o.customer_id AS customer_id,
                                        o.execution_type AS execution_type,
                                        ARRAY_AGG(DISTINCT i.image_link) 
                                            FILTER 
                                                (WHERE i.image_link IS NOT NULL) 
                                            AS images_links,
                                        ARRAY_AGG(t.name) AS tags
                                    FROM orders o
                                    LEFT JOIN orders_images oi
                                        ON oi.order_id = o.id
                                    LEFT JOIN images i
                                        ON oi.image_id = i.id
                                    LEFT JOIN orders_tags ot
                                        ON ot.order_id = o.id
                                    LEFT JOIN tags t
                                        ON ot.tag_id = t.id
                                    GROUP BY 
                                        o.id,
                                        o.name,
                                        o.description,
                                        o.customer_id,
                                        o.execution_type;
                                """
                            )
                            result_order = cursor.fetchone()

                            cursor.execute(
                                """
                                    SELECT name
                                    FROM teams
                                    WHERE id = %s
                                """,
                                (order["performer_team_id"], )
                            )
                            team = cursor.fetchone()

                            cursor.execute(
                                """
                                    INSERT INTO teams_users (team_id, user_id)
                                    VALUES (%s, %s);
                                """,
                                (order["performer_team_id"], performer_id, )
                            )
                            cursor.execute(
                                """
                                    SELECT 
                                        username,
                                        first_name,
                                        last_name,
                                        photo_link
                                    FROM users u
                                    JOIN teams_users tu
                                        ON tu.user_id = u.id
                                    WHERE tu.team_id = %s
                                """,
                                (order["performer_team_id"], )
                            )
                            team_users = cursor.fetchall()

                            team["performers"] = team_users
                            result_order["team"] = team

                            return result_order
                    else:
                        cursor.execute(
                            """
                                SELECT 
                                    o.id AS id,
                                    o.name AS name,
                                    o.description AS description,
                                    o.customer_id AS customer_id,
                                    o.execution_type AS execution_type,
                                    ARRAY_AGG(DISTINCT i.image_link) 
                                        FILTER 
                                            (WHERE i.image_link IS NOT NULL) 
                                        AS images_links,
                                    ARRAY_AGG(t.name) AS tags
                                FROM orders o
                                LEFT JOIN orders_images oi
                                    ON oi.order_id = o.id
                                LEFT JOIN images i
                                    ON oi.image_id = i.id
                                LEFT JOIN orders_tags ot
                                    ON ot.order_id = o.id
                                LEFT JOIN tags t
                                    ON ot.tag_id = t.id
                                WHERE o.id = %s
                                GROUP BY 
                                    o.id,
                                    o.name,
                                    o.description,
                                    o.customer_id,
                                    o.execution_type;
                            """,
                            (order_id, )
                        )
                        result_order = cursor.fetchone()
                        
                        team_name = generate_team_name(order.get("tags"))

                        cursor.execute(
                            """
                                WITH inserted_team AS (
                                    INSERT INTO teams (name, customer_id)
                                    VALUES (%s, %s)
                                    RETURNING id, name
                                ), 
                                inserted_users AS (
                                    INSERT INTO teams_users (team_id, user_id)
                                    SELECT id, %s
                                    FROM inserted_team
                                    RETURNING team_id
                                ),
                                updated_order AS (
                                    UPDATE orders
                                    SET performer_team_id = (SELECT id from inserted_team)
                                    WHERE id = %s
                                )
                                SELECT inserted_team.name AS name
                                FROM inserted_team;
                            """,
                            (team_name, order["customer_id"], performer_id, order_id, )
                        )
                        team = cursor.fetchone()

                        cursor.execute(
                            """
                                SELECT 
                                    username,
                                    first_name,
                                    last_name,
                                    photo_link
                                FROM users
                                WHERE id = %s;
                            """,
                            (performer_id, )
                        )
                        performer = cursor.fetchone()
                        
                        team["performers"] = performer
                        result_order["team"] = team
                        print(result_order)
                        return result_order

    @staticmethod
    def get_assigned_orders_by_performer(performer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_teams AS (
                        SELECT t.id AS id
                        FROM teams_users tu
                        JOIN teams t
                            ON t.id = tu.team_id
                        WHERE tu.user_id = %s
                    )
                    SELECT
                        o.id AS id,
                        o.name AS name,
                        o.description AS description,
                        o.customer_id AS customer_id,
                        o.execution_type AS execution_type,
                        ARRAY_AGG(DISTINCT(i.image_link))
                            FILTER
                                (WHERE i.image_link IS NOT NULL)
                            AS images_links,
                        ARRAY_AGG(t.name) AS tags
                        FROM orders o
                        LEFT JOIN orders_images oi
                            ON oi.order_id = o.id
                        LEFT JOIN images i
                            ON oi.image_id = i.id
                        LEFT JOIN orders_tags ot
                            ON ot.order_id = o.id
                        LEFT JOIN tags t
                            ON ot.tag_id = t.id
                        WHERE performer_id = %s 
                            OR performer_team_id = ANY(SELECT id FROM selected_teams)
                        GROUP BY 
                            o.id,
                            o.name,
                            o.description,
                            o.customer_id,
                            o.execution_type;
                """,
                (performer_id, performer_id, ),
                is_all=True
            )

    @staticmethod
    def get_customers_by_performer(performer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_teams AS (
                        SELECT t.id AS id
                        FROM teams_users tu
                        JOIN teams t
                            ON t.id = tu.team_id
                        WHERE tu.user_id = %s
                    ),
                    selected_customers AS (
                        SELECT 
                            ARRAY_AGG(id) AS order_ids,
                            customer_id
                        FROM orders
                        WHERE performer_id = %s
                            OR performer_team_id = ANY(SELECT id from selected_teams)
                        GROUP BY customer_id
                    )
                    SELECT 
                        sc.order_ids AS order_ids,
                        username,
                        first_name,
                        last_name,
                        photo_link
                    FROM selected_customers sc
                    JOIN users u
                        ON sc.customer_id = u.id
                """,
                (performer_id, performer_id, ),
                is_all=True
            )
