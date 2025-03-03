import json
import os

import psycopg2
from psycopg2.extras import RealDictCursor

from server.app.utils.exceptions import GlobalException


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as config_file:
        return json.load(config_file)


class PostgresDatabase:
    def __init__(self, on_commit: bool = False):
        self.config = load_config()
        self.connection = None
        self.on_commit = on_commit

    def __enter__(self):
        try:
            self.connection = psycopg2.connect(**self.config)
            self.connection.autocommit = False
        except Exception as e:
             GlobalException.CustomHTTPException.raise_exception(
                 status_code=500,
                 detail=f"Could not connect to PostgreSQL: {e}"
             )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.connection.rollback()
        if self.on_commit:
            self.connection.commit()
        self.connection.close()

    def execute_query(self, query: str, params: tuple | None = None) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

    def fetch(self, query: str, params: tuple | None = None, is_all: bool = False) -> list[dict] | dict[str,None] | None:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall() if is_all else cursor.fetchone()
            return result if result else {} if not is_all else []
