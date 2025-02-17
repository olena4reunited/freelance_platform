from server.app.models.order_model import Order
from server.app.models.user_model import User
from server.app.utils.exceptions import CustomHTTPException


class OrderCustomerValidator:
    def __init__(self, customer_id: int):
        self.customer_id = customer_id

    def validate_customer(self):
        user = User.get_record_by_id(self.customer_id)

        if not user:
            CustomHTTPException.bad_request(detail="Invalid customer ID")
        if user.get("is_blocked"):
            CustomHTTPException.forbidden(detail="User is forbidden to create order")

    def validate_order_creator(self, order_id: int):
        order = Order.get_record_by_id(order_id)

        if not order:
            CustomHTTPException.bad_request(detail="Invalid order ID")
        if order.get("customer_id") != self.customer_id:
            CustomHTTPException.forbidden(detail="User can read only orders created by them")
