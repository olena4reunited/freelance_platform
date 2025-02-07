from typing import Any

from server.app.database.database import PostgresDatabase


class BaseModel:
    table_name: str = ""

    @classmethod
    def get_record_by_id(cls, record_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                f"SELECT * FROM {cls.table_name} WHERE id = %s",
                (record_id,),
            )

    @classmethod
    def get_all_records(cls) -> list[dict[str, Any]] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                f"SELECT * FROM {cls.table_name}",
                is_all=True,
            )

    @classmethod
    def create_record(cls, **kwargs) -> dict[str, Any] | None:
        columns = ", ".join(kwargs.keys())
        values_placeholder = ", ".join(["%s"] * len(kwargs))

        with PostgresDatabase() as db:
            return db.fetch(
                f"""
                INSERT INTO {cls.table_name} ({columns}) VALUES ({values_placeholder})
                """,
                tuple(kwargs.values()),
            )

    @classmethod
    def update_record(cls, record_id: int, **kwargs) -> dict[str, Any] | None:
        set_clause = ", ".join(f"{key} = %s" for key in kwargs.keys())

        with PostgresDatabase() as db:
            return db.fetch(
                f"UPDATE {cls.table_name} SET {set_clause} WHERE id = %s",
                (*kwargs.values(), record_id,),
            )

    @classmethod
    def delete_record_by_id(cls, record_id: int) -> int | None:
        with PostgresDatabase() as db:
            return db.execute_query(
                f"DELETE FROM {cls.table_name} WHERE id = %s",
                (record_id,),
            )


