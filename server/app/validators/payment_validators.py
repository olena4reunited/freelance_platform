from server.app.models.payment_model import Payment
from server.app.utils.exceptions import CustomHTTPException


class PaymentValidator:
    def __init__(
            self,
            payment_id: int | None = None,
            payment_data: str | None = None
    ):
        self.payment_id = payment_id
        self.payment_data = payment_data

    def validate_payment_ownership(self, user_id: int):
        if not self.payment_id:
            CustomHTTPException.bad_request(detail="Could not process request: Payment ID is required")
        if Payment.get_record_by_id(self.payment_id)["user_id"] != user_id:
            CustomHTTPException.forbidden(detail="Request is forbidden: You don't have permission to access this payment")
        return self
