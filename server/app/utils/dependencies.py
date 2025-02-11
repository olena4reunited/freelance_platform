from functools import wraps
from typing import Any

import jwt
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

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


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict[str, Any] | None:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_token(credentials.credentials)
        username = payload.get("sub")

        return User.get_user_by_field("username", username)

    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@handle_jwt_errors
def role_required(allowed_plans: list[str]):
    def dependency(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        plan_name = Plan.get_record_by_id(user["plan_id"])["name"]

        if not plan_name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        if plan_name not in allowed_plans:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access for current user denied"
            )

        return user

    return dependency
