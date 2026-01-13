"""SQLite database configuration and initialization."""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

from ..core.config import settings

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """
    Get a database connection.

    Returns:
        SQLite connection object
    """
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database with required tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT UNIQUE NOT NULL,
                plan_type TEXT NOT NULL,
                context TEXT NOT NULL,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                estimated_hours REAL,
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans (plan_id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plans_plan_id
            ON plans(plan_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_plan_id
            ON tasks(plan_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status)
        """)

        conn.commit()
        conn.close()

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
