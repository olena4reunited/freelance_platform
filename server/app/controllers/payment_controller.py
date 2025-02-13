from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.payment_model import Payment
from server.app.utils.crypto import encrypt_data, get_masked_payment


class PaymentController:
    @staticmethod
    def create_payment(user_id: int, payment: str) -> dict[str, str]:
        encrypted_payment = encrypt_data(bytes(payment, "utf-8"))
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
    def get_user_payments(user_id: int) -> list[dict[str, str]]:
        payments = Payment.get_payments_by_user(user_id)

        for payment in payments:
            payment["payment"] = get_masked_payment(payment["payment"])

        return payments

    @staticmethod
    def delete_payment(payment_id: int) -> None:
        Payment.delete_record_by_id(payment_id)

    @staticmethod
    def get_all_users_payments():
        payments = Payment.get_all_records()

        for payment in payments:
            payment["payment"] = get_masked_payment(payment["payment"])

        return payments

    @staticmethod
    def get_user_payment_details(user_id: int, payment_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            payment = db.fetch(
                f"SELECT id, user_id, payment FROM payments WHERE user_id = %s AND id = %s",
                (user_id, payment_id),
            )

        payment["payment"] = get_masked_payment(payment["payment"])
