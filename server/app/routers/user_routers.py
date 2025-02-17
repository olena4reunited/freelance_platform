from typing import Any

import jwt
from fastapi import APIRouter, Depends, Query
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
from server.app.utils.dependencies import (
    get_current_user,
    required_plans,
    required_permissions,
    handle_jwt_errors
)
from server.app.utils.exceptions import (
    handle_db_errors,
    CustomHTTPException
)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/customer/register", response_model=UserResponse)
@handle_db_errors
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
        CustomHTTPException.bad_request(detail=f"Could not register user: {repr(e)}")


@router.post("/performer/register", response_model=UserResponse)
@handle_db_errors
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
        CustomHTTPException.bad_request(detail=f"Could not register user: {repr(e)}")


@router.post("/token", response_model=Token)
@handle_db_errors
def create_user_token(user_data: UserCreateToken):
    try:
        UserTokenValidator(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password) \
        .validate_user_exists()

        return UserController.authenticate_user(user_data.model_dump())
    except Exception as e:
        CustomHTTPException.unauthorised(detail=f"Could not authenticate user: {repr(e)}")

@router.post("/token/refresh", response_model=Token)
@handle_jwt_errors
@handle_db_errors
def refresh_user_token(refresh_tkn: dict[str, str]):
    try:
        return UserController.refresh_bearer_token(refresh_tkn["refresh_token"])
    except Exception as e:
        CustomHTTPException.unauthorised(detail=f"Could not refresh the token: {repr(e)}")


@router.get("/me", response_model=UserResponse)
@handle_db_errors
@required_plans(["admin", "moderator", "customer", "performer"])
@required_permissions(["read_own_user_details"])
def read_user_me(user: dict[str, Any] = Depends(get_current_user)):
    try:
        return user
    except Exception as e:
        CustomHTTPException.unauthorised(detail=f"Could not read user: {repr(e)}")


@router.patch("/me", response_model=UserResponse)
@handle_db_errors
@required_plans(["admin", "moderator", "customer", "performer"])
@required_permissions(["read_own_user_details", "update_own_user_details"])
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
        CustomHTTPException.bad_request(detail=f"Could not update user: {repr(e)}")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@handle_db_errors
@required_plans(["admin", "moderator", "customer", "performer"])
@required_permissions(["read_own_user_details", "update_own_user_details", "delete_own_user"])
def delete_user(
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        UserController.delete_user(user["id"])
        return
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not delete user: {repr(e)}")


@router.get("/list", response_model=list[UserResponse])
@handle_db_errors
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_users_list"])
def read_all_users(
        plan: str = Query(None, description="filter by role"),
        limit: int = Query(None, description="number of users to return"),
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        return UserController.get_all_users(plan, limit)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not retrieve users: {repr(e)}")


@router.get("/{user_id}", response_model=UserResponse)
@handle_db_errors
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_users_list", "read_user_details"])
def get_user(
        user_id: int,
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        return UserController.get_user(user_id)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not retrieve user: {repr(e)}")


@router.patch("/{user_id}", response_model=UserResponse)
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_all_users_list", "read_user_details", "update_user_details"])
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
        CustomHTTPException.bad_request(detail=f"Could not update user: {repr(e)}")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_user_details", "update_user_details", "delete_user"])
def delete_user(
        user_id: int,
        user : dict[str, Any] = Depends(get_current_user)
):
    try:
        return UserController.delete_user(user_id)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not delete user: {repr(e)}")
