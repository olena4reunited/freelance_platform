from enum import Enum
from typing import Any

from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class UserPlanEnum(Enum):
    customer = "customer"
    performer = "performer"


class User(BaseModel):
    table_name = "users"

    @staticmethod
    def get_user_by_id(user_id: int) -> dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT 
                        u.id AS id,
                        first_name,
                        last_name,
                        username,
                        email,
                        phone_number,
                        photo_link,
                        description,
                        balance,
                        rating,
                        pln.name AS plan_name,
                        is_verified,
                        block_expired,
                        delete_date,
                        is_blocked
                    FROM users u
                    JOIN plans pln
                        ON pln.id = u.plan_id
                    WHERE u.id = %s 
                """,
                (user_id, )
            )

    @staticmethod
    def get_user_by_field(field: str, value: str | int) -> dict[str, Any]:
        query = sql.SQL(
            """
                SELECT 
                    u.id AS id,
                    first_name,
                    last_name,
                    username,
                    email,
                    phone_number,
                    photo_link,
                    description,
                    balance,
                    rating,
                    pln.name AS plan_name
                FROM users u
                JOIN plans pln
                    ON pln.id = u.plan_id
                WHERE {} = {} 
            """
        ).format(sql.Identifier(field), sql.Placeholder())

        with PostgresDatabase() as db:
            return db.fetch(
                query,
                (value, )
            )

    @staticmethod
    def get_order_performer(user_id: int) -> dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT 
                        username,
                        first_name,
                        last_name,
                        photo_link
                    FROM users
                    WHERE id = %s;
                """,
                (user_id, )
            )

    @staticmethod
    def get_user_hashed_password(user_id: int):
        with PostgresDatabase() as db:
            with db.connection.cursor() as cursor:
                cursor.execute(
                    """
                        SELECT password
                        FROM users
                        WHERE id = %s
                    """,
                    (user_id, )
                )

                return cursor.fetchone()[0]

    @staticmethod
    def get_all_users(plan_name: str, limit: int) -> list[dict[str, Any]]:
        query = sql.SQL("""
            SELECT
                u.id,
                u.first_name,
                u.last_name,
                u.username,
                u.email,
                u.phone_number,
                u.photo_link,
                u.description,
                u.balance,
                u.rating,
                p.name as plan_name
            FROM users u
            INNER JOIN plans p ON u.plan_id = p.id 
        """)
        params = tuple()

        if plan_name:
            query = sql.Composed([
                query,
                sql.SQL(" WHERE p.name = {}").format(sql.Placeholder())
            ])
            params += (plan_name, )
        if limit:
            query = sql.Composed([
                query,
                sql.SQL(" LIMIT {}").format(sql.Placeholder())
            ])
            params += (limit, )

        with PostgresDatabase() as db:
            return db.fetch(
                query=query,
                params=params,
                is_all=True,
            )

    @staticmethod
    def _create_user(user_plan: UserPlanEnum) -> sql.Composed:
        return sql.SQL("""
            WITH selected_plan AS (
                SELECT id, name 
                FROM plans 
                WHERE name = {user_plan}
                LIMIT 1
            )
            INSERT INTO users 
                (first_name, 
                 last_name, 
                 username, 
                 email, 
                 phone_number, 
                 password, 
                 plan_id)
            VALUES (%s, %s, %s, %s, %s, %s, (SELECT id FROM selected_plan))
            RETURNING 
                    id, 
                    first_name, 
                    last_name, 
                    username, 
                    email, 
                    phone_number, 
                    photo_link, 
                    description, 
                    balance, 
                    rating, 
                    (SELECT name FROM selected_plan) AS plan_name;
        """).format(user_plan=sql.Literal(user_plan.value))
  
    @staticmethod
    def create_user_customer(user_data: dict[str, Any]) -> dict[str, Any]:
        query = User._create_user(UserPlanEnum.customer)

        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    (
                        user_data.get("first_name"),
                        user_data.get("last_name"),
                        user_data.get("username"),
                        user_data.get("email"),
                        user_data.get("phone_number", None),
                        user_data.get("password"),
                    )
                )
                user = cursor.fetchone()
                user_payment = user_data.get("payment")

                cursor.execute(
                    """
                        INSERT INTO payments (user_id, payment)
                        VALUES (%s, %s)
                    """,
                    (user.get("id"), user_payment)
                )
    
        return user

    @staticmethod
    def create_user_performer(user_data: dict[str, Any]) -> dict[str, Any]:
        query = User._create_user(UserPlanEnum.performer)
        
        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    (
                        user_data.get("first_name"),
                        user_data.get("last_name"),
                        user_data.get("username"),
                        user_data.get("email"),
                        user_data.get("phone_number", None),
                        user_data.get("password"),
                    )
                )
                user = cursor.fetchone()    
                user_specialities = user_data.get("specialities", None)

                if user_specialities:
                    cursor.execute(
                        """
                            WITH selected_specialities AS (
                                SELECT id
                                FROM specialities
                                WHERE name = ANY(%s)
                            )
                            INSERT INTO users_specialities (user_id, speciality_id)
                            SELECT %s, ssp.id
                            FROM selected_specialities ssp
                        """,
                        (user_specialities, user.get("id"))
                    )
                
        user["specialities"] = user_specialities
        
        return user

    @staticmethod
    def _update_user(user_data: dict[str, Any]) -> sql.Composed:
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder(k))
            for k in user_data.keys()
        )

        return sql.SQL("""
            UPDATE users
            SET {set_clause}
            WHERE id = {id_placeholder}
        """).format(
            set_clause=set_clause,
            id_placeholder=sql.Placeholder("user_id"),
        )

    @staticmethod
    def update_user(user_id: int, user_data: dict[str, Any]) -> dict[str, Any]:
        query = User._update_user(user_data)

        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    {"user_id": user_id, **user_data},
                )
                cursor.execute(
                    """
                        SELECT 
                            u.id,
                            u.first_name,
                            u.last_name,
                            u.username,
                            u.email,
                            u.phone_number,
                            u.photo_link,
                            u.description,
                            u.balance,
                            u.rating,
                            p.name as plan_name
                        FROM users u
                        INNER JOIN plans p ON u.plan_id = p.id 
                        WHERE u.id = %s;
                    """,
                    (user_id, ),
                )

                return cursor.fetchone()
    
    @staticmethod
    def update_user_performer(user_id: int, user_data: dict[str, Any]) -> dict[str, Any]:
        query = User._update_user(user_data)

        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    {"user_id": user_id, **user_data}
                )

                user_specialities = user_data.get("specialities", None)

                if user_specialities:
                    cursor.execute(
                        """
                            DELETE FROM users_specialities 
                            WHERE user_id = %s
                        """,
                        (user_id, )
                    )

                    cursor.execute(
                        """
                            WITH selected_specialities AS (
                                SELECT id
                                FROM specialities
                                WHERE name = ANY(%s)
                            )
                            INSERT INTO users_specialities (user_id, speciality_id)
                            SELECT %s, ssp.id
                            FROM selected_specialities ssp
                        """,
                        (user_specialities, user_id)
                    )
                
                cursor.execute(
                    """
                        SELECT 
                            u.id AS id,
                            first_name,
                            last_name,
                            username,
                            email,
                            phone_number,
                            photo_link,
                            description,
                            balance,
                            rating,
                            pln.name AS plan_name,
                            is_verified,
                            block_expired,
                            delete_date,
                            is_blocked
                        FROM users u
                        JOIN plans pln
                            ON pln.id = u.plan_id
                        WHERE u.id = %s 
                    """,
                    (user_id, )
                )
                
                return cursor.fetchone()

    @staticmethod
    def update_user_details(user_id: int, user_data: dict[str, Any]) -> dict[str, Any]:
        query = User._update_user(user_data)

        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    {"user_id": user_id, **user_data},
                )
                cursor.execute(
                    """
                        SELECT 
                            u.id AS id,
                            first_name,
                            last_name,
                            username,
                            email,
                            phone_number,
                            photo_link,
                            description,
                            balance,
                            rating,
                            pln.name AS plan_name,
                            is_verified,
                            block_expired,
                            delete_date,
                            is_blocked
                        FROM users u
                        JOIN plans pln
                            ON pln.id = u.plan_id
                        WHERE u.id = %s 
                    """,
                    (user_id, ),
                )

                return cursor.fetchone()
