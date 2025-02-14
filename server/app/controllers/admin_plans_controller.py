from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.plan_model import Plan


class AdminPlansController:
    @staticmethod
    def get_all_plans() -> list[dict[str, Any]] | dict[str, Any]:
        return Plan.get_all_records()

    @staticmethod
    def create_plan(plan_data: dict[str, str]) -> dict[str, Any]:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    INSERT INTO plans (name)
                    VALUES (%s)
                    RETURNING id, name;
                """,
                (plan_data["plan"], ),
            )

    @staticmethod
    def get_plan_by_id(plan_id: int) -> dict[str, Any]:
        return Plan.get_plan_detail_by_id(plan_id)

    @staticmethod
    def update_plan_by_id(
            plan_id: int,
            plan_data: dict[str, str]
    ) -> dict[str, Any]:
        return Plan.update_plan_by_id(plan_id, plan_data["plan"])

    @staticmethod
    def delete_plan_by_id(plan_id: int) -> None:
        Plan.delete_record_by_id(plan_id)
