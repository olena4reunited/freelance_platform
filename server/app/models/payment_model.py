from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class Payment(BaseModel):
    table_name = "payments"

    @staticmethod
    def get_payments_by_user(user_id: int) -> list[dict[str, Any]]:
        with PostgresDatabase() as db:
            return db.fetch(
                f"""
                    SELECT id, payment FROM {Payment.table_name}
                    WHERE user_id = %s;
                """,
                (user_id, ),
                is_all=True
            )
