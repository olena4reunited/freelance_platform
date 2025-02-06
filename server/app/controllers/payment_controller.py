from typing import Any

from server.app.models.models import Payment
from server.app.utils.crypto import encrypt_data


class PaymentController:
    @staticmethod
    def create_payment(user_id: int, payment_data: str):
        encrypted_payment_data = encrypt_data(bytes(payment_data, "utf-8"))

        Payment.create_record(user_id=user_id, payment=encrypted_payment_data)

