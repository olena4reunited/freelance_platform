from enum import Enum
from typing import Any

from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel
from server.app.models.sql_builder import SQLBuilder


class UserPlanEnum(Enum):
    customer = "customer"
    performer = "performer"


class User(BaseModel):
    table_name = "users"

    @staticmethod
    def get_user_by_id(user_id: int) -> dict[str, Any]:
        query, params = (
            SQLBuilder(table_name=User.table_name) \
            .select(
                "id",
                "first_name",
                "last_name",
                "username",
                "email",
                "phone_number",
                "photo_link",
                "description",
                "balance",
                "rating",
                "plan_id",
                "is_verified",
                "block_expired",
                "delete_date",
                "is_blocked"
            ) \
            .where(where_column="id", params=user_id) \
            .get()
        )

        with PostgresDatabase() as db:
            return db.fetch(query, params)

    @staticmethod
    def get_user_by_field(field: str, value: str | int) -> dict[str, Any]:
        query, params = (
            SQLBuilder(table_name=User.table_name) \
            .select() \
            .where(where_column=field, params=value) \
            .get()
        )

        with PostgresDatabase() as db:
            return db.fetch(query, params)

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
    def create_user(user_data: dict[str, Any], user_plan: UserPlanEnum) -> dict[str, Any]:
        query = sql.SQL("""
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
            RETURNING id, first_name, last_name, username, email, phone_number, photo_link, description, balance, rating, (SELECT name FROM selected_plan) AS plan_name;
        """).format(user_plan=sql.Literal(user_plan.value))

        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                query=query,
                params=(
                    user_data.get("first_name"),
                    user_data.get("last_name"),
                    user_data.get("username"),
                    user_data.get("email"),
                    user_data.get("phone_number", None),
                    user_data.get("password"),
                )
            )

    @staticmethod
    def update_user(user_id: int, user_data: dict[str, Any]) -> dict[str, Any]:
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder(k))
            for k in user_data.keys()
        )

        query = sql.SQL("""
            UPDATE users
            SET {set_clause}
            WHERE id = {id_placeholder}
        """).format(
            set_clause=set_clause,
            id_placeholder=sql.Placeholder("user_id"),
        )

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
