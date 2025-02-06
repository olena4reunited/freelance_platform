from typing import Any

from server.app.models.models import User
from server.app.utils.auth import get_password_hash


class UserController:
    @staticmethod
    def create_user_customer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data.pop("password_repeat")
        new_user = User.create_record(**user_data)

        return new_user

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
    def authenticate_user():
        ...

    @staticmethod
    def verify_user():
        ...
