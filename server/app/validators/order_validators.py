from server.app.models.order_model import Order
from server.app.models.user_model import User
from server.app.utils.exceptions import CustomHTTPException


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
            CustomHTTPException.bad_request(detail="Invalid customer ID")
        if customer.get("is_blocked"):
            CustomHTTPException.forbidden(detail="User is forbidden to create order")

        return self

    def validate_order(self):
        order = Order.get_record_by_id(self.order_id)

        if not order:
            CustomHTTPException.bad_request(detail="Invalid order ID")
        if order.get("customer_id") != self.customer_id:
            CustomHTTPException.forbidden(detail="User can read only orders created by them")
        if order.get("is_blocked"):
            CustomHTTPException.forbidden(detail="Access to current order is forbidden")

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
            CustomHTTPException.bad_request(detail="Invalid performer ID")
        if performer.get("is_blocked"):
            CustomHTTPException.forbidden(detail="User is forbidden to assign themself to the order")

        return self

    def validate_order(self):
        order = Order.get_record_by_id(self.order_id)

        if not order:
            CustomHTTPException.bad_request(detail="Invalid order ID")
        if order.get("performer_id") == self.performer_id:
            CustomHTTPException.bad_request(detail="User is already assigned themselves to the order")
        if order.get("performer_id"):
            CustomHTTPException.bad_request(detail="This order is already assigned to another user")
        if order.get("is_blocked"):
            CustomHTTPException.forbidden(detail="Access to current order is forbidden")
