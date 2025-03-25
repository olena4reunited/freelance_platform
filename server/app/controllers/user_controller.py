from datetime import timedelta
from typing import Any

from server.app.models.user_model import User
from server.app.models.plan_model import Plan
from server.app.models.speciality_model import Speciality
from server.app.models.user_model import UserPlanEnum
from server.app.utils.auth import (
    get_password_hash,
    create_token,
    refresh_token,
    verify_token,
    generate_password,
    generate_username
)
from server.app.utils.crypto import encrypt_data
from server.app.utils.auth import oauth
from server.app.utils.exceptions import GlobalException
from server.app.utils.redis_client import redis_reset_passwd
from server.app.services.smtp_service import generate_code


class UserController:
    @staticmethod
    def create_user_customer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data["payment"] = encrypt_data(user_data["payment"])

        return User.create_user_customer(user_data)

    @staticmethod
    def create_user_performer(user_data: dict) -> dict[str, Any]:
        user_data["password"] = get_password_hash(user_data["password"])

        return User.create_user_performer(user_data)

    @staticmethod
    def authenticate_user(user_data: dict) -> dict[str, Any]:
        user = dict()

        if user_data["username"]:
            user = User.get_user_by_field("username", user_data["username"])
        elif user_data["email"]:
            user = User.get_user_by_field("email", user_data["email"])

        user_data_tokenize = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "username": user["username"],
            "email": user["email"],
            "phone_number": user["phone_number"],
            "plan_name": user["plan_name"],
        }

        access_tkn = create_token(user_data_tokenize, timedelta(minutes=3000))
        refresh_tkn = create_token(user_data_tokenize, timedelta(days=7))

        return {
            "access_token": access_tkn,
            "refresh_token": refresh_tkn,
            "token_type": "bearer"
        }

    @staticmethod
    async def authenticate_user_google(token: dict[str, Any], plan: str):
        user_info = await oauth.google.parse_id_token(token, None)
        plan_enum = UserPlanEnum(plan) if plan else None

        if not User.get_user_by_field("email", user_info.get("email")):
            if not plan:
                GlobalException.CustomHTTPException.raise_exception(
                    status_code=400,
                    detail="Plan is required in user creation"
                )

            user_data = {
                "first_name": user_info.get("given_name"),
                "last_name": user_info.get("family_name"),
                "username": generate_username(
                    first_name=user_info.get("given_name"),
                    last_name=user_info.get("family_name")
                ),
                "email": user_info.get("email"),
                "phone_number": None,
                "password": generate_password()
            }

            user = User.create_user(
                user_data=user_data,
                user_plan=plan_enum
            )
        else:
            user = User.get_user_by_field("email", user_info.get("email"))
        
        user_data_tokenize = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "username": user["username"],
            "email": user["email"],
            "phone_number": user["phone_number"],
            "plan_name": user["plan_name"],
        }

        access_tkn = create_token(user_data_tokenize, timedelta(minutes=3000))
        refresh_tkn = create_token(user_data_tokenize, timedelta(days=7))

        return {
            "access_token": access_tkn,
            "refresh_token": refresh_tkn,
            "token_type": "bearer"
        }

    @staticmethod
    def password_reset_request(email: str) -> None:
        user = User.get_user_by_field("email", email)
        
        if not user:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=404,
                detail="User with this email is not exist"
            )
        
            return
        
        code = generate_code()
        redis_reset_passwd.hset(name="passwd_reset", key=email, value=code)
      
        return code

    @staticmethod
    def password_reset_confirm_request(confirm_data: dict[str, Any]):
        user = User.get_user_by_field("email", confirm_data["email"])
        
        if not user:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=404,
                detail="User with this email is not exist"
            )
        
            return
        if redis_reset_passwd.hget(name="passwd_reset", key=confirm_data["email"]) != confirm_data["code"]:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Reset code is not match"
            )
    
            return
        
        if confirm_data["password"] != confirm_data["password_repeat"]:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password is not match"
            )
        
            return
        
        hashed_password = get_password_hash(confirm_data["password"])
        redis_reset_passwd.hdel("passwd_reset", confirm_data["email"])
        
        return User.update_user(user_id=user["id"], user_data={"password": hashed_password})


    @staticmethod
    def refresh_bearer_token(refresh_tkn: str) -> dict[str, Any]:
        return refresh_token(refresh_tkn)

    @staticmethod
    def get_user(user_id: int) -> dict[str, Any]:
        return User.get_user_by_id(user_id)

    @staticmethod
    def get_user_by_token(access_tkn: str) -> dict[str, Any]:
        username = verify_token(access_tkn)["content"]["username"]
        user = User.get_user_by_field("username", username)

        return user

    @staticmethod
    def add_performer_specialities(user: dict[str, Any]):
        user.update(
            Speciality.get_users_specialities_array(user.get("id"))
        )

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
