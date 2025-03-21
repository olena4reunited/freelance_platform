import os

from server.app.database.database import PostgresDatabase


def apply_migrations():
   with PostgresDatabase() as db:
       for filename in sorted(os.listdir("sql")):
            if filename.endswith("_up.sql"):
                with open(os.path.join("sql", filename), "r") as file:
                    db.execute_query(file.read())


if __name__ == "__main__":
    apply_migrations()
