import os

from server.app.database.database import PostgresDatabase


def rollback_migrations():
    with PostgresDatabase() as db:
        for filename in sorted(os.listdir("sql"), reverse=True):
            if filename.endswith("_down.sql"):
                with open(os.path.join("sql", filename), "r") as file:
                    db.execute_query(file.read())


if __name__ == "__main__":
    rollback_migrations()