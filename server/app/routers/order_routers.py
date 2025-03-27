from typing import Any, Union

from fastapi import APIRouter, Depends, Query

from server.app.schemas.order_schemas import (
    OrderCreate,
    OrderUpdate,
    OrderListResponse,
    OrderDetailResponseBase,
    OrderDetailResponseSingle,
    OrderDetailResponseTeam,
    OrderListPerformerResponse,
    OrderPerformerAssignedResponse,
    OrderAdminUpdate,
    OrderSingleResponseExtended
)
from server.app.schemas.users_schemas import (
    UserPerformerResponse,
    UserCustomerResponse
)
from server.app.schemas.admin_schemas import BlockRequest
from server.app.validators.order_validators import (
    OrderCustomerValidator,
    OrderPerformerValidator
)
from server.app.controllers.order_customer_controller import OrderCustomerController
from server.app.controllers.order_performer_controller import OrderPerformerController
from server.app.controllers.order_admin_controller import OrderAdminController
from server.app.utils.exceptions import GlobalException
from server.app.utils.dependencies.dependencies import (
    get_current_user,
    required_plans,
    required_permissions
)
from server.app.services.mqtt_service.mqtt_service import mqtt


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/customer/me/list", response_model=Union[list[OrderListResponse], OrderListResponse])
@GlobalException.catcher
@required_plans(["customer"])
@required_permissions(["read_own_orders"])
def get_order_list(user: dict[str, Any] = Depends(get_current_user)):
    return OrderCustomerController.get_all_customer_orders(user.get("id"))


@router.get("/customer/me/performers", response_model=Union[list[UserPerformerResponse], UserPerformerResponse])
@GlobalException.catcher
@required_plans(["customer"])
@required_permissions(["read_own_orders", "read_own_orders_performers"])
def get_order_list_performers(user: dict[str, Any] = Depends(get_current_user)):
    return OrderCustomerController.get_all_customer_performers(user.get("id"))


@router.get("/customer/me/list/{order_id}", response_model=Union[OrderDetailResponseBase, OrderDetailResponseSingle, OrderDetailResponseTeam])
@GlobalException.catcher
@required_plans(["customer"])
@required_permissions(["read_own_orders", "read_own_order_details"])
def get_order_list(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    OrderCustomerValidator(customer_id=user.get("id"), order_id=order_id) \
    .validate_order()

    return OrderCustomerController.get_order_details(order_id)


@router.post("/customer/me", response_model=OrderDetailResponseBase)
@GlobalException.catcher
@required_plans(["customer"])
@required_permissions(["create_order"])
def create_order(
        order_data: OrderCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    order = OrderCustomerController.create_order(
        order_data=order_data.model_dump(),
        customer_id=user.get("id")
    )

    mqtt.publish_new_order(
        order_data=order,
        user_data=user
    )

    return order


@router.patch("/customer/me/list/{order_id}", response_model=OrderDetailResponseBase)
@GlobalException.catcher
@required_plans(["customer"])
@required_permissions(["read_own_orders", "read_own_order_details", "update_own_order"])
def update_order(
        order_id: int,
        updated_order_data: OrderUpdate,
        user: dict[str, Any] = Depends(get_current_user),
):
    OrderCustomerValidator(customer_id=user.get("id"), order_id=order_id) \
    .validate_order()

    return OrderCustomerController.update_order(order_id, updated_order_data.model_dump())


@router.delete("/customer/me/list/{order_id}", response_model=Union[list[OrderListResponse], OrderListResponse])
@GlobalException.catcher
@required_plans(["customer"])
@required_permissions(["update_own_order", "delete_own_order"])
def delete_order(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    OrderCustomerValidator(customer_id=user.get("id"), order_id=order_id) \
    .validate_order()

    OrderCustomerController.delete_order(order_id)
    return OrderCustomerController.get_all_customer_orders(user.get("id"))


@router.get("/performer/list", response_model=Union[list[OrderListPerformerResponse], OrderListPerformerResponse])
@GlobalException.catcher
@required_plans(["performer"])
@required_permissions(["read_unassigned_orders"])
def get_all_unassigned_orders(
        limit: int = Query(10, description="number of output results"),
        page: int = Query(1, description="pagination"),
        user: dict[str, Any] = Depends(get_current_user)
):
    return OrderPerformerController.get_orders(limit=limit, page=page)


@router.post("/performer/list/{order_id}", response_model=OrderPerformerAssignedResponse)
@GlobalException.catcher
@required_plans(["performer"])
@required_permissions(["read_unassigned_orders", "assign_themself_to_order"])
def assign_themself_to_order(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    OrderPerformerValidator(performer_id=user.get("id"), order_id=order_id) \
    .validate_order()

    return OrderPerformerController.assign_to_the_order(order_id=order_id, performer_id=user.get("id"))


@router.get("/performer/me/list", response_model=Union[list[OrderPerformerAssignedResponse], OrderPerformerAssignedResponse])
@GlobalException.catcher
@required_plans(["performer"])
@required_permissions(["read_own_orders"])
def get_all_own_orders(
        user: dict[str, Any] = Depends(get_current_user)
):
    return OrderPerformerController.get_assigned_orders(performer_id=user.get("id"))


@router.get("/performer/me/customers", response_model=Union[list[UserCustomerResponse], UserCustomerResponse])
@GlobalException.catcher
@required_plans(["performer"])
@required_permissions(["read_own_orders", "read_own_orders_customers"])
def get_all_assigned_orders_customers(
        user: dict[str, Any] = Depends(get_current_user)
):
    return OrderPerformerController.get_all_performer_customers(performer_id=user.get("id"))


@router.get("/admin/orders", response_model=Union[list[OrderListResponse], OrderListResponse])
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_orders"])
def get_all_orders(
        user: dict[str, Any] = Depends(get_current_user)
):
    return OrderAdminController.get_all_orders()


@router.get("/admin/orders/{order_id}", response_model=OrderDetailResponseBase)
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_orders", "read_all_orders_details"])
def get_single_order(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    return OrderAdminController.get_order_by_id(order_id=order_id)


@router.patch("/admin/orders/{order_id}", response_model=OrderDetailResponseBase)
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_orders_details", "update_all_orders_details"])
def update_order(
        order_id: int,
        updated_order_data: OrderAdminUpdate,
        user: dict[str, Any] = Depends(get_current_user)
):
    return OrderAdminController.update_order_by_id(order_id=order_id, order_data=updated_order_data.model_dump())


@router.delete("/admin/orders/{order_id}", response_model=Union[list[OrderListResponse], OrderListResponse])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_orders_details", "update_all_orders_details", "delete_all_orders"])
def delete_order(
        order_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    OrderAdminController.delete_order_by_id(order_id=order_id)
    return OrderAdminController.get_all_orders()


@router.put("/admin/orders/{order_id}", response_model=OrderSingleResponseExtended)
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_orders_details", "update_all_orders_details", "block_order"])
def block_order(
        order_id: int,
        order_block_request: BlockRequest,
        user: dict[str, Any] = Depends(get_current_user)
):
    return OrderAdminController.block_order_by_id(
        order_id=order_id,
        block_timestamp=order_block_request.block_timestamp,
    )
