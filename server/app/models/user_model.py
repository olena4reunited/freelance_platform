from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models._base_model import BaseModel


class User(BaseModel):
    table_name = "users"

    @staticmethod
    def get_user_by_field(field: str, value: str) -> dict[str, Any]:
        with PostgresDatabase() as db:
            return db.fetch(
                f"SELECT * FROM {User.table_name} WHERE {field} = %s",
                (value,),
            )
