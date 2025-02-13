from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class Permission(BaseModel):
    table_name = "permissions"

    @staticmethod
    def get_permissions(plan_name: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
        query = """
            SELECT pln.name as plan, prm.name as permission
            FROM permissions prm
            LEFT JOIN plans_permissions pp ON prm.id = pp.permission_id
            LEFT JOIN plans pln ON pp.plan_id = pln.id
        """
        params = tuple()

        if plan_name:
            query += " WHERE pln.name = %s"
            params = (plan_name,)

        with PostgresDatabase() as db:
            return db.fetch(query, params, is_all=True)
