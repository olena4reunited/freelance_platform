import os
from datetime import timedelta, datetime, timezone

import jwt
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from starlette import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


with open("../../keys/private.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

with open("../../keys/public.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read())


def create_access_token(username: str):
    exp = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": username,
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": exp
    }

    token = jwt.encode(payload=payload, key=private_key, alg="RS256")

    return token


def verify_token(token: str) -> dict[str, str] | None:
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


