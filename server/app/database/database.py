import json
import os

import psycopg2

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as config_file:
        return json.load(config_file)


config = load_config()


def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=config["DB_NAME"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
            host=config["DB_HOST"],
            port=config["DB_PORT"],
        )
        return conn
    except Exception as e:
        print(e)
        return None
