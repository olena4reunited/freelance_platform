from server.app.models.order_model import Order
from server.app.models.user_model import User
from server.app.utils.exceptions import GlobalException


class OrderCustomerValidator:
    def __init__(
            self,
            customer_id: int | None = None,
            order_id: int | None = None,
    ):
        self.customer_id = customer_id
        self.order_id = order_id

    def validate_customer(self):
        customer = User.get_record_by_id(self.customer_id)

        if not customer:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Customer not found",
                extra={"customer_id": self.customer_id},
            )
        if customer.get("is_blocked"):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="Customer is blocked",
                extra={"customer_id": self.customer_id, "blocked_until": customer.get("block_expired", None)},
            )
        return self

    def validate_order(self):
        order = Order.get_record_by_id(self.order_id)

        if not order:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Order not found",
                extra={"order_id": self.order_id},
            )
        if order.get("customer_id") != self.customer_id:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="Order does not belong to customer",
                extra={"order_id": self.order_id, "customer_id": self.customer_id},
            )
        if order.get("is_blocked"):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="Order is blocked",
                extra={"order_id": self.order_id, "blocked_until": order.get("blocked_until", None)},
            )
        return self


class OrderPerformerValidator:
    def __init__(
            self,
            performer_id: int | None = None,
            order_id: int | None = None
    ):
        self.performer_id = performer_id
        self.order_id = order_id

    def validate_performer(self):
        performer = User.get_record_by_id(self.performer_id)

        if not performer:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Performer not found",
                extra={"performer_id": self.performer_id},
            )
        if performer.get("is_blocked"):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="Performer is blocked",
                extra={"performer_id": self.performer_id, "block_expired": performer.get("block_expired", None)}
            )
        return self

    def validate_order(self):
        order = Order.get_record_by_id(self.order_id)

        if not order:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Order not found",
                extra={"order_id": self.order_id},
            )
        if order.get("performer_id") == self.performer_id:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Performer is already assigned themself to the order",
                extra={"order_id": self.order_id, "performer_id": self.performer_id},
            )
        if order.get("performer_id"):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Order is already accepted by performer",
                extra={"order_id": self.order_id, "performer_id": self.performer_id},
            )
        if order.get("is_blocked"):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="Order is blocked",
                extra={"order_id": self.order_id, "blocked_until": order.get("blocked_until", None)}
            )
