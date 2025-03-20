from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.sql_builder import SQLBuilder


class BaseModel:
    table_name: str = ""

    @classmethod
    def get_record_by_id(cls, record_id: int) -> dict[str, Any] | None:
        query, params = SQLBuilder(table_name=cls.table_name).select().where("id", params=record_id).get()

        with PostgresDatabase() as db:
            return db.fetch(query, params)

    @classmethod
    def get_all_records(cls) -> list[dict[str, Any]] | None:
        query, params = SQLBuilder(table_name=cls.table_name).select().get()

        with PostgresDatabase() as db:
            return db.fetch(query, params, is_all=True)

    @classmethod
    def create_record(cls, **kwargs) -> dict[str, Any] | None:
        columns = ", ".join(kwargs.keys())
        values_placeholder = ", ".join(["%s"] * len(kwargs))

        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                f"""
                INSERT INTO {cls.table_name} ({columns}) VALUES ({values_placeholder})
                """,
                tuple(kwargs.values()),
            )

    @classmethod
    def update_record(cls, record_id: int, **kwargs) -> int | None:
        set_clause = ", ".join(f"{key} = %s" for key in kwargs.keys())

        with PostgresDatabase(on_commit=True) as db:
            return db.execute_query(
                f"""
                    UPDATE {cls.table_name} 
                    SET {set_clause} 
                    WHERE id = %s
                """,
                tuple(kwargs.values()) + (record_id,),
            )

    @classmethod
    def delete_record_by_id(cls, record_id: int) -> int | None:
        with PostgresDatabase(on_commit=True) as db:
            return db.execute_query(
                f"DELETE FROM {cls.table_name} WHERE id = %s",
                (record_id,),
            )
