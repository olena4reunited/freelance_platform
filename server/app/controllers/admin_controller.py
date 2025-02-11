from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.models import Permission


class AdminController:
    @staticmethod
    def get_all_permissions() -> list[dict[str, str]] | dict[str, str]:
        return Permission.get_permissions()

    @staticmethod
    def get_all_permissions_by_plan(plan_name: str) -> list[dict[str, str]] | dict[[str, str]]:
        return Permission.get_permissions(plan_name)

    @staticmethod
    def create_permission(
            permission_data: dict[str, Any]
    ) -> list[dict[str, str]] | dict[str, str]:
        plan_names = permission_data["plans"] if permission_data["plans"] else ["admin"]

        if isinstance(plan_names, str):
            plan_names = list({plan_names, 'admin'})
        elif isinstance(plan_names, list):
            plan_names = list(set(plan_names + ['admin']))

        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                     WITH selected_plans AS (
                        SELECT id, name from plans
                        WHERE name = ANY(%s)
                    ), inserted_permission AS (
                        INSERT INTO permissions (name)
                        VALUES (%s)
                        RETURNING id, name
                    ), inserted_pp AS (
                        INSERT INTO plans_permissions (plan_id, permission_id)
                        SELECT sp.id, ip.id 
                        FROM selected_plans sp, inserted_permission ip
                    )
                    SELECT selected_plans.name AS plan, inserted_permission.name AS permission
                    FROM selected_plans, inserted_permission;
                """,
                (plan_names, permission_data["permission"]),
                is_all=True
            )
