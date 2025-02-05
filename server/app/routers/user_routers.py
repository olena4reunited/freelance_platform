from fastapi import APIRouter, HTTPException

from server.app.schemas.users_schemas import (
    UserResponse,
    UserBase
)
from server.app.controllers.user_controller import UserController


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(user_data: UserBase):
    try:
        return UserController.create_user(**user_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    try:
        return UserController.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user_data: dict):
    try:
        return UserController.update_user(user_id, **updated_user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        return UserController.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
