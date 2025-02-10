from datetime import timedelta
from typing import Any
import threading

from server.app.models.models import User, Plan
from server.app.controllers.payment_controller import PaymentController
from server.app.utils.auth import (
    get_password_hash,
    create_token,
    refresh_token,
    verify_token
)
from server.app.utils.crypto import encrypt_data
from server.app.database.database import PostgresDatabase
from server.app.utils.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)


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

            payment_threading = threading.Thread(target=PaymentController.create_payment, args=(user["id"], user["payment"]))
            payment_threading.start()

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

        access_tkn = create_token(user_data_tokenize, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_tkn = create_token(user_data_tokenize, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

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
    def get_user_by_token(access_tkn: str) -> dict[str, Any]:
        username = verify_token(access_tkn)["content"]["username"]

        user = User.get_user_by_field("username", username)
        plan_name = Plan.get_record_by_id(user["plan_id"])["name"]

        user["plan_name"] = plan_name
        user.pop("plan_id")

        return user
