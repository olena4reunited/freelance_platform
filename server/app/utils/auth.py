import os
from datetime import timedelta, datetime, timezone
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from server.app.utils.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


with open(os.path.join(os.path.dirname(__file__), "../../keys/private.pem"), "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

with open(os.path.join(os.path.dirname(__file__), "../../keys/public.pem"), "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read())


def create_token(user_data: dict[str, Any], expires_in: timedelta):
    exp = datetime.now(timezone.utc) + expires_in

    payload = {
        "sub": user_data["username"],
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": exp,
        "content": user_data
    }

    token = jwt.encode(payload=payload, key=private_key, algorithm="RS256")

    return token


def refresh_token(token: str):
    payload = jwt.decode(token, key=public_key, algorithms=["RS256"])

    user_data = payload["content"]

    access_tkn = create_token(user_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_tkn = create_token(user_data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    return (
        {
            "access_token": access_tkn,
            "refresh_token": refresh_tkn,
            "token_type": "bearer"
        }
    )


def verify_token(token: str) -> dict[str, Any] | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])

        if not payload.get("sub") or not isinstance(payload.get("sub"), str):
            raise credentials_exception

        return payload

    except jwt.PyJWTError:
        raise credentials_exception
