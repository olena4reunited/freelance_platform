from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class Plan(BaseModel):
    table_name = "plans"


class Permission(BaseModel):
    table_name = "permissions"


class PlanPermission(BaseModel):
    table_name = "plans_permissions"


class User(BaseModel):
    table_name = "users"

    @staticmethod
    def get_user_by_field(field: str, value: str) -> dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch_one(
                f"SELECT * FROM {User.table_name} WHERE {field} = %s",
                (value,),
            )


class Payment(BaseModel):
    table_name = "payments"
