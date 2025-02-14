from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class Permission(BaseModel):
    table_name = "permissions"

    @staticmethod
    def get_permissions() -> list[dict[str, Any]] | dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT pln.name as plan, prm.name as permission
                    FROM permissions prm
                    LEFT JOIN plans_permissions pp ON prm.id = pp.permission_id
                    LEFT JOIN plans pln ON pp.plan_id = pln.id
                    ORDER BY pln.id;
                """,
                is_all=True
            )

    @staticmethod
    def get_permissions_by_plan(plan_name: str) -> list[dict[str, Any]] | dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT pln.name as plan, prm.name as permission
                    FROM permissions prm
                    LEFT JOIN plans_permissions pp ON prm.id = pp.permission_id
                    LEFT JOIN plans pln ON pp.plan_id = pln.id
                    WHERE pln.name = %s;
                """,
                (plan_name, ),
                is_all=True
            )

