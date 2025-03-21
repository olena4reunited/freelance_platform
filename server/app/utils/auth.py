import os
from datetime import timedelta, datetime, timezone
from typing import Any
import string
import secrets
import random

import jwt
from cryptography.hazmat.primitives import serialization
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

from server.app.utils.exceptions import GlobalException


CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

config = Config(os.path.join(os.path.dirname(__file__), ".env"))
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

selection_list = string.ascii_letters + string.digits + string.punctuation
selection_leterrs_nums = string.ascii_lowercase + string.digits


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_password():
    passwd = ""
    
    for _ in range(random.randint(16, 64)):
        passwd += "".join(secrets.choice(selection_list))
    
    return get_password_hash(password=passwd)


def generate_username(first_name: str, last_name: str):
    username = f"{first_name.lower()}_{last_name.lower()}_"

    for _ in range(16):
        username += "".join(secrets.choice(selection_leterrs_nums))
    
    return username


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

    access_tkn = create_token(user_data, timedelta(minutes=3000))
    refresh_tkn = create_token(user_data, timedelta(days=7))

    return (
        {
            "access_token": access_tkn,
            "refresh_token": refresh_tkn,
            "token_type": "bearer"
        }
    )


def verify_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])

        if not payload.get("sub") or not isinstance(payload.get("sub"), str):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=401,
                detail="Invalid token",
            )

        return payload

    except (jwt.PyJWTError, jwt.ExpiredSignatureError) as e:
        GlobalException.CustomHTTPException.raise_exception(
            status_code=401,
            detail="Invalid token",
        )
