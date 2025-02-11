from typing import Any, Union

from fastapi import APIRouter, Header, HTTPException, Depends
from starlette import status

from server.app.schemas.users_schemas import UserResponse
from server.app.utils.auth import verify_token
from server.app.utils.dependencies import (
    get_current_user,
    required_plans,
    required_permissions
)
from server.app.controllers.admin_controller import AdminController
from server.app.schemas.permission_schemas import (
    PermissionCreate,
    PermissionResponse
)


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/permissions", response_model=list[PermissionResponse])
@required_plans(["admin"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminController.get_all_permissions()


@router.get("/me/permissions", response_model=list[PermissionResponse])
@required_plans(["admin", "moderator"])
@required_permissions(["get_user_permissions"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminController.get_all_permissions_by_plan(user["plan_name"])


@router.post("/permissions", response_model=Union[list[PermissionResponse], PermissionResponse])
@required_plans(["admin"])
def create_permission(
        permission_data: PermissionCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminController.create_permission(permission_data.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
