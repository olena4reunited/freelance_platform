from typing import Any

from server.app.database.database import PostgresDatabase
from server.app.models.permission_model import Permission


class AdminPermissionsController:
    @staticmethod
    def get_all_permissions() -> list[dict[str, str]] | dict[str, str]:
        return Permission.get_permissions()

    @staticmethod
    def get_all_permissions_by_plan(plan_name: str) -> list[dict[str, str]] | dict[[str, str]]:
        return Permission.get_permissions_by_plan(plan_name)

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

    @staticmethod
    def get_permission_by_id(permission_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT prm.name AS permission, pln.name AS plan
                    FROM permissions prm
                    LEFT JOIN plans_permissions pp ON pp.permission_id = prm.id
                    LEFT JOIN plans pln ON pln.id = pp.plan_id
                    WHERE prm.id = %s;
                """,
                (permission_id,),
                is_all=True
            )

    @staticmethod
    def update_permission(
            permission_id: int,
            permission_data: dict[str, Any]
    ) -> list[dict[str, Any]] | dict[str, Any]:
        updated_permission = permission_data.get("permission", None)
        updated_plans = permission_data.get("plans", None)

        with PostgresDatabase(on_commit=True) as db:
            if not updated_plans:
                updated_plans = db.fetch(
                    """
                        SELECT pln.name AS plan
                        FROM permissions prm
                        LEFT JOIN plans_permissions pp ON pp.permission_id = prm.id
                        LEFT JOIN plans pln ON pln.id = pp.plan_id
                        WHERE prm.id = %s;
                    """,
                    (permission_id,),
                    is_all=True
                )
                updated_plans = [plan.get("plan") for plan in updated_plans]

            return db.fetch(
                """
                    WITH updated_permission AS (
                        UPDATE permissions
                        SET name = COALESCE(%s, name)
                        WHERE id = %s
                        RETURNING id, name
                    ), deleted_plans AS (
                        DELETE FROM plans_permissions
                        WHERE permission_id = %s
                    ), inserted_plans_permissions AS (
                        INSERT INTO plans_permissions (permission_id, plan_id)
                        SELECT %s, id
                        FROM plans
                        WHERE name = ANY(%s)
                        ON CONFLICT (plan_id, permission_id) 
                        DO UPDATE SET 
                            permission_id = EXCLUDED.permission_id, 
                            plan_id = EXCLUDED.plan_id
                    )
                    SELECT prm.name AS permission, pln.name AS plan
                    FROM permissions prm
                    LEFT JOIN plans_permissions pp ON pp.permission_id = prm.id
                    LEFT JOIN plans pln ON pln.id = pp.plan_id
                    WHERE prm.id = %s;
                """,
                (updated_permission, permission_id, permission_id, permission_id, updated_plans, permission_id),
                is_all=True
            )

    @staticmethod
    def delete_permission(permission_id: int) -> None:
        Permission.delete_record_by_id(permission_id)

