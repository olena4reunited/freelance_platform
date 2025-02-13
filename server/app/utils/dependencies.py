from functools import wraps
from typing import Any, Annotated

import jwt
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from server.app.controllers.user_controller import UserController
from server.app.database.database import PostgresDatabase
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


def required_permissions(permissions: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict[str, Any] = Depends(get_current_user), **kwargs) -> dict[str, Any]:
            plan_name = user["plan_name"]

            if not plan_name:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plan not found"
                )

            with PostgresDatabase() as db:
                user_permissions = db.fetch(
                    """
                        SELECT prm.name AS permission_name
                        FROM plans pln
                        INNER JOIN plans_permissions pp ON pln.id = pp.plan_id
                        INNER JOIN permissions prm ON pp.permission_id = prm.id
                        WHERE pln.name = %s
                    """,
                    (plan_name, ),
                    is_all=True
                )

            if not set(permissions).issubset({perm["permission_name"] for perm in user_permissions}):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access for current user denied"
                )

            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator
