from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class Plan(BaseModel):
    table_name = "plans"

    @staticmethod
    def get_plan_detail_by_id(plan_id: int) -> dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch(
                f"""
                    SELECT *
                    FROM plans pln
                    JOIN plans_permissions pp
                        ON pln.id = pp.plan_id
                    JOIN permissions prm
                        ON pp.permission_id = prm.id
                    WHERE pln.id = %s
                """,
                (plan_id,),
            )
