from typing import Any

from server.app.models.plan_model import Plan


class AdminPlansController:
    @staticmethod
    def get_all_plans() -> list[dict[str, Any]] | dict[str, Any]:
        return Plan.get_all_records()

    @staticmethod
    def get_plan_by_id(plan_id: int) -> dict[str, Any] | None:
        return Plan.get_plan_detail_by_id(plan_id)
