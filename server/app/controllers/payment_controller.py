from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.payment_model import Payment
from server.app.utils.crypto import encrypt_data, get_masked_payment


class PaymentController:
    @staticmethod
    def create_payment(user_id: int, payment_data: str) -> dict[str, Any] | None:
        encrypted_payment = encrypt_data(payment_data)

        payment = Payment.create_payment(user_id=user_id, payment=encrypted_payment)
        payment["payment"] = get_masked_payment(payment["payment"])

        return payment

    @staticmethod
    def get_payment(payment_id: int) -> dict[str, str]:
        payment = Payment.get_record_by_id(payment_id)
        payment["payment"] = get_masked_payment(payment["payment"])
        payment.pop("user_id")

        return payment

    @staticmethod
    def get_user_payments(user_id: int) -> list[dict[str, str]]:
        payments = Payment.get_payments_by_user(user_id)

        return list(map(get_masked_payment, payments))

    @staticmethod
    def delete_payment(payment_id: int) -> None:
        Payment.delete_record_by_id(payment_id)

    @staticmethod
    def get_all_users_payments():
        payments = Payment.get_all_records()

        return list(map(get_masked_payment, payments))

    @staticmethod
    def get_user_payment_details(payment_id: int) -> dict[str, Any] | None:
        payment = Payment.get_record_by_id(payment_id)

        return get_masked_payment(payment)
