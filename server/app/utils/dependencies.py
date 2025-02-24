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
            CustomHTTPException.raise_exception(
                status_code=401,
                detail="Signature expired. Please login again."
            )
        except jwt.InvalidTokenError as e:
            CustomHTTPException.raise_exception(
                status_code=403,
                detail="Invalid token. Could not process request."
            )
    return wrapper


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> dict[str, Any] | None:
    if credentials is None:
        CustomHTTPException.raise_exception(
            status_code=401,
            detail="Authentication credentials were not provided"
        )
    try:
        token = credentials.credentials
        verify_token(token)
        user = UserController.get_user_by_token(token)

        if user is None:
            CustomHTTPException.raise_exception(
                status_code=400,
                detail="User does not exist. Provide valid credentials."
            )

        return user

    except jwt.PyJWTError as e:
        CustomHTTPException.raise_exception(
            status_code=401,
            detail="Could not validate credentials."
        )

@handle_jwt_errors
def required_plans(allowed_plans: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user: dict[str, Any] = Depends(get_current_user), **kwargs) -> dict[str, Any]:
            plan_name = user["plan_name"]

            if not plan_name:
                CustomHTTPException.raise_exception(
                    status_code=400,
                    detail="No plan name provided or provided plan does not exist.",
                    extra={"plan_name": plan_name}
                )
            if plan_name not in allowed_plans:
                CustomHTTPException.raise_exception(
                    status_code=403,
                    detail="Plan '{}' is not allowed to get access to resource".format(plan_name)
                )

            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def required_permissions(permissions: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user: dict[str, Any] = Depends(get_current_user), **kwargs) -> dict[str, Any]:
            plan_name = user["plan_name"]

            if not plan_name:
                CustomHTTPException.raise_exception(
                    status_code=400,
                    detail="No plan name provided or provided plan does not exist.",
                    extra={"plan_name": plan_name}
                )

            user_permissions = set(json.loads(redis_client.hgetall(plan_name).get("permissions")))

            if not set(permissions).issubset(user_permissions):
                CustomHTTPException.raise_exception(
                    status_code=403,
                    detail="User does not have permission to access resource"
                )

            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator
