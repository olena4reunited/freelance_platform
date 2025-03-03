from typing import Any, Union

from fastapi import APIRouter, Depends

from server.app.controllers.admin_plans_controller import AdminPlansController
from server.app.controllers.admin_permissions_controller import AdminPermissionsController
from server.app.controllers.admin_user_controller import AdminUserController
from server.app.schemas.users_schemas import UserResponseExtended
from server.app.schemas.admin_schemas import BlockRequest
from server.app.utils.dependencies import (
    get_current_user,
    required_plans,
    required_permissions
)
from server.app.schemas.permission_schemas import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate
)
from server.app.schemas.plan_schemas import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    PlanResponseExtended
)
from server.app.utils.exceptions import GlobalException


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/permissions", response_model=list[PermissionResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_permissions", "read_all_plans"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPermissionsController.get_all_permissions()


@router.post("/permissions", response_model=Union[list[PermissionResponse], PermissionResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["create_permissions"])
def create_permission(
        permission_data: PermissionCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPermissionsController.create_permission(permission_data.model_dump())


@router.get("/permissions/me", response_model=list[PermissionResponse])
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_own_permissions"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPermissionsController.get_all_permissions_by_plan(user["plan_name"])


@router.get("/permissions/{permission_id}", response_model=Union[list[PermissionResponse], PermissionResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_permission_details"])
def get_permission(
        permission_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPermissionsController.get_permission_by_id(permission_id)


@router.patch("/permissions/{permission_id}", response_model=Union[list[PermissionResponse], PermissionResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_permission_details", "update_permission_details"])
def update_permission(
        permission_id: int,
        permission_data: PermissionUpdate,
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPermissionsController.update_permission(permission_id, permission_data.model_dump())


@router.delete("/permissions/{permission_id}", response_model=list[PermissionResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_permission_details", "update_permission_details", "delete_permission"])
def delete_permission(
        permission_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    AdminPermissionsController.delete_permission(permission_id)
    return AdminPermissionsController.get_all_permissions()


@router.get("/plans", response_model=Union[list[PlanResponse], PlanResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions"])
def get_all_plans(
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPlansController.get_all_plans()


@router.post("/plans", response_model=PlanResponse)
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_plan_details", "create_plans"])
def create_plan(
        plan_data: PlanCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPlansController.create_plan(plan_data.model_dump())


@router.get("/plans/{plan_id}", response_model=Union[list[PlanResponseExtended], PlanResponseExtended])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions", "read_plan_details"])
def get_all_plans(
        plan_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPlansController.get_plan_by_id(plan_id)


@router.patch("/plans/{plan_id}", response_model=PlanResponse)
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_plan_details", "update_plan_details"])
def get_all_plans(
        plan_id: int,
        plan_data: PlanUpdate,
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminPlansController.update_plan_by_id(plan_id, plan_data.model_dump())


@router.delete("/plans/{plan_id}", response_model=Union[list[PlanResponse], PlanResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions", "read_plan_details", "delete_plan"])
def delete_plan(
        plan_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    AdminPlansController.delete_plan_by_id(plan_id)
    return AdminPlansController.get_all_plans()


@router.patch("/users/{user_id}", response_model=UserResponseExtended)
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["block_user"])
def block_user(
        user_id: int,
        user_block_request: BlockRequest,
        user: dict[str, Any] = Depends(get_current_user)
):
    return AdminUserController.block_user_by_id(
        user_id=user_id,
        block_timestamp=user_block_request.block_timestamp
    )
