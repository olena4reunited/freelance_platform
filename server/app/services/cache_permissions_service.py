import json

from server.app.utils.redis_client import redis_client
from server.app.database.database import PostgresDatabase


def load_permissions():
    with PostgresDatabase() as db:
        rows = db.fetch(
            """
                WITH selected_pp AS (
                    SELECT pln.id AS id, pln.name AS name, prm.name AS permission 
                    FROM plans pln
                    JOIN plans_permissions pp ON pp.plan_id = pln.id
                    JOIN permissions prm ON pp.permission_id = prm.id
                )
                SELECT id, name, permission 
                FROM selected_pp;
            """,
            is_all=True
        )

    plans_permissions = {}
    for row in rows:
        row = dict(row)
        if row.get("id") not in plans_permissions:
            plans_permissions[row.get("id")] = {
                "name": row.get("name"),
                "permissions": []
            }
        plans_permissions[row.get("id")]["permissions"].append(row.get("permission"))

    for plan_id, data in plans_permissions.items():
        key = data["name"]
        redis_client.hset(key, mapping={
            "permissions": json.dumps(data["permissions"])
        })


if __name__ == '__main__':
    load_permissions()
