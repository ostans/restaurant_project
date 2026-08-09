import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from src import log
from src.utils.exceptions import (
    DatabaseConnectionError,
    DuplicateItemError,
    InvalidDateFormatError,
)

load_dotenv()


def check_connection(func):
    def wrapper(self, *args, **kwargs):
        if self.conn is None:
            self.connect()
        return func(self, *args, **kwargs)

    return wrapper


class Database:
    def __init__(self) -> None:
        self.log = log.bind(service="DatabaseConnection")
        self.conn = self.connect()

    def connect(self):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("NAME"),
                user=os.getenv("PG_USER"),
                password=os.getenv("PASSWORD"),
                host=os.getenv("HOST"),
                port=os.getenv("PORT"),
            )
            self.log.success("Connected to the database successfully")
            return conn
        except Exception as e:
            self.log.error(f"Failed to connect to the database: {e}")
            raise DatabaseConnectionError()

    @check_connection
    def execute(self, query, params=None, fetch=None):

        cursor_factory = psycopg2.extras.RealDictCursor if fetch else None
        try:
            with self.conn.cursor(cursor_factory=cursor_factory) as cursor:
                cursor.execute(query, params or ())
                result = None
                if fetch == "one":
                    result = cursor.fetchone()
                elif fetch == "all":
                    result = cursor.fetchall()
            self.conn.commit()
            self.log.success("Query executed successfully")
            return result
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            self.log.error(f"{e.diag.constraint_name} {e}")
            raise DuplicateItemError()
        except (
            psycopg2.errors.InvalidDatetimeFormat,
            psycopg2.errors.DatetimeFieldOverflow,
        ) as e:
            self.conn.rollback()
            self.log.error(f"Invalid date format: {e}")
            raise InvalidDateFormatError()
        except Exception as e:
            self.conn.rollback()
            self.log.error(f"Failed to execute query: {e}")
            raise
