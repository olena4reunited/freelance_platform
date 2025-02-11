BEGIN;

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
        INSERT INTO permissions (name)
        VALUES (permission_record.name)
        RETURNING id INTO perm_id;

        FOR plan_name IN
            SELECT jsonb_array_elements_text(permission_record.plans)
        LOOP
            INSERT INTO plans_permissions (plan_id, permission_id)
            SELECT id, perm_id
            FROM plans
            WHERE name = plan_name;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMIT;