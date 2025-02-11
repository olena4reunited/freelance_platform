from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class Plan(BaseModel):
    table_name = "plans"


class Permission(BaseModel):
    table_name = "permissions"

    @staticmethod
    def get_permissions(plan_name: str | None = None) -> list[dict[str, str]] | dict[str, str]:
        query = """
            SELECT pln.name as plan, prm.name as permission
            FROM permissions prm
            LEFT JOIN plans_permissions pp ON prm.id = pp.permission_id
            LEFT JOIN plans pln ON pp.plan_id = pln.id
        """
        params = ()

        if plan_name:
            query += " WHERE pln.name = %s"
            params = (plan_name,)

        with PostgresDatabase() as db:
            return db.fetch(query, params, is_all=True)


class PlanPermission(BaseModel):
    table_name = "plans_permissions"


class User(BaseModel):
    table_name = "users"

    @staticmethod
    def get_user_by_field(field: str, value: str) -> dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch(
                f"SELECT * FROM {User.table_name} WHERE {field} = %s",
                (value,),
            )


class Payment(BaseModel):
    table_name = "payments"

    @staticmethod
    def get_payments_by_user(user_id: int) -> list[dict[str, Any]]:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT id, payment FROM payments
                    WHERE user_id = %s;
                """,
                (user_id, ),
                is_all=True
            )
