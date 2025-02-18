from typing import Any, Union

from fastapi import APIRouter, Depends, Query
from starlette import status

from server.app.schemas.order_schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderSingleResponse,
    OrderListPerformerResponse,
    OrderPerformerAssignedResponse
)
from server.app.schemas.users_schemas import (
    UserPerformerResponse,
    UserCustomerResponse
)
from server.app.validators.order_validators import (
    OrderCustomerValidator,
    OrderPerformerValidator
)
from server.app.controllers.order_customer_controller import OrderCustomerController
from server.app.controllers.order_performer_controller import OrderPerformerController
from server.app.utils.exceptions import (
    handle_db_errors,
    CustomHTTPException
)
from server.app.utils.dependencies import (
    get_current_user,
    required_plans,
    required_permissions
)


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/customer/me/list", response_model=Union[list[OrderListResponse], OrderListResponse])
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["read_own_orders"])
def get_order_list(user: dict[str, Any] = Depends(get_current_user)):
    try:
        OrderCustomerValidator(user.get("id")) \
        .validate_customer()

        return OrderCustomerController.get_all_customer_orders(user.get("id"))
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.get("/customer/me/performers", response_model=Union[list[UserPerformerResponse], UserPerformerResponse])
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["read_own_orders", "read_own_orders_performers"])
def get_order_list_performers(user: dict[str, Any] = Depends(get_current_user)):
    try:
        OrderCustomerValidator(user.get("id")) \
        .validate_customer()

        return OrderCustomerController.get_all_customer_performers(user.get("id"))
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.get("/customer/me/list/{order_id}", response_model=OrderSingleResponse)
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["read_own_orders", "read_own_order_details"])
def get_order_list(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        OrderCustomerValidator(customer_id=user.get("id"), order_id=order_id) \
        .validate_customer()\
        .validate_order()

        return OrderCustomerController.get_single_customer_order(order_id)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.post("/customer/me", response_model=OrderResponse)
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["create_order"])
def create_order(
        order_data: OrderCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        OrderCustomerValidator(user.get("id")) \
        .validate_customer()

        order_dict = order_data.model_dump()
        order_dict["customer_id"] = user.get("id")

        return OrderCustomerController.create_order(order_dict)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not create order: {repr(e)}")


@router.patch("/customer/me/list/{order_id}", response_model=OrderSingleResponse)
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["read_own_orders", "read_own_order_details", "update_own_order"])
def update_order(
        order_id: int,
        updated_order_data: OrderUpdate,
        user: dict[str, Any] = Depends(get_current_user),
):
    try:
        OrderCustomerValidator(customer_id=user.get("id"), order_id=order_id) \
        .validate_customer() \
        .validate_order()

        return OrderCustomerController.update_order(order_id, updated_order_data.model_dump())
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.delete("/customer/me/list/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["update_own_order", "delete_own_order"])
def delete_order(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    try:
        OrderCustomerValidator(customer_id=user.get("id"), order_id=order_id) \
        .validate_customer() \
        .validate_order()

        OrderCustomerController.delete_order(order_id)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.get("/performers/list", response_model=Union[list[OrderListPerformerResponse], OrderListPerformerResponse])
@handle_db_errors
@required_plans(["performer"])
@required_permissions(["read_unassigned_orders"])
def get_all_unassigned_orders(
        limit: int = Query(10, description="number of output results"),
        page: int = Query(1, description="pagination"),
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        OrderPerformerValidator(user.get("id")) \
        .validate_performer()

        return OrderPerformerController.get_orders(limit=limit, page=page)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.post("/performers/list/{order_id}", response_model=OrderPerformerAssignedResponse)
@handle_db_errors
@required_plans(["performer"])
@required_permissions(["read_unassigned_orders", "assign_themself_to_order"])
def assign_themself_to_order(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        OrderPerformerValidator(performer_id=user.get("id"), order_id=order_id) \
        .validate_performer() \
        .validate_order()

        return OrderPerformerController.assign_to_the_order(order_id=order_id, performer_id=user.get("id"))
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.get("/performers/me/list", response_model=Union[list[OrderPerformerAssignedResponse], OrderPerformerAssignedResponse])
@handle_db_errors
@required_plans(["performer"])
@required_permissions(["read_own_orders"])
def get_all_own_orders(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        OrderPerformerValidator(performer_id=user.get("id")) \
        .validate_performer()

        return OrderPerformerController.get_assigned_orders(performer_id=user.get("id"))
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.get("/performers/me/customers", response_model=Union[list[UserCustomerResponse], UserCustomerResponse])
@handle_db_errors
@required_plans(["performer"])
@required_permissions(["read_own_orders", "read_own_orders_customers"])
def get_all_assigned_orders_customers(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        OrderPerformerValidator(performer_id=user.get("id")) \
        .validate_performer()

        return OrderPerformerController.get_all_performer_customers(performer_id=user.get("id"))
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")
