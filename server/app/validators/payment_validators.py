from server.app.models.payment_model import Payment
from server.app.utils.exceptions import GlobalException


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
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Payment ID not provided"
            )
        if Payment.get_record_by_id(self.payment_id)["user_id"] != user_id:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="Payment is not owned by this user",
                extra={"user_id": user_id}
            )
        return self
