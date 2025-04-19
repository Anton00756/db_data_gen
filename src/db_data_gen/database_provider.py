"""Module for DB"""

import psycopg2
from psycopg2.extensions import cursor as db_cursor


class DB:
    """Context manager for DB"""

    conn = None
    cursor = None

    def __init__(self, config):
        self.config = config

    def __enter__(self) -> db_cursor:
        self.conn = psycopg2.connect(**self.config)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, *args):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
