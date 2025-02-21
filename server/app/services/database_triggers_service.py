from server.app.database.database import PostgresDatabase


def create_routines():
    with PostgresDatabase(on_commit=True) as db:
        db.execute_query(
            """
                CREATE OR REPLACE FUNCTION set_blocked_timestamp_orders()
                RETURNS TRIGGER AS $$
                    BEGIN
                        IF NEW.blocked_until is NULL AND NEW.is_blocked = TRUE THEN
                            NEW.blocked_until = CURRENT_TIMESTAMP + INTERVAL '30 days';
                        END IF;
                        RETURN NEW;
                    END;
                $$ LANGUAGE plpgsql;
            """
        )

        db.execute_query(
            """
                CREATE OR REPLACE FUNCTION set_blocked_timestamp_users()
                RETURNS TRIGGER AS $$
                    BEGIN
                        IF NEW.block_expired is NULL AND NEW.is_blocked = TRUE THEN
                            NEW.block_expired = CURRENT_TIMESTAMP + INTERVAL '30 days';
                        END IF;
                        RETURN NEW;
                    END;
                $$ LANGUAGE plpgsql;
            """
        )


def create_triggers():
    with PostgresDatabase(on_commit=True) as db:
        db.execute_query(
            """
                CREATE TRIGGER trigger_set_blocked_timestamp_orders
                AFTER UPDATE ON orders
                FOR EACH STATEMENT
                EXECUTE PROCEDURE set_blocked_timestamp_orders();
            """
        )

        db.execute_query(
            """
                CREATE TRIGGER trigger_set_blocked_timestamp_users
                AFTER UPDATE ON users
                FOR EACH STATEMENT
                EXECUTE PROCEDURE set_blocked_timestamp_users();
            """
        )


if __name__ == "__main__":
    create_routines()
    create_triggers()
