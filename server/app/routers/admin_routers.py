from typing import Any, Union

from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from server.app.controllers.admin_plans_controller import AdminPlansController
from server.app.utils.dependencies import (
    get_current_user,
    required_plans,
    required_permissions
)
from server.app.controllers.admin_permissions_controller import AdminPermissionsController
from server.app.schemas.permission_schemas import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate
)


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/permissions", response_model=list[PermissionResponse])
@required_plans(["admin"])
@required_permissions(["read_all_permissions", "read_all_plans"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.get_all_permissions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/permissions", response_model=Union[list[PermissionResponse], PermissionResponse])
@required_plans(["admin"])
@required_permissions(["create_permissions"])
def create_permission(
        permission_data: PermissionCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.create_permission(permission_data.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/permissions/me", response_model=list[PermissionResponse])
@required_plans(["admin", "moderator"])
@required_permissions(["read_own_permissions"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.get_all_permissions_by_plan(user["plan_name"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/permissions/{permission_id}", response_model=Union[list[PermissionResponse], PermissionResponse])
@required_plans(["admin"])
@required_permissions(["read_permission_details"])
def get_permission(
        permission_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.get_permission_by_id(permission_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/permissions/{permission_id}", response_model=Union[list[PermissionResponse], PermissionResponse])
@required_plans(["admin"])
@required_permissions(["read_permission_details", "update_permission_details"])
def update_permission(
        permission_id: int,
        permission_data: PermissionUpdate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.update_permission(permission_id, permission_data.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
@required_plans(["admin"])
@required_permissions(["read_permission_details", "update_permission_details", "delete_permission"])
def delete_permission(
        permission_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        AdminPermissionsController.delete_permission(permission_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/plans")
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions"])
def get_all_plans(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPlansController.get_all_plans()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/plans/{plan_id}")
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions", "read_plan_details"])
def get_all_plans(
        plan_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPlansController.get_plan_by_id(plan_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

