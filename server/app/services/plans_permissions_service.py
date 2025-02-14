import json

from server.app.database.database import PostgresDatabase


def load_json() -> str:
    with open("plans_permissions_config.json", "r") as f:
        json_data = json.load(f)

    return json.dumps(json_data)


def insert_plans() -> None:
    with PostgresDatabase() as db:
        db.execute_query(
            """
            INSERT INTO plans (name)
            VALUES
                ('admin'),
                ('moderator'),
                ('customer'),
                ('performer');
            """
        )


def set_plans_permissions():
    with PostgresDatabase(on_commit=True) as db:
        db.execute_query(
            """
                CREATE OR REPLACE FUNCTION insert_permissions(json_data jsonb)
                RETURNS VOID AS $$
                DECLARE
                    permission_record RECORD;
                    perm_id INT;
                    plan_name TEXT;
                BEGIN
                    FOR permission_record IN
                        SELECT
                            p ->> 'name' AS name,
                            p -> 'plans' AS plans
                        FROM jsonb_array_elements(json_data) p
                        LOOP
                            BEGIN
                            
                            INSERT INTO permissions (name)
                            VALUES (permission_record.name)
                            RETURNING id INTO perm_id;
                            
                        EXCEPTION WHEN UNIQUE_VIOLATION THEN
                            CONTINUE;
                        END;
                    
                        FOR plan_name IN
                            SELECT jsonb_array_elements_text(permission_record.plans)
                        LOOP
                            BEGIN
                            
                                INSERT INTO plans_permissions (plan_id, permission_id)
                                SELECT id, perm_id
                                FROM plans
                                WHERE name = plan_name;
                            
                            EXCEPTION WHEN UNIQUE_VIOLATION THEN
                                CONTINUE;
                            
                            END;
                        END LOOP;
            
                    END LOOP;
                END;
                $$ LANGUAGE plpgsql;
            """
        )

        json_data = load_json()

        db.execute_query(
            "SELECT insert_permissions(%s::jsonb);",
            (json_data,)
        )


if __name__ == "__main__":
    set_plans_permissions()
