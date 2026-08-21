import pymysql
from typing import Optional
from common.config import settings
from common.logger import log

def get_db_connection() -> Optional[pymysql.Connection]:
    """
    Creates and returns a MySQL database connection with DictCursor.
    """
    try:
        conn = pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASS,
            database=settings.DB_NAME,
            port=settings.DB_PORT,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            autocommit=True,
            charset="utf8mb4"
        )
        return conn
    except Exception as e:
        log.error(f"Failed to connect to MySQL database at {settings.DB_HOST}: {e}")
        return None
