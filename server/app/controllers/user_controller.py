import re
from typing import Any

from server.app.models.models import User
from server.app.utils.auth import get_password_hash, verify_password
from server.app.utils.crypto import encrypt_data
from server.app.database.database import PostgresDatabase


class UserController:
    @staticmethod
    def create_user_customer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data.pop("password_repeat")

        user_data["payment"] = encrypt_data(bytes(user_data["payment"], encoding="utf-8"))

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
                (
                    user["id"],
                    user_data["payment"],
                )
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
    def get_user(user_id: int) -> dict[str, Any]:
        user = User.get_record_by_id(user_id)

        return user

    @staticmethod
    def update_user(user_id: int, updated_user_data: dict) -> dict[str, Any]:
        if "password" in updated_user_data:
            updated_user_data["password"] = get_password_hash(updated_user_data["password"])

        updated_user = User.update_record(user_id, **updated_user_data)

        return updated_user

    @staticmethod
    def delete_user(user_id: int) -> dict[str, Any]:
        User.delete_record_by_id(user_id)

        return {"message": "User profile was deleted successfully"}

    @staticmethod
    def authenticate_user(login_field: str, password: str):
        if re.match(r"\w+@[a-zA-Z_]+\.[a-zA-Z]{2,6}", login_field):
            user = User.get_user_by_field(field="email", value=login_field)
        else:
            user = User.get_user_by_field(field="username", value=login_field)

        if not user:
            return False
        if not verify_password(password, user["password"]):
            return False

        return user

    @staticmethod
    def verify_user():
        ...
