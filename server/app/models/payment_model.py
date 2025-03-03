from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class Payment(BaseModel):
    table_name = "payments"

    @staticmethod
    def get_payments_by_user(user_id: int) -> list[dict[str, Any]]:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT id, payment FROM payments WHERE user_id = %s;
                """,
                (user_id, ),
                is_all=True
            )

    @staticmethod
    def create_payment(user_id: int, payment_data: bytes) -> None:
        with PostgresDatabase(on_commit=True) as db:
            db.execute_query(
                """
                    INSERT INTO payments (user_id, payment)
                    VALUES (%s, %s);
                """,
                (user_id, payment_data)
            )
