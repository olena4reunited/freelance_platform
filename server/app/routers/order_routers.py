from typing import Any, Union

from fastapi import APIRouter, Depends

from server.app.schemas.order_schemas import (
    OrderCreate,
    OrderResponse
)
from server.app.validators.order_validators import OrderCustomerValidator
from server.app.controllers.order_controller import OrderController
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


@router.get("/customer/me/list", response_model=Union[list[OrderResponse], OrderResponse])
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["read_own_orders"])
def get_order_list(user: dict[str, Any] = Depends(get_current_user)):
    try:
        OrderCustomerValidator(user.get("id")) \
        .validate_customer()
        ...
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.get("/customer/me/list/{order_id}", response_model=OrderResponse)
@handle_db_errors
@required_plans(["customer"])
@required_permissions(["read_own_orders"])
def get_order_list(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        OrderCustomerValidator(user.get("id")) \
        .validate_customer()\
        .validate_order_creator(order_id)
        ...
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not process request: {repr(e)}")


@router.post("/customer/me/list", response_model=OrderResponse)
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

        return OrderController.create_order(order_dict)
    except Exception as e:
        CustomHTTPException.bad_request(detail=f"Could not create order: {repr(e)}")
