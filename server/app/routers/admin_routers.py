from typing import Any, Union

from fastapi import APIRouter, Depends
from starlette import status

from server.app.controllers.admin_plans_controller import AdminPlansController
from server.app.controllers.admin_permissions_controller import AdminPermissionsController
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
from server.app.utils.exceptions import handle_db_errors, CustomHTTPException


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/permissions", response_model=list[PermissionResponse])
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_all_permissions", "read_all_plans"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.get_all_permissions()
    except Exception as e:
        CustomHTTPException.forbidden(detail=f"Access denied: {repr(e)}")


@router.post("/permissions", response_model=Union[list[PermissionResponse], PermissionResponse])
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["create_permissions"])
def create_permission(
        permission_data: PermissionCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.create_permission(permission_data.model_dump())
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.get("/permissions/me", response_model=list[PermissionResponse])
@handle_db_errors
@required_plans(["admin", "moderator"])
@required_permissions(["read_own_permissions"])
def get_all_permissions(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.get_all_permissions_by_plan(user["plan_name"])
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.get("/permissions/{permission_id}", response_model=Union[list[PermissionResponse], PermissionResponse])
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_permission_details"])
def get_permission(
        permission_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPermissionsController.get_permission_by_id(permission_id)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.patch("/permissions/{permission_id}", response_model=Union[list[PermissionResponse], PermissionResponse])
@handle_db_errors
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
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_permission_details", "update_permission_details", "delete_permission"])
def delete_permission(
        permission_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        AdminPermissionsController.delete_permission(permission_id)
        return
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.get("/plans", response_model=Union[list[PlanResponse], PlanResponse])
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions"])
def get_all_plans(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPlansController.get_all_plans()
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.post("/plans", response_model=PlanResponse)
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_plan_details", "create_plans"])
def create_plan(
        plan_data: PlanCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPlansController.create_plan(plan_data.model_dump())
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.get("/plans/{plan_id}", response_model=Union[list[PlanResponseExtended], PlanResponseExtended])
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions", "read_plan_details"])
def get_all_plans(
        plan_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPlansController.get_plan_by_id(plan_id)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.patch("/plans/{plan_id}", response_model=PlanResponse)
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_plan_details", "update_plan_details"])
def get_all_plans(
        plan_id: int,
        plan_data: PlanUpdate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return AdminPlansController.update_plan_by_id(plan_id, plan_data.model_dump())
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_db_errors
@required_plans(["admin"])
@required_permissions(["read_all_plans", "read_all_permissions", "read_plan_details", "delete_plan"])
def delete_plan(
        plan_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        AdminPlansController.delete_plan_by_id(plan_id)
        return
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Bad request: {repr(e)}")
