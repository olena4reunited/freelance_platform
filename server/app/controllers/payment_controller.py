from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.models import Payment
from server.app.utils.crypto import encrypt_data, decrypt_data, get_masked_payment


class PaymentController:
    @staticmethod
    def create_payment(user_id: int, payment: str) -> dict[str, str]:
        encrypted_payment = encrypt_data(bytes(payment, "unf-8"))
        payment = Payment.create_record(user_id=user_id, payment=encrypted_payment)
        payment["payment"] = get_masked_payment(payment["payment"])
        payment.pop("user_id")

        return payment

    @staticmethod
    def get_payment(payment_id: int) -> dict[str, str]:
        payment = Payment.get_record_by_id(payment_id)
        payment["payment"] = get_masked_payment(payment["payment"])
        payment.pop("user_id")

        return payment

    @staticmethod
    def get_all_user_payments(user_id: int) -> list[dict[str, str]]:
        payments = Payment.get_payments_by_user(user_id)

        for payment in payments:
            payment["payment"] = get_masked_payment(payment["payment"])

        return payments

    @staticmethod
    def delete_payment(payment_id: int) -> None:
        Payment.delete_record_by_id(payment_id)

