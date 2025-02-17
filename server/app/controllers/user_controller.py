from datetime import timedelta
from typing import Any

from server.app.models.user_model import User
from server.app.models.plan_model import Plan
from server.app.utils.auth import (
    get_password_hash,
    create_token,
    refresh_token,
    verify_token
)
from server.app.utils.crypto import encrypt_data
from server.app.database.database import PostgresDatabase


class UserController:
    @staticmethod
    def create_user_customer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data.pop("password_repeat")

        user_data["payment"] = encrypt_data(user_data["payment"])

        with PostgresDatabase(on_commit=True) as db:
            user = db.fetch(
                """
                WITH selected_plan AS (
                    SELECT id, name FROM plans WHERE name = 'customer' LIMIT 1
                )
                INSERT INTO users (first_name, last_name, username, email, phone_number, password, plan_id)
                VALUES (%s, %s, %s, %s, %s, %s, (SELECT id FROM selected_plan))
                RETURNING id, first_name, last_name, username, email, phone_number, photo_link, description, balance, rating, (SELECT name FROM selected_plan) AS plan_name;
                """,
                (
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["username"],
                    user_data["email"],
                    user_data["phone_number"],
                    user_data["password"],
                )
            )

            db.execute_query(
                """
                    INSERT INTO payments (user_id, payment)
                    VALUES (%s, %s) 
                """,
                (user["id"], user_data["payment"])
            )

        return user


    @staticmethod
    def create_user_performer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data.pop("password_repeat")

        with PostgresDatabase(on_commit=True) as db:
            result = db.fetch(
                """
                WITH selected_plan AS (
                    SELECT id, name FROM plans WHERE name = 'performer' LIMIT 1
                )
                INSERT INTO users (first_name, last_name, username, email, phone_number, password, plan_id)
                VALUES (%s, %s, %s, %s, %s, %s, (SELECT id FROM selected_plan))
                RETURNING id, first_name, last_name, username, email, phone_number, photo_link, description, balance, rating, (SELECT name FROM selected_plan) AS plan_name;
                """,
                (
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["username"],
                    user_data["email"],
                    user_data["phone_number"],
                    user_data["password"],
                )
            )

            return result

    @staticmethod
    def authenticate_user(user_data: dict) -> dict[str, Any]:
        user = dict()

        if user_data["username"]:
            user = User.get_user_by_field("username", user_data["username"])
        elif user_data["email"]:
            user = User.get_user_by_field("email", user_data["email"])

        plan_name = Plan.get_record_by_id(user["plan_id"])

        user_data_tokenize = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "username": user["username"],
            "email": user["email"],
            "phone_number": user["phone_number"],
            "plan_name": plan_name["name"],
        }

        access_tkn = create_token(user_data_tokenize, timedelta(minutes=3000))
        refresh_tkn = create_token(user_data_tokenize, timedelta(days=7))

        return {
            "access_token": access_tkn,
            "refresh_token": refresh_tkn,
            "token_type": "bearer"
        }

    @staticmethod
    def refresh_bearer_token(refresh_tkn: str) -> dict[str, Any]:
        return refresh_token(refresh_tkn)

    @staticmethod
    def get_user(user_id: int) -> dict[str, Any]:
        with PostgresDatabase() as db:
            return db. fetch(
                """
                    SELECT u.id, u.first_name, u.last_name, u.username, u.email, u.phone_number, u.photo_link, u.description, u.balance, u.rating, p.name as plan_name
                    FROM users u
                    INNER JOIN plans p ON u.plan_id = p.id
                    WHERE u.id = %s
                """,
                (user_id,)
            )

    @staticmethod
    def get_user_by_token(access_tkn: str) -> dict[str, Any]:
        username = verify_token(access_tkn)["content"]["username"]

        user = User.get_user_by_field("username", username)
        plan_name = Plan.get_record_by_id(user["plan_id"])["name"]

        user["plan_name"] = plan_name
        user.pop("plan_id")

        return user

    @staticmethod
    def get_all_users(
            plan: str,
            limit: int = 0
    ) -> list[dict[str, Any]]:
        with PostgresDatabase() as db:
            query = """
                SELECT u.id, u.first_name, u.last_name, u.username, u.email, u.phone_number, u.photo_link, u.description, u.balance, u.rating, p.name as plan_name
                FROM users u
                INNER JOIN plans p ON u.plan_id = p.id 
            """
            params = tuple()

            if plan:
                query += " WHERE p.name = %s"
                params += (plan,)
            if limit:
                query += " LIMIT %s"
                params += (limit,)

            return db.fetch(query + ";", params, is_all=True)


    @staticmethod
    def update_user(user_id: int, updated_user_data: dict) -> dict[str, Any]:
        if "password" in updated_user_data:
            updated_user_data["password"] = get_password_hash(updated_user_data["password"])

        set_clause = ", ".join(f"{key} = %s" for key in updated_user_data.keys())

        with PostgresDatabase() as db:
            db.execute_query(
                f"UPDATE users SET {set_clause} WHERE id = %s",
                tuple(updated_user_data.values()) + (user_id,),
            )

            return db.fetch(
                """
                    SELECT u.id, u.first_name, u.last_name, u.username, u.email, u.phone_number, u.photo_link, u.description, u.balance, u.rating, p.name as plan_name
                    FROM users u
                    INNER JOIN plans p ON u.plan_id = p.id 
                    WHERE u.id = %s;
                """,
                (user_id, )
            )


    @staticmethod
    def delete_user(user_id: int) -> None:
        User.delete_record_by_id(user_id)
