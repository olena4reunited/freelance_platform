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

        with PostgresDatabase() as db:
            result = db.fetch_one(
                """
                WITH new_user AS (
                    INSERT INTO users (first_name, last_name, username, email, phone_number, password, plan_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, first_name, last_name, username, email, phone_number, password, photo_link, description, balance, rating, plan_id
                )
                INSERT INTO payments (user_id, payment)
                VALUES ((SELECT id FROM new_user), %s)
                RETURNING (
                    SELECT json_build_object(
                        'id', id,
                        'first_name', first_name,
                        'last_name', last_name,
                        'username', username,
                        'email', email,
                        'phone_number', phone_number,
                        'photo_link', photo_link,
                        'description', description,
                        'balance', balance,
                        'rating', rating,
                        'plan_id', plan_id
                    ) 
                    FROM new_user
                ) AS user_data;
                """,
                (
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["username"],
                    user_data["email"],
                    user_data["phone_number"],
                    user_data["password"],
                    user_data["plan_id"],
                    user_data["payment"],
                )
            )

        return result["user_data"]


    @staticmethod
    def create_user_performer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data.pop("password_repeat")
        new_user = User.create_record(**user_data)

        return new_user

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
