from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.models import Payment
from server.app.utils.crypto import encrypt_data


class PaymentController:
    @staticmethod
    def create_payment(user_id, payment):
        with PostgresDatabase(on_commit=True) as db:
            db.execute_query(
                """
                INSERT INTO payments (user_id, payment)
                VALUES (%s, %s)
                """,
                (user_id, payment)
            )