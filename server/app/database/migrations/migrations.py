from server.app.database.database import connect_db


def create_initial_migration():
    conn = connect_db()
    if not conn:
        return

    queries = [
        """
        CREATE TABLE IF NOT EXISTS plans (
            id SERIAL PRIMARY KEY,
            name VARCHAR(32) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS permissions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(32) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS plans_permissions (
            id SERIAL PRIMARY KEY,
            plan_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            UNIQUE (plan_id, permission_id),
            FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(64) NOT NULL,
            last_name VARCHAR(64) NOT NULL,
            email VARCHAR(128) UNIQUE NOT NULL,
            phone_number VARCHAR(12) UNIQUE,
            password VARCHAR(256) NOT NULL,
            photo_link TEXT,
            description TEXT,
            is_verified BOOLEAN DEFAULT FALSE NOT NULL,
            block_expired TIMESTAMP NULL,
            delete_date DATE NULL,
            balance REAL,
            rating SMALLINT CHECK (rating > 0 AND rating <= 5),
            plan_id INTEGER NOT NULL,
            FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE SET NULL
        );
        """
    ]

    with conn.cursor() as cursor:
        for query in queries:
            cursor.execute(query)

        conn.commit()

    conn.close()
