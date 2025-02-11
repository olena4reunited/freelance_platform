from functools import wraps
from typing import Any, Annotated

import jwt
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from server.app.controllers.user_controller import UserController
from server.app.database.database import PostgresDatabase
from server.app.models.models import User, Plan
from server.app.utils.auth import verify_token


security = HTTPBearer()


def handle_jwt_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Expired token")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=403, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return wrapper


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> dict[str, Any] | None:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        payload = verify_token(token)
        user = UserController.get_user_by_token(token)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or token invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@handle_jwt_errors
def required_plans(allowed_plans: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict[str, Any] = Depends(get_current_user), **kwargs) -> dict[str, Any]:
            plan_name = user["plan_name"]

            if not plan_name:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
            if plan_name not in allowed_plans:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access for current user denied"
                )

            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator
