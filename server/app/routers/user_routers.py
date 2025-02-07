from typing import Union

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import RedirectResponse

from server.app.schemas.users_schemas import (
    UserResponse,
    UserCreateCustomer,
    UserCreatePerformer
)
from server.app.controllers.user_controller import UserController
from server.app.validators.user_validators import UserValidator, MethodEnum


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
def create_user(user_data: Union[UserCreateCustomer, UserCreatePerformer]):
    try:
        UserValidator(
            MethodEnum.create,
            user_data.username,
            user_data.email,
            user_data.password,
            user_data.password_repeat,
            user_data.phone_number) \
            .validate_username() \
            .validate_email() \
            .validate_password() \
            .validate_phone_number()

        if user_data.plan_id == 3 and isinstance(user_data, UserCreateCustomer):
            return UserController.create_user_customer(**user_data.model_dump())
        elif user_data.plan_id == 4 and isinstance(user_data, UserCreatePerformer):
            return UserController.create_user_performer(**user_data.model_dump())
        else:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to choose this plan"
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    try:
        return UserController.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user_data: dict):
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

        return UserController.update_user(user_id, **updated_user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        return UserController.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
