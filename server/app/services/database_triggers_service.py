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
        db.execute_query(
            """
                CREATE OR REPLACE FUNCTION update_user_rating()
                RETURNS TRIGGER AS $$
                    BEGIN
                        WITH aggregated_rating AS (
                            SELECT avg(rate) AS avg_rating, profile_id
                            FROM users_profile_feedbacks
                            WHERE profile_id = NEW.profile_id
                            GROUP BY profile_id
                        )
                        UPDATE users
                        SET rating = aggr.avg_rating
                        FROM aggregated_rating aggr
                        WHERE id = aggr.profile_id;
                        RETURN NULL;
                    END;
                $$ LANGUAGE plpgsql;
            """
        )


def create_triggers():
    with PostgresDatabase(on_commit=True) as db:
        db.execute_query(
            """
                CREATE OR REPLACE TRIGGER trigger_set_blocked_timestamp_orders
                AFTER UPDATE ON orders
                FOR EACH STATEMENT
                EXECUTE PROCEDURE set_blocked_timestamp_orders();
            """
        )
        db.execute_query(
            """
                CREATE OR REPLACE TRIGGER trigger_set_blocked_timestamp_users
                AFTER UPDATE ON users
                FOR EACH STATEMENT
                EXECUTE PROCEDURE set_blocked_timestamp_users();
            """
        )
        db.execute_query(
            """
                CREATE OR REPLACE TRIGGER trigger_update_user_rating
                AFTER INSERT OR UPDATE ON users_profile_feedbacks
                FOR EACH STATEMENT
                EXECUTE PROCEDURE update_user_rating();
            """
        )


if __name__ == "__main__":
    create_routines()
    create_triggers()
