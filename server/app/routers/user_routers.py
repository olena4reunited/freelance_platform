from typing import Any

import jwt
from fastapi import APIRouter, HTTPException, Depends, Query
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
from server.app.utils.dependencies import required_plans, get_current_user


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
@required_plans(["admin", "moderator", "customer", "performer"])
def read_user_me(user: dict[str, Any] = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserResponse)
@required_plans(["admin", "moderator", "customer", "performer"])
def update_user(
        updated_user_data: dict[str, Any],
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
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

        return UserController.update_user(user["id"], updated_user_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@required_plans(["admin", "moderator", "customer", "performer"])
def delete_user(
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        UserController.delete_user(user["id"])
        return
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/list", response_model=list[UserResponse])
@required_plans(["admin", "moderator"])
def read_all_users(
        plan: str = Query(None, description="filter by role"),
        limit: int = Query(None, description="number of users to return"),
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        return UserController.get_all_users(plan, limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
@required_plans(["admin", "moderator"])
def get_user(
        user_id: int,
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        return UserController.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
@required_plans(["admin"])
def edit_user(
        user_id: int,
        updated_user_data: dict[str, Any],
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
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

        return UserController.update_user(user_id, updated_user_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}")
@required_plans(["admin"])
def delete_user(
        user_id: int,
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        return UserController.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
