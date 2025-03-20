from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel
from server.app.models.sql_builder import SQLBuilder


class Payment(BaseModel):
    table_name = "payments"

    @staticmethod
    def create_payment(user_id: int, payment: bytes) -> dict[str, Any]:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    INSERT INTO payments (user_id, payment)
                    VALUES (%s, %s)
                    RETURNING id, payment 
                """,
                (user_id, payment)
            )

    @staticmethod
    def get_payments_by_user(user_id: int) -> list[dict[str, Any]]:
        query, params = SQLBuilder("payments").select("id", "payment").where("user_id", params=user_id).get()

        with PostgresDatabase() as db:
            return db.fetch(query, params, is_all=True)
