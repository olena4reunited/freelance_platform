from server.app.database.database import PostgresDatabase


def alter_users_table():
    query = "ALTER TABLE users ADD COLUMN username VARCHAR(64) NOT NULL;"

    with PostgresDatabase() as db:
        db.execute_query(query)
