from fastapi import HTTPException
from starlette import status

from server.app.controllers.payment_controller import PaymentController
from server.app.models.models import Payment


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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment id is required")

        if not Payment.get_record_by_id(self.payment_id)["user_id"] == user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to access this payment")

        return self
