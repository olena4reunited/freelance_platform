import json
from functools import wraps
from typing import Any, Annotated, Callable

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from server.app.controllers.user_controller import UserController
from server.app.utils.auth import verify_token
from server.app.utils.redis_client import redis_client
from server.app.utils.exceptions import CustomHTTPException


security = HTTPBearer()


def handle_jwt_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError as e:
            CustomHTTPException.unauthorised(detail=f"Signature expired: {repr(e)}")
        except jwt.InvalidTokenError as e:
            CustomHTTPException.forbidden(detail=f"Invalid token: {repr(e)}")
    return wrapper


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> dict[str, Any] | None:
    if credentials is None:
        CustomHTTPException.unauthorised(detail="Authorization header is missing")

    try:
        token = credentials.credentials
        payload = verify_token(token)
        user = UserController.get_user_by_token(token)

        if user is None:
            CustomHTTPException.bad_request(detail="User not found")

        return user

    except jwt.PyJWTError as e:
        CustomHTTPException.unauthorised(detail="Authorization error: " + str(e))


@handle_jwt_errors
def required_plans(allowed_plans: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user: dict[str, Any] = Depends(get_current_user), **kwargs) -> dict[str, Any]:
            plan_name = user["plan_name"]

            if not plan_name:
                CustomHTTPException.not_found(detail="Plan not found")
            if plan_name not in allowed_plans:
                CustomHTTPException.forbidden(detail="Access denied")

            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def required_permissions(permissions: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user: dict[str, Any] = Depends(get_current_user), **kwargs) -> dict[str, Any]:
            plan_name = user["plan_name"]

            if not plan_name:
                CustomHTTPException.not_found(detail="Plan not found")

            user_permissions = set(json.loads(redis_client.hgetall(plan_name).get("permissions")))

            if not set(permissions).issubset(user_permissions):
                CustomHTTPException.forbidden(detail="Permission denied")

            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator
