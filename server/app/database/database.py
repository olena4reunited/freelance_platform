import json
import os

import psycopg2


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as config_file:
        return json.load(config_file)


class PostgresDatabase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.config = load_config()
            self.connection = None
            self.initialized = True

    def __enter__(self):
        if not self.connection:
            try:
                self.connection = psycopg2.connect(**self.config)
            except Exception as e:
                print(f"Database connection error: {e}")
                raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.connection.rollback()
        else:
            self.connection.commit()

        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: tuple | None = None) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

    def fetch_one(self, query: str, params: tuple | None = None) -> dict:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple | None = None) -> list[dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


database = PostgresDatabase()
