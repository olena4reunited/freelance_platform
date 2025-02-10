from typing import Any

import jwt
from fastapi import APIRouter, HTTPException, Header
from starlette import status

from server.app.schemas.token_schemas import Token
from server.app.schemas.users_schemas import (
    UserResponse,
    UserCreateCustomer,
    UserCreatePerformer,
    UserCreateToken
)
from server.app.controllers.user_controller import UserController
from server.app.validators.user_validators import (
    UserValidator,
    UserTokenValidator,
    MethodEnum
)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/customer/register", response_model=UserResponse)
def create_user_customer(user_customer_data: UserCreateCustomer):
    try:
        UserValidator(
            MethodEnum.create,
            user_customer_data.username,
            user_customer_data.email,
            user_customer_data.password,
            user_customer_data.password_repeat,
            user_customer_data.phone_number) \
            .validate_username() \
            .validate_email() \
            .validate_password() \
            .validate_phone_number()

        return UserController.create_user_customer(user_customer_data.model_dump())

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/performer/register", response_model=UserResponse)
def create_user_performer(user_performer_data: UserCreatePerformer):
    try:
        UserValidator(
            MethodEnum.create,
            user_performer_data.username,
            user_performer_data.email,
            user_performer_data.password,
            user_performer_data.password_repeat,
            user_performer_data.phone_number) \
            .validate_username() \
            .validate_email() \
            .validate_password() \
            .validate_phone_number()

        return UserController.create_user_performer(user_performer_data.model_dump())

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/token", response_model=Token)
def create_user_token(user_data: UserCreateToken):
    try:
        UserTokenValidator(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password) \
        .validate_user_exists()

        return UserController.authenticate_user(user_data.model_dump())

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/token/refresh", response_model=Token)
def refresh_user_token(refresh_tkn: dict[str, str]):
    if not refresh_tkn["refresh_token"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Refresh Token")

    try:
        return UserController.refresh_bearer_token(refresh_tkn["refresh_token"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserResponse)
def read_user_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")

        user = UserController.get_user_by_token(token)

        return user
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/me", response_model=UserResponse)
def update_user( updated_user_data: dict[str, Any], authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")

        UserValidator(
            MethodEnum.update,
            updated_user_data.get("username", None),
            updated_user_data.get("email", None),
            updated_user_data.get("password", None),
            updated_user_data.get("password_repeat", None),
            updated_user_data.get("phone_number", None)) \
            .validate_username() \
            .validate_email() \
            .validate_password() \
            .validate_phone_number()

        user = UserController.get_user_by_token(token)

        return UserController.update_user(user["id"], **updated_user_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    try:
        return UserController.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        return UserController.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
