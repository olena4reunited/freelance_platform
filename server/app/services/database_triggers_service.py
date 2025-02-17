from server.app.database.database import PostgresDatabase


def create_trigger_delete_blocked_records():
    with PostgresDatabase() as db:
        db.execute_query(
            """
                CREATE OR REPLACE FUNCTION delete_blocked_records()
                RETURNS TRIGGER AS $$
                    BEGIN
                        DELETE FROM orders
                        WHERE blocked_until IS NULL AND is_blocked = TRUE;
                
                        RETURN NULL;
                    END;
                $$ LANGUAGE plpgsql;
            """
        )

        db.execute_query(
            """
                CREATE TRIGGER trigger_delete_blocked_orders
                AFTER UPDATE ON orders
                FOR EACH STATEMENT
                EXECUTE PROCEDURE delete_blocked_records();
            """
        )

def create_trigger_delete_blocked_users():
    with PostgresDatabase() as db:
        db.execute_query(
            """
                CREATE OR REPLACE FUNCTION delete_blocked_users()
                RETURNS TRIGGER AS $$
                    BEGIN
                        DELETE FROM users
                        WHERE block_expired IS NULL AND is_blocked = TRUE;
                
                        RETURN NULL;
                    END;
                $$ LANGUAGE plpgsql;
            """
        )

        db.execute_query(
            """
                CREATE TRIGGER trigger_delete_blocked_users
                AFTER UPDATE ON users
                FOR EACH STATEMENT
                EXECUTE PROCEDURE delete_blocked_users();
            """
        )
