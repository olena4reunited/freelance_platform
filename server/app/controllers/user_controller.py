from datetime import timedelta
from typing import Any

from server.app.models.payment_model import Payment
from server.app.models.user_model import User
from server.app.models.plan_model import Plan
from server.app.models.user_model import UserPlanEnum
from server.app.utils.auth import (
    get_password_hash,
    create_token,
    refresh_token,
    verify_token
)
from server.app.utils.crypto import encrypt_data


class UserController:
    @staticmethod
    def create_user_customer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data.pop("password_repeat")
        user_data["payment"] = encrypt_data(user_data["payment"])

        user = User.create_user(user_data, UserPlanEnum.customer)
        Payment.create_payment(user["id"], user_data["payment"])

        return user

    @staticmethod
    def create_user_performer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data.pop("password_repeat")

        return User.create_user(user_data, UserPlanEnum.performer)

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
        return User.get_user_by_field("id", user_id)

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
        return User.get_all_users(plan, limit)


    @staticmethod
    def update_user(user_id: int, updated_user_data: dict) -> dict[str, Any]:
        if "password" in updated_user_data:
            updated_user_data["password"] = get_password_hash(updated_user_data["password"])

        return User.update_user(user_id, updated_user_data)


    @staticmethod
    def delete_user(user_id: int) -> None:
        User.delete_record_by_id(user_id)
