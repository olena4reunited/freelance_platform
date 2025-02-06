from fastapi import APIRouter, HTTPException

from server.app.schemas.users_schemas import (
    UserResponse,
    UserBase
)
from server.app.controllers.user_controller import UserController
from server.app.validators.user_validators import validate_email, validate_password, validate_phone_number

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserResponse)
def create_user(user_data: UserBase):
    try:
        validate_email(user_data.email)
        validate_password(user_data.password)
        validate_phone_number(user_data.phone_number)
        return UserController.create_user(**user_data.model_dump())
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
        if updated_user_data.get("email"):
            validate_email(updated_user_data.get("email"))
        if updated_user_data.get("password"):
            validate_password(updated_user_data.get("password"))
        if updated_user_data.get("phone_number"):
            validate_phone_number(updated_user_data.get("phone_number"))

        return UserController.update_user(user_id, **updated_user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        return UserController.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
