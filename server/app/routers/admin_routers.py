from typing import Any, Union

from fastapi import APIRouter, HTTPException, Depends
from starlette import status

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
@required_permissions(["read_all_permissions", "read_all_plans"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminController.get_all_permissions()


@router.get("/me/permissions", response_model=list[PermissionResponse])
@required_plans(["admin", "moderator"])
@required_permissions(["read_own_permissions"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminController.get_all_permissions_by_plan(user["plan_name"])


@router.post("/permissions", response_model=Union[list[PermissionResponse], PermissionResponse])
@required_plans(["admin"])
@required_permissions(["create_permissions"])
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

@router.get("/permissions/{permission_id}")
@required_plans(["admin"])
@required_permissions(["read_permission_details"])
def get_permission(
        permission_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        ...
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
