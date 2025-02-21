from datetime import datetime
from typing import Any

from server.app.database.database import PostgresDatabase


class AdminUserController:
    @staticmethod
    def block_user_by_id(user_id: int, block_timestamp: datetime) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    WITH blocked_user AS (
                        UPDATE users
                        SET block_expired = TIMESTAMP %s, is_blocked = TRUE
                        WHERE id = %s
                        RETURNING id, first_name, last_name, username, email, phone_number, photo_link, description, balance, rating, plan_id, is_verified, block_expired, delete_date, is_blocked
                    )
                    SELECT blu.id AS id, first_name, last_name, username, email, phone_number, photo_link, description, balance, rating, pln.name AS plan_name, is_verified, block_expired, delete_date, is_blocked
                    FROM blocked_user blu
                    JOIN plans pln on pln.id = blu.plan_id
                """,
                (block_timestamp, user_id, ),
            )
