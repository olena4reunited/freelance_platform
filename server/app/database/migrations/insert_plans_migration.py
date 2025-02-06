from server.app.database.database import PostgresDatabase


def insert_plans():
    query = (
        """
        INSERT INTO plans (name)
        VALUES
            ('admin'),
            ('moderator'),
            ('customer'),
            ('performer'); 
        """
    )

    with PostgresDatabase() as db:
        db.execute_query(query)
