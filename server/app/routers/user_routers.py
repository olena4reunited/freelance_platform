from typing import Union

from fastapi import APIRouter, HTTPException
from starlette.responses import RedirectResponse

from server.app.schemas.users_schemas import (
    UserCreate,
    UserResponse
)
from server.app.controllers.user_controller import UserController
from server.app.validators.user_validators import UserValidator, MethodEnum


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=Union[UserResponse, RedirectResponse])
def create_user(user_data: UserCreate):
    try:
        UserValidator(
            MethodEnum.create,
            user_data.email,
            user_data.password,
            user_data.password_repeat,
            user_data.phone_number) \
            .validate_email() \
            .validate_password() \
            .validate_phone_number()

        match user_data.plan_id:
            case 3:
                UserController.create_user_customer(**user_data.model_dump())
                return RedirectResponse(url="/payments/add_payment", status_code=302)
            case 4:
                return UserController.create_user_performer(**user_data.model_dump())
            case _:
                raise HTTPException(
                    status_code=403,
                    detail="You are not allowed to choose this role"
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
            updated_user_data.get("email", None),
            updated_user_data.get("password", None),
            updated_user_data.get("password_repeat", None),
            updated_user_data.get("phone_number", None)) \
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
